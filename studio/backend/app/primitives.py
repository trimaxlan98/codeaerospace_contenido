"""Orquestador de propuestas de primitivas de Manim generadas por Fable 5.

Cada propuesta vive en memoria + un directorio de staging efimero (fuera de
git, mismo patron que render_jobs/) hasta que se aprueba (se copia a
studio/content/manim_extensions/) o se rechaza (se borra el staging). Sin
persistencia en SQLite: si el backend se reinicia, las propuestas pendientes
se pierden — aceptable para una herramienta experimental de uso esporadico
con aprobacion humana obligatoria.
"""

import asyncio
import shutil
import time
import uuid
from pathlib import Path

from .config import Settings
from .events import EventBus
from .fable import FableAssistant, FableError
from .jobs import JobManager
from .scenes import detect_scenes

_PROPOSAL_KEYS = ("id", "slug", "description", "status", "primitive_code",
                  "demo_scene_code", "explanation", "job_id", "error",
                  "created_at", "feedback_history")


class PrimitiveError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


def proposal_public(p: dict) -> dict:
    return {k: p.get(k) for k in _PROPOSAL_KEYS}


class PrimitiveManager:
    def __init__(self, cfg: Settings, fable: FableAssistant, jobs: JobManager,
                 bus: EventBus) -> None:
        self.cfg = cfg
        self.fable = fable
        self.jobs = jobs
        self.bus = bus
        self.proposals: dict[str, dict] = {}

    # ── API publica ──────────────────────────────────────────────────────

    def list_proposals(self) -> list[dict]:
        return sorted((proposal_public(p) for p in self.proposals.values()),
                      key=lambda p: p["created_at"], reverse=True)

    def get_proposal(self, proposal_id: str) -> dict | None:
        p = self.proposals.get(proposal_id)
        return proposal_public(p) if p else None

    def propose(self, slug: str, description: str) -> dict:
        if not self.fable.enabled:
            raise PrimitiveError(503, "Fable 5 no configurado")
        proposal_id = uuid.uuid4().hex[:16]
        proposal = {
            "id": proposal_id, "slug": slug, "description": description,
            "status": "generating", "primitive_code": None,
            "demo_scene_code": None, "explanation": None, "job_id": None,
            "error": None, "created_at": time.time(), "feedback_history": [],
        }
        self.proposals[proposal_id] = proposal
        self._publish(proposal_id)
        asyncio.create_task(
            self._generate_and_render(proposal_id, description, None, None))
        return proposal_public(proposal)

    def iterate(self, proposal_id: str, feedback: str) -> dict:
        proposal = self._get_or_404(proposal_id)
        if proposal["status"] == "generating":
            raise PrimitiveError(409, "Ya hay una generacion en curso para esta propuesta")
        proposal["feedback_history"].append(feedback)
        previous_code = proposal["primitive_code"]
        description = proposal["description"]
        proposal["status"] = "generating"
        proposal["error"] = None
        self._publish(proposal_id)
        asyncio.create_task(
            self._generate_and_render(proposal_id, description, feedback, previous_code))
        return proposal_public(proposal)

    def approve(self, proposal_id: str) -> dict:
        proposal = self._get_or_404(proposal_id)
        if proposal["status"] != "rendering" or self._job_status(proposal["job_id"]) != "done":
            raise PrimitiveError(409, "La propuesta no tiene un render listo para aprobar")
        target = self.cfg.manim_extensions_dir / f"{proposal['slug']}.py"
        if target.is_file():
            raise PrimitiveError(
                409, f"Ya existe una primitiva con el slug '{proposal['slug']}'")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(proposal["primitive_code"], encoding="utf-8")
        proposal["status"] = "approved"
        self._publish(proposal_id)
        self._cleanup_staging(proposal_id)
        return proposal_public(proposal)

    def reject(self, proposal_id: str) -> dict:
        proposal = self._get_or_404(proposal_id)
        if proposal["status"] == "generating":
            raise PrimitiveError(409, "Ya hay una generacion en curso para esta propuesta")
        proposal["status"] = "rejected"
        self._publish(proposal_id)
        self._cleanup_staging(proposal_id)
        return proposal_public(proposal)

    # ── internos ─────────────────────────────────────────────────────────

    async def _generate_and_render(self, proposal_id: str, description: str,
                                   feedback: str | None, previous_code: str | None) -> None:
        proposal = self.proposals[proposal_id]
        try:
            result = await self.fable.propose_primitive(
                description, feedback=feedback, previous_code=previous_code)
        except FableError as e:
            proposal["status"] = "failed"
            proposal["error"] = e.detail
            self._publish(proposal_id)
            return
        except Exception as e:  # nunca debe morir el task en segundo plano
            proposal["status"] = "failed"
            proposal["error"] = f"error interno: {e}"
            self._publish(proposal_id)
            return

        proposal["primitive_code"] = result["primitive_code"]
        proposal["demo_scene_code"] = result["demo_scene_code"]
        proposal["explanation"] = result["explanation"]

        try:
            scenes = detect_scenes(result["demo_scene_code"])
        except ValueError as e:
            proposal["status"] = "failed"
            proposal["error"] = f"escena demo invalida: {e}"
            self._publish(proposal_id)
            return
        if len(scenes) != 1:
            proposal["status"] = "failed"
            proposal["error"] = (
                f"la escena demo debe definir exactamente 1 escena (encontradas: {len(scenes)})")
            self._publish(proposal_id)
            return
        scene_name = scenes[0]

        try:
            staging = self._staging_dir(proposal_id)
            staging.mkdir(parents=True, exist_ok=True)
            (staging / "primitive.py").write_text(
                result["primitive_code"], encoding="utf-8")

            bootstrap = f'import sys\nsys.path.insert(0, "/workspace/pending_primitives/{proposal_id}")\n\n'
            full_script = bootstrap + result["demo_scene_code"]

            job = self.jobs.create_job(full_script, scene_name, "ql",
                                       self.cfg.default_timeout)
        except Exception as e:
            proposal["status"] = "failed"
            proposal["error"] = f"no se pudo lanzar el render de muestra: {e}"
            self._publish(proposal_id)
            return

        proposal["job_id"] = job["id"]
        proposal["status"] = "rendering"
        self._publish(proposal_id)

    def _staging_dir(self, proposal_id: str) -> Path:
        return self.cfg.pending_primitives_dir / proposal_id

    def _cleanup_staging(self, proposal_id: str) -> None:
        shutil.rmtree(self._staging_dir(proposal_id), ignore_errors=True)

    def _job_status(self, job_id: str | None) -> str | None:
        if not job_id:
            return None
        job = self.jobs.db.get_job(job_id)
        return job["status"] if job else None

    def _get_or_404(self, proposal_id: str) -> dict:
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise PrimitiveError(404, "Propuesta no encontrada")
        return proposal

    def _publish(self, proposal_id: str) -> None:
        proposal = self.proposals.get(proposal_id)
        if proposal:
            self.bus.publish({"type": "primitive", "proposal": proposal_public(proposal)})
