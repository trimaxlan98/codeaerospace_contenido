"""Pruebas de studio/tools/subir_curso.py: sincronizar un curso versionado
en el repo (curso.json + style_block + clips) con la base del backend.

Sin HTTP: se ejercitan cargar_curso() y sincronizar() directo contra una
Database temporal, que es exactamente lo que hace el CLI.
"""

import json
import sys
from pathlib import Path

import pytest

from app.db import Database
from app.projects import ProjectService, content_hash

TOOLS = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(TOOLS))

import subir_curso  # noqa: E402

STYLE = "from manim import *\n\nC_ACENTO = '#f59e0b'\n"

CLIP_TPL = (
    "class Clip{n}(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle(color=C_ACENTO)))\n"
)


def _curso_dir(tmp_path, titulos=("1 · Intro", "2 · Cierre")):
    """Arma en disco un curso minimo de len(titulos) clips."""
    d = tmp_path / "curso-demo"
    (d / "clips").mkdir(parents=True)
    (d / "style_block.py").write_text(STYLE)
    clips = []
    for i, titulo in enumerate(titulos, start=1):
        nombre = f"clips/{i:02d}-clip.py"
        (d / nombre).write_text(CLIP_TPL.format(n=i))
        clips.append({"file": nombre, "title": titulo,
                      "scene": f"Clip{i}",
                      "final_state": f"estado final {i}"})
    (d / "curso.json").write_text(json.dumps({
        "name": "Curso demo", "description": "d", "quality": "qm",
        "style_block": "style_block.py", "clips": clips,
    }))
    return d


def _service(tmp_path):
    db = Database(tmp_path / "db" / "manimstudio.db")
    return db, ProjectService(db)


def test_carga_y_creacion_completa(tmp_path):
    d = _curso_dir(tmp_path)
    db, service = _service(tmp_path)

    curso = subir_curso.cargar_curso(d)
    reporte = subir_curso.sincronizar(service, db, curso, dry_run=False)

    assert any("proyecto nuevo" in l for l in reporte)
    proyectos = db.list_projects()
    assert len(proyectos) == 1
    p = proyectos[0]
    assert p["name"] == "Curso demo"
    assert p["style_block"] == STYLE

    clips = db.list_clips(p["id"])
    assert [c["title"] for c in clips] == ["1 · Intro", "2 · Cierre"]
    assert [c["scene"] for c in clips] == ["Clip1", "Clip2"]
    assert clips[0]["final_state"] == "estado final 1"
    assert "class Clip1(Scene)" in clips[0]["script"]


def test_resincronizar_es_idempotente_y_detecta_cambios(tmp_path):
    d = _curso_dir(tmp_path)
    db, service = _service(tmp_path)
    subir_curso.sincronizar(service, db, subir_curso.cargar_curso(d), False)

    # Sin cambios: todo "al dia", nada nuevo.
    reporte = subir_curso.sincronizar(service, db,
                                      subir_curso.cargar_curso(d), False)
    assert all(l.startswith(("=",)) for l in reporte), reporte
    assert len(db.list_clips(db.list_projects()[0]["id"])) == 2

    # Cambia el script del clip 2: se actualiza solo ese.
    (d / "clips" / "02-clip.py").write_text(CLIP_TPL.format(n=2).replace(
        "Circle", "Square"))
    reporte = subir_curso.sincronizar(service, db,
                                      subir_curso.cargar_curso(d), False)
    assert any(l.startswith("~ clip 2") for l in reporte)
    clip2 = db.list_clips(db.list_projects()[0]["id"])[1]
    assert "Square" in clip2["script"]


def test_clip_con_render_queda_stale(tmp_path):
    """Si el clip cambiado tenia render vigente, el reporte avisa STALE."""
    d = _curso_dir(tmp_path)
    db, service = _service(tmp_path)
    subir_curso.sincronizar(service, db, subir_curso.cargar_curso(d), False)

    pid = db.list_projects()[0]["id"]
    clip = db.list_clips(pid)[0]
    # Simula un render vigente: hash del contenido actual.
    db.update_clip(clip["id"], job_id="cafe1234cafe1234",
                   rendered_hash=content_hash(STYLE, clip["script"],
                                              clip["scene"]))

    (d / "clips" / "01-clip.py").write_text(CLIP_TPL.format(n=1).replace(
        "Circle", "Dot"))
    reporte = subir_curso.sincronizar(service, db,
                                      subir_curso.cargar_curso(d), False)
    assert any("STALE" in l for l in reporte), reporte


def test_dry_run_no_escribe(tmp_path):
    d = _curso_dir(tmp_path)
    db, service = _service(tmp_path)
    reporte = subir_curso.sincronizar(service, db,
                                      subir_curso.cargar_curso(d), True)
    assert any("proyecto nuevo" in l for l in reporte)
    assert db.list_projects() == []


def test_escena_ausente_aborta(tmp_path):
    d = _curso_dir(tmp_path)
    manifest = json.loads((d / "curso.json").read_text())
    manifest["clips"][0]["scene"] = "NoExiste"
    (d / "curso.json").write_text(json.dumps(manifest))
    with pytest.raises(SystemExit, match="NoExiste"):
        subir_curso.cargar_curso(d)


def test_clips_sobrantes_en_base_no_se_borran(tmp_path):
    d = _curso_dir(tmp_path, titulos=("1 · Intro", "2 · Medio", "3 · Fin"))
    db, service = _service(tmp_path)
    subir_curso.sincronizar(service, db, subir_curso.cargar_curso(d), False)

    # El curso.json se recorta a 2 clips: el tercero sobra pero se conserva.
    manifest = json.loads((d / "curso.json").read_text())
    manifest["clips"] = manifest["clips"][:2]
    (d / "curso.json").write_text(json.dumps(manifest))
    reporte = subir_curso.sincronizar(service, db,
                                      subir_curso.cargar_curso(d), False)
    assert any(l.startswith("!") and "no se borran" in l for l in reporte)
    assert len(db.list_clips(db.list_projects()[0]["id"])) == 3
