"""API del audio de un promo: manifiesto, mezcla y estado.

Router aparte por la misma razon que projects_api/narracion_api: `main.py`
crea las piezas y monta el router despues, sin ciclos de import.

El reparto de trabajo:

  - este modulo decide QUE hacer y en que orden;
  - `audio_promo` valida y avisa (puro, sin Vertex ni Docker);
  - `narracion.sintetizar` pone la voz (misma service account que el
    asistente IA; sin credenciales, el promo se mezcla mudo de voz);
  - el runner corre `sfx.py promo` en el contenedor.

Solo se ofrece en proyectos de tipo `promo`. Un curso narra por otro camino
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

    def _promo(pid: str) -> dict:
        project = db.get_project(pid)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        if (project.get("tipo") or "curso") != "promo":
            raise HTTPException(
                status_code=409,
                detail="El audio de promo solo se monta en proyectos de tipo promo;"
                       " un curso se narra desde «Generar narración».")
        return project

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
        m = service.manifiesto_audio(clip, cfg.tts_voice)
        _job, dur = _video(clip)
        return {
            "clip_id": clip["id"],
            "manifiesto": m,
            "estado": service.estado_audio(clip),
            "avisos": audio_promo.avisos(m, dur),
            "duracion_video": dur,
            "sonidos": list(audio_promo.SONIDOS),
            "voz_disponible": narracion.enabled,
            "silabas_por_s": audio_promo.SILABAS_POR_S,
        }

    @router.get("/{pid}/clips/{cid}/audio")
    async def leer(pid: str, cid: str, _=Depends(require_auth)):
        project = _promo(pid)
        return _vista(project, _clip(pid, cid))

    @router.put("/{pid}/clips/{cid}/audio")
    async def guardar(pid: str, cid: str, body: ManifiestoBody,
                      _=Depends(require_auth)):
        project = _promo(pid)
        clip = _clip(pid, cid)
        m = audio_promo.normalizar(body.a_manifiesto(), cfg.tts_voice)
        errores = audio_promo.validar(m)
        if errores:
            raise HTTPException(status_code=422, detail="; ".join(errores))
        service.update_clip(cid, audio_json=json.dumps(m, ensure_ascii=False))
        return _vista(project, db.get_clip(cid))

    @router.post("/{pid}/clips/{cid}/audio/mezclar")
    async def mezclar(pid: str, cid: str, _=Depends(require_auth)):
        project = _promo(pid)
        clip = _clip(pid, cid)
        m = service.manifiesto_audio(clip, cfg.tts_voice)
        if not clip.get("audio_json"):
            raise HTTPException(status_code=422,
                                detail="Este clip no tiene manifiesto de audio")
        errores = audio_promo.validar(m)
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
                    detail="La voz requiere la service account de Vertex;"
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
            await asyncio.to_thread(sintetizar, narracion._vertex(),
                                    m["voz"]["secciones"], m["voz"]["voz"],
                                    wav, limite)
        except Exception as e:
            raise HTTPException(status_code=502,
                                detail=f"La síntesis de voz falló: {e}")
        marca.write_text(h)

    return router
