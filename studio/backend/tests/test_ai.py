"""Pruebas del asistente IA. El cliente Vertex SIEMPRE va mockeado:
estos tests no deben tocar la red ni generar coste."""

import pytest


@pytest.fixture()
def ai_client(client, tmp_path):
    """Cliente autenticado con el asistente habilitado y Vertex mockeado."""
    from .conftest import TEST_PASSWORD
    r = client.post("/api/login", json={"username": "tester",
                                        "password": TEST_PASSWORD})
    assert r.status_code == 200
    # Habilitar el feature-flag: existe el archivo de clave (contenido dummy,
    # jamas se lee porque _generate se mockea en cada test).
    (tmp_path / "gcp-key.json").write_text('{"project_id": "test"}')
    return client


def _mock_generate(monkeypatch, result="EXPLICACION DE PRUEBA", record=None):
    """Mockea SOLO la llamada al SDK: feature-flag, rate limit y truncado
    reales siguen ejecutandose."""
    from app.main import assistant

    def fake(model, system, user):
        if record is not None:
            record.update({"model": model, "system": system, "user": user})
        return result

    monkeypatch.setattr(assistant, "_call_model", fake)


def test_ai_requires_auth(client):
    for path in ("/api/ai/explain", "/api/ai/fix", "/api/ai/generate"):
        assert client.post(path, json={}).status_code == 401


def test_ai_disabled_503(authed):
    r = authed.post("/api/ai/explain", json={"script": "x", "logs": "err"})
    assert r.status_code == 503
    # /api/me refleja el feature-flag apagado
    assert authed.get("/api/me").json()["ai_enabled"] is False


def test_ai_enabled_flag(ai_client):
    assert ai_client.get("/api/me").json()["ai_enabled"] is True


def test_explain_uses_fast_model(ai_client, monkeypatch):
    rec = {}
    _mock_generate(monkeypatch, "El error es X", record=rec)
    r = ai_client.post("/api/ai/explain",
                       json={"script": "print(1)", "logs": "Traceback..."})
    assert r.status_code == 200
    assert r.json() == {"explanation": "El error es X"}
    assert rec["model"] == "gemini-2.5-flash"
    assert "print(1)" in rec["user"] and "Traceback" in rec["user"]


def test_fix_uses_deep_model_and_extracts_code(ai_client, monkeypatch):
    rec = {}
    _mock_generate(monkeypatch,
                   "Claro:\n```python\nfrom manim import *\n```\nlisto", record=rec)
    r = ai_client.post("/api/ai/fix", json={"script": "bad", "logs": "err"})
    assert r.status_code == 200
    assert r.json()["script"] == "from manim import *\n"
    assert rec["model"] == "gemini-2.5-pro"


def test_generate_returns_script(ai_client, monkeypatch):
    _mock_generate(monkeypatch, "```python\nclass A(Scene): pass\n```")
    r = ai_client.post("/api/ai/generate", json={"prompt": "un circulo azul"})
    assert r.status_code == 200
    assert "class A(Scene)" in r.json()["script"]


def test_generate_validates_prompt(ai_client):
    assert ai_client.post("/api/ai/generate", json={"prompt": ""}).status_code == 422


def test_ai_rate_limit(ai_client, monkeypatch):
    from app.main import assistant
    _mock_generate(monkeypatch, "ok")
    assistant.limiter.per_minute = 3
    try:
        codes = [ai_client.post("/api/ai/explain",
                                json={"script": "x", "logs": ""}).status_code
                 for _ in range(5)]
    finally:
        assistant.limiter.per_minute = 10
        assistant.limiter._hits.clear()
    assert codes[:3] == [200, 200, 200]
    assert codes[3] == 429 and codes[4] == 429


def test_truncation_helpers():
    from app.ai import _clip, _clip_tail
    assert _clip("abc", 10) == "abc"
    assert _clip("x" * 20, 10).startswith("x" * 10)
    assert "[truncado]" in _clip("x" * 20, 10)
    tail = _clip_tail("a" * 30 + "FINAL", 10)
    assert tail.endswith("FINAL") and tail.startswith("[truncado]")
