"""Pruebas de exportacion de proyectos (Sprint 3): manifest + archive zip.

Sin runner real: los "renders" se simulan escribiendo un mp4 falso dentro
del directorio del job y actualizando la fila en la Database directo
(mismo patron que test_purge_protects_clip_renders en test_projects_api.py).
"""

import io
import tempfile
import time
import zipfile
from pathlib import Path

from app.projects import content_hash

from .conftest import TEST_PASSWORD

VALID_SCRIPT = (
    "from manim import *\n"
    "class Demo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle()))\n"
)


def _create_project(authed, **overrides):
    body = {"name": "Curso Export", "description": "d", "quality": "ql",
            "style_block": ""}
    body.update(overrides)
    r = authed.post("/api/projects", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def _make_rendered_clip(authed, db, cfg, pid, title, job_id, size_bytes=1234):
    """Crea un clip con render 'done' vigente, con mp4 falso en su job dir."""
    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": title, "script": VALID_SCRIPT,
                             "scene": "Demo"}).json()

    job_dir = cfg.render_jobs_dir / job_id / "media" / "videos" / "x" / "y"
    job_dir.mkdir(parents=True, exist_ok=True)
    video_path = job_dir / "Demo.mp4"
    video_path.write_bytes(b"fake-mp4-data")

    started = time.time() - 5
    finished = time.time()
    db.insert_job({"id": job_id, "scene": "Demo", "quality": "ql", "timeout": 120,
                  "status": "queued", "script": VALID_SCRIPT, "created_at": started,
                  "project_id": pid, "clip_id": clip["id"], "content_hash": None})
    db.update_job(job_id, status="done", started_at=started, finished_at=finished,
                  video_path=str(video_path), size_bytes=size_bytes)

    project = db.get_project(pid)
    chash = content_hash(project["style_block"], VALID_SCRIPT, "Demo")
    db.update_clip(clip["id"], job_id=job_id, rendered_hash=chash)
    return clip


def test_manifest_endpoint(authed):
    from app.main import cfg, db

    project = _create_project(authed)
    pid = project["id"]

    _make_rendered_clip(authed, db, cfg, pid, "Intro", "cafe00001111beef")
    authed.post(f"/api/projects/{pid}/clips",
               json={"title": "Sin render", "script": VALID_SCRIPT})

    r = authed.get(f"/api/projects/{pid}/export")
    assert r.status_code == 200
    manifest = r.json()

    assert manifest["project"]["id"] == pid
    assert manifest["project"]["name"] == project["name"]
    assert manifest["project"]["quality"] == "ql"
    assert manifest["specs"]["resolution"] == "854x480"
    assert manifest["specs"]["fps"] == 15
    assert "generated_at" in manifest

    by_title = {c["title"]: c for c in manifest["clips"]}
    assert by_title["Intro"]["has_video"] is True
    assert by_title["Intro"]["filename"] == "001-intro.mp4"
    assert by_title["Intro"]["stale"] is False
    assert by_title["Intro"]["size_bytes"] == 1234
    assert by_title["Intro"]["duration_s"] > 0

    assert by_title["Sin render"]["has_video"] is False
    assert by_title["Sin render"]["stale"] is False
    assert by_title["Sin render"]["duration_s"] is None

    # concat solo trae el clip realmente renderizado
    assert manifest["concat"] == ["file '001-intro.mp4'"]


def test_archive_zip(authed):
    from app.main import cfg, db

    project = _create_project(authed)
    pid = project["id"]
    _make_rendered_clip(authed, db, cfg, pid, "Intro", "cafe00002222beef")
    authed.post(f"/api/projects/{pid}/clips",
               json={"title": "Sin render", "script": VALID_SCRIPT})

    r = authed.get(f"/api/projects/{pid}/archive")
    assert r.status_code == 200
    assert "zip" in r.headers["content-type"]

    zf = zipfile.ZipFile(io.BytesIO(r.content))
    names = set(zf.namelist())
    assert "001-intro.mp4" in names
    assert "concat.txt" in names
    assert "manifest.json" in names
    assert "LEEME.txt" in names
    # el clip sin render no genera entrada de video en el zip
    assert not any(n.endswith("sin-render.mp4") for n in names)

    concat_content = zf.read("concat.txt").decode("utf-8")
    assert concat_content.strip() == "file '001-intro.mp4'"

    leeme = zf.read("LEEME.txt").decode("utf-8")
    assert "ffmpeg -f concat -safe 0 -i concat.txt -c copy curso.mp4" in leeme


def test_archive_empty_404(authed):
    project = _create_project(authed)
    pid = project["id"]
    authed.post(f"/api/projects/{pid}/clips",
               json={"title": "Sin render", "script": VALID_SCRIPT})

    r = authed.get(f"/api/projects/{pid}/archive")
    assert r.status_code == 404
    assert "detail" in r.json()


def test_archive_zip_build_failure_cleans_tempfile(client, monkeypatch):
    """Si zipfile.ZipFile.write revienta a mitad (disco lleno, mp4 ilegible...),
    el endpoint debe devolver 500 SIN dejar el tempfile del zip huerfano en
    el directorio temporal (regresion del fix post-review: antes el
    BackgroundTask que borra el tmp solo se agendaba si el FileResponse
    llegaba a construirse).
    """
    from app.main import app as fastapi_app, cfg, db
    from fastapi.testclient import TestClient

    import app.projects_api as projects_api

    # TestClient por defecto re-lanza las excepciones del servidor en vez de
    # devolver el 500 como respuesta; aqui queremos inspeccionar la respuesta.
    lenient = TestClient(fastapi_app, raise_server_exceptions=False)
    r = lenient.post("/api/login", json={"username": "tester", "password": TEST_PASSWORD})
    assert r.status_code == 200

    project = _create_project(lenient)
    pid = project["id"]
    _make_rendered_clip(lenient, db, cfg, pid, "Intro", "cafe00003333beef")

    def _boom_write(self, *args, **kwargs):
        raise OSError("disco lleno (simulado)")

    monkeypatch.setattr(projects_api.zipfile.ZipFile, "write", _boom_write)

    tmp_dir = Path(tempfile.gettempdir())
    before = {p.name for p in tmp_dir.iterdir() if p.name.endswith(".zip")}

    r = lenient.get(f"/api/projects/{pid}/archive")

    after = {p.name for p in tmp_dir.iterdir() if p.name.endswith(".zip")}

    assert r.status_code == 500
    assert after - before == set(), (
        f"quedaron tempfiles .zip huerfanos: {after - before}")
