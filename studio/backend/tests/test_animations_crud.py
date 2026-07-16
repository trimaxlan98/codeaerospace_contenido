"""Tests del alta web de secciones y animaciones en la Biblioteca."""

import os
from pathlib import Path

SCRIPT = """from manim import *


class OrbitaNueva(Scene):
    def construct(self):
        self.wait()
"""

CATS = """- slug: dinamica-orbital
  name: Dinámica Orbital
- slug: satelites
  name: Satélites
"""


def _seed(tmp_path: Path) -> None:
    lessons_root = Path(os.environ["MS_LESSONS_DIR"])
    anim_root = Path(os.environ["MS_ANIMATIONS_DIR"])
    lessons_root.mkdir(parents=True, exist_ok=True)
    (lessons_root / "categories.yaml").write_text(CATS, encoding="utf-8")
    (anim_root / "dinamica-orbital").mkdir(parents=True, exist_ok=True)
    (anim_root / "dinamica-orbital" / "01-orbitas-kepler.py").write_text(
        SCRIPT, encoding="utf-8")


# ── secciones (categorias) ────────────────────────────────────────────────────

def test_crear_seccion(authed, tmp_path):
    _seed(tmp_path)
    r = authed.post("/api/animations/categories",
                    json={"name": "Propulsión Iónica"})
    assert r.status_code == 201
    assert r.json() == {"slug": "propulsion-ionica", "name": "Propulsión Iónica"}

    # aparece en el indice (vacia pero con directorio) y en el yaml
    cats = authed.get("/api/animations").json()["categories"]
    nueva = next(c for c in cats if c["slug"] == "propulsion-ionica")
    assert nueva["count"] == 0
    assert nueva["has_dir"] is True
    assert (Path(os.environ["MS_ANIMATIONS_DIR"]) / "propulsion-ionica").is_dir()
    yaml_text = (Path(os.environ["MS_LESSONS_DIR"]) / "categories.yaml").read_text()
    assert "propulsion-ionica" in yaml_text
    assert "Propulsión Iónica" in yaml_text


def test_categorias_sin_directorio_no_tienen_has_dir(authed, tmp_path):
    """Las categorias solo-lecciones (sin dir de animaciones) van con has_dir False."""
    _seed(tmp_path)
    cats = authed.get("/api/animations").json()["categories"]
    por_slug = {c["slug"]: c for c in cats}
    assert por_slug["dinamica-orbital"]["has_dir"] is True
    assert por_slug["satelites"]["has_dir"] is False


def test_crear_seccion_duplicada(authed, tmp_path):
    _seed(tmp_path)
    r = authed.post("/api/animations/categories", json={"name": "Satélites"})
    assert r.status_code == 409


def test_crear_seccion_nombre_sin_slug_valido(authed, tmp_path):
    _seed(tmp_path)
    r = authed.post("/api/animations/categories", json={"name": "···"})
    assert r.status_code == 422


def test_crear_seccion_requiere_auth(client, tmp_path):
    _seed(tmp_path)
    r = client.post("/api/animations/categories", json={"name": "X"})
    assert r.status_code == 401


# ── animaciones ───────────────────────────────────────────────────────────────

def test_crear_animacion(authed, tmp_path):
    _seed(tmp_path)
    r = authed.post("/api/animations", json={
        "category": "dinamica-orbital",
        "title": "Nueva órbita",
        "script": SCRIPT,
    })
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == "dinamica-orbital/02-nueva-orbita"
    assert body["scene"] == "OrbitaNueva"

    detalle = authed.get("/api/animations/dinamica-orbital/02-nueva-orbita")
    assert detalle.status_code == 200
    assert "class OrbitaNueva(Scene)" in detalle.json()["script"]

    cats = authed.get("/api/animations").json()["categories"]
    dyn = next(c for c in cats if c["slug"] == "dinamica-orbital")
    assert dyn["count"] == 2


def test_crear_animacion_en_seccion_nueva_vacia(authed, tmp_path):
    _seed(tmp_path)
    authed.post("/api/animations/categories", json={"name": "Cohetes"})
    r = authed.post("/api/animations", json={
        "category": "cohetes", "title": "Despegue", "script": SCRIPT,
    })
    assert r.status_code == 201
    assert r.json()["id"] == "cohetes/01-despegue"


def test_titulos_repetidos_numeran_consecutivo(authed, tmp_path):
    _seed(tmp_path)
    body = {"category": "dinamica-orbital", "title": "Órbita", "script": SCRIPT}
    r1 = authed.post("/api/animations", json=body)
    r2 = authed.post("/api/animations", json=body)
    assert r1.json()["id"] == "dinamica-orbital/02-orbita"
    assert r2.json()["id"] == "dinamica-orbital/03-orbita"


def test_crear_animacion_categoria_inexistente(authed, tmp_path):
    _seed(tmp_path)
    r = authed.post("/api/animations", json={
        "category": "no-existe", "title": "X", "script": SCRIPT,
    })
    assert r.status_code == 404


def test_crear_animacion_categoria_maliciosa(authed, tmp_path):
    _seed(tmp_path)
    for cat in ("../evil", "a/b", "..", "A-Mayus"):
        r = authed.post("/api/animations", json={
            "category": cat, "title": "X", "script": SCRIPT,
        })
        assert r.status_code in (404, 422), cat
    assert not (Path(os.environ["MS_ANIMATIONS_DIR"]).parent / "evil").exists()


def test_crear_animacion_script_invalido(authed, tmp_path):
    _seed(tmp_path)
    r = authed.post("/api/animations", json={
        "category": "dinamica-orbital", "title": "Rota",
        "script": "def sin_cerrar(:",
    })
    assert r.status_code == 422


def test_crear_animacion_script_sin_escenas(authed, tmp_path):
    _seed(tmp_path)
    r = authed.post("/api/animations", json={
        "category": "dinamica-orbital", "title": "Sin escena",
        "script": "x = 1\n",
    })
    assert r.status_code == 422


def test_crear_animacion_requiere_auth(client, tmp_path):
    _seed(tmp_path)
    r = client.post("/api/animations", json={
        "category": "dinamica-orbital", "title": "X", "script": SCRIPT,
    })
    assert r.status_code == 401
