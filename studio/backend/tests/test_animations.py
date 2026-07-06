"""Tests de la biblioteca de animaciones (indice, detalle, seguridad, cache)."""

import os
import time
from pathlib import Path

LESSON = """---
title: Órbitas de Kepler
level: intro
summary: Las tres leyes que gobiernan el movimiento orbital.
tags: [kepler, orbitas]
minutes: 12
order: 1
---

# Órbitas de Kepler
"""

SCRIPT = """from manim import *


class OrbitasKepler(Scene):
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
    (lessons_root / "dinamica-orbital").mkdir(parents=True, exist_ok=True)
    (lessons_root / "categories.yaml").write_text(CATS, encoding="utf-8")
    (lessons_root / "dinamica-orbital" / "01-orbitas-kepler.md").write_text(
        LESSON, encoding="utf-8")
    (anim_root / "dinamica-orbital").mkdir(parents=True, exist_ok=True)
    (anim_root / "dinamica-orbital" / "01-orbitas-kepler.py").write_text(
        SCRIPT, encoding="utf-8")


def test_indice_lista_categorias_y_metadatos(authed, tmp_path):
    _seed(tmp_path)
    r = authed.get("/api/animations")
    assert r.status_code == 200
    cats = r.json()["categories"]
    assert [c["slug"] for c in cats] == ["dinamica-orbital", "satelites"]
    dyn = cats[0]
    assert dyn["count"] == 1
    animation = dyn["animations"][0]
    assert animation["id"] == "dinamica-orbital/01-orbitas-kepler"
    # el titulo y el orden se toman de la leccion homonima
    assert animation["title"] == "Órbitas de Kepler"
    assert animation["order"] == 1
    assert animation["scene"] == "OrbitasKepler"
    assert "script" not in animation  # el indice no incluye el codigo


def test_detalle_devuelve_script_y_escena(authed, tmp_path):
    _seed(tmp_path)
    r = authed.get("/api/animations/dinamica-orbital/01-orbitas-kepler")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Órbitas de Kepler"
    assert body["scene"] == "OrbitasKepler"
    assert "class OrbitasKepler(Scene)" in body["script"]


def test_titulo_por_defecto_sin_leccion_homonima(authed, tmp_path):
    """Sin leccion .md correspondiente, el titulo se deriva del slug."""
    anim_root = Path(os.environ["MS_ANIMATIONS_DIR"])
    lessons_root = Path(os.environ["MS_LESSONS_DIR"])
    (lessons_root / "satelites").mkdir(parents=True, exist_ok=True)
    (lessons_root / "categories.yaml").write_text(CATS, encoding="utf-8")
    (anim_root / "satelites").mkdir(parents=True, exist_ok=True)
    (anim_root / "satelites" / "02-cubesats.py").write_text(SCRIPT, encoding="utf-8")

    r = authed.get("/api/animations")
    animation = r.json()["categories"][1]["animations"][0]
    assert animation["title"] == "Cubesats"
    assert animation["order"] == 99


def test_detalle_404_y_path_traversal(authed, tmp_path):
    _seed(tmp_path)
    assert authed.get("/api/animations/dinamica-orbital/99-no-existe").status_code == 404
    assert authed.get("/api/animations/../../etc/passwd").status_code == 404
    assert authed.get(
        "/api/animations/dinamica-orbital/..%2F..%2Fsecreto").status_code == 404


def test_animaciones_requieren_auth(client, tmp_path):
    _seed(tmp_path)
    assert client.get("/api/animations").status_code == 401
    assert client.get(
        "/api/animations/dinamica-orbital/01-orbitas-kepler").status_code == 401


def test_indice_se_actualiza_al_cambiar_archivos(authed, tmp_path):
    _seed(tmp_path)
    assert authed.get("/api/animations").json()["categories"][1]["count"] == 0
    anim_root = Path(os.environ["MS_ANIMATIONS_DIR"])
    (anim_root / "satelites").mkdir(exist_ok=True)
    time.sleep(0.02)  # asegura mtime distinto
    (anim_root / "satelites" / "01-anatomia.py").write_text(SCRIPT, encoding="utf-8")
    assert authed.get("/api/animations").json()["categories"][1]["count"] == 1


def test_script_sin_escena_valida(authed, tmp_path):
    """Un .py sin ninguna Scene no debe romper el indice: scene queda None."""
    lessons_root = Path(os.environ["MS_LESSONS_DIR"])
    anim_root = Path(os.environ["MS_ANIMATIONS_DIR"])
    (lessons_root / "dinamica-orbital").mkdir(parents=True, exist_ok=True)
    (lessons_root / "categories.yaml").write_text(CATS, encoding="utf-8")
    (anim_root / "dinamica-orbital").mkdir(parents=True, exist_ok=True)
    (anim_root / "dinamica-orbital" / "01-sin-escena.py").write_text(
        "x = 1\n", encoding="utf-8")

    r = authed.get("/api/animations")
    animation = r.json()["categories"][0]["animations"][0]
    assert animation["scene"] is None
