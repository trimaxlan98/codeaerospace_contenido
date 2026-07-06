"""Pruebas del cliente Fable 5. El SDK de Anthropic SIEMPRE va mockeado:
estos tests no deben tocar la red ni generar coste."""

import asyncio

import pytest


@pytest.fixture()
def fable_client(client, monkeypatch):
    """Cliente autenticado con Fable 5 habilitado (API key dummy)."""
    from .conftest import TEST_PASSWORD
    r = client.post("/api/login", json={"username": "tester",
                                        "password": TEST_PASSWORD})
    assert r.status_code == 200
    monkeypatch.setenv("MS_ANTHROPIC_API_KEY", "dummy-key-for-tests")
    from app.main import fable_assistant
    fable_assistant.cfg.anthropic_api_key = "dummy-key-for-tests"
    return client


def _mock_call(monkeypatch, text, record=None):
    from app.main import fable_assistant

    def fake(user):
        if record is not None:
            record["user"] = user
        return text

    monkeypatch.setattr(fable_assistant, "_call_model", fake)


FAKE_RESPONSE = (
    "Un efecto de disolucion en particulas.\n\n"
    "```python:primitive\n"
    "class Dissolve:\n"
    "    def __init__(self):\n"
    "        pass\n"
    "```\n"
    "```python:demo\n"
    "from manim import *\n"
    "from primitive import Dissolve\n\n\n"
    "class DemoScene(Scene):\n"
    "    def construct(self):\n"
    "        self.wait(1)\n"
    "```\n"
)


def test_disabled_by_default(client):
    from app.fable import FableError
    from app.main import fable_assistant
    assert fable_assistant.enabled is False
    with pytest.raises(FableError):
        asyncio.run(fable_assistant.propose_primitive("algo"))


def test_propose_primitive_extracts_both_blocks(fable_client, monkeypatch):
    from app.main import fable_assistant
    rec = {}
    _mock_call(monkeypatch, FAKE_RESPONSE, record=rec)
    result = asyncio.run(fable_assistant.propose_primitive("una disolucion en particulas"))
    assert "class Dissolve" in result["primitive_code"]
    assert "class DemoScene(Scene)" in result["demo_scene_code"]
    assert "disolucion" in rec["user"]


def test_propose_primitive_includes_feedback_and_previous_code(fable_client, monkeypatch):
    from app.main import fable_assistant
    rec = {}
    _mock_call(monkeypatch, FAKE_RESPONSE, record=rec)
    asyncio.run(fable_assistant.propose_primitive(
        "una disolucion en particulas",
        feedback="hazlo mas lento",
        previous_code="class Dissolve:\n    pass\n",
    ))
    assert "hazlo mas lento" in rec["user"]
    assert "class Dissolve" in rec["user"]


def test_propose_primitive_missing_blocks_raises(fable_client, monkeypatch):
    from app.fable import FableError
    _mock_call(monkeypatch, "solo texto sin bloques de codigo")
    from app.main import fable_assistant
    with pytest.raises(FableError):
        asyncio.run(fable_assistant.propose_primitive("algo"))


def test_rate_limit(fable_client, monkeypatch):
    from app.main import fable_assistant
    from app.fable import FableError
    _mock_call(monkeypatch, FAKE_RESPONSE)
    fable_assistant.limiter.per_minute = 2
    try:
        asyncio.run(fable_assistant.propose_primitive("a"))
        asyncio.run(fable_assistant.propose_primitive("b"))
        with pytest.raises(FableError) as exc_info:
            asyncio.run(fable_assistant.propose_primitive("c"))
        assert exc_info.value.status == 429
    finally:
        fable_assistant.limiter.per_minute = 5
        fable_assistant.limiter._hits.clear()
