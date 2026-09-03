"""ManimStudio API — FastAPI, escucha solo en 127.0.0.1 detras de nginx/TLS."""

import asyncio
import json
import re
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from . import metrics
from .ai import AIError, Assistant
from .animations import AnimationStore
from .auth import (change_password as auth_change_password, client_ip,
                   clear_session, create_session, get_rate_limiter,
                   require_auth, session_valid, verify_credentials)
from .audio_api import make_router as make_audio_router
from .config import get_settings
from .conocimiento import Conocimiento
from .db import Database
from .events import EventBus
from .jobs import QUALITIES, JobManager, job_public
from .lessons import LessonStore
from .musica_api import make_router as make_musica_router
from .narracion import NarracionService
from .narracion_api import make_router as make_narracion_router
from .pelicula import PeliculaService
from .pelicula_api import make_router as make_pelicula_router
from .presentaciones import PresentacionService
from .presentaciones_api import make_router as make_presentaciones_router
from .projects import FORMATO_DEFECTO, ProjectService
from .projects_api import make_router as make_projects_router
from .runner_client import RunnerClient
from .sfx_api import make_router as make_sfx_router
from .scenes import detect_scenes

RE_JOB_ID = re.compile(r"^[a-f0-9]{8,32}$")

# Techo del listado de jobs. Con el limite historico de 50, los renders mas
# viejos desaparecian de la Biblioteca pero seguian contando contra la cuota
# de disco; 500 cubre con holgura el uso real de un solo usuario.
JOBS_LIST_LIMIT = 500

cfg = get_settings()
db = Database(cfg.db_path)
db.ensure_auth_seed(cfg.admin_password_hash)
bus = EventBus()
runner = RunnerClient(cfg.runner_socket)
manager = JobManager(cfg, db, runner, bus)
service = ProjectService(db)
manager.on_job_done = service.handle_job_done
narracion_service = NarracionService(cfg, db)
pelicula_service = PeliculaService(cfg, db, runner, narracion_service)
presentacion_service = PresentacionService(cfg, db, runner)
# 30 min de historia al intervalo configurado (450 muestras a 4 s).
history = metrics.History(maxlen=max(360, int(1800 // cfg.metrics_interval)))
conocimiento = Conocimiento(cfg)
assistant = Assistant(cfg, conocimiento)
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
app.include_router(make_projects_router(cfg, db, manager, service,
                                        narracion_service))
app.include_router(make_narracion_router(cfg, db, narracion_service))
app.include_router(make_pelicula_router(cfg, db, pelicula_service))
app.include_router(make_presentaciones_router(cfg, db,
                                             presentacion_service))
app.include_router(make_sfx_router(cfg, runner))
app.include_router(make_musica_router(cfg, runner))
app.include_router(make_audio_router(cfg, db, manager, service,
                                     narracion_service))

# Endpoints que deben seguir accesibles con must_change_password activo: sin
# ellos el usuario quedaria atrapado sin poder ni cambiar la password ni
# salir. Todo lo demas bajo /api/ se bloquea con 403 hasta que la cambie.
_PASSWORD_GATE_EXEMPT = {"/api/login", "/api/logout", "/api/me",
                        "/api/change-password", "/api/health"}


@app.middleware("http")
async def _enforce_password_change(request: Request, call_next):
    path = request.url.path
    if (path.startswith("/api/") and path not in _PASSWORD_GATE_EXEMPT
            and session_valid(cfg, request)):
        auth_row = db.get_auth()
        if auth_row and auth_row["must_change_password"]:
            return JSONResponse(
                status_code=403,
                content={"detail": "Debes cambiar la contraseña antes de continuar",
                        "code": "PASSWORD_CHANGE_REQUIRED"})
    return await call_next(request)


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


class ChangePasswordBody(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=1, max_length=256)


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
    if not verify_credentials(cfg, db, body.username, body.password):
        limiter.record_failure(ip)
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    limiter.record_success(ip)
    create_session(cfg, response)
    auth_row = db.get_auth()
    return {"ok": True, "user": cfg.admin_user,
            "must_change_password": bool(auth_row and auth_row["must_change_password"])}


@app.post("/api/logout")
async def logout(response: Response, _=Depends(require_auth)):
    clear_session(cfg, response)
    return {"ok": True}


@app.get("/api/me")
async def me(request: Request):
    if session_valid(cfg, request):
        auth_row = db.get_auth()
        return {"authenticated": True, "user": cfg.admin_user,
                "ai_enabled": assistant.enabled,
                "must_change_password": bool(auth_row and auth_row["must_change_password"])}
    return {"authenticated": False}


@app.post("/api/change-password")
async def change_password(body: ChangePasswordBody, _=Depends(require_auth)):
    try:
        auth_change_password(db, body.current_password, body.new_password)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"ok": True}


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
    _check_quota()
    return manager.create_job(body.script, body.scene, body.quality, timeout)


def _check_quota() -> None:
    quota = cfg.max_storage_mb * 1024 * 1024
    used = manager.storage_usage()
    if used >= quota:
        raise HTTPException(
            status_code=507,
            detail=(f"Almacenamiento lleno: {used / 2**20:.0f} MB usados de "
                    f"{cfg.max_storage_mb} MB. Borra videos de la Biblioteca "
                    "para liberar espacio."))


def _storage_public() -> dict:
    return {"used_bytes": manager.storage_usage(),
            "quota_bytes": cfg.max_storage_mb * 1024 * 1024}


@app.get("/api/jobs")
async def list_jobs(_=Depends(require_auth)):
    return {"jobs": [job_public(j) | {"script_len": j.get("script_len")}
                     for j in db.list_jobs(limit=JOBS_LIST_LIMIT)],
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
    # Si el promo ya se mezcló, lo que sirve la app es el video CON sonido.
    # El mudo se conserva al lado: re-mezclar no obliga a re-renderizar.
    ruta = job.get("audio_path") or job["video_path"]
    video = Path(ruta).resolve()
    # El video debe vivir dentro del directorio del job (defensa en profundidad)
    job_dir = (cfg.render_jobs_dir / job_id).resolve()
    if not video.is_file() or job_dir not in video.parents:
        video = Path(job["video_path"]).resolve()
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


# Nombre de archivo de la verificacion: un conjunto cerrado, no una ruta.
# Los escribe promo_verifica.py dentro de <job>/verificacion/.
RE_FRAME = re.compile(r"^(primero|ultimo|costura|f[0-9]{2})\.png$")


@app.get("/api/jobs/{job_id}/verificacion/{archivo}")
async def get_frame_verificacion(job_id: str, archivo: str,
                                 _=Depends(require_auth)):
    """Frames del informe: la tira de revisión y el par primero|último.

    Mirar los frames es la costumbre que caza lo que ningún número dice (un
    elemento fuera del lienzo, dos cifras que se leen pegadas).
    """
    _get_job_or_404(job_id)
    if not RE_FRAME.match(archivo):
        raise HTTPException(status_code=404, detail="Frame no disponible")
    job_dir = (cfg.render_jobs_dir / job_id).resolve()
    png = (job_dir / "verificacion" / archivo).resolve()
    if not png.is_file() or job_dir not in png.parents:
        raise HTTPException(status_code=404, detail="Frame no disponible")
    return FileResponse(png, media_type="image/png")


@app.delete("/api/jobs/failed")
async def delete_failed_jobs(_=Depends(require_auth)):
    """Borra en lote todos los jobs error/timeout/cancelled."""
    deleted = manager.delete_failed_jobs()
    return {"deleted": deleted, "storage": _storage_public()}


@app.delete("/api/jobs/finished")
async def delete_finished_jobs(_=Depends(require_auth)):
    """Vacia el historial completo (terminados, videos incluidos)."""
    deleted, freed = manager.delete_finished_jobs()
    return {"deleted": deleted, "freed_bytes": freed, "storage": _storage_public()}


@app.post("/api/jobs/{job_id}/retry", status_code=201)
async def retry_job(job_id: str, _=Depends(require_auth)):
    """Reencola un job terminado con su mismo script/escena/calidad/formato."""
    job = _get_job_or_404(job_id)
    if job["status"] in ("queued", "running"):
        raise HTTPException(status_code=409, detail="El job ya esta activo")
    _check_quota()
    # El formato y el fondo viajan con el job (no se vuelven a leer del
    # proyecto): un reintento tiene que producir el MISMO archivo que el
    # intento original.
    # El tipo se relee del proyecto y no viaja con el job: es inmutable
    # (update_project no lo acepta), asi que da siempre la misma respuesta.
    proyecto = db.get_project(job["project_id"]) if job.get("project_id") else None
    return manager.create_job(job["script"], job["scene"], job["quality"],
                              job["timeout"], project_id=job.get("project_id"),
                              clip_id=job.get("clip_id"),
                              content_hash=job.get("content_hash"),
                              formato=job.get("formato") or FORMATO_DEFECTO,
                              fondo=job.get("fondo") or "marca",
                              tipo=(proyecto or {}).get("tipo") or "curso")


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

class AnimationCategoryBody(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class AnimationCreateBody(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=120)
    script: str


@app.get("/api/animations")
async def animations_index(_=Depends(require_auth)):
    return animations_store.index()


@app.post("/api/animations/categories", status_code=201)
async def create_animation_category(body: AnimationCategoryBody,
                                    _=Depends(require_auth)):
    try:
        return animations_store.create_category(body.name)
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/animations", status_code=201)
async def create_animation(body: AnimationCreateBody, _=Depends(require_auth)):
    _check_script(body.script)
    try:
        return animations_store.create_animation(body.category, body.title,
                                                 body.script)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


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
