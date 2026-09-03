"""API del audio de un promo: manifiesto, mezcla y estado.

Router aparte por la misma razon que projects_api/narracion_api: `main.py`
crea las piezas y monta el router despues, sin ciclos de import.

El reparto de trabajo:

  - este modulo decide QUE hacer y en que orden;
  - `audio_promo` valida y avisa (puro, sin Vertex ni Docker);
  - `narracion.sintetizar` pone la voz (misma service account que el
    asistente IA; sin credenciales, el promo se mezcla mudo de voz);
  - el runner corre `sfx.py promo` en el contenedor.

Se ofrece en promos y, desde el sprint E3, en clips de CURSO — con una
diferencia que manda: un curso no lleva voz aqui, solo la cama. Su narracion
(Narracion, guion escrito por Gemini) y no lleva cama de sonido.
"""

import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from . import audio_promo
from .auth import require_auth
from .db import Database
from .jobs import JobManager
from .narracion import NarracionService, duracion_mp4, sintetizar
from .projects import ProjectService
from .runner_client import RunnerError

SALIDA = "promo_audio.mp4"


class EventoBody(BaseModel):
    sonido: str = Field(max_length=64)
    t: float
    db: float


class SeccionBody(BaseModel):
    t_inicio: float
    texto: str = Field(max_length=audio_promo.MAX_TEXTO)


class ManifiestoBody(BaseModel):
    eventos: list[EventoBody] = Field(default_factory=list,
                                      max_length=audio_promo.MAX_EVENTOS)
    secciones: list[SeccionBody] = Field(default_factory=list,
                                         max_length=audio_promo.MAX_SECCIONES)
    voz: str = Field(default="Charon", max_length=32)
    pico_db: float = audio_promo.PICO_DB
    pico_db_con_voz: float = audio_promo.PICO_DB_CON_VOZ
    fade_in: float = audio_promo.FADE_IN
    fade_out: list[float] | None = None

    def a_manifiesto(self) -> dict:
        audio = {"pico_db": self.pico_db,
                 "pico_db_con_voz": self.pico_db_con_voz,
                 "fade_in": self.fade_in,
                 "eventos": [[e.sonido, e.t, e.db] for e in self.eventos]}
        if self.fade_out:
            audio["fade_out"] = list(self.fade_out)
        return {"audio": audio,
                "voz": {"voz": self.voz,
                        "secciones": [s.model_dump() for s in self.secciones]}}


def make_router(cfg, db: Database, manager: JobManager, service: ProjectService,
                narracion: NarracionService) -> APIRouter:
    router = APIRouter(prefix="/api/projects", tags=["audio"])

    def _proyecto(pid: str) -> dict:
        """Cualquier proyecto: la cama de sonido sirve a promos y a cursos.

        El `tipo` no cierra la puerta, pero SI cambia las reglas — quien lo
        necesita se lo pasa a `audio_promo.validar/avisos`.
        """
        project = db.get_project(pid)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return project

    def _tipo(project: dict) -> str:
        return project.get("tipo") or "curso"

    def _solo_promo(project: dict, que: str) -> None:
        """La verificacion mide la costura del BUCLE y una duracion de 8-15 s:
        las dos cosas son del formato promo. En un curso no significan nada."""
        if _tipo(project) != "promo":
            raise HTTPException(
                status_code=409,
                detail=f"{que} solo tiene sentido en un promo: mide la costura"
                       " del bucle y el rango de duración de redes.")

    def _clip(pid: str, cid: str) -> dict:
        clip = db.get_clip(cid)
        if not clip or clip.get("project_id") != pid:
            raise HTTPException(status_code=404, detail="Clip no encontrado")
        return clip

    def _video(clip: dict) -> tuple[dict | None, float | None]:
        """Job con render vigente del clip y duracion de su video."""
        job_id = clip.get("job_id")
        job = db.get_job(job_id) if job_id else None
        if not job or job.get("status") != "done" or not job.get("video_path"):
            return None, None
        return job, duracion_mp4(Path(job["video_path"]))

    def _vista(project: dict, clip: dict) -> dict:
        tipo = _tipo(project)
        m = service.manifiesto_audio(clip, cfg.tts_voice, tipo)
        job, dur = _video(clip)
        return {
            "clip_id": clip["id"],
            "tipo": tipo,
            "manifiesto": m,
            "estado": service.estado_audio(clip),
            "avisos": audio_promo.avisos(m, dur, tipo),
            "duracion_video": dur,
            "sonidos": list(audio_promo.SONIDOS),
            # En un curso la voz NO se escribe aqui: sale de «Generar
            # narracion» y la pelicula la pega al montar.
            "voz_aqui": tipo == "promo",
            "voz_disponible": narracion.enabled,
            "silabas_por_s": audio_promo.SILABAS_POR_S,
            "verificacion": service.estado_verificacion(clip)
            | {"informe": service.informe_verificacion(clip)},
            "job_id": job["id"] if job else None,
        }

    async def _verificar(clip: dict) -> dict | None:
        """Mide el promo y guarda el informe. Devuelve el informe o None.

        No es fatal: una mezcla buena no se invalida porque la medicion no
        se pueda hacer (se vera como «sin verificar», que es la verdad).
        """
        job_id = clip.get("job_id")
        job = db.get_job(job_id) if job_id else None
        if not job or job.get("status") != "done":
            return None
        informe = await manager.verificar_promo(
            job_id, frames=6, dur_min=audio_promo.DUR_MIN,
            dur_max=audio_promo.DUR_MAX)
        db.update_job(job_id,
                      verify_json=json.dumps(informe, ensure_ascii=False),
                      verify_hash=audio_promo.hash_verificacion(db.get_job(job_id)))
        manager.invalidate_storage()  # los PNG de la verificacion ocupan
        return informe

    @router.get("/{pid}/clips/{cid}/audio")
    async def leer(pid: str, cid: str, _=Depends(require_auth)):
        project = _proyecto(pid)
        return _vista(project, _clip(pid, cid))

    @router.put("/{pid}/clips/{cid}/audio")
    async def guardar(pid: str, cid: str, body: ManifiestoBody,
                      _=Depends(require_auth)):
        project = _proyecto(pid)
        clip = _clip(pid, cid)
        m = audio_promo.normalizar(body.a_manifiesto(), cfg.tts_voice)
        errores = audio_promo.validar(m, _tipo(project))
        if errores:
            raise HTTPException(status_code=422, detail="; ".join(errores))
        service.update_clip(cid, audio_json=json.dumps(m, ensure_ascii=False))
        return _vista(project, db.get_clip(cid))

    @router.post("/{pid}/clips/{cid}/verificar")
    async def verificar(pid: str, cid: str, _=Depends(require_auth)):
        project = _proyecto(pid)
        _solo_promo(project, "La verificación")
        clip = _clip(pid, cid)
        job, _dur = _video(clip)
        if not job:
            raise HTTPException(
                status_code=409,
                detail="El clip no tiene un video vigente que medir")
        try:
            await _verificar(clip)
        except (RunnerError, asyncio.TimeoutError) as e:
            raise HTTPException(status_code=502,
                                detail=f"La verificación falló: {e}")
        return _vista(project, db.get_clip(cid))

    @router.post("/{pid}/clips/{cid}/audio/mezclar")
    async def mezclar(pid: str, cid: str, _=Depends(require_auth)):
        project = _proyecto(pid)
        clip = _clip(pid, cid)
        m = service.manifiesto_audio(clip, cfg.tts_voice, _tipo(project))
        if not clip.get("audio_json"):
            raise HTTPException(status_code=422,
                                detail="Este clip no tiene manifiesto de audio")
        errores = audio_promo.validar(m, _tipo(project))
        if errores:
            raise HTTPException(status_code=422, detail="; ".join(errores))

        job, dur = _video(clip)
        if not job:
            raise HTTPException(
                status_code=409,
                detail="El clip no tiene un video vigente: renderízalo antes de mezclar")

        job_dir = (cfg.render_jobs_dir / job["id"]).resolve()
        if not job_dir.is_dir():
            raise HTTPException(status_code=409,
                                detail="El directorio del render ya no existe")
        (job_dir / "promo.json").write_text(
            json.dumps(audio_promo.para_sfx(m), ensure_ascii=False, indent=2))

        con_voz = bool(m["voz"]["secciones"])
        if con_voz:
            if not narracion.enabled:
                raise HTTPException(
                    status_code=503,
                    detail="No hay ningun proveedor de voz disponible;"
                           " quita las frases para mezclar solo la cama.")
            await _voz(m, job_dir, dur)

        try:
            rel = await manager.mezclar_audio(job["id"], con_voz)
        except (RunnerError, asyncio.TimeoutError) as e:
            raise HTTPException(status_code=502, detail=f"La mezcla falló: {e}")

        salida = (cfg.workspace / rel).resolve()
        if not salida.is_file() or job_dir not in salida.parents:
            raise HTTPException(status_code=502,
                                detail="La mezcla no dejó archivo")
        db.update_job(job["id"], audio_path=str(salida),
                      audio_hash=audio_promo.hash_mezcla(m, job["id"]),
                      size_bytes=salida.stat().st_size)
        manager.invalidate_storage()
        # Recien mezclado es cuando toca medir: el informe anterior (si lo
        # habia) es de otro archivo. Si la medicion falla, la mezcla sigue
        # siendo buena y el estado dira «sin verificar». Solo en un promo:
        # lo que mide (bucle y 8-15 s) no existe en un curso.
        if _tipo(project) == "promo":
            try:
                await _verificar(db.get_clip(cid))
            except (RunnerError, asyncio.TimeoutError):
                pass
        return _vista(project, db.get_clip(cid))

    async def _voz(m: dict, job_dir: Path, dur: float | None) -> None:
        """Sintetiza la voz si hace falta. Se cachea por el hash del bloque
        `voz`: reordenar un sonido de la cama no vuelve a gastar TTS."""
        wav = job_dir / "voz.wav"
        marca = job_dir / "voz.hash"
        h = audio_promo.hash_voz(m)
        if wav.is_file() and marca.is_file() and marca.read_text().strip() == h:
            return
        # La voz tiene que CALLAR antes del ultimo frame o el salto del
        # bucle se oye: se sintetiza contra ese limite, no contra el final.
        limite = (dur - audio_promo.COLA_SILENCIO_S) if dur else None
        try:
            proveedor, voz = narracion.resolver_voz(
                m["voz"].get("proveedor"), m["voz"]["voz"] or None)
            await asyncio.to_thread(sintetizar, narracion._narrador(proveedor),
                                    m["voz"]["secciones"], voz, wav, limite)
        except Exception as e:
            raise HTTPException(status_code=502,
                                detail=f"La síntesis de voz falló: {e}")
        marca.write_text(h)

    return router
