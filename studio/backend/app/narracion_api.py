"""API HTTP de narracion de proyectos: estado por clip, generacion en
segundo plano, guion editable, grabacion propia y descarga de audio/texto.

Router aparte (`make_router`) por la misma razon que projects_api: `main.py`
crea `db`/`narracion` y monta el router despues, sin ciclos de import.
"""

import asyncio
import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import tts as tts_mod
from .auth import require_auth
from .db import Database
from .narracion import NarracionService, etiqueta_clip
from .runner_client import RunnerError

# Extensiones que se aceptan como grabacion propia. Las cuatro primeras las
# decodifica el backend (miniaudio); el resto pasa por ffmpeg en el
# contenedor (comando `normalizar_voz` del runner).
EXT_SUBIDA = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".mp4",
              ".webm", ".opus", ".oga", ".wma", ".aiff", ".aif"}
RE_NOMBRE = re.compile(r"^[A-Za-z0-9._ \-()]{1,120}$")


class NarracionStartBody(BaseModel):
    clips: list[str] | None = Field(default=None, max_length=200)
    force: bool = False
    proveedor: str | None = Field(default=None, max_length=16)
    voz: str | None = Field(default=None, max_length=64)
    # Con guion ya escrito: no llamar a Gemini para reescribirlo.
    solo_audio: bool = False


class GuionBody(BaseModel):
    secciones: list[dict] = Field(max_length=200)


def make_router(cfg, db: Database, narracion: NarracionService,
                runner=None) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["narracion"])

    def _require_project(pid: str) -> dict:
        project = db.get_project(pid)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return project

    def _require_clip(project: dict, cid: str) -> dict:
        clip = db.get_clip(cid)
        if not clip or clip.get("project_id") != project["id"]:
            raise HTTPException(status_code=404, detail="Clip no encontrado")
        return clip

    def _clip_file(project: dict, cid: str, ext: str) -> Path:
        clip = _require_clip(project, cid)
        destino = narracion.destino(project)
        estado = narracion._leer_estado(destino)
        previo = estado.get(cid) or {}
        etiqueta = previo.get("etiqueta") or etiqueta_clip(
            clip["position"], clip["title"])
        path = (destino / f"{etiqueta}{ext}").resolve()
        # Defensa en profundidad (misma politica que /api/jobs/{id}/video):
        # el archivo debe vivir dentro del directorio de guiones del proyecto.
        if not path.is_file() or destino.resolve() not in path.parents:
            raise HTTPException(status_code=404, detail="Narracion no disponible")
        return path

    @router.get("/narracion/proveedores")
    async def proveedores(_=Depends(require_auth)):
        """Que voces hay: por proveedor, con motivo si no esta disponible."""
        return {"proveedor": narracion.proveedor_defecto(),
                "voz": narracion.voz_defecto(),
                "proveedores": narracion.proveedores()}

    @router.get("/projects/{pid}/narracion")
    async def estado(pid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        return narracion.estado_proyecto(project)

    @router.post("/projects/{pid}/narracion", status_code=202)
    async def generar(pid: str, body: NarracionStartBody,
                      _=Depends(require_auth)):
        project = _require_project(pid)
        try:
            res = narracion.start(project, clip_ids=body.clips,
                                  force=body.force, proveedor=body.proveedor,
                                  voz=body.voz, solo_audio=body.solo_audio)
        except ValueError as e:
            msg = str(e)
            status = 503 if "no disponible" in msg else 409
            raise HTTPException(status_code=status, detail=msg)
        return res | {"run": narracion.run_public()}

    @router.post("/projects/{pid}/narracion/cancel")
    async def cancelar(pid: str, _=Depends(require_auth)):
        _require_project(pid)
        if not narracion.cancel():
            raise HTTPException(status_code=409,
                                detail="No hay ninguna narracion en curso")
        return {"ok": True}

    # ── guion editable ───────────────────────────────────────────────────

    @router.get("/projects/{pid}/narracion/{cid}/guion")
    async def leer_guion(pid: str, cid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        clip = _require_clip(project, cid)
        secciones = narracion.leer_guion(project, clip)
        video_s = narracion._video_s(clip)
        return {"secciones": secciones or [],
                "existe": secciones is not None,
                "video_s": video_s and round(video_s, 1)}

    @router.put("/projects/{pid}/narracion/{cid}/guion")
    async def guardar_guion(pid: str, cid: str, body: GuionBody,
                            _=Depends(require_auth)):
        project = _require_project(pid)
        clip = _require_clip(project, cid)
        if narracion.running and narracion.run_public()["project_id"] == pid:
            raise HTTPException(status_code=409,
                                detail="Hay una narracion en curso en este "
                                       "proyecto; espera a que termine")
        try:
            entry = narracion.guardar_guion(project, clip, body.secciones)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        return {"ok": True, "palabras": entry.get("palabras"),
                "etiqueta": entry.get("etiqueta")}

    # ── grabacion propia ─────────────────────────────────────────────────

    @router.put("/projects/{pid}/narracion/{cid}/audio")
    async def subir_audio(pid: str, cid: str, request: Request,
                          nombre: str = "voz.wav", _=Depends(require_auth)):
        """Sube la narracion grabada por el dueno (cuerpo crudo, cualquier
        formato de audio comun). Se decodifica a PCM mono 24 kHz, se le
        recorta el silencio y queda como LA narracion del clip."""
        project = _require_project(pid)
        clip = _require_clip(project, cid)
        if not RE_NOMBRE.match(nombre):
            raise HTTPException(status_code=422, detail="nombre de archivo invalido")
        ext = Path(nombre).suffix.lower()
        if ext not in EXT_SUBIDA:
            raise HTTPException(
                status_code=415,
                detail=f"formato {ext or 'desconocido'} no admitido; sube "
                       "wav, mp3, flac, ogg, m4a, aac, webm u opus")
        tope = cfg.max_upload_audio_mb * 1024 * 1024
        largo = request.headers.get("content-length")
        if largo and largo.isdigit() and int(largo) > tope:
            raise HTTPException(status_code=413,
                                detail=f"archivo mayor de {cfg.max_upload_audio_mb} MB")
        datos = await request.body()
        if len(datos) > tope:
            raise HTTPException(status_code=413,
                                detail=f"archivo mayor de {cfg.max_upload_audio_mb} MB")
        if len(datos) < 1024:
            raise HTTPException(status_code=422, detail="archivo vacio")

        if tts_mod.decodificable(nombre):
            try:
                pcm = await asyncio.to_thread(tts_mod.decodificar, datos, ext)
            except Exception as e:
                raise HTTPException(status_code=422,
                                    detail=f"no se pudo decodificar el audio: {e}")
        else:
            pcm = await _convertir_en_contenedor(project, clip, datos, ext)

        try:
            entry = narracion.registrar_subida(project, clip, pcm, nombre)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        return {"ok": True, "audio_s": entry["audio_s"],
                "video_s": entry["video_s"], "etiqueta": entry["etiqueta"]}

    async def _convertir_en_contenedor(project: dict, clip: dict,
                                       datos: bytes, ext: str) -> bytes:
        """m4a/aac/webm/opus: el backend no tiene ffmpeg, el contenedor si.
        Deja el archivo en el directorio de guiones del proyecto (montado rw
        solo para esa llamada) y lee el WAV que ffmpeg produce."""
        if runner is None:
            raise HTTPException(status_code=503,
                                detail="sin runner: sube wav, mp3, flac u ogg")
        destino = narracion.destino(project)
        destino.mkdir(parents=True, exist_ok=True)
        etiqueta = narracion._etiqueta(project, clip)
        entrada = destino / f"{etiqueta}.subida{ext}"
        salida = destino / f"{etiqueta}.subida.wav"
        entrada.write_bytes(datos)
        try:
            await runner.normalizar_voz(destino.name, entrada.name, salida.name)
        except (RunnerError, asyncio.TimeoutError) as e:
            raise HTTPException(status_code=502,
                                detail=f"la conversion fallo: {e}")
        finally:
            entrada.unlink(missing_ok=True)
        if not salida.is_file():
            raise HTTPException(status_code=502,
                                detail="la conversion no dejo archivo")
        try:
            pcm = await asyncio.to_thread(tts_mod.decodificar,
                                          salida.read_bytes(), ".wav")
        except Exception as e:
            raise HTTPException(status_code=422,
                                detail=f"no se pudo leer el WAV convertido: {e}")
        finally:
            salida.unlink(missing_ok=True)
        return pcm

    # ── descargas ────────────────────────────────────────────────────────

    @router.get("/projects/{pid}/narracion/{cid}/audio")
    async def audio(pid: str, cid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        path = _clip_file(project, cid, ".wav")
        return FileResponse(path, media_type="audio/wav", filename=path.name)

    @router.get("/projects/{pid}/narracion/{cid}/texto")
    async def texto(pid: str, cid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        md = _clip_file(project, cid, ".md")
        txt = md.with_suffix(".txt")
        return {"md": md.read_text(),
                "txt": txt.read_text() if txt.is_file() else ""}

    return router
