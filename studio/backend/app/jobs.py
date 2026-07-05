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
STORAGE_TTL = 15.0  # s: caché de storage_usage() para no recorrer el FS en cada request


def job_public(job: dict) -> dict:
    """Vista del job para la API (sin el script completo)."""
    keys = ("id", "scene", "quality", "timeout", "status", "video_path", "error",
            "created_at", "started_at", "finished_at", "size_bytes")
    return {k: job.get(k) for k in keys} | {"has_thumb": bool(job.get("thumb_path"))}


class JobManager:
    FAILED_STATES = ("error", "timeout", "cancelled")

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
        self._storage_cache: int | None = None
        self._storage_cache_at: float = 0.0

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
        if buf is not None:
            return list(buf)
        # Fallback: render.log persistido (sobrevive reinicios del backend).
        # job_id ya paso el regex de la API; la ruta es la canonica del job.
        log_file = self.cfg.render_jobs_dir / job_id / "render.log"
        try:
            return log_file.read_text(encoding="utf-8", errors="replace") \
                           .splitlines()[-LOG_BUFFER_MAX:]
        except OSError:
            return []

    def delete_job(self, job_id: str) -> bool:
        """Borra fila + directorio. Jobs activos deben cancelarse antes."""
        job = self.db.get_job(job_id)
        if not job or job["status"] in ACTIVE_STATES:
            return False
        self.logs.pop(job_id, None)
        self.delete_job_files(job_id)
        self._invalidate_storage()  # se liberó espacio; la Biblioteca debe reflejar la cuota al instante
        self.db.delete_job(job_id)
        return True

    def storage_usage(self) -> int:
        """Bytes totales usados por render_jobs/ (videos, scripts, logs).

        Cacheado STORAGE_TTL s: recorrer el FS en cada GET /api/jobs es
        O(nº archivos). Se invalida al terminar o borrar un job.
        """
        now = time.time()
        if self._storage_cache is not None and now - self._storage_cache_at < STORAGE_TTL:
            return self._storage_cache
        total = 0
        root = self.cfg.render_jobs_dir
        if root.is_dir():
            for p in root.rglob("*"):
                try:
                    if p.is_file():
                        total += p.stat().st_size
                except OSError:
                    pass
        self._storage_cache = total
        self._storage_cache_at = now
        return total

    def _invalidate_storage(self) -> None:
        """Fuerza recálculo de storage_usage() en la próxima lectura."""
        self._storage_cache = None

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
                extra = {"size_bytes": video.stat().st_size}
                thumb = await self._make_thumbnail(job_id, buf)
                if thumb:
                    extra["thumb_path"] = thumb
                self._finish(job_id, "done", video_path=str(video), **extra)
            else:
                self._finish(job_id, "error",
                             error="render termino sin producir video (revisa los logs)")
        else:
            self._finish(job_id, "error", error=f"manim salio con codigo {exit_code}")

    async def _make_thumbnail(self, job_id: str, buf: deque) -> str | None:
        """Miniatura via runner (ffmpeg dentro del contenedor). No fatal si falla."""
        try:
            thumb_rel = await self.runner.thumbnail(job_id)
            thumb = (self.cfg.workspace / thumb_rel).resolve()
            if thumb.is_file():
                return str(thumb)
        except (RunnerError, asyncio.TimeoutError) as e:
            buf.append(f"[studio] miniatura no generada: {e}")
        return None

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
        if status in ("done", "error", "timeout"):
            # Persistir el log y liberar el buffer en memoria (get_logs hace
            # fallback al archivo). Para error/timeout el directorio quedo
            # vacio: se recrea solo con render.log (pocos KB) para que el
            # diagnostico sobreviva reinicios del backend.
            self._persist_log(job_id)
        elif status == "cancelled":
            self.logs.pop(job_id, None)
        self._invalidate_storage()  # el tamaño en disco cambió (video nuevo o archivos borrados)
        self._publish_job(job_id)

    def _persist_log(self, job_id: str) -> None:
        buf = self.logs.pop(job_id, None)
        if not buf:
            return
        try:
            job_dir = self.cfg.render_jobs_dir / job_id
            job_dir.mkdir(parents=True, exist_ok=True)
            (job_dir / "render.log").write_text("\n".join(buf) + "\n", encoding="utf-8")
        except OSError as e:
            print(f"[jobs] no se pudo persistir render.log de {job_id}: {e!r}")

    def _publish_job(self, job_id: str) -> None:
        job = self.db.get_job(job_id)
        if job:
            self.bus.publish({"type": "job", "job": job_public(job)})

    # ── mantenimiento ────────────────────────────────────────────────────────

    def delete_failed_jobs(self) -> int:
        """Borra todos los jobs fallidos/cancelados. Devuelve el conteo."""
        count = 0
        for job in self.db.list_jobs(limit=100_000):
            if job["status"] in self.FAILED_STATES and self.delete_job(job["id"]):
                count += 1
        return count

    def delete_jobs_older_than(self, days: int) -> tuple[int, int]:
        """Borra jobs 'done' terminados hace mas de `days` dias.

        Devuelve (conteo, bytes liberados segun size_bytes registrado).
        """
        cutoff = time.time() - days * 86400
        count = freed = 0
        for job in self.db.list_jobs(limit=100_000):
            if job["status"] == "done" and (job.get("finished_at") or 0) < cutoff:
                size = job.get("size_bytes") or 0
                if self.delete_job(job["id"]):
                    count += 1
                    freed += size
        return count, freed

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
