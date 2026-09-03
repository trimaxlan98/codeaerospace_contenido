"""API HTTP de Proyectos (cursos): CRUD de proyectos/clips y su enlace con
el JobManager para renderizar clips con el estilo del proyecto compuesto.

Se monta como router aparte (`make_router`) en vez de vivir en `main.py`
para no importar los globals de ahi (evita un ciclo de import): `main.py`
crea `db`/`manager`/`service` y llama a `make_router(cfg, db, manager,
service)` despues.
"""

import json
import os
import re
import tempfile
import time
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from . import importar as importar_mod
from .auth import require_auth
from .db import Database
from .jobs import JobManager
from .lotes import LoteManager
from .narracion import NarracionService
from .projects import (FONDO_DEFECTO, FORMATO_DEFECTO, FORMATOS, QUALITIES,
                       TIPOS, ProjectService, clip_public, compose_script,
                       content_hash, project_slug, style_offset, valida_fondo)
from .scenes import detect_scenes

# Script incluido en el zip del curso: pega la narracion a cada clip (silencio
# donde no la haya, apad hasta el final del video para no desincronizar el
# concat) y une el curso completo. Corre fuera de la app (requiere ffmpeg).
MUX_SH = """#!/bin/sh
# Une cada clip con su narracion y concatena el curso completo.
# Requiere ffmpeg (ffprobe y awk incluidos). Uso:  sh mux.sh
set -e
# Locale C: con LANG=es_* (y mawk) el printf de abajo escribe el ratio con
# coma decimal -> "atempo=1,1500", que ffmpeg rechaza; ademas romperia la
# comparacion con "1.0000". En el VPS no se ve porque ya corre en locale C.
export LC_ALL=C
mkdir -p con_audio
dur() {
  ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"
}
for v in [0-9][0-9][0-9]-*.mp4; do
  w="${v%.mp4}.wav"
  if [ -f "$w" ]; then
    # Si la voz es mas larga que el video, se acelera lo justo (atempo
    # preserva el tono) en vez de dejar que -shortest le corte la cola.
    r=$(awk -v a="$(dur "$w")" -v b="$(dur "$v")" 'BEGIN{
      r = (b > 0) ? a / b : 1
      if (r < 1.005) r = 1        # holgura: no vale la pena tocarlo
      if (r > 1.15) r = 1.15      # mas alla se nota; el resto se recorta
      printf "%.4f", r }')
    if [ "$r" = "1.0000" ]; then af="apad"; else
      af="atempo=$r,apad"
      echo "  $v: voz $r x mas rapida para caber en el video"
    fi
    # apad + -shortest: la voz se rellena con silencio hasta el final del
    # video, asi cada clip conserva su duracion exacta y el concat no se
    # desincroniza.
    ffmpeg -y -i "$v" -i "$w" -c:v copy -c:a aac -b:a 192k \\
      -af "$af" -shortest "con_audio/$v"
  else
    # Sin narracion: pista de silencio para que el concat no mezcle clips
    # con y sin audio.
    ffmpeg -y -i "$v" -f lavfi -i anullsrc=r=24000:cl=mono \\
      -c:v copy -c:a aac -b:a 192k -shortest "con_audio/$v"
  fi
done
# La lista se copia DENTRO de con_audio a proposito: ffmpeg resuelve las rutas
# relativas de un concat.txt respecto al directorio del propio archivo, no al
# cwd. Leerla desde ../ concatenaba los mp4 originales, sin narracion.
cp concat.txt con_audio/concat.txt
cd con_audio && ffmpeg -y -f concat -safe 0 -i concat.txt -c copy \\
  ../curso_narrado.mp4
echo "Listo: curso_narrado.mp4"
"""

LEEME_TXT = (
    "Contenido del zip:\n"
    "  NNN-*.mp4        clips renderizados en orden\n"
    "  NNN-*.wav        narracion de cada clip (si existe)\n"
    "  NNN-*.txt        texto de la narracion\n"
    "  concat.txt       lista para ffmpeg -f concat\n"
    "  manifest.json    metadatos del curso (incluye estado de narracion)\n"
    "  mux.sh           une video + narracion y concatena todo\n\n"
    "Curso completo CON narracion:\n\n"
    "  sh mux.sh        (genera curso_narrado.mp4)\n\n"
    "Curso completo SIN narracion:\n\n"
    "  ffmpeg -f concat -safe 0 -i concat.txt -c copy curso.mp4\n")

RE_JOB_ID = re.compile(r"^[a-f0-9]{8,32}$")


def _public_manifest(manifest: dict) -> dict:
    """Quita los campos internos (`video_path`, `job_id`) del manifiesto."""
    clips = [{k: v for k, v in c.items() if k not in ("video_path", "job_id")}
             for c in manifest["clips"]]
    return {**manifest, "clips": clips}


# ── modelos ───────────────────────────────────────────────────────────────────

class ProjectCreateBody(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    quality: str
    style_block: str = ""
    tipo: str = "curso"
    formato: str = FORMATO_DEFECTO
    fondo: str = FONDO_DEFECTO


class ProjectUpdateBody(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    quality: str | None = None
    style_block: str | None = None
    formato: str | None = None
    fondo: str | None = None


class ClipCreateBody(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    script: str = ""
    scene: str = Field(default="", max_length=128)
    position: int | None = None
    from_job_id: str | None = None


class ClipUpdateBody(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    script: str | None = None
    scene: str | None = None
    final_state: str | None = None
    notes: str | None = None


class MoveBody(BaseModel):
    position: int


class ImportarBody(BaseModel):
    """Import desde el repo: `studio/content/<origen>/<slug>/`."""
    slug: str = Field(min_length=1, max_length=80)
    origen: str = "cursos"


class RenderLoteBody(BaseModel):
    """Un lote de renders. `clips` a None son TODOS los del proyecto."""
    clips: list[str] | None = None
    calidad: str | None = None
    force: bool = False


class DuplicarBody(BaseModel):
    name: str = Field(min_length=1, max_length=120)


def make_router(cfg, db: Database, manager: JobManager, service: ProjectService,
                narracion: NarracionService) -> APIRouter:
    router = APIRouter(prefix="/api/projects", tags=["projects"])
    # Progreso agregado del lote de renders (ver app/lotes.py): estado en
    # memoria + derivacion desde los jobs para sobrevivir a un reinicio.
    lotes = LoteManager(db)

    def _narr_por_clip(project: dict) -> dict[str, dict]:
        """Estado publico de narracion por clip para manifest/archive."""
        try:
            estado = narracion.estado_proyecto(project)
        except Exception:
            return {}
        return {c["clip_id"]: {"estado": c["estado"], "voz": c["voz"],
                               "audio_s": c["audio_s"],
                               "has_audio": c["has_audio"],
                               "aviso_largo": c["aviso_largo"],
                               "etiqueta": c["etiqueta"]}
                for c in estado["clips"]}

    def _check_style_size(text: str) -> None:
        if len(text.encode("utf-8", errors="replace")) > cfg.max_script_bytes:
            raise HTTPException(status_code=413, detail="Bloque de estilo demasiado grande")

    def _check_clip_script_size(text: str) -> None:
        if len(text.encode("utf-8", errors="replace")) > cfg.max_script_bytes:
            raise HTTPException(status_code=413, detail="Script demasiado grande")

    def _check_script(script: str) -> None:
        if len(script.encode("utf-8", errors="replace")) > cfg.max_script_bytes:
            raise HTTPException(status_code=413, detail="Script demasiado grande")
        if not script.strip():
            raise HTTPException(status_code=422, detail="Script vacio")

    def _check_quota() -> None:
        quota = cfg.max_storage_mb * 1024 * 1024
        used = manager.storage_usage()
        if used >= quota:
            raise HTTPException(
                status_code=507,
                detail=(f"Almacenamiento lleno: {used / 2**20:.0f} MB usados de "
                        f"{cfg.max_storage_mb} MB. Borra videos de la Biblioteca "
                        "para liberar espacio."))

    def _require_project(pid: str) -> dict:
        project = db.get_project(pid)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return project

    def _require_clip(pid: str, cid: str) -> dict:
        clip = db.get_clip(cid)
        if not clip or clip.get("project_id") != pid:
            raise HTTPException(status_code=404, detail="Clip no encontrado")
        return clip

    # ── proyectos ────────────────────────────────────────────────────────────

    def _narr_resumen(project: dict, clips: list[dict]) -> dict:
        # El indice de cursos tiene que poder decir que falta narrar sin
        # abrir los ~60 cursos uno a uno. Nunca puede tumbar el listado: si
        # el directorio de guiones no existe o no se puede leer, el indice
        # sale sin ese dato.
        try:
            return narracion.resumen_audio(project, clips)
        except Exception:
            return {}

    @router.get("")
    async def list_projects(_=Depends(require_auth)):
        return {"projects": service.list_projects_summary(_narr_resumen)}

    @router.post("", status_code=201)
    async def create_project(body: ProjectCreateBody, _=Depends(require_auth)):
        if body.quality not in QUALITIES:
            raise HTTPException(status_code=422, detail="Calidad invalida (ql/qm/qh)")
        if body.tipo not in TIPOS:
            raise HTTPException(status_code=422,
                                detail="Tipo invalido (curso/promo/presentacion)")
        if body.formato not in FORMATOS:
            raise HTTPException(
                status_code=422,
                detail=f"Formato invalido ({'/'.join(sorted(FORMATOS))})")
        try:
            valida_fondo(body.fondo)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        _check_style_size(body.style_block)
        return service.create_project(body.name, body.description, body.quality,
                                      body.style_block, tipo=body.tipo,
                                      formato=body.formato, fondo=body.fondo)

    # -- importar un proyecto como archivos (paridad con subir_curso.py) ----

    async def _importar(curso: dict, dry_run: bool,
                        guiones: dict[int, list] | None = None) -> dict:
        resultado = importar_mod.aplicar(service, db, curso, dry_run)
        salida = resultado.publico()
        salida["name"] = curso["name"]
        salida["dry_run"] = dry_run
        if dry_run or not guiones or not resultado.project_id:
            return salida
        # Los guiones se restauran DESPUES de que existan los clips, y por
        # el camino de siempre (`guardar_guion`), no escribiendo archivos a
        # mano: asi el estado.json queda coherente y la narracion se marca
        # como desactualizada, que es la verdad (hay guion, no hay audio).
        project = db.get_project(resultado.project_id)
        clips = db.list_clips(resultado.project_id)
        restaurados = 0
        for pos, secciones in guiones.items():
            if pos >= len(clips):
                continue
            try:
                narracion.guardar_guion(project, clips[pos], secciones)
                restaurados += 1
            except ValueError as e:
                salida["reporte"].append(
                    f"! guion del clip {pos + 1}: {e}")
        salida["guiones"] = restaurados
        return salida

    @router.post("/importar")
    async def importar_proyecto(request: Request, dry_run: int = 0,
                                _=Depends(require_auth)):
        """Mete un curso-como-archivos en la base. Dos modos:

          - cuerpo crudo `application/zip`: el mismo layout que produce
            `GET /{pid}/fuentes.zip` (curso.json + style_block.py + clips/ +
            guiones/), tope 5 MB;
          - cuerpo JSON `{slug, origen}`: lee `studio/content/<origen>/<slug>/`
            del propio repo (`cursos`, `verticales` o `promos`).

        Idempotente por nombre exacto, igual que el CLI: actualiza los clips
        por posicion y no borra ninguno. Con `?dry_run=1` valida y reporta
        sin escribir nada.
        """
        seco = bool(dry_run)
        tipo_cuerpo = (request.headers.get("content-type") or "").split(";")[0].strip().lower()

        if tipo_cuerpo in ("application/zip", "application/x-zip-compressed",
                           "application/octet-stream"):
            tope = importar_mod.MAX_ZIP_BYTES
            largo = request.headers.get("content-length")
            if largo and largo.isdigit() and int(largo) > tope:
                raise HTTPException(status_code=413,
                                    detail=f"el zip pasa de {tope // (1024 * 1024)} MB")
            datos = await request.body()
            if len(datos) > tope:
                raise HTTPException(status_code=413,
                                    detail=f"el zip pasa de {tope // (1024 * 1024)} MB")
            with tempfile.TemporaryDirectory() as tmp:
                try:
                    raiz = importar_mod.abrir_zip(datos, Path(tmp))
                    curso = importar_mod.cargar_curso(raiz)
                    guiones = importar_mod.guiones_del_zip(raiz, curso)
                except importar_mod.ErrorImportacion as e:
                    raise HTTPException(status_code=422, detail=str(e))
                _check_style_size(curso["style_block"])
                for clip in curso["clips"]:
                    _check_clip_script_size(clip["script"])
                return await _importar(curso, seco, guiones)

        try:
            crudo = await request.json()
        except ValueError:
            raise HTTPException(
                status_code=415,
                detail="Envia un zip (Content-Type: application/zip) o un JSON "
                       "{slug, origen}")
        try:
            body = ImportarBody(**(crudo or {}))
        except Exception:
            raise HTTPException(status_code=422,
                                detail="Falta el slug del proyecto a importar")
        try:
            curso = importar_mod.cargar_del_repo(cfg.content_dir, body.origen,
                                                 body.slug)
        except importar_mod.ErrorImportacion as e:
            raise HTTPException(status_code=422, detail=str(e))
        _check_style_size(curso["style_block"])
        for clip in curso["clips"]:
            _check_clip_script_size(clip["script"])
        return await _importar(curso, seco)

    @router.get("/importables")
    async def listar_importables(_=Depends(require_auth)):
        """Los slugs que hay en `studio/content/` por origen."""
        return {"content_dir": str(cfg.content_dir),
                "origenes": importar_mod.listar_del_repo(cfg.content_dir)}

    @router.get("/{pid}")
    async def get_project(pid: str, _=Depends(require_auth)):
        detail = service.get_project_detail(pid)
        if not detail:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return detail

    @router.patch("/{pid}")
    async def update_project(pid: str, body: ProjectUpdateBody, _=Depends(require_auth)):
        _require_project(pid)
        raw = body.model_dump(exclude_unset=True)
        if "quality" in raw and raw["quality"] not in QUALITIES:
            raise HTTPException(status_code=422, detail="Calidad invalida (ql/qm/qh)")
        if "formato" in raw and raw["formato"] not in FORMATOS:
            raise HTTPException(
                status_code=422,
                detail=f"Formato invalido ({'/'.join(sorted(FORMATOS))})")
        if "fondo" in raw:
            try:
                valida_fondo(raw["fondo"])
            except ValueError as e:
                raise HTTPException(status_code=422, detail=str(e))
        if "style_block" in raw:
            _check_style_size(raw["style_block"])
        # Whitelist explicita (M3): nunca reenviar el body crudo a update_project.
        allowed = {"name", "description", "style_block", "quality", "formato",
                   "fondo"}
        fields = {k: v for k, v in raw.items() if k in allowed}
        try:
            return service.update_project(pid, **fields)
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))

    @router.delete("/{pid}")
    async def delete_project(pid: str, _=Depends(require_auth)):
        _require_project(pid)
        service.delete_project(pid)
        return {"ok": True}

    # ── clips ────────────────────────────────────────────────────────────────

    @router.get("/{pid}/clips/{cid}/script")
    async def get_clip_script(pid: str, cid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        clip = _require_clip(pid, cid)
        return {"script": clip.get("script") or "",
                "style_offset": style_offset(project["style_block"])}

    @router.post("/{pid}/clips", status_code=201)
    async def create_clip(pid: str, body: ClipCreateBody, _=Depends(require_auth)):
        _require_project(pid)
        _check_clip_script_size(body.script)

        adopt_job = None
        if body.from_job_id is not None:
            if not RE_JOB_ID.match(body.from_job_id):
                raise HTTPException(status_code=404, detail="Job no encontrado")
            adopt_job = db.get_job(body.from_job_id)
            if not adopt_job:
                raise HTTPException(status_code=404, detail="Job no encontrado")

        try:
            clip = service.add_clip(pid, body.title, script=body.script,
                                    scene=body.scene, position=body.position,
                                    adopt_job=adopt_job)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return clip_public(clip)

    @router.patch("/{pid}/clips/{cid}")
    async def update_clip(pid: str, cid: str, body: ClipUpdateBody,
                          _=Depends(require_auth)):
        _require_clip(pid, cid)
        raw = body.model_dump(exclude_unset=True)
        if "script" in raw and raw["script"] is not None:
            _check_clip_script_size(raw["script"])
        # Whitelist explicita (M3): nunca reenviar el body crudo a update_clip.
        allowed = {"title", "script", "scene", "final_state", "notes"}
        fields = {k: v for k, v in raw.items() if k in allowed}
        clip = service.update_clip(cid, **fields)
        return clip_public(clip)

    @router.delete("/{pid}/clips/{cid}")
    async def delete_clip(pid: str, cid: str, _=Depends(require_auth)):
        _require_clip(pid, cid)
        try:
            service.delete_clip(pid, cid)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return {"ok": True}

    @router.post("/{pid}/clips/{cid}/move")
    async def move_clip(pid: str, cid: str, body: MoveBody, _=Depends(require_auth)):
        _require_clip(pid, cid)
        try:
            service.move_clip(pid, cid, body.position)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        detail = service.get_project_detail(pid)
        return {"clips": detail["clips"]}

    # ── render ───────────────────────────────────────────────────────────────

    @router.post("/{pid}/clips/{cid}/render", status_code=201)
    async def render_clip(pid: str, cid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        clip = _require_clip(pid, cid)
        if not clip.get("scene"):
            raise HTTPException(status_code=422, detail="El clip no tiene escena asignada")

        script = clip.get("script") or ""
        composed = compose_script(project["style_block"], script)
        _check_script(composed)
        try:
            available = detect_scenes(composed)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Script invalido: {e}")
        if clip["scene"] not in available:
            raise HTTPException(status_code=422,
                                detail=f"La escena '{clip['scene']}' no existe en el script")
        _check_quota()

        chash = content_hash(project["style_block"], script, clip["scene"])
        return manager.create_job(composed, clip["scene"], project["quality"],
                                  timeout=cfg.default_timeout, project_id=pid,
                                  clip_id=cid, content_hash=chash,
                                  formato=project.get("formato") or FORMATO_DEFECTO,
                                  fondo=project.get("fondo") or FONDO_DEFECTO,
                                  tipo=project.get("tipo") or "curso")

    def _encolar(project: dict, cid: str) -> tuple[str | None, str | None]:
        """Encola el render de un clip. Devuelve (job_id, error): el error es
        el motivo por el que NO se encolo, en texto para el operador.

        Es el mismo camino que `POST .../clips/{cid}/render`, pero devolviendo
        el fallo en vez de lanzarlo: en un lote, un clip roto no puede tumbar
        los otros veintinueve.
        """
        clip = db.get_clip(cid)
        if not clip:
            return None, "el clip ya no existe"
        script = clip.get("script") or ""
        scene = clip.get("scene") or ""
        if not scene:
            return None, "el clip no tiene escena asignada"

        composed = compose_script(project["style_block"], script)
        try:
            _check_script(composed)
            available = detect_scenes(composed)
        except HTTPException as e:
            return None, e.detail
        except ValueError as e:
            return None, f"script invalido: {e}"
        if scene not in available:
            return None, f"la escena '{scene}' no existe en el script"
        try:
            _check_quota()
        except HTTPException as e:
            return None, e.detail

        chash = content_hash(project["style_block"], script, scene)
        job = manager.create_job(composed, scene, project["quality"],
                                 timeout=cfg.default_timeout,
                                 project_id=project["id"], clip_id=cid,
                                 content_hash=chash,
                                 formato=project.get("formato") or FORMATO_DEFECTO,
                                 fondo=project.get("fondo") or FONDO_DEFECTO,
                                 tipo=project.get("tipo") or "curso")
        return job["id"], None

    def _clips_en_vuelo(pid: str) -> set[str]:
        """Clips con un render `queued`/`running`: no se vuelven a encolar."""
        return {j["clip_id"] for j in db.project_jobs(pid)
                if j.get("clip_id") and j["status"] in ("queued", "running")}

    @router.post("/{pid}/render-stale")
    async def render_stale(pid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        detail = service.get_project_detail(pid)

        queued: list[str] = []
        skipped: list[dict] = []
        for clip_summary in detail["clips"]:
            if clip_summary["status"] not in ("stale", "no_render"):
                continue
            job_id, error = _encolar(project, clip_summary["id"])
            if error:
                skipped.append({"clip_id": clip_summary["id"], "error": error})
            else:
                queued.append(job_id)

        if queued:
            lotes.abrir(pid, queued, project["quality"], len(skipped))
        return {"queued": queued, "skipped": skipped}

    # -- lote de renders (paridad con `render_local.py --todos`) -------------

    @router.post("/{pid}/render-lote")
    async def render_lote(pid: str, body: RenderLoteBody, _=Depends(require_auth)):
        """Encola varios clips en orden, con la calidad que pida el operador.

        La calidad es del PROYECTO, no del job: si la pedida es otra, el lote
        la cambia en el proyecto antes de encolar -- que es exactamente lo que
        se hace a mano con `render_local.py --calidad qh`. Ese cambio saltaria
        el guardian de `update_project` (que protege un curso a medio
        renderizar de quedar con videos de dos tamanos), asi que solo se
        permite cuando el lote va a rehacer el curso ENTERO: con `clips`
        elegidos a dedo se responde 409 en vez de dejar el proyecto mezclado.
        """
        project = _require_project(pid)
        calidad_cambiada = None
        force = body.force

        if body.calidad is not None:
            if body.calidad not in QUALITIES:
                raise HTTPException(status_code=422,
                                    detail="Calidad invalida (ql/qm/qh)")
            if body.calidad != project["quality"]:
                if body.clips is not None:
                    raise HTTPException(
                        status_code=409,
                        detail="Cambiar la calidad rehace el curso entero: "
                               "lanza el lote sobre todos los clips")
                db.update_project(pid, quality=body.calidad,
                                  updated_at=time.time())
                calidad_cambiada = {"de": project["quality"], "a": body.calidad}
                project = db.get_project(pid)
                # La calidad NO entra en el hash de contenido (un clip no se
                # vuelve `stale` por cambiarla), asi que sin esto el lote
                # saltaria todos los clips por estar "al dia" con un video
                # del tamano viejo.
                force = True

        detail = service.get_project_detail(pid)
        por_id = {c["id"]: c for c in detail["clips"]}
        if body.clips is None:
            seleccion = list(detail["clips"])
        else:
            for cid in body.clips:
                if cid not in por_id:
                    raise HTTPException(status_code=404,
                                        detail=f"Clip no encontrado: {cid}")
            seleccion = sorted((por_id[cid] for cid in set(body.clips)),
                               key=lambda c: c["position"])

        en_vuelo = _clips_en_vuelo(pid)
        queued: list[str] = []
        saltados: list[dict] = []
        for resumen in seleccion:
            cid = resumen["id"]
            if cid in en_vuelo:
                saltados.append({"clip_id": cid,
                                 "error": "ya hay un render en curso"})
                continue
            if not force and resumen["status"] == "rendered":
                saltados.append({"clip_id": cid, "error": "al dia"})
                continue
            job_id, error = _encolar(project, cid)
            if error:
                saltados.append({"clip_id": cid, "error": error})
            else:
                queued.append(job_id)

        lote_id = (lotes.abrir(pid, queued, project["quality"], len(saltados))
                   if queued else None)
        return {"queued": queued, "lote_id": lote_id, "saltados": saltados,
                "calidad": project["quality"],
                "calidad_cambiada": calidad_cambiada}

    @router.get("/{pid}/lote")
    async def get_lote(pid: str, _=Depends(require_auth)):
        _require_project(pid)
        return {"lote": lotes.estado(pid)}

    # -- duplicar -----------------------------------------------------------

    @router.post("/{pid}/duplicar", status_code=201)
    async def duplicar_project(pid: str, body: DuplicarBody,
                               _=Depends(require_auth)):
        _require_project(pid)
        try:
            return service.duplicar_project(pid, body.name.strip())
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))

    @router.post("/{pid}/clips/{cid}/duplicar", status_code=201)
    async def duplicar_clip(pid: str, cid: str, _=Depends(require_auth)):
        _require_project(pid)
        _require_clip(pid, cid)
        try:
            return clip_public(service.duplicar_clip(pid, cid))
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ── exportacion ──────────────────────────────────────────────────────────

    def _jobs_for_project(pid: str) -> dict[str, dict]:
        jobs: dict[str, dict] = {}
        for clip in db.list_clips(pid):
            job_id = clip.get("job_id")
            if job_id and job_id not in jobs:
                job = db.get_job(job_id)
                if job:
                    jobs[job_id] = job
        return jobs

    @router.get("/{pid}/export")
    async def export_project(pid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        manifest = service.export_full_manifest(pid, _jobs_for_project(pid))
        narr = _narr_por_clip(project)
        for c in manifest["clips"]:
            c["narracion"] = narr.get(c["clip_id"])
        return _public_manifest(manifest)

    @router.get("/{pid}/fuentes.zip")
    async def export_fuentes(pid: str, _=Depends(require_auth)):
        """El proyecto como ARCHIVOS: el camino de vuelta del importador.

        No lleva videos (para eso esta `/archive`): lleva lo que hace falta
        para reconstruir el proyecto en otra base o versionarlo en git —
        curso.json, style_block.py, un .py por clip y, si los hay, los
        guiones. Reimportarlo produce el mismo proyecto, byte a byte.
        """
        project = _require_project(pid)
        clips = db.list_clips(pid)

        guiones: dict[str, Path] = {}
        destino = narracion.destino(project)
        try:
            estado = narracion.estado_proyecto(project)
        except Exception:
            estado = {"clips": []}
        for entrada in estado.get("clips", []):
            if entrada.get("has_guion"):
                guiones[entrada["clip_id"]] = destino / entrada["etiqueta"]

        datos = importar_mod.exportar_fuentes(project, clips, guiones)
        nombre = f"{project_slug(project['name'])}-fuentes.zip"
        return Response(
            content=datos, media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{nombre}"'})

    @router.get("/{pid}/archive")
    async def archive_project(pid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        manifest = service.export_full_manifest(pid, _jobs_for_project(pid))
        video_clips = [c for c in manifest["clips"] if c["has_video"]]
        if not video_clips:
            raise HTTPException(
                status_code=404,
                detail="El proyecto no tiene ningun clip con video vigente")

        narr = _narr_por_clip(project)
        for c in manifest["clips"]:
            c["narracion"] = narr.get(c["clip_id"])
        public_manifest = _public_manifest(manifest)
        guiones_dir = narracion.destino(project)

        tmp = tempfile.NamedTemporaryFile(delete=False, dir=tempfile.gettempdir(),
                                          suffix=".zip")
        tmp_path = tmp.name
        tmp.close()
        try:
            with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_STORED) as zf:
                for clip in video_clips:
                    video = Path(clip["video_path"]).resolve()
                    # Misma defensa en profundidad que /api/jobs/{id}/video: el
                    # video debe vivir dentro del directorio del job.
                    job_dir = (cfg.render_jobs_dir / clip["job_id"]).resolve()
                    if not video.is_file() or job_dir not in video.parents:
                        continue  # desaparecio a mitad de la exportacion: se salta
                    zf.write(video, arcname=clip["filename"])
                    # Narracion del clip (si existe): wav y texto con el mismo
                    # nombre base que el mp4, para que mux.sh los empareje.
                    n = clip.get("narracion")
                    if n and n.get("has_audio"):
                        stem = clip["filename"][:-len(".mp4")]
                        wav = guiones_dir / f"{n['etiqueta']}.wav"
                        txt = guiones_dir / f"{n['etiqueta']}.txt"
                        if wav.is_file():
                            zf.write(wav, arcname=f"{stem}.wav")
                        if txt.is_file():
                            zf.write(txt, arcname=f"{stem}.txt")
                zf.writestr("concat.txt",
                            "".join(f"{line}\n" for line in manifest["concat"]))
                zf.writestr("manifest.json",
                            json.dumps(public_manifest, indent=2, ensure_ascii=False))
                zf.writestr("mux.sh", MUX_SH)
                zf.writestr("LEEME.txt", LEEME_TXT)
        except BaseException:
            # Si el zip revienta a mitad (disco lleno, fallo leyendo un mp4...),
            # el tempfile queda huerfano porque el BackgroundTask que lo borra
            # solo se agenda si llegamos a construir el FileResponse.
            Path(tmp_path).unlink(missing_ok=True)
            raise

        filename = f"{project_slug(project['name'])}.zip"
        return FileResponse(tmp_path, media_type="application/zip",
                            filename=filename,
                            background=BackgroundTask(os.unlink, tmp_path))

    return router
