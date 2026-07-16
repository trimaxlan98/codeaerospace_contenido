"""Pruebas de persistencia y servicio de Proyectos (cursos) — Sprint 1.

Usa Database directo sobre tmp_path, sin TestClient: este sprint es
backend puro (sin API todavia).
"""

import time

import pytest

from app.db import Database
from app.projects import (
    QUALITY_SPECS,
    ProjectService,
    compose_script,
    content_hash,
    style_offset,
)


@pytest.fixture()
def db(tmp_path):
    database = Database(tmp_path / "t.db")
    yield database
    database.close()


@pytest.fixture()
def svc(db):
    return ProjectService(db)


def test_compose_and_hash():
    # Sin estilo: compose devuelve el script tal cual.
    assert compose_script("", "print(1)") == "print(1)"
    assert compose_script("   \n  ", "print(1)") == "print(1)"

    # Con estilo: contiene el marcador y ambas partes.
    composed = compose_script("COLOR = 'red'", "print(1)")
    assert "COLOR = 'red'" in composed
    assert "# --- fin estilo del proyecto ---" in composed
    assert composed.endswith("print(1)")

    # El hash cambia si cambia el estilo o el script.
    h1 = content_hash("COLOR = 'red'", "print(1)")
    h2 = content_hash("COLOR = 'blue'", "print(1)")
    h3 = content_hash("COLOR = 'red'", "print(2)")
    assert h1 != h2
    assert h1 != h3
    assert h1 == content_hash("COLOR = 'red'", "print(1)")

    # style_offset
    assert style_offset("") == 0
    assert style_offset("   ") == 0
    composed2 = compose_script("a\nb", "X")
    assert composed2.splitlines() == [
        "a", "b", "", "# --- fin estilo del proyecto ---", "", "X",
    ]
    assert style_offset("a\nb") == 5


def test_project_crud(svc):
    p = svc.create_project("Curso 1", "desc", "qm", "")
    assert p["id"]
    assert p["quality"] == "qm"

    fetched = svc.get_project_detail(p["id"])
    assert fetched["name"] == "Curso 1"
    assert fetched["clips"] == []

    updated = svc.update_project(p["id"], name="Curso renombrado")
    assert updated["name"] == "Curso renombrado"

    svc.add_clip(p["id"], "Clip 1")
    svc.delete_project(p["id"])
    assert svc.get_project_detail(p["id"]) is None
    assert svc.db.list_clips(p["id"]) == []


def test_clip_ordering(svc):
    p = svc.create_project("Curso", "", "ql", "")
    c0 = svc.add_clip(p["id"], "A")
    c1 = svc.add_clip(p["id"], "B")
    c2 = svc.add_clip(p["id"], "C")
    assert [c["position"] for c in (c0, c1, c2)] == [0, 1, 2]

    svc.move_clip(p["id"], c2["id"], 0)
    clips = svc.db.list_clips(p["id"])
    assert [c["id"] for c in clips] == [c2["id"], c0["id"], c1["id"]]
    assert [c["position"] for c in clips] == [0, 1, 2]

    svc.delete_clip(p["id"], c0["id"])
    clips = svc.db.list_clips(p["id"])
    assert [c["id"] for c in clips] == [c2["id"], c1["id"]]
    assert [c["position"] for c in clips] == [0, 1]


def test_stale_detection(svc):
    p = svc.create_project("Curso", "", "ql", "")
    clip = svc.add_clip(p["id"], "A", script="print(1)")
    h = content_hash("", "print(1)")
    svc.db.update_clip(clip["id"], job_id="job1", rendered_hash=h)

    detail = svc.get_project_detail(p["id"])
    c = detail["clips"][0]
    assert c["stale"] is False
    assert c["status"] == "rendered"

    svc.update_clip(clip["id"], script="print(2)")
    detail = svc.get_project_detail(p["id"])
    c = detail["clips"][0]
    assert c["stale"] is True
    assert c["status"] == "stale"

    # Revertir el script y en cambio tocar el estilo del proyecto: tambien stale.
    svc.update_clip(clip["id"], script="print(1)")
    svc.update_project(p["id"], style_block="COLOR = 'red'")
    detail = svc.get_project_detail(p["id"])
    c = detail["clips"][0]
    assert c["stale"] is True


def test_handle_job_done(svc):
    p = svc.create_project("Curso", "", "ql", "")
    clip = svc.add_clip(p["id"], "A", script="print(1)")

    job = {"id": "jobA", "clip_id": clip["id"], "project_id": p["id"],
           "content_hash": "deadbeef"}
    svc.handle_job_done(job)
    updated = svc.db.get_clip(clip["id"])
    assert updated["job_id"] == "jobA"
    assert updated["rendered_hash"] == "deadbeef"

    # Clip borrado no explota.
    svc.delete_clip(p["id"], clip["id"])
    svc.handle_job_done({"id": "jobB", "clip_id": clip["id"], "project_id": p["id"],
                          "content_hash": "x"})

    # Clip de otro proyecto no se enlaza.
    p2 = svc.create_project("Curso 2", "", "ql", "")
    clip2 = svc.add_clip(p2["id"], "B", script="print(1)")
    svc.handle_job_done({"id": "jobC", "clip_id": clip2["id"], "project_id": "otro-proyecto",
                          "content_hash": "y"})
    unchanged = svc.db.get_clip(clip2["id"])
    assert unchanged["job_id"] is None


def test_quality_immutable_with_renders(svc):
    p = svc.create_project("Curso", "", "ql", "")
    clip = svc.add_clip(p["id"], "A", script="print(1)")

    # Sin renders: se puede cambiar.
    svc.update_project(p["id"], quality="qm")

    svc.db.update_clip(clip["id"], job_id="job1", rendered_hash="x")
    with pytest.raises(ValueError):
        svc.update_project(p["id"], quality="qh")


def test_adopt_job(svc):
    p = svc.create_project("Curso", "", "ql", "")
    job = {"id": "jobX", "script": "print(1)", "scene": "Demo", "quality": "ql"}
    clip = svc.add_clip(p["id"], "A", adopt_job=job)
    assert clip["job_id"] == "jobX"
    assert clip["script"] == "print(1)"
    assert clip["rendered_hash"] == content_hash("", "print(1)")

    job2 = {"id": "jobY", "script": "print(2)", "scene": "Demo", "quality": "qh"}
    clip2 = svc.add_clip(p["id"], "B", adopt_job=job2)
    assert clip2["job_id"] is None
    assert clip2["script"] == "print(2)"


def test_manifest(svc):
    p = svc.create_project("Curso", "", "ql", "")
    c0 = svc.add_clip(p["id"], "Intro genial", script="print(1)")
    c1 = svc.add_clip(p["id"], "Sin render", script="print(2)")
    c2 = svc.add_clip(p["id"], "Cierre", script="print(3)")

    h0 = content_hash("", "print(1)")
    h2 = content_hash("", "print(3)")
    svc.db.update_clip(c0["id"], job_id="job0", rendered_hash=h0)
    svc.db.update_clip(c2["id"], job_id="job2", rendered_hash=h2)

    jobs_by_id = {
        "job0": {"id": "job0", "video_path": "/x/0.mp4", "size_bytes": 100},
        "job2": {"id": "job2", "video_path": "/x/2.mp4", "size_bytes": 200},
    }
    manifest = svc.export_manifest(p["id"], jobs_by_id)

    assert manifest["quality"] == "ql"
    assert manifest["resolution"] == QUALITY_SPECS["ql"]["resolution"]
    assert manifest["fps"] == QUALITY_SPECS["ql"]["fps"]

    ids_in_manifest = [item["clip_id"] for item in manifest["clips"]]
    assert c1["id"] not in ids_in_manifest
    assert ids_in_manifest == [c0["id"], c2["id"]]

    filenames = [item["filename"] for item in manifest["clips"]]
    assert filenames == ["001-intro-genial.mp4", "003-cierre.mp4"]
