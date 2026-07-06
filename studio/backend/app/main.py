"""ManimStudio API — FastAPI, escucha solo en 127.0.0.1 detras de nginx/TLS."""

import asyncio
import json
import re
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from . import metrics
from .ai import AIError, Assistant
from .animations import AnimationStore
from .auth import (client_ip, clear_session, create_session, get_rate_limiter,
                   require_auth, session_valid, verify_credentials)
from .config import get_settings
from .db import Database
from .fable import FableAssistant
from .events import EventBus
from .jobs import QUALITIES, JobManager, job_public
from .lessons import LessonStore
from .runner_client import RunnerClient
from .scenes import detect_scenes

RE_JOB_ID = re.compile(r"^[a-f0-9]{8,32}$")

cfg = get_settings()
db = Database(cfg.db_path)
bus = EventBus()
runner = RunnerClient(cfg.runner_socket)
manager = JobManager(cfg, db, runner, bus)
# 30 min de historia al intervalo configurado (450 muestras a 4 s).
history = metrics.History(maxlen=max(360, int(1800 // cfg.metrics_interval)))
assistant = Assistant(cfg)
fable_assistant = FableAssistant(cfg)
lessons_store = LessonStore(cfg.lessons_dir)
animations_store = AnimationStore(cfg.animations_dir, lessons_store)


@asynccontextmanager
async def lifespan(app: FastAPI):
    history.load(cfg.metrics_snapshot_path, cfg.metrics_interval)
    manager.start()
    metrics_task = asyncio.get_event_loop().create_task(_metrics_loop())
    yield
    metrics_task.cancel()
    history.save(cfg.metrics_snapshot_path)
    await manager.stop()
    db.close()


app = FastAPI(title="ManimStudio", docs_url=None, redoc_url=None, openapi_url=None,
              lifespan=lifespan)


async def _metrics_loop() -> None:
    """Publica metricas de host + contenedores al bus SSE cada N segundos.

    Solo consulta docker stats si hay algun cliente SSE conectado seria un
    refinamiento; el runner ya cachea stats 4s, y el intervalo es moderado
    (sin polling agresivo) para respetar las 2 vCPU compartidas.
    """
    last_snapshot = time.time()
    while True:
        try:
            payload = {"type": "metrics", "host": metrics.host_metrics()}
            try:
                payload["containers"] = await runner.stats()
            except Exception:
                payload["containers"] = None  # runner caido: se informa en UI
            history.add(payload["host"], payload["containers"])
            bus.publish(payload)
            now = time.time()
            if now - last_snapshot >= cfg.metrics_snapshot_interval:
                history.save(cfg.metrics_snapshot_path)  # persistencia periodica: no depende del shutdown limpio
                last_snapshot = now
        except Exception as e:
            print(f"[metrics] error: {e!r}")
        await asyncio.sleep(cfg.metrics_interval)


# ── modelos ───────────────────────────────────────────────────────────────────

class LoginBody(BaseModel):
    username: str = Field(max_length=128)
    password: str = Field(max_length=256)


class ScenesBody(BaseModel):
    script: str


class JobBody(BaseModel):
    script: str
    scene: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")
    quality: str
    timeout: int | None = None


# ── auth ──────────────────────────────────────────────────────────────────────

@app.post("/api/login")
async def login(body: LoginBody, request: Request, response: Response):
    limiter = get_rate_limiter(cfg)
    ip = client_ip(request)
    wait = limiter.check(ip)
    if wait > 0:
        raise HTTPException(status_code=429,
                            detail=f"Demasiados intentos. Espera {int(wait)} s.")
    if not verify_credentials(cfg, body.username, body.password):
        limiter.record_failure(ip)
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    limiter.record_success(ip)
    create_session(cfg, response)
    return {"ok": True, "user": cfg.admin_user}


@app.post("/api/logout")
async def logout(response: Response, _=Depends(require_auth)):
    clear_session(cfg, response)
    return {"ok": True}


@app.get("/api/me")
async def me(request: Request):
    if session_valid(cfg, request):
        return {"authenticated": True, "user": cfg.admin_user,
                "ai_enabled": assistant.enabled}
    return {"authenticated": False}


# ── escenas y jobs ────────────────────────────────────────────────────────────

def _check_script(script: str) -> None:
    if len(script.encode("utf-8", errors="replace")) > cfg.max_script_bytes:
        raise HTTPException(status_code=413, detail="Script demasiado grande")
    if not script.strip():
        raise HTTPException(status_code=422, detail="Script vacio")


@app.post("/api/scenes")
async def scenes(body: ScenesBody, _=Depends(require_auth)):
    _check_script(body.script)
    try:
        return {"scenes": detect_scenes(body.script)}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/jobs", status_code=201)
async def create_job(body: JobBody, _=Depends(require_auth)):
    _check_script(body.script)
    if body.quality not in QUALITIES:
        raise HTTPException(status_code=422, detail="Calidad invalida (ql/qm/qh)")
    timeout = body.timeout or cfg.default_timeout
    if not (30 <= timeout <= cfg.max_timeout):
        raise HTTPException(status_code=422,
                            detail=f"Timeout fuera de rango (30–{cfg.max_timeout}s)")
    try:
        available = detect_scenes(body.script)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Script invalido: {e}")
    if body.scene not in available:
        raise HTTPException(status_code=422,
                            detail=f"La escena '{body.scene}' no existe en el script")
    quota = cfg.max_storage_mb * 1024 * 1024
    used = manager.storage_usage()
    if used >= quota:
        raise HTTPException(
            status_code=507,
            detail=(f"Almacenamiento lleno: {used / 2**20:.0f} MB usados de "
                    f"{cfg.max_storage_mb} MB. Borra videos de la Biblioteca "
                    "para liberar espacio."))
    return manager.create_job(body.script, body.scene, body.quality, timeout)


def _storage_public() -> dict:
    return {"used_bytes": manager.storage_usage(),
            "quota_bytes": cfg.max_storage_mb * 1024 * 1024}


@app.get("/api/jobs")
async def list_jobs(_=Depends(require_auth)):
    return {"jobs": [job_public(j) | {"script_len": j.get("script_len")}
                     for j in db.list_jobs()],
            "current": manager.current_job_id,
            "storage": _storage_public()}


def _get_job_or_404(job_id: str) -> dict:
    if not RE_JOB_ID.match(job_id):
        raise HTTPException(status_code=404, detail="Job no encontrado")
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return job


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str, _=Depends(require_auth)):
    job = _get_job_or_404(job_id)
    return job_public(job) | {"logs": manager.get_logs(job_id)}


@app.get("/api/jobs/{job_id}/script")
async def get_job_script(job_id: str, _=Depends(require_auth)):
    _get_job_or_404(job_id)
    return {"script": db.get_script(job_id)}


@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, _=Depends(require_auth)):
    _get_job_or_404(job_id)
    ok = await manager.cancel_job(job_id)
    if not ok:
        raise HTTPException(status_code=409, detail="El job ya no esta activo")
    return {"ok": True}


@app.get("/api/jobs/{job_id}/video")
async def get_video(job_id: str, _=Depends(require_auth)):
    job = _get_job_or_404(job_id)
    if job["status"] != "done" or not job.get("video_path"):
        raise HTTPException(status_code=404, detail="Video no disponible")
    video = Path(job["video_path"]).resolve()
    # El video debe vivir dentro del directorio del job (defensa en profundidad)
    job_dir = (cfg.render_jobs_dir / job_id).resolve()
    if not video.is_file() or job_dir not in video.parents:
        raise HTTPException(status_code=404, detail="Video no disponible")
    return FileResponse(video, media_type="video/mp4",
                        filename=f"{job['scene']}_{job_id}.mp4")


@app.get("/api/jobs/{job_id}/thumb")
async def get_thumb(job_id: str, _=Depends(require_auth)):
    job = _get_job_or_404(job_id)
    if not job.get("thumb_path"):
        raise HTTPException(status_code=404, detail="Miniatura no disponible")
    thumb = Path(job["thumb_path"]).resolve()
    # Misma defensa en profundidad que /video: solo dentro del dir del job.
    job_dir = (cfg.render_jobs_dir / job_id).resolve()
    if not thumb.is_file() or job_dir not in thumb.parents:
        raise HTTPException(status_code=404, detail="Miniatura no disponible")
    return FileResponse(thumb, media_type="image/jpeg")


@app.delete("/api/jobs/failed")
async def delete_failed_jobs(_=Depends(require_auth)):
    """Borra en lote todos los jobs error/timeout/cancelled."""
    deleted = manager.delete_failed_jobs()
    return {"deleted": deleted, "storage": _storage_public()}


@app.delete("/api/jobs/older-than/{days}")
async def delete_old_jobs(days: int, _=Depends(require_auth)):
    """Purga jobs 'done' con mas de `days` dias de antiguedad."""
    if not (1 <= days <= 3650):
        raise HTTPException(status_code=422, detail="Dias fuera de rango (1-3650)")
    deleted, freed = manager.delete_jobs_older_than(days)
    return {"deleted": deleted, "freed_bytes": freed, "storage": _storage_public()}


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str, _=Depends(require_auth)):
    job = _get_job_or_404(job_id)
    if job["status"] in ("queued", "running"):
        raise HTTPException(status_code=409,
                            detail="El job esta activo: cancelalo antes de borrarlo")
    manager.delete_job(job_id)
    return {"ok": True, "storage": _storage_public()}


# ── biblioteca de lecciones ───────────────────────────────────────────────────

@app.get("/api/lessons")
async def lessons_index(_=Depends(require_auth)):
    return lessons_store.index()


@app.get("/api/lessons/{lesson_id:path}")
async def lesson_detail(lesson_id: str, _=Depends(require_auth)):
    lesson = lessons_store.get(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Leccion no encontrada")
    return lesson


# ── biblioteca de animaciones ─────────────────────────────────────────────────

@app.get("/api/animations")
async def animations_index(_=Depends(require_auth)):
    return animations_store.index()


@app.get("/api/animations/{animation_id:path}")
async def animation_detail(animation_id: str, _=Depends(require_auth)):
    animation = animations_store.get(animation_id)
    if not animation:
        raise HTTPException(status_code=404, detail="Animación no encontrada")
    return animation


# ── asistente IA ──────────────────────────────────────────────────────────────

class AIDebugBody(BaseModel):
    script: str = Field(max_length=200_000)
    logs: str = Field(default="", max_length=400_000)


class AIGenerateBody(BaseModel):
    prompt: str = Field(min_length=3, max_length=8_000)


@app.post("/api/ai/explain")
async def ai_explain(body: AIDebugBody, _=Depends(require_auth)):
    try:
        return {"explanation": await assistant.explain(body.script, body.logs)}
    except AIError as e:
        raise HTTPException(status_code=e.status, detail=e.detail)


@app.post("/api/ai/fix")
async def ai_fix(body: AIDebugBody, _=Depends(require_auth)):
    try:
        return {"script": await assistant.fix(body.script, body.logs)}
    except AIError as e:
        raise HTTPException(status_code=e.status, detail=e.detail)


@app.post("/api/ai/generate")
async def ai_generate(body: AIGenerateBody, _=Depends(require_auth)):
    try:
        return {"script": await assistant.generate(body.prompt)}
    except AIError as e:
        raise HTTPException(status_code=e.status, detail=e.detail)


# ── monitoreo / SSE ───────────────────────────────────────────────────────────

@app.get("/api/metrics")
async def get_metrics(_=Depends(require_auth)):
    payload = {"host": metrics.host_metrics(), "containers": None}
    try:
        payload["containers"] = await runner.stats()
    except Exception:
        pass
    return payload


@app.get("/api/metrics/history")
async def metrics_history(_=Depends(require_auth)):
    """Ultimos ~30 min de CPU/RAM/disco (+ contenedor de render si lo hubo)."""
    return {"interval": cfg.metrics_interval, "samples": list(history.samples)}


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


@app.get("/api/events")
async def sse_events(request: Request, _=Depends(require_auth)):
    """Stream SSE unico: metricas, cambios de estado de jobs y logs en vivo."""
    queue = bus.subscribe()

    async def gen():
        try:
            # estado inicial inmediato para que la UI pinte sin esperar el tick
            yield _sse({"type": "metrics", "host": metrics.host_metrics(),
                        "containers": None})
            while True:
                if await request.is_disconnected():
                    return
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                    yield _sse(event)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            bus.unsubscribe(queue)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


@app.get("/api/health")
async def health():
    return {"ok": True, "runner": await runner.ping()}
