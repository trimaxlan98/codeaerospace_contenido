"""La pelicula de un curso: los clips en orden, su narracion y la marca, en un
solo archivo, montado dentro de la app.

Hasta ahora la union se hacia FUERA: `GET /api/projects/{pid}/archive` daba un
zip con `concat.txt` y `mux.sh`, y el operador corria ffmpeg en su maquina. Eso
funcionaba, pero significaba que ManimStudio producia piezas y no obras.

Quien monta es `studio/tools/ensamblar.py` DENTRO del contenedor manim (el unico
sitio con ffmpeg), disparado por el comando `ensamblar` del runner. El backend
solo escribe el **plan** y lee el informe: ninguna ruta del exterior llega al
runner, que trabaja siempre sobre `exports/peliculas/<project_id>/`.

Estados de la pelicula:
    sin_clips        el proyecto no tiene clips
    faltan_renders   ningun clip tiene video vigente
    sin_montar       hay material, no hay pelicula
    desactualizada   cambio un render, la narracion o las opciones
    al_dia           la pelicula corresponde a lo que hay ahora
    montando         hay una corrida en curso
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from pathlib import Path

from .narracion import etiqueta_clip, slugify
from .projects import specs

# Opciones de empalme que la API acepta. `corte` no recodifica (concat -c copy);
# el resto pasa por xfade y recodifica la pelicula entera.
TRANSICIONES = ("corte", "fundido", "negro", "blanco", "deslizar", "barrido",
                "disolver")
TRANSICION_DEFECTO = "corte"
DUR_MIN, DUR_MAX = 0.1, 3.0
DUR_DEFECTO = 0.6

NOMBRE_VIDEO = "pelicula.mp4"
NOMBRE_INFORME = "pelicula.json"
NOMBRE_PLAN = "plan.json"


class PeliculaError(Exception):
    """No se puede montar; el mensaje va tal cual al usuario."""


def normaliza_opciones(op: dict | None) -> dict:
    op = dict(op or {})
    tipo = op.get("transicion") or TRANSICION_DEFECTO
    if tipo not in TRANSICIONES:
        raise PeliculaError(f"transicion desconocida: {tipo}")
    dur = float(op.get("duracion_transicion") or DUR_DEFECTO)
    if not (DUR_MIN <= dur <= DUR_MAX):
        raise PeliculaError(
            f"la transicion debe durar entre {DUR_MIN} y {DUR_MAX} s")
    return {
        "transicion": tipo,
        "duracion_transicion": round(dur, 3),
        "narracion": bool(op.get("narracion", True)),
        "intro_job_id": op.get("intro_job_id") or None,
        "cierre_job_id": op.get("cierre_job_id") or None,
    }


class PeliculaService:
    def __init__(self, cfg, db, runner, narracion) -> None:
        self.cfg = cfg
        self.db = db
        self.runner = runner
        self.narracion = narracion
        self._task: asyncio.Task | None = None
        self._run: dict | None = None

    # ── rutas ────────────────────────────────────────────────────────────────

    def destino(self, project: dict) -> Path:
        """`exports/peliculas/<project_id>/`.

        El directorio se nombra por el **id** y no por el slug a proposito: es
        lo unico que el runner valida con un regex cerrado, y renombrar el
        proyecto no deja peliculas huerfanas.
        """
        return self.cfg.peliculas_dir / project["id"]

    def _rel(self, path: Path) -> str:
        """Ruta relativa al workspace (que dentro del contenedor es /workspace)."""
        try:
            return str(Path(path).resolve().relative_to(
                self.cfg.workspace.resolve()))
        except ValueError as exc:
            raise PeliculaError(
                f"{path} vive fuera del workspace y el contenedor no la ve"
            ) from exc

    # ── el plan ──────────────────────────────────────────────────────────────

    def _pieza_de_job(self, job: dict, titulo: str) -> dict:
        """La pieza usa el mp4 que la app SIRVE, no siempre el que salio de
        manim.

        Desde el sprint E3 un clip puede tener su cama de sonido mezclada al
        lado del mudo (`audio_path`), y es esa la que ve quien reproduce el
        clip en la Biblioteca. Montar la pelicula con el mudo daria un curso
        que suena distinto a sus propios clips.
        """
        video = job.get("audio_path") or job["video_path"]
        return {"titulo": titulo, "video": self._rel(Path(video))}

    def _job_marca(self, job_id: str, cual: str, esperada: str) -> dict:
        job = self.db.get_job(job_id)
        if not job or job.get("status") != "done" or not job.get("video_path"):
            raise PeliculaError(f"el {cual} de marca no tiene render vigente")
        medida = job.get("resolution") or ""
        if medida and esperada and medida != esperada:
            raise PeliculaError(
                f"el {cual} de marca es {medida} y el curso es {esperada}: "
                "un empalme de dos tamanos no se puede pegar")
        return job

    def plan(self, project: dict, opciones: dict) -> dict:
        """Plan que lee `ensamblar.py`. Levanta PeliculaError si no hay obra."""
        op = opciones
        clips = self.db.list_clips(project["id"])
        if not clips:
            raise PeliculaError("el proyecto no tiene clips")

        sp = specs(project["quality"], project.get("formato", "horizontal"))
        esperada = f"{sp['width']}x{sp['height']}"
        destino_voz = self.narracion.destino(project)
        estado_voz = self.narracion._leer_estado(destino_voz)

        piezas: list[dict] = []
        sin_render: list[str] = []
        for clip in clips:
            job = self.db.get_job(clip["job_id"]) if clip.get("job_id") else None
            if not job or job.get("status") != "done" or not job.get("video_path"):
                sin_render.append(clip["title"])
                continue
            pieza = self._pieza_de_job(job, clip["title"])
            if op["narracion"]:
                previo = estado_voz.get(clip["id"]) or {}
                etiqueta = previo.get("etiqueta") or etiqueta_clip(
                    clip["position"], clip["title"])
                wav = destino_voz / f"{etiqueta}.wav"
                if wav.is_file():
                    pieza["voz"] = self._rel(wav)
            piezas.append(pieza)

        if not piezas:
            raise PeliculaError("ningun clip del curso tiene render vigente")

        if op["intro_job_id"]:
            job = self._job_marca(op["intro_job_id"], "intro", esperada)
            piezas.insert(0, self._pieza_de_job(job, "Intro de marca"))
        if op["cierre_job_id"]:
            job = self._job_marca(op["cierre_job_id"], "cierre", esperada)
            piezas.append(self._pieza_de_job(job, "Cierre de marca"))

        return {
            "proyecto": project["name"],
            "raiz": "/workspace",
            "fps": sp["fps"],
            "resolucion": esperada,
            "transicion": {"tipo": op["transicion"],
                           "duracion": op["duracion_transicion"]},
            "piezas": piezas,
            "faltan": sin_render,
        }

    # ── estado ───────────────────────────────────────────────────────────────

    def _hash_plan(self, plan: dict) -> str:
        """Que hace vieja a una pelicula: el material y como se pego.

        Se hashea el plan sin `faltan` (que es informativo) y con el mtime de
        cada archivo: un re-render deja la misma ruta y otro contenido.
        """
        partes = [plan["proyecto"], plan["resolucion"], str(plan["fps"]),
                  plan["transicion"]["tipo"], str(plan["transicion"]["duracion"])]
        for p in plan["piezas"]:
            for clave in ("video", "voz"):
                ruta = p.get(clave)
                if not ruta:
                    continue
                abs_ = self.cfg.workspace / ruta
                try:
                    marca = f"{ruta}:{abs_.stat().st_mtime_ns}"
                except OSError:
                    marca = f"{ruta}:?"
                partes.append(marca)
        return hashlib.sha256("|".join(partes).encode()).hexdigest()[:16]

    def informe(self, project: dict) -> dict | None:
        p = self.destino(project) / NOMBRE_INFORME
        try:
            return json.loads(p.read_text()) if p.is_file() else None
        except (OSError, ValueError):
            return None

    def video_path(self, project: dict) -> Path | None:
        p = self.destino(project) / NOMBRE_VIDEO
        return p if p.is_file() else None

    def estado(self, project: dict, opciones: dict | None = None) -> dict:
        """Estado + informe de la ultima pelicula montada.

        No abre un solo mp4: el informe guarda lo medido al montar y el hash
        dice si sigue correspondiendo.
        """
        corriendo = self._run if self.running else None
        if corriendo and corriendo.get("project_id") != project["id"]:
            corriendo = None
        informe = self.informe(project)
        video = self.video_path(project)
        op = normaliza_opciones(opciones or (informe or {}).get("opciones"))

        try:
            plan = self.plan(project, op)
            hash_actual = self._hash_plan(plan)
            piezas = len(plan["piezas"])
            faltan = plan["faltan"]
            con_voz = sum(1 for p in plan["piezas"] if p.get("voz"))
            problema = None
        except PeliculaError as exc:
            hash_actual, piezas, faltan, con_voz = None, 0, [], 0
            problema = str(exc)

        if corriendo:
            estado = "montando"
        elif problema and not video:
            estado = "sin_clips" if "no tiene clips" in problema else "faltan_renders"
        elif not video:
            estado = "sin_montar"
        elif informe and informe.get("hash") == hash_actual:
            estado = "al_dia"
        else:
            estado = "desactualizada"

        return {
            "estado": estado,
            "problema": problema,
            "opciones": op,
            "piezas": piezas,
            "con_voz": con_voz,
            "faltan": faltan,
            "informe": informe,
            "verificacion": self.estado_verificacion(informe),
            "run": corriendo,
            "transiciones": list(TRANSICIONES),
        }

    # ── montar ───────────────────────────────────────────────────────────────

    @property
    def running(self) -> bool:
        return self._task is not None and not self._task.done()

    def start(self, project: dict, opciones: dict | None = None) -> dict:
        if self.running:
            raise PeliculaError("ya hay una pelicula montandose")
        op = normaliza_opciones(opciones)
        plan = self.plan(project, op)

        destino = self.destino(project)
        destino.mkdir(parents=True, exist_ok=True)
        (destino / NOMBRE_PLAN).write_text(json.dumps(plan, indent=1))

        self._run = {
            "project_id": project["id"],
            "nombre": project["name"],
            "piezas": len(plan["piezas"]),
            "transicion": op["transicion"],
            "iniciado": time.time(),
            "estado": "montando",
        }
        hash_plan = self._hash_plan(plan)
        self._task = asyncio.get_event_loop().create_task(
            self._correr(project, op, hash_plan))
        return {"iniciado": True, "piezas": len(plan["piezas"]),
                "faltan": plan["faltan"]}

    async def _correr(self, project: dict, op: dict, hash_plan: str) -> None:
        destino = self.destino(project)
        try:
            informe = await self.runner.ensamblar(project["id"])
            informe = dict(informe or {})
            informe["hash"] = hash_plan
            informe["opciones"] = op
            informe["montada"] = time.time()
            (destino / NOMBRE_INFORME).write_text(json.dumps(informe, indent=1))
            # Recien montada es cuando toca medir: la union puede salir mal SIN
            # fallar (una pieza que se pierde, el audio que se cae) y nadie lo
            # ve mirando el mp4 una vez. Si la medicion falla, la pelicula sigue
            # siendo buena y el panel dira «sin verificar».
            try:
                await self.verificar(project)
            except Exception:  # noqa: BLE001
                pass
            if self._run:
                self._run["estado"] = "listo"
        except Exception as exc:  # noqa: BLE001 - el error va a la UI tal cual
            if self._run:
                self._run["estado"] = "error"
                self._run["error"] = str(exc)[:400]
        finally:
            if self._run:
                self._run["terminado"] = time.time()

    async def verificar(self, project: dict) -> dict:
        """Mide la pelicula montada contra su plan y guarda el informe.

        El resultado vive DENTRO de `pelicula.json`, junto al informe del
        montaje y con el mismo hash: asi caduca sola. Una medicion de otra
        pelicula no vale, y ensenar sus numeros seria peor que no ensenar
        ninguno.
        """
        destino = self.destino(project)
        informe = self.informe(project) or {}
        if not (destino / NOMBRE_VIDEO).is_file():
            raise PeliculaError("no hay pelicula que medir")
        medida = await self.runner.ensamblar(project["id"], modo="verificar")
        informe["verificacion"] = dict(medida or {})
        informe["verificacion"]["medida"] = time.time()
        informe["verificacion"]["hash"] = informe.get("hash")
        (destino / NOMBRE_INFORME).write_text(json.dumps(informe, indent=1))
        return informe["verificacion"]

    def estado_verificacion(self, informe: dict | None) -> str:
        """'sin_verificar' | 'vieja' | 'pasa' | 'no_pasa'."""
        v = (informe or {}).get("verificacion")
        if not v:
            return "sin_verificar"
        if v.get("hash") != (informe or {}).get("hash"):
            return "vieja"
        return "pasa" if v.get("ok") else "no_pasa"

    def cancel(self) -> bool:
        if not self.running:
            return False
        self._task.cancel()
        if self._run:
            self._run["estado"] = "cancelado"
        return True

    def borrar(self, project: dict) -> bool:
        """Borra la pelicula montada (no el material del que salio)."""
        destino = self.destino(project)
        borrado = False
        for nombre in (NOMBRE_VIDEO, NOMBRE_INFORME, NOMBRE_PLAN):
            p = destino / nombre
            if p.is_file():
                p.unlink()
                borrado = True
        return borrado

    def nombre_descarga(self, project: dict) -> str:
        return f"{slugify(project['name'])}.mp4"
