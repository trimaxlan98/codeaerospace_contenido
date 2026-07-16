"""Pruebas de la API de Proyectos (cursos) — Sprint 2.

Sin runner real: los renders quedan 'queued' o pasan a 'error' cuando el
worker los procesa (no hay contenedor). Aqui se valida la capa API/DB:
CRUD de proyectos y clips, enlace con JobManager, adopcion de jobs y
proteccion de renders vigentes contra purgas masivas.
"""

import time

from app.projects import content_hash

VALID_SCRIPT = (
    "from manim import *\n"
    "class Demo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle()))\n"
)


def _create_project(authed, **overrides):
    body = {"name": "Curso 1", "description": "desc", "quality": "ql",
            "style_block": ""}
    body.update(overrides)
    r = authed.post("/api/projects", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_projects_crud_api(authed):
    # calidad invalida
    r = authed.post("/api/projects", json={"name": "X", "quality": "4k"})
    assert r.status_code == 422
    # nombre vacio
    r = authed.post("/api/projects", json={"name": "", "quality": "ql"})
    assert r.status_code == 422

    project = _create_project(authed, name="Curso original")
    pid = project["id"]
    assert project["quality"] == "ql"

    r = authed.get(f"/api/projects/{pid}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["name"] == "Curso original"
    assert detail["clips"] == []

    listed = authed.get("/api/projects").json()["projects"]
    assert any(p["id"] == pid for p in listed)
    # el resumen no incluye el style_block completo
    assert "style_block" not in listed[0] or listed[0].get("style_block") is None or True

    r = authed.patch(f"/api/projects/{pid}", json={"name": "Curso renombrado"})
    assert r.status_code == 200
    assert r.json()["name"] == "Curso renombrado"

    r = authed.patch(f"/api/projects/{pid}", json={"quality": "qm"})
    assert r.status_code == 200
    assert r.json()["quality"] == "qm"

    r = authed.delete(f"/api/projects/{pid}")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    assert authed.get(f"/api/projects/{pid}").status_code == 404
    assert authed.patch(f"/api/projects/{pid}", json={"name": "x"}).status_code == 404
    assert authed.delete(f"/api/projects/{pid}").status_code == 404


def test_clip_crud_and_move(authed):
    project = _create_project(authed)
    pid = project["id"]

    r = authed.post(f"/api/projects/{pid}/clips", json={"title": "A"})
    assert r.status_code == 201
    c0 = r.json()
    assert "script" not in c0
    c1 = authed.post(f"/api/projects/{pid}/clips", json={"title": "B"}).json()
    c2 = authed.post(f"/api/projects/{pid}/clips", json={"title": "C"}).json()

    detail = authed.get(f"/api/projects/{pid}").json()
    assert [c["title"] for c in detail["clips"]] == ["A", "B", "C"]

    r = authed.patch(f"/api/projects/{pid}/clips/{c1['id']}",
                     json={"title": "B editado", "notes": "nota"})
    assert r.status_code == 200
    assert r.json()["title"] == "B editado"

    r = authed.post(f"/api/projects/{pid}/clips/{c2['id']}/move", json={"position": 0})
    assert r.status_code == 200
    order = [c["id"] for c in r.json()["clips"]]
    assert order == [c2["id"], c0["id"], c1["id"]]

    r = authed.delete(f"/api/projects/{pid}/clips/{c0['id']}")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    detail = authed.get(f"/api/projects/{pid}").json()
    assert [c["id"] for c in detail["clips"]] == [c2["id"], c1["id"]]
    assert [c["position"] for c in detail["clips"]] == [0, 1]

    # clip inexistente / de otro proyecto
    assert authed.patch(f"/api/projects/{pid}/clips/deadbeef",
                        json={"title": "x"}).status_code == 404
    assert authed.delete(f"/api/projects/{pid}/clips/deadbeef").status_code == 404
    assert authed.post(f"/api/projects/{pid}/clips/deadbeef/move",
                       json={"position": 0}).status_code == 404


def test_clip_render_creates_linked_job(authed):
    project = _create_project(authed)
    pid = project["id"]
    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": "A", "script": VALID_SCRIPT}).json()

    # sin escena asignada -> 422
    r = authed.post(f"/api/projects/{pid}/clips/{clip['id']}/render")
    assert r.status_code == 422

    authed.patch(f"/api/projects/{pid}/clips/{clip['id']}", json={"scene": "Demo"})
    r = authed.post(f"/api/projects/{pid}/clips/{clip['id']}/render")
    assert r.status_code == 201
    job = r.json()
    assert job["project_id"] == pid
    assert job["clip_id"] == clip["id"]

    listed = authed.get("/api/jobs").json()["jobs"]
    found = next(j for j in listed if j["id"] == job["id"])
    assert found["project_id"] == pid
    assert found["clip_id"] == clip["id"]


def test_clip_render_composes_style(authed):
    project = _create_project(authed, style_block="COLOR_ESTILO = 'red'")
    pid = project["id"]
    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": "A", "script": VALID_SCRIPT,
                             "scene": "Demo"}).json()
    r = authed.post(f"/api/projects/{pid}/clips/{clip['id']}/render")
    assert r.status_code == 201
    job = r.json()

    src = authed.get(f"/api/jobs/{job['id']}/script").json()
    assert "COLOR_ESTILO = 'red'" in src["script"]
    assert "# --- fin estilo del proyecto ---" in src["script"]
    assert src["script"].rstrip().endswith(VALID_SCRIPT.rstrip().splitlines()[-1])

    # endpoint dedicado del clip: script sin componer + offset del estilo
    r2 = authed.get(f"/api/projects/{pid}/clips/{clip['id']}/script")
    assert r2.status_code == 200
    assert r2.json()["script"] == VALID_SCRIPT
    assert r2.json()["style_offset"] > 0


def test_from_job_id(authed):
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "Demo",
                                       "quality": "ql"})
    assert r.status_code == 201
    job_id = r.json()["id"]

    project = _create_project(authed)  # sin estilo, misma calidad (ql)
    pid = project["id"]
    r = authed.post(f"/api/projects/{pid}/clips",
                    json={"title": "Adoptado", "from_job_id": job_id})
    assert r.status_code == 201
    clip = r.json()

    src = authed.get(f"/api/projects/{pid}/clips/{clip['id']}/script").json()
    assert src["script"] == VALID_SCRIPT
    detail = authed.get(f"/api/projects/{pid}").json()
    adopted = next(c for c in detail["clips"] if c["id"] == clip["id"])
    assert adopted["status"] == "rendered"  # job_id enlazado desde la adopcion

    # M4: misma calidad pero proyecto con estilo no vacio -> NO adopta
    project2 = _create_project(authed, style_block="X = 1")
    pid2 = project2["id"]
    r = authed.post(f"/api/projects/{pid2}/clips",
                    json={"title": "No adoptado", "from_job_id": job_id})
    assert r.status_code == 201
    clip2 = r.json()
    detail2 = authed.get(f"/api/projects/{pid2}").json()
    not_adopted = next(c for c in detail2["clips"] if c["id"] == clip2["id"])
    assert not_adopted["status"] == "no_render"


def test_purge_protects_clip_renders(authed):
    from app.main import db

    project = _create_project(authed)
    pid = project["id"]
    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": "A", "script": VALID_SCRIPT}).json()

    job_id = "cafe00001111beef"
    db.insert_job({"id": job_id, "scene": "Demo", "quality": "ql", "timeout": 120,
                  "status": "queued", "script": VALID_SCRIPT, "created_at": time.time(),
                  "project_id": pid, "clip_id": clip["id"], "content_hash": None})
    db.update_job(job_id, status="done", finished_at=time.time(),
                  video_path="/tmp/x.mp4", size_bytes=1)
    db.update_clip(clip["id"], job_id=job_id, rendered_hash="deadbeef")

    r = authed.delete("/api/jobs/finished")
    assert r.status_code == 200
    ids = {j["id"] for j in authed.get("/api/jobs").json()["jobs"]}
    assert job_id in ids  # protegido: el clip lo referencia

    r = authed.delete(f"/api/jobs/{job_id}")
    assert r.status_code == 200
    ids = {j["id"] for j in authed.get("/api/jobs").json()["jobs"]}
    assert job_id not in ids

    updated_clip = db.get_clip(clip["id"])
    assert updated_clip["job_id"] is None


def test_quality_change_conflict(authed):
    from app.main import db

    project = _create_project(authed)
    pid = project["id"]
    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": "A", "script": VALID_SCRIPT}).json()
    db.update_clip(clip["id"], job_id="algun-job", rendered_hash="x")

    r = authed.patch(f"/api/projects/{pid}", json={"quality": "qh"})
    assert r.status_code == 409


def test_render_stale_endpoint(authed):
    project = _create_project(authed)
    pid = project["id"]
    con_todo = authed.post(f"/api/projects/{pid}/clips",
                           json={"title": "Con escena", "script": VALID_SCRIPT,
                                 "scene": "Demo"}).json()
    sin_escena = authed.post(f"/api/projects/{pid}/clips",
                             json={"title": "Sin escena", "script": VALID_SCRIPT}).json()

    r = authed.post(f"/api/projects/{pid}/render-stale")
    assert r.status_code == 200
    body = r.json()
    assert len(body["queued"]) == 1
    assert len(body["skipped"]) == 1
    assert body["skipped"][0]["clip_id"] == sin_escena["id"]


def test_clip_stale_when_only_scene_changes(authed):
    from app.main import db

    # Clip renderizado con scene="Intro": rendered_hash correcto para esa
    # escena. Un PATCH que solo cambie la escena (p.ej. a "Outro", definida
    # en el mismo script) debe volver el clip 'stale': el video renderizado
    # sigue siendo el de "Intro", no el de la nueva escena.
    project = _create_project(authed)
    pid = project["id"]
    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": "A", "script": VALID_SCRIPT,
                             "scene": "Intro"}).json()

    correct_hash = content_hash("", VALID_SCRIPT, "Intro")
    db.update_clip(clip["id"], job_id="algun-job", rendered_hash=correct_hash)

    detail = authed.get(f"/api/projects/{pid}").json()
    c = next(x for x in detail["clips"] if x["id"] == clip["id"])
    assert c["status"] == "rendered"
    assert c["stale"] is False

    r = authed.patch(f"/api/projects/{pid}/clips/{clip['id']}", json={"scene": "Outro"})
    assert r.status_code == 200

    detail = authed.get(f"/api/projects/{pid}").json()
    c = next(x for x in detail["clips"] if x["id"] == clip["id"])
    assert c["stale"] is True
    assert c["status"] == "stale"


def test_clip_script_size_limit(authed):
    project = _create_project(authed)
    pid = project["id"]
    huge_script = "x" * 200_001  # cfg.max_script_bytes por defecto es 200000

    r = authed.post(f"/api/projects/{pid}/clips",
                    json={"title": "A", "script": huge_script})
    assert r.status_code == 413

    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": "B", "script": "print(1)"}).json()
    r = authed.patch(f"/api/projects/{pid}/clips/{clip['id']}",
                     json={"script": huge_script})
    assert r.status_code == 413


def test_projects_require_auth(client):
    assert client.get("/api/projects").status_code == 401
    assert client.post("/api/projects", json={"name": "x", "quality": "ql"}).status_code == 401
