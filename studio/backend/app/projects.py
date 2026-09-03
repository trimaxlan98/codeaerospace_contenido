"""Servicio de Proyectos (cursos): agrupan clips ordenados con continuidad.

Un proyecto fija la calidad de render (resolucion/fps) para todos sus
clips, de forma que los videos resultantes se puedan unir sin recodificar
(`ffmpeg -f concat -c copy`). El estilo visual compartido (`style_block`)
se antepone al script de cada clip antes de renderizar; el hash del
compuesto detecta cuando un clip quedo desactualizado respecto a su
ultimo render bueno (`stale`).

Este modulo es puro (sin FastAPI, sin cola de jobs): la integracion con
la API y el JobManager llega en el Sprint 2.
"""

import hashlib
import json
import re
import time
import uuid

from . import audio_promo
from .db import Database

QUALITY_SPECS = {
    "ql": {"resolution": "854x480", "fps": 15},
    "qm": {"resolution": "1280x720", "fps": 30},
    "qh": {"resolution": "1920x1080", "fps": 60},
}
QUALITIES = set(QUALITY_SPECS)

# --- formato del lienzo -----------------------------------------------
# La calidad fija el LADO CORTO y los fps; el formato fija la PROPORCION.
# Fijar el ALTO seria otra cosa: un "1080p" en 9:16 con 1080 de alto sale
# 607x1080, que no es calidad alta sino un video pequeno.
#
# Los nombres y las proporciones son los de promo.py (la libreria que
# configura el lienzo desde dentro de la escena). Al renderizar, el
# backend le pasa por entorno el lado corto y los fps, de modo que lo que
# se anuncia aqui y lo que produce manim salen del MISMO numero.
FORMATO_DEFECTO = "horizontal"
PROPORCIONES = {
    "horizontal": (16, 9),
    "vertical": (9, 16),
    "cuadrado": (1, 1),
    # 4:3 existe para las presentaciones: auditorios con proyector
    # viejo y plantillas de tesis. Ningun curso ni promo lo usa.
    "clasico": (4, 3),
}
FORMATOS = set(PROPORCIONES)

# Fondos con nombre de una presentacion. Los hex son los MISMOS que en
# `manim_extensions/presentacion.py`, que es quien los pinta: se repiten porque
# el backend no puede importar ese modulo (vive en el contenedor, e importa
# manim). Cualquier otro valor se acepta como color "#rrggbb" a secas.
FONDOS = {
    "marca": "#05070a",
    "blanco": "#ffffff",
    "pizarra": "#0f172a",
}
FONDO_DEFECTO = "marca"
RE_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\Z")


def valida_fondo(fondo: str) -> str:
    """El fondo pedido, o ValueError. Acepta un nombre o un #rrggbb."""
    if fondo in FONDOS or RE_COLOR.match(fondo or ""):
        return fondo
    raise ValueError(f"fondo invalido: {fondo!r}"
                     f" (usa {', '.join(FONDOS)} o un #rrggbb)")

# Un promo de redes no es un curso: dura 8-15 s, va en bucle y no se
# exporta como zip concatenado. El tipo solo cambia lo que la interfaz
# ofrece; el modelo (proyecto -> clips -> jobs) es exactamente el mismo.
TIPO_DEFECTO = "curso"
# Una PRESENTACION es una animacion para una charla o una defensa de tesis:
# se entrega como .pptx, avanza cuando el ponente hace clic y su fondo lo
# elige quien presenta. Ver studio/docs/PRESENTACIONES.md.
#
# No se llama "pieza" a proposito: en este repo esa palabra ya significa el
# SEGMENTO de una pelicula montada (`pelicula.py`, `ensamblar.py`) y tambien
# una plantilla de curso ("Pieza de simulacion"). Un tercer significado en la
# misma app habria sido imposible de leer.
TIPOS = {"curso", "promo", "presentacion"}


def specs(quality: str, formato: str = FORMATO_DEFECTO) -> dict:
    """Resolucion y fps reales de un proyecto, segun calidad y formato.

    En horizontal devuelve la tabla de manim tal cual: 854x480 no es
    exactamente 16:9, y es lo que produce el flag `-ql`. Anunciar 852x480
    seria mentir sobre el archivo que sale.
    """
    if quality not in QUALITY_SPECS:
        raise ValueError(f"calidad invalida: {quality}")
    if formato not in PROPORCIONES:
        raise ValueError(f"formato invalido: {formato}")
    base = QUALITY_SPECS[quality]
    ancho, alto = (int(v) for v in base["resolution"].split("x"))
    corto = min(ancho, alto)
    if formato == "horizontal":
        px_ancho, px_alto = ancho, alto
    else:
        p_ancho, p_alto = PROPORCIONES[formato]
        largo = round(corto * max(p_ancho, p_alto) / min(p_ancho, p_alto))
        largo -= largo % 2  # libx264 exige lados pares
        px_ancho, px_alto = ((corto, largo) if p_alto > p_ancho
                             else (largo, corto))
    return {"resolution": f"{px_ancho}x{px_alto}", "fps": base["fps"],
            "width": px_ancho, "height": px_alto, "corto": corto,
            "formato": formato}

STYLE_MARKER = "# --- fin estilo del proyecto ---"


def compose_script(style_block: str, script: str) -> str:
    """Antepone el estilo del proyecto al script del clip.

    Sin estilo (vacio o solo espacios) devuelve el script tal cual, para
    que los proyectos sin `style_block` se comporten igual que un render
    suelto de hoy.
    """
    if not style_block.strip():
        return script
    return f"{style_block.rstrip()}\n\n{STYLE_MARKER}\n\n{script}"


def content_hash(style_block: str, script: str, scene: str) -> str:
    """sha256 hex del script compuesto (estilo + clip) mas la escena.

    La escena participa del hash a proposito: dos renders del mismo script
    compuesto pero con `scene` distinta producen videos distintos (el
    script puede definir varias escenas, p.ej. Intro y Outro), asi que un
    cambio de escena sin tocar el script debe marcar el clip como `stale`
    igual que un cambio de script. La combinacion es determinista: mismo
    (style_block, script, scene) siempre produce el mismo hash.
    """
    composed = compose_script(style_block, script)
    digest = hashlib.sha256(composed.encode("utf-8"))
    digest.update(b"\n# scene: " + scene.encode("utf-8"))
    return digest.hexdigest()


def style_offset(style_block: str) -> int:
    """Lineas que el estilo antepone al script del clip (0 si no hay estilo)."""
    if not style_block.strip():
        return 0
    return len(compose_script(style_block, "X").splitlines()) - 1


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
    return slug or "clip"


def project_slug(name: str) -> str:
    """Slug de nombre de proyecto, para el nombre de archivo del zip."""
    return _slugify(name)


def clip_public(clip: dict) -> dict:
    """Vista del clip sin el script completo (evita respuestas pesadas).

    El manifiesto de audio tampoco viaja en el listado: se pide aparte
    (`GET .../clips/{cid}/audio`), y aqui solo se dice si existe.
    """
    public = {k: v for k, v in clip.items() if k not in ("script", "audio_json")}
    public["script_len"] = len(clip.get("script") or "")
    public["has_audio"] = bool(clip.get("audio_json"))
    return public


class ProjectService:
    def __init__(self, db: Database) -> None:
        self.db = db

    # ── proyectos ────────────────────────────────────────────────────────────

    def create_project(self, name: str, description: str, quality: str,
                        style_block: str, tipo: str = TIPO_DEFECTO,
                        formato: str = FORMATO_DEFECTO,
                        fondo: str = FONDO_DEFECTO,
                        estilo: str = "") -> dict:
        if quality not in QUALITIES:
            raise ValueError(f"calidad invalida: {quality}")
        if tipo not in TIPOS:
            raise ValueError(f"tipo invalido: {tipo}")
        if formato not in FORMATOS:
            raise ValueError(f"formato invalido: {formato}")
        valida_fondo(fondo)
        now = time.time()
        project = {
            "id": uuid.uuid4().hex[:16],
            "name": name,
            "description": description or "",
            "quality": quality,
            "style_block": style_block or "",
            "tipo": tipo,
            "formato": formato,
            "fondo": fondo,
            # Estilo con nombre ("lienzo"): dato del manifiesto, no del
            # render. Se acota para que un curso.json cualquiera no meta
            # una novela en la columna.
            "estilo": (estilo or "")[:40],
            "created_at": now,
            "updated_at": now,
        }
        self.db.insert_project(project)
        return project

    def duplicar_project(self, pid: str, name: str) -> dict:
        """Copia el proyecto y sus clips SIN sus renders.

        Se copia lo que define como se ve y como suena (estilo compartido,
        formato, calidad, fondo, y por clip script/escena/notas/manifiesto de
        audio); no se copian `job_id` ni `rendered_hash`, porque un video es
        de UN clip: dos clips apuntando al mismo mp4 harian que borrarlo
        dejara sin render a un proyecto que nadie estaba tocando.
        """
        origen = self.db.get_project(pid)
        if not origen:
            raise ValueError("proyecto no encontrado")
        if any(p["name"] == name for p in self.db.list_projects()):
            raise ValueError(f"ya existe un proyecto llamado {name!r}")
        copia = self.create_project(
            name, origen.get("description") or "", origen["quality"],
            origen.get("style_block") or "",
            tipo=origen.get("tipo") or TIPO_DEFECTO,
            formato=origen.get("formato") or FORMATO_DEFECTO,
            fondo=origen.get("fondo") or FONDO_DEFECTO,
            estilo=origen.get("estilo") or "")
        for clip in self.db.list_clips(pid):
            nuevo = self.add_clip(copia["id"], clip["title"],
                                  script=clip.get("script") or "",
                                  scene=clip.get("scene") or "")
            self.update_clip(nuevo["id"],
                             final_state=clip.get("final_state") or "",
                             notes=clip.get("notes") or "",
                             audio_json=clip.get("audio_json"))
        return copia

    def duplicar_clip(self, pid: str, cid: str) -> dict:
        """Inserta una copia del clip JUSTO DESPUES del original.

        Detras de un clip es donde se lo quiere: duplicar un clip es casi
        siempre "hazme una variante de este", y variante y original se
        comparan mirandolos uno al lado del otro.
        """
        clip = self.db.get_clip(cid)
        if not clip or clip.get("project_id") != pid:
            raise ValueError("clip no encontrado")
        copia = self.add_clip(pid, f"{clip['title']} (copia)",
                              script=clip.get("script") or "",
                              scene=clip.get("scene") or "",
                              position=clip["position"] + 1)
        return self.update_clip(copia["id"],
                                final_state=clip.get("final_state") or "",
                                notes=clip.get("notes") or "",
                                audio_json=clip.get("audio_json"))

    def get_project_detail(self, pid: str) -> dict | None:
        project = self.db.get_project(pid)
        if not project:
            return None
        # El estado del audio solo se calcula en promos: un curso no lleva
        # cama de sonido (su voz va por Narracion) y son ~18 clips por
        # proyecto a los que no hay que consultarles el job.
        es_promo = (project.get("tipo") or TIPO_DEFECTO) == "promo"
        clips = []
        for clip in self.db.list_clips(pid):
            expected = content_hash(project["style_block"], clip.get("script") or "",
                                    clip.get("scene") or "")
            has_render = bool(clip.get("job_id"))
            stale = has_render and clip.get("rendered_hash") != expected
            if not has_render:
                status = "no_render"
            elif stale:
                status = "stale"
            else:
                status = "rendered"
            entrada = {**clip_public(clip), "stale": stale, "status": status}
            # El estado de la cama de sonido es de los dos tipos desde el
            # sprint E3 (un curso tambien la lleva, sin voz). La VERIFICACION
            # sigue siendo solo del promo: mide la costura del bucle y el
            # rango 8-15 s, que en un curso no significan nada.
            entrada["audio"] = self.estado_audio(clip)
            if es_promo:
                entrada["verificacion"] = self.estado_verificacion(clip)
            clips.append(entrada)
        # `specs` viaja con el detalle para que la interfaz sepa la
        # proporcion del lienzo antes de que exista el primer render (y no
        # tenga que repetir la tabla de calidades en JavaScript).
        return {**project, "clips": clips,
                "specs": specs(project["quality"],
                               project.get("formato") or FORMATO_DEFECTO)}

    def list_projects_summary(self, extra=None) -> list[dict]:
        """Resumen por proyecto para el indice de cursos.

        `extra(project, clips) -> dict` inyecta campos calculados fuera de
        este servicio (hoy: el estado de narracion, que vive en
        NarracionService) sin volver a recorrer los clips de los ~60 cursos.
        """
        summaries = []
        for project in self.db.list_projects():
            clips = self.db.list_clips(project["id"])
            rendered_count = stale_count = 0
            for clip in clips:
                if not clip.get("job_id"):
                    continue
                expected = content_hash(project["style_block"], clip.get("script") or "",
                                        clip.get("scene") or "")
                if clip.get("rendered_hash") != expected:
                    stale_count += 1
                else:
                    rendered_count += 1
            public = {k: v for k, v in project.items() if k != "style_block"}
            summaries.append({
                **public,
                "clip_count": len(clips),
                "rendered_count": rendered_count,
                "stale_count": stale_count,
                **(extra(project, clips) if extra else {}),
            })
        return summaries

    # ── audio del promo ──────────────────────────────────────────────────────

    def manifiesto_audio(self, clip: dict, voz_defecto: str = "Charon",
                         tipo: str = "promo") -> dict:
        """Manifiesto normalizado del clip (el vacio si aun no tiene).

        `tipo` solo decide el pico por defecto de una cama nueva: la de un
        clip de curso nace por debajo de la voz, porque ese clip se narra.
        """
        crudo = clip.get("audio_json")
        try:
            guardado = json.loads(crudo) if crudo else None
        except ValueError:
            guardado = None
        if guardado is None and tipo == "curso":
            return audio_promo.vacio(voz_defecto, "curso")
        return audio_promo.normalizar(guardado, voz_defecto)

    def estado_audio(self, clip: dict) -> dict:
        """Como esta la mezcla de este clip.

          sin_manifiesto  no se ha escrito nada todavia
          sin_render      hay manifiesto pero el clip no tiene video vigente
          sin_mezclar     hay manifiesto y video, pero nadie ha mezclado
          desactualizado  se mezclo, pero despues cambio el manifiesto o el video
          al_dia          el mp4 que sirve la app suena como dice el manifiesto
        """
        if not clip.get("audio_json"):
            return {"estado": "sin_manifiesto", "has_audio": False}
        job_id = clip.get("job_id")
        job = self.db.get_job(job_id) if job_id else None
        if not job or job.get("status") != "done":
            return {"estado": "sin_render", "has_audio": False}
        esperado = audio_promo.hash_mezcla(self.manifiesto_audio(clip), job_id)
        if not job.get("audio_path"):
            return {"estado": "sin_mezclar", "has_audio": False}
        al_dia = job.get("audio_hash") == esperado
        return {"estado": "al_dia" if al_dia else "desactualizado",
                "has_audio": True}

    def informe_verificacion(self, clip: dict) -> dict | None:
        """El ultimo informe medido del clip, o None."""
        job_id = clip.get("job_id")
        job = self.db.get_job(job_id) if job_id else None
        if not job or not job.get("verify_json"):
            return None
        try:
            return json.loads(job["verify_json"])
        except ValueError:
            return None

    def estado_verificacion(self, clip: dict) -> dict:
        """'sin_render' | 'sin_verificar' | 'desactualizada' | 'al_dia'.

        Un informe medido sobre otro archivo (otro render, u otra mezcla) no
        vale: se marca desactualizado en vez de enseñar numeros viejos.
        """
        job_id = clip.get("job_id")
        job = self.db.get_job(job_id) if job_id else None
        if not job or job.get("status") != "done":
            return {"estado": "sin_render", "ok": None}
        if not job.get("verify_json"):
            return {"estado": "sin_verificar", "ok": None}
        informe = self.informe_verificacion(clip) or {}
        al_dia = job.get("verify_hash") == audio_promo.hash_verificacion(job)
        return {"estado": "al_dia" if al_dia else "desactualizada",
                "ok": bool(informe.get("ok"))}

    def update_project(self, pid: str, **fields) -> dict:
        # Calidad y formato definen el archivo que sale del render: si ya
        # hay videos, cambiarlos dejaria clips de dos tamanos distintos en
        # el mismo proyecto (y un `concat -c copy` que no pega).
        # El fondo entra en la lista por la misma razon, aunque no cambie el
        # TAMANO del archivo: cambiarlo con renders vigentes dejaria un deck
        # con slides de dos colores distintos.
        NOMBRES = {"quality": "la calidad", "formato": "el formato",
                   "fondo": "el fondo"}
        fijos = [k for k in ("quality", "formato", "fondo") if k in fields]
        if fijos:
            clips = self.db.list_clips(pid)
            if any(c.get("job_id") for c in clips):
                que = " ni ".join(NOMBRES[k] for k in fijos)
                raise ValueError(
                    f"no se puede cambiar {que}: hay clips con render vigente"
                )
        if "formato" in fields and fields["formato"] not in FORMATOS:
            raise ValueError(f"formato invalido: {fields['formato']}")
        if "fondo" in fields:
            valida_fondo(fields["fondo"])
        fields["updated_at"] = time.time()
        self.db.update_project(pid, **fields)
        return self.db.get_project(pid)

    def delete_project(self, pid: str) -> None:
        # Los jobs conservan project_id/clip_id como texto historico: solo
        # se borran las filas de projects/clips (los jobs quedan sueltos).
        self.db.delete_project(pid)

    # ── clips ────────────────────────────────────────────────────────────────

    def add_clip(self, pid: str, title: str, script: str = "", scene: str = "",
                 position: int | None = None, adopt_job: dict | None = None) -> dict:
        project = self.db.get_project(pid)
        if not project:
            raise ValueError("proyecto no encontrado")

        job_id = None
        rendered_hash = None
        if adopt_job:
            script = adopt_job.get("script") or ""
            scene = adopt_job.get("scene") or ""
            composed = compose_script(project["style_block"], script)
            # Solo se adopta como render vigente un job terminado con video real;
            # la API no filtra por estado (la UI si) y un job error/queued
            # dejaria un clip "renderizado" sin video exportable.
            if (adopt_job.get("quality") == project["quality"]
                    and composed == adopt_job.get("script")
                    and adopt_job.get("status") == "done"
                    and adopt_job.get("video_path")):
                job_id = adopt_job.get("id")
                rendered_hash = content_hash(project["style_block"], script, scene)

        existing = self.db.list_clips(pid)
        n = len(existing)
        if position is None:
            position = n
        else:
            position = max(0, min(position, n))

        cid = uuid.uuid4().hex[:16]
        now = time.time()
        clip = {
            "id": cid, "project_id": pid, "position": position, "title": title,
            "script": script, "scene": scene, "final_state": "", "notes": "",
            "job_id": job_id, "rendered_hash": rendered_hash,
            "created_at": now, "updated_at": now,
        }
        self.db.insert_clip(clip)

        ordered_ids = [c["id"] for c in existing]
        ordered_ids.insert(position, cid)
        self.db.renumber_clips(pid, ordered_ids)

        if job_id:
            # El job adoptado debe apuntar de vuelta al clip/proyecto: sin
            # esto el job queda "suelto" (clip_id/project_id en None) y la
            # Biblioteca no puede avisar "el clip quedara sin video" al
            # borrarlo (lee j.clip_id). La proteccion de purgas ya funciona
            # via clips.job_id; esto es solo la señal para la UI.
            self.db.update_job(job_id, clip_id=cid, project_id=pid)

        return self.db.get_clip(cid)

    def update_clip(self, cid: str, **fields) -> dict:
        fields["updated_at"] = time.time()
        self.db.update_clip(cid, **fields)
        return self.db.get_clip(cid)

    def move_clip(self, pid: str, cid: str, position: int) -> None:
        # list+renumber en una sola seccion critica (evita la carrera entre
        # leer el orden y renumerar que existia con list_clips+renumber_clips).
        if self.db.reorder_clips(pid, cid, position) is None:
            raise ValueError("clip no encontrado en el proyecto")

    def delete_clip(self, pid: str, cid: str) -> None:
        # Misma seccion critica que move_clip; ademas valida que el clip
        # pertenezca al proyecto antes de borrar (igual que move_clip).
        if self.db.reorder_clips(pid, cid, position=None, delete=True) is None:
            raise ValueError("clip no encontrado en el proyecto")

    # ── ciclo de vida del render ─────────────────────────────────────────────

    def handle_job_done(self, job: dict) -> None:
        """Al terminar un job ligado a un clip, actualiza el render vigente.

        Solo enlaza si el clip aun existe y sigue perteneciendo al mismo
        proyecto que el job (evita colgar referencias tras borrados a
        mitad de render).
        """
        clip_id = job.get("clip_id")
        if not clip_id:
            return
        clip = self.db.get_clip(clip_id)
        if not clip or clip.get("project_id") != job.get("project_id"):
            return
        self.db.update_clip(
            clip_id,
            job_id=job["id"],
            rendered_hash=job.get("content_hash"),
            updated_at=time.time(),
        )

    # ── exportacion ──────────────────────────────────────────────────────────

    def export_manifest(self, pid: str, jobs_by_id: dict[str, dict]) -> dict:
        project = self.db.get_project(pid)
        if not project:
            raise ValueError("proyecto no encontrado")
        spec = specs(project["quality"], project.get("formato") or FORMATO_DEFECTO)

        items = []
        for clip in self.db.list_clips(pid):
            job_id = clip.get("job_id")
            if not job_id:
                continue
            job = jobs_by_id.get(job_id)
            if not job:
                continue
            expected = content_hash(project["style_block"], clip.get("script") or "",
                                    clip.get("scene") or "")
            if clip.get("rendered_hash") != expected:
                continue  # desactualizado: no entra en el manifiesto
            filename = f"{clip['position'] + 1:03d}-{_slugify(clip['title'])}.mp4"
            items.append({
                "clip_id": clip["id"],
                "position": clip["position"],
                "title": clip["title"],
                "filename": filename,
                "job_id": job_id,
                "content_hash": clip.get("rendered_hash"),
                "final_state": clip.get("final_state") or "",
                "notes": clip.get("notes") or "",
                "video_path": job.get("video_path"),
                "size_bytes": job.get("size_bytes"),
            })

        return {
            "project_id": pid,
            "name": project["name"],
            "quality": project["quality"],
            "resolution": spec["resolution"],
            "fps": spec["fps"],
            "clips": items,
        }

    def export_full_manifest(self, pid: str, jobs_by_id: dict[str, dict]) -> dict:
        """Manifiesto completo del curso, para los endpoints /export y /archive.

        A diferencia de `export_manifest` (uso interno del Sprint 1, que solo
        lista clips con render vigente), este incluye TODOS los clips del
        proyecto -- con o sin render, vigente o no -- para que la UI y el zip
        de exportacion puedan mostrar el estado completo del curso. `has_video`
        solo es `True` si el clip tiene un render vigente (no `stale`) con
        video asociado: un clip desactualizado no entra en `concat` aunque su
        video anterior siga en disco.
        """
        project = self.db.get_project(pid)
        if not project:
            raise ValueError("proyecto no encontrado")
        spec = specs(project["quality"], project.get("formato") or FORMATO_DEFECTO)

        clips = []
        concat = []
        for clip in self.db.list_clips(pid):
            job_id = clip.get("job_id")
            expected = content_hash(project["style_block"], clip.get("script") or "",
                                    clip.get("scene") or "")
            has_render = bool(job_id)
            stale = has_render and clip.get("rendered_hash") != expected
            job = jobs_by_id.get(job_id) if job_id else None
            # Alineado con /api/jobs/{id}/video (main.py): solo cuenta como
            # video vigente si el job terminó en "done" (evita ofrecer un
            # video_path de un job aún en curso o fallido).
            has_video = bool(job and job.get("status") == "done"
                             and job.get("video_path") and not stale)
            filename = f"{clip['position'] + 1:03d}-{_slugify(clip['title'])}.mp4"

            duration_s = None
            size_bytes = None
            video_path = None
            if has_video:
                started = job.get("started_at")
                finished = job.get("finished_at")
                if started is not None and finished is not None:
                    duration_s = finished - started
                size_bytes = job.get("size_bytes")
                video_path = job.get("video_path")

            clips.append({
                "clip_id": clip["id"],
                "position": clip["position"],
                "title": clip["title"],
                "scene": clip.get("scene") or "",
                "filename": filename,
                "has_video": has_video,
                "duration_s": duration_s,
                "size_bytes": size_bytes,
                "stale": stale,
                # Internos, no forman parte del manifiesto publico (se
                # descartan antes de responder / escribir manifest.json):
                "video_path": video_path,
                "job_id": job_id if has_video else None,
            })
            if has_video:
                concat.append(f"file '{filename}'")

        return {
            "project": {
                "id": project["id"],
                "name": project["name"],
                "description": project["description"],
                "quality": project["quality"],
            },
            "specs": spec,
            "generated_at": time.time(),
            "clips": clips,
            "concat": concat,
        }
