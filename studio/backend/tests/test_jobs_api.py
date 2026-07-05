"""Pruebas de la API de jobs: validacion, encolado y ciclo de vida.

El runner real no corre en tests; los jobs quedan 'queued' o fallan con
'runner no disponible' — aqui validamos la capa API/cola, no Docker.
"""

import time

VALID_SCRIPT = (
    "from manim import *\n"
    "class Demo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle()))\n"
)


def test_scenes_endpoint(authed):
    r = authed.post("/api/scenes", json={"script": VALID_SCRIPT})
    assert r.status_code == 200
    assert r.json() == {"scenes": ["Demo"]}


def test_create_job_validations(authed):
    # calidad invalida
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "Demo",
                                       "quality": "4k"})
    assert r.status_code == 422
    # escena inexistente
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "NoExiste",
                                       "quality": "ql"})
    assert r.status_code == 422
    # nombre de escena malicioso (inyeccion de argumentos) rechazado por pydantic
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT,
                                       "scene": "Demo; rm -rf /", "quality": "ql"})
    assert r.status_code == 422
    # timeout fuera de rango
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "Demo",
                                       "quality": "ql", "timeout": 99999})
    assert r.status_code == 422
    # script vacio
    r = authed.post("/api/jobs", json={"script": "  ", "scene": "Demo",
                                       "quality": "ql"})
    assert r.status_code == 422


def test_script_too_large(authed):
    big = VALID_SCRIPT + "#" + "x" * 300_000
    r = authed.post("/api/jobs", json={"script": big, "scene": "Demo", "quality": "ql"})
    assert r.status_code == 413


def test_create_job_writes_script_and_lists(authed, tmp_path):
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "Demo",
                                       "quality": "ql", "timeout": 120})
    assert r.status_code == 201
    job = r.json()
    assert job["status"] in ("queued", "running", "error")
    # el script quedo escrito en la ruta canonica del workspace
    script_file = tmp_path / "render_jobs" / job["id"] / "scene.py"
    assert script_file.read_text() == VALID_SCRIPT

    listed = authed.get("/api/jobs").json()["jobs"]
    assert any(j["id"] == job["id"] for j in listed)

    detail = authed.get(f"/api/jobs/{job['id']}").json()
    assert detail["scene"] == "Demo"
    assert "logs" in detail

    src = authed.get(f"/api/jobs/{job['id']}/script").json()
    assert src["script"] == VALID_SCRIPT


def test_job_runs_and_fails_without_runner(authed):
    """Sin runner, el worker debe marcar error limpio (no colgarse)."""
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "Demo",
                                       "quality": "ql", "timeout": 60})
    job_id = r.json()["id"]
    deadline = time.time() + 10
    status = None
    while time.time() < deadline:
        status = authed.get(f"/api/jobs/{job_id}").json()["status"]
        if status not in ("queued", "running"):
            break
        time.sleep(0.2)
    assert status == "error"
    detail = authed.get(f"/api/jobs/{job_id}").json()
    assert "runner" in (detail["error"] or "")


def test_video_404_before_done(authed):
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "Demo",
                                       "quality": "ql"})
    job_id = r.json()["id"]
    assert authed.get(f"/api/jobs/{job_id}/video").status_code == 404


def test_unknown_job_404(authed):
    assert authed.get("/api/jobs/deadbeef00000000").status_code == 404
    assert authed.get("/api/jobs/../../etc/passwd").status_code == 404


def test_storage_usage_cached_until_invalidated(client):
    from app.main import manager
    root = manager.cfg.render_jobs_dir
    root.mkdir(parents=True, exist_ok=True)

    (root / "a.bin").write_bytes(b"x" * 100)
    assert manager.storage_usage() == 100          # primera lectura: calcula

    (root / "b.bin").write_bytes(b"y" * 50)
    assert manager.storage_usage() == 100          # dentro del TTL: cacheado

    manager._invalidate_storage()
    assert manager.storage_usage() == 150          # invalidado: recalcula

    (root / "c.bin").write_bytes(b"z" * 10)
    manager._storage_cache_at = 0.0                # simula TTL expirado
    assert manager.storage_usage() == 160          # recalcula por TTL
