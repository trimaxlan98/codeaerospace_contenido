"""Tests de la biblioteca de lecciones (indice, detalle, seguridad, cache)."""

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

La primera ley dice que $r = \\frac{p}{1 + e\\cos\\theta}$.
"""

CATS = """- slug: dinamica-orbital
  name: Dinámica Orbital
- slug: satelites
  name: Satélites
"""


def _seed(tmp: Path) -> None:
    root = Path(os.environ["MS_LESSONS_DIR"])
    (root / "dinamica-orbital").mkdir(parents=True, exist_ok=True)
    (root / "categories.yaml").write_text(CATS, encoding="utf-8")
    (root / "dinamica-orbital" / "01-orbitas-kepler.md").write_text(
        LESSON, encoding="utf-8")


def test_indice_lista_categorias_y_metadatos(authed, tmp_path):
    _seed(tmp_path)
    r = authed.get("/api/lessons")
    assert r.status_code == 200
    cats = r.json()["categories"]
    assert [c["slug"] for c in cats] == ["dinamica-orbital", "satelites"]
    dyn = cats[0]
    assert dyn["name"] == "Dinámica Orbital"
    assert dyn["count"] == 1
    lesson = dyn["lessons"][0]
    assert lesson["id"] == "dinamica-orbital/01-orbitas-kepler"
    assert lesson["title"] == "Órbitas de Kepler"
    assert lesson["minutes"] == 12
    assert "markdown" not in lesson  # el indice no incluye el cuerpo


def test_detalle_devuelve_markdown(authed, tmp_path):
    _seed(tmp_path)
    r = authed.get("/api/lessons/dinamica-orbital/01-orbitas-kepler")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Órbitas de Kepler"
    assert "# Órbitas de Kepler" in body["markdown"]
    assert "---" not in body["markdown"].split("\n")[0]  # sin frontmatter


def test_detalle_404_y_path_traversal(authed, tmp_path):
    _seed(tmp_path)
    assert authed.get("/api/lessons/dinamica-orbital/99-no-existe").status_code == 404
    assert authed.get("/api/lessons/../../etc/passwd").status_code == 404
    assert authed.get("/api/lessons/dinamica-orbital/..%2F..%2Fsecreto").status_code == 404


def test_lecciones_requieren_auth(client, tmp_path):
    _seed(tmp_path)
    assert client.get("/api/lessons").status_code == 401
    assert client.get(
        "/api/lessons/dinamica-orbital/01-orbitas-kepler").status_code == 401


def test_indice_se_actualiza_al_cambiar_archivos(authed, tmp_path):
    _seed(tmp_path)
    assert authed.get("/api/lessons").json()["categories"][1]["count"] == 0
    root = Path(os.environ["MS_LESSONS_DIR"])
    (root / "satelites").mkdir(exist_ok=True)
    nueva = LESSON.replace("Órbitas de Kepler", "Anatomía de un satélite")
    time.sleep(0.02)  # asegura mtime distinto
    (root / "satelites" / "01-anatomia.md").write_text(nueva, encoding="utf-8")
    assert authed.get("/api/lessons").json()["categories"][1]["count"] == 1


def test_frontmatter_corrupto_no_tumba_el_indice(authed, tmp_path):
    """YAML corrupto en una leccion no debe tumbar el indice completo."""
    root = Path(os.environ["MS_LESSONS_DIR"])
    (root / "dinamica-orbital").mkdir(parents=True, exist_ok=True)
    (root / "categories.yaml").write_text(CATS, encoding="utf-8")

    # Leccion valida
    (root / "dinamica-orbital" / "01-orbitas-kepler.md").write_text(
        LESSON, encoding="utf-8")
    # Leccion con frontmatter YAML corrupto (list sin cierre)
    corrupt = "---\ntitle: [unclosed\n---\n\n# Contenido\n"
    (root / "dinamica-orbital" / "02-corrupt.md").write_text(
        corrupt, encoding="utf-8")

    # GET /api/lessons debe devolver 200 e incluir ambas
    r = authed.get("/api/lessons")
    assert r.status_code == 200
    cats = r.json()["categories"]
    assert len(cats) == 2
    dyn = cats[0]
    assert dyn["count"] == 2
    ids = {l["id"] for l in dyn["lessons"]}
    assert "dinamica-orbital/01-orbitas-kepler" in ids
    assert "dinamica-orbital/02-corrupt" in ids

    # Leccion corrupta debe tener title con su id (default)
    corrupt_lesson = [l for l in dyn["lessons"]
                      if l["id"] == "dinamica-orbital/02-corrupt"][0]
    assert corrupt_lesson["title"] == "dinamica-orbital/02-corrupt"

    # GET /api/lessons/<corrupta> debe devolver 200 con markdown
    r = authed.get("/api/lessons/dinamica-orbital/02-corrupt")
    assert r.status_code == 200
    assert "# Contenido" in r.json()["markdown"]


def test_borrar_leccion_actualiza_indice(authed, tmp_path):
    """Borrar archivo .md debe actualizar el indice."""
    _seed(tmp_path)

    # Verificar que hay 1 leccion
    r = authed.get("/api/lessons")
    assert r.status_code == 200
    assert r.json()["categories"][0]["count"] == 1

    # Borrar el archivo
    root = Path(os.environ["MS_LESSONS_DIR"])
    md_path = root / "dinamica-orbital" / "01-orbitas-kepler.md"
    time.sleep(0.02)  # asegura mtime distinto
    md_path.unlink()

    # Verificar que el indice se actualizo
    r = authed.get("/api/lessons")
    assert r.status_code == 200
    assert r.json()["categories"][0]["count"] == 0
