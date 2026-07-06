"""Pruebas del orquestador de propuestas de primitivas. Fable 5 y el render
van siempre mockeados/mediante el JobManager real sobre un workspace temporal
(sin Docker real: se fuerza el estado del job manipulando la DB)."""

import asyncio

import pytest


FAKE_RESULT = {
    "primitive_code": "class Dissolve:\n    pass\n",
    "demo_scene_code": (
        "from manim import *\n"
        "from primitive import Dissolve\n\n\n"
        "class DemoScene(Scene):\n"
        "    def construct(self):\n"
        "        self.wait(1)\n"
    ),
    "explanation": "Una disolucion en particulas.",
}


@pytest.fixture()
def manager_with_deps(client, tmp_path, monkeypatch):
    """PrimitiveManager real, con FableAssistant.propose_primitive mockeado
    y el JobManager/EventBus reales de la app ya cargada por `client`."""
    from app.main import primitives_manager, fable_assistant

    async def fake_propose(description, feedback=None, previous_code=None):
        return FAKE_RESULT

    monkeypatch.setattr(fable_assistant, "propose_primitive", fake_propose)
    # `enabled` es una property derivada de la API key: se habilita via cfg.
    monkeypatch.setattr(fable_assistant.cfg, "anthropic_api_key", "dummy-key-for-tests")
    return primitives_manager


async def _wait_until(manager, proposal_id, predicate, attempts=50):
    for _ in range(attempts):
        await asyncio.sleep(0.02)
        current = manager.get_proposal(proposal_id)
        if predicate(current):
            return current
    raise AssertionError(f"la propuesta {proposal_id} nunca cumplio la condicion esperada")


def test_propose_creates_proposal_and_job(manager_with_deps):
    async def _run():
        proposal = manager_with_deps.propose("disolucion-particulas", "un efecto de disolucion")
        assert proposal["status"] == "generating"
        current = await _wait_until(manager_with_deps, proposal["id"],
                                    lambda p: p["status"] != "generating")
        assert current["status"] == "rendering"
        assert current["job_id"] is not None
        assert "class Dissolve" in current["primitive_code"]

        staging = manager_with_deps.cfg.pending_primitives_dir / proposal["id"] / "primitive.py"
        assert staging.is_file()
        assert "class Dissolve" in staging.read_text()

    asyncio.run(_run())


def test_approve_requires_job_done(manager_with_deps):
    async def _run():
        proposal = manager_with_deps.propose("otra-primitiva", "otro efecto")
        await _wait_until(manager_with_deps, proposal["id"], lambda p: p["job_id"])
        with pytest.raises(Exception):
            manager_with_deps.approve(proposal["id"])  # job aun no "done"

    asyncio.run(_run())


def test_approve_writes_to_manim_extensions(manager_with_deps):
    async def _run():
        proposal = manager_with_deps.propose("aprobada-slug", "efecto aprobable")
        current = await _wait_until(manager_with_deps, proposal["id"], lambda p: p["job_id"])

        manager_with_deps.jobs.db.update_job(current["job_id"], status="done")

        result = manager_with_deps.approve(proposal["id"])
        assert result["status"] == "approved"
        target = manager_with_deps.cfg.manim_extensions_dir / "aprobada-slug.py"
        assert target.is_file()
        assert "class Dissolve" in target.read_text()
        # el staging se limpia tras aprobar
        assert not (manager_with_deps.cfg.pending_primitives_dir / proposal["id"]).exists()

    asyncio.run(_run())


def test_get_proposal_unknown_returns_none(manager_with_deps):
    assert manager_with_deps.get_proposal("no-existe") is None


def test_reject_unknown_raises(manager_with_deps):
    from app.primitives import PrimitiveError
    with pytest.raises(PrimitiveError) as exc_info:
        manager_with_deps.reject("no-existe")
    assert exc_info.value.status == 404
