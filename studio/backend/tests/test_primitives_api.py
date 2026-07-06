"""Pruebas de los endpoints /api/primitives. Fable 5 mockeado."""

import time

import pytest


@pytest.fixture()
def fable_enabled(authed, monkeypatch):
    from app.main import fable_assistant

    async def fake_propose(description, feedback=None, previous_code=None):
        return {
            "primitive_code": "class Dissolve:\n    pass\n",
            "demo_scene_code": (
                "from manim import *\n"
                "from primitive import Dissolve\n\n\n"
                "class DemoScene(Scene):\n"
                "    def construct(self):\n"
                "        self.wait(1)\n"
            ),
            "explanation": "explicacion",
        }

    monkeypatch.setattr(fable_assistant, "propose_primitive", fake_propose)
    # `enabled` es una property derivada de la API key: se habilita via cfg.
    monkeypatch.setattr(fable_assistant.cfg, "anthropic_api_key", "dummy-key-for-tests")
    return authed


def test_primitives_requires_auth(client):
    assert client.get("/api/primitives").status_code == 401
    assert client.post("/api/primitives", json={"slug": "x", "description": "y"}).status_code == 401


def test_me_reports_fable_flag(authed):
    assert authed.get("/api/me").json()["fable_enabled"] is False


def test_propose_disabled_returns_503(authed):
    r = authed.post("/api/primitives", json={"slug": "x", "description": "un efecto"})
    assert r.status_code == 503


def _wait_until_rendering(client, proposal_id, attempts=50):
    for _ in range(attempts):
        time.sleep(0.02)
        r = client.get(f"/api/primitives/{proposal_id}")
        if r.json()["status"] != "generating":
            return r.json()
    raise AssertionError("la propuesta nunca salio de 'generating'")


def test_propose_list_and_get(fable_enabled):
    r = fable_enabled.post("/api/primitives",
                           json={"slug": "disolucion", "description": "un efecto de disolucion"})
    assert r.status_code == 201
    proposal_id = r.json()["id"]
    assert r.json()["status"] == "generating"

    current = _wait_until_rendering(fable_enabled, proposal_id)
    assert current["status"] == "rendering"
    assert current["job_id"]

    listed = fable_enabled.get("/api/primitives").json()["proposals"]
    assert any(p["id"] == proposal_id for p in listed)


def test_approve_flow(fable_enabled):
    from app.main import primitives_manager
    r = fable_enabled.post("/api/primitives",
                           json={"slug": "aprobar-api", "description": "otro efecto"})
    proposal_id = r.json()["id"]
    current = _wait_until_rendering(fable_enabled, proposal_id)
    primitives_manager.jobs.db.update_job(current["job_id"], status="done")

    r = fable_enabled.post(f"/api/primitives/{proposal_id}/approve")
    assert r.status_code == 200
    assert r.json()["status"] == "approved"

    target = primitives_manager.cfg.manim_extensions_dir / "aprobar-api.py"
    assert target.is_file()


def test_reject_with_feedback_relaunches(fable_enabled):
    r = fable_enabled.post("/api/primitives",
                           json={"slug": "iterar-api", "description": "otro efecto mas"})
    proposal_id = r.json()["id"]
    _wait_until_rendering(fable_enabled, proposal_id)

    r = fable_enabled.post(f"/api/primitives/{proposal_id}/iterate",
                           json={"feedback": "hazlo mas lento"})
    assert r.status_code == 200
    assert r.json()["status"] == "generating"


def test_get_unknown_proposal_404(authed):
    assert authed.get("/api/primitives/no-existe").status_code == 404
