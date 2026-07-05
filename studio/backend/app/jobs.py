"""Gestor de renders: cola estricta de 1 job simultaneo + logs en vivo.

Este VPS tiene 2 vCPU compartidas con produccion: los renders se ejecutan
uno a uno. La cola vive en memoria y el historial en SQLite; si el backend
se reinicia, los jobs pendientes se marcan como interrumpidos.
"""

import asyncio
import shutil
import time
import uuid
from collections import deque
from pathlib import Path

from .config import Settings
from .db import Database
from .events import EventBus
from .runner_client import RunnerClient, RunnerError

QUALITIES = {"ql", "qm", "qh"}
ACTIVE_STATES = ("queued", "running")
LOG_BUFFER_MAX = 5000


def job_public(job: dict) -> dict:
    """Vista del job para la API (sin el script completo)."""
    keys = ("id", "scene", "quality", "timeout", "status", "video_path", "error",
            "created_at", "started_at", "finished_at")
    return {k: job.get(k) for k in keys}


class JobManager:
    def __init__(self, cfg: Settings, db: Database, runner: RunnerClient, bus: EventBus) -> None:
        self.cfg = cfg
        self.db = db
        self.runner = runner
        self.bus = bus
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self.logs: dict[str, deque[str]] = {}
        self.current_job_id: str | None = None
        self._cancelled: set[str] = set()
        self._worker_task: asyncio.Task | None = None

    # ── ciclo de vida ────────────────────────────────────────────────────────

    def start(self) -> None:
        interrupted = self.db.mark_interrupted()
        if interrupted:
            print(f"[jobs] {interrupted} job(s) marcados como interrumpidos tras reinicio")
        self._worker_task = asyncio.get_event_loop().create_task(self._worker())

    async def stop(self) -> None:
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

    # ── API publica ──────────────────────────────────────────────────────────

    def create_job(self, script: str, scene: str, quality: str, timeout: int) -> dict:
        job_id = uuid.uuid4().hex[:16]
        now = time.time()
        job = {
            "id": job_id, "scene": scene, "quality": quality, "timeout": timeout,
            "status": "queued", "script": script, "created_at": now,
        }
        # El script se escribe en la ruta canonica que el runner espera.
        job_dir = self.cfg.render_jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        (job_dir / "scene.py").write_text(script, encoding="utf-8")

        self.db.insert_job(job)
        self.logs[job_id] = deque(maxlen=LOG_BUFFER_MAX)
        self.queue.put_nowait(job_id)
        self._publish_job(job_id)
        return job_public({**job, "video_path": None, "error": None,
                           "started_at": None, "finished_at": None})

    async def cancel_job(self, job_id: str) -> bool:
        job = self.db.get_job(job_id)
        if not job or job["status"] not in ACTIVE_STATES:
            return False
        self._cancelled.add(job_id)
        if job["status"] == "running":
            try:
                await self.runner.cancel(job_id)  # docker rm -f del contenedor
            except RunnerError:
                pass
        else:
            self._finish(job_id, "cancelled")
        return True

    def get_logs(self, job_id: str) -> list[str]:
        buf = self.logs.get(job_id)
        return list(buf) if buf is not None else []

    # ── worker ───────────────────────────────────────────────────────────────

    async def _worker(self) -> None:
        while True:
            job_id = await self.queue.get()
            if job_id in self._cancelled:
                continue
            try:
                await self._run_job(job_id)
            except Exception as e:  # el worker nunca debe morir
                print(f"[jobs] error inesperado en job {job_id}: {e!r}")
                self._finish(job_id, "error", error=f"error interno: {e}")
            finally:
                self.current_job_id = None

    async def _run_job(self, job_id: str) -> None:
        job = self.db.get_job(job_id)
        if not job or job["status"] != "queued":
            return
        self.current_job_id = job_id
        self.db.update_job(job_id, status="running", started_at=time.time())
        self._publish_job(job_id)

        buf = self.logs.setdefault(job_id, deque(maxlen=LOG_BUFFER_MAX))
        exit_code: int | None = None
        timed_out = False
        runner_error: str | None = None

        try:
            async for event in self.runner.render(
                job_id, job["scene"], job["quality"], job["timeout"]
            ):
                etype = event.get("type")
                if etype == "log":
                    line = event.get("line", "")
                    buf.append(line)
                    self.bus.publish({"type": "joblog", "job_id": job_id, "line": line})
                elif etype == "done":
                    exit_code = event.get("exit_code", 1)
                    timed_out = bool(event.get("timed_out"))
                elif etype == "error":
                    runner_error = event.get("error", "error del runner")
        except (RunnerError, asyncio.TimeoutError) as e:
            runner_error = str(e)

        if job_id in self._cancelled:
            self._finish(job_id, "cancelled")
        elif runner_error:
            self._finish(job_id, "error", error=runner_error)
        elif timed_out:
            self._finish(job_id, "timeout",
                         error=f"render supero el timeout de {job['timeout']}s")
        elif exit_code == 0:
            video = self._find_video(job_id)
            if video:
                self._cleanup_partial_files(job_id)
                self._finish(job_id, "done", video_path=str(video))
            else:
                self._finish(job_id, "error",
                             error="render termino sin producir video (revisa los logs)")
        else:
            self._finish(job_id, "error", error=f"manim salio con codigo {exit_code}")

    def _find_video(self, job_id: str) -> Path | None:
        media = self.cfg.render_jobs_dir / job_id / "media"
        if not media.is_dir():
            return None
        candidates = sorted(media.glob("videos/**/*.mp4"),
                            key=lambda p: p.stat().st_mtime, reverse=True)
        # Ignorar videos parciales de manim
        finals = [p for p in candidates if "partial_movie_files" not in p.parts]
        return finals[0] if finals else None

    def _finish(self, job_id: str, status: str, **extra) -> None:
        self._cancelled.discard(job_id)
        self.db.update_job(job_id, status=status, finished_at=time.time(), **extra)
        if status in ("error", "timeout", "cancelled"):
            self.delete_job_files(job_id)
        self._publish_job(job_id)

    def _publish_job(self, job_id: str) -> None:
        job = self.db.get_job(job_id)
        if job:
            self.bus.publish({"type": "job", "job": job_public(job)})

    # ── mantenimiento ────────────────────────────────────────────────────────

    def _cleanup_partial_files(self, job_id: str) -> None:
        """Elimina los archivos parciales de manim tras un render exitoso."""
        try:
            for partial_dir in self.cfg.render_jobs_dir.glob(
                f"{job_id}/media/videos/*/*/partial_movie_files"
            ):
                if partial_dir.is_dir():
                    shutil.rmtree(partial_dir, ignore_errors=True)
        except Exception as e:
            print(f"[jobs] error limpiando parciales de {job_id}: {e!r}")

    def delete_job_files(self, job_id: str) -> None:
        job_dir = self.cfg.render_jobs_dir / job_id
        if job_dir.is_dir():
            shutil.rmtree(job_dir, ignore_errors=True)
