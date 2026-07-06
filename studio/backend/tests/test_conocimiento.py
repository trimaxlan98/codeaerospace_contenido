"""Pruebas del paquete de conocimiento del asistente IA (Vertex mockeado)."""

import pytest


FUENTE_PRIMITIVA = (
    '"""Primitiva de prueba."""\n\n'
    "class EfectoDePrueba:\n"
    "    pass\n"
)

FUENTE_DEMO = (
    "import sys\n"
    'sys.path.insert(0, "/workspace/studio/content/manim_extensions")\n\n'
    "from manim import *\n\n\n"
    "class DemoPrueba(Scene):\n"
    "    def construct(self):\n"
    "        self.wait(1)\n"
)


@pytest.fixture()
def con_contenido(client):
    """Crea una primitiva y una demo en el workspace temporal de la app."""
    from app.main import cfg
    cfg.manim_extensions_dir.mkdir(parents=True, exist_ok=True)
    (cfg.manim_extensions_dir / "efecto.py").write_text(
        FUENTE_PRIMITIVA, encoding="utf-8")
    demos = cfg.animations_dir / "experimentacion"
    demos.mkdir(parents=True, exist_ok=True)
    (demos / "01-demo-prueba.py").write_text(FUENTE_DEMO, encoding="utf-8")
    return client


def test_contexto_incluye_guia_primitivas_y_ejemplo(con_contenido):
    from app.main import conocimiento
    texto = conocimiento.contexto()
    assert "GUIA DEL PROYECTO" in texto
    assert "class EfectoDePrueba" in texto          # fuente de la primitiva
    assert "efecto.py" in texto
    assert "class DemoPrueba(Scene)" in texto        # ejemplo real


def test_contexto_sin_contenido_solo_guia(client):
    from app.main import conocimiento
    texto = conocimiento.contexto()
    assert "GUIA DEL PROYECTO" in texto
    assert "FUENTE DE LAS PRIMITIVAS" not in texto


def test_contexto_se_actualiza_por_mtime(con_contenido):
    from app.main import cfg, conocimiento
    assert "class EfectoDePrueba" in conocimiento.contexto()
    (cfg.manim_extensions_dir / "otro.py").write_text(
        "class OtroEfecto:\n    pass\n", encoding="utf-8")
    assert "class OtroEfecto" in conocimiento.contexto()


def test_generate_inyecta_conocimiento(con_contenido, tmp_path, monkeypatch):
    from .conftest import TEST_PASSWORD
    from app.main import assistant

    r = con_contenido.post("/api/login", json={"username": "tester",
                                               "password": TEST_PASSWORD})
    assert r.status_code == 200
    (tmp_path / "gcp-key.json").write_text('{"project_id": "test"}')

    rec = {}

    def fake(model, system, user):
        rec.update({"system": system, "user": user})
        return "```python\nfrom manim import *\n```"

    monkeypatch.setattr(assistant, "_call_model", fake)
    r = con_contenido.post("/api/ai/generate", json={"prompt": "una orbita"})
    assert r.status_code == 200
    assert "class EfectoDePrueba" in rec["system"]   # el modelo VE la primitiva
    assert "GUIA DEL PROYECTO" in rec["system"]


def test_fix_inyecta_conocimiento(con_contenido, tmp_path, monkeypatch):
    from .conftest import TEST_PASSWORD
    from app.main import assistant

    con_contenido.post("/api/login", json={"username": "tester",
                                           "password": TEST_PASSWORD})
    (tmp_path / "gcp-key.json").write_text('{"project_id": "test"}')

    rec = {}

    def fake(model, system, user):
        rec.update({"system": system})
        return "```python\nfrom manim import *\n```"

    monkeypatch.setattr(assistant, "_call_model", fake)
    r = con_contenido.post("/api/ai/fix",
                           json={"script": "x = 1", "logs": "Traceback"})
    assert r.status_code == 200
    assert "class EfectoDePrueba" in rec["system"]
