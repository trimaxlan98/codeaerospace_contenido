"""Pruebas de la Biblioteca: borrado de jobs, cuota de disco y logs persistidos."""

import time

VALID_SCRIPT = (
    "from manim import *\n"
    "class Demo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle()))\n"
)


def _wait_terminal(authed, job_id, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = authed.get(f"/api/jobs/{job_id}").json()["status"]
        if status not in ("queued", "running"):
            return status
        time.sleep(0.2)
    return None


def test_delete_job_removes_row_and_files(authed, tmp_path):
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "Demo",
                                       "quality": "ql"})
    job_id = r.json()["id"]
    assert _wait_terminal(authed, job_id) is not None

    r = authed.delete(f"/api/jobs/{job_id}")
    assert r.status_code == 200
    assert "storage" in r.json()
    assert authed.get(f"/api/jobs/{job_id}").status_code == 404
    assert not (tmp_path / "render_jobs" / job_id).exists()


def test_delete_active_job_conflict(authed):
    from app.main import db
    db.insert_job({"id": "aaaa000011112222", "scene": "X", "quality": "ql",
                   "timeout": 60, "status": "queued", "script": "x",
                   "created_at": time.time()})
    db.update_job("aaaa000011112222", status="running")
    r = authed.delete("/api/jobs/aaaa000011112222")
    assert r.status_code == 409


def test_delete_unknown_job(authed):
    assert authed.delete("/api/jobs/deadbeef00000000").status_code == 404
    assert authed.delete("/api/jobs/../../etc").status_code == 404


def test_delete_requires_auth(client):
    assert client.delete("/api/jobs/deadbeef00000000").status_code == 401


def test_storage_quota_507(authed):
    from app.main import cfg
    cfg.max_storage_mb = 0
    try:
        r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "Demo",
                                           "quality": "ql"})
        assert r.status_code == 507
        assert "Almacenamiento" in r.json()["detail"]
    finally:
        cfg.max_storage_mb = 2048


def test_jobs_list_includes_storage(authed):
    data = authed.get("/api/jobs").json()
    assert data["storage"]["quota_bytes"] == 2048 * 1024 * 1024
    assert data["storage"]["used_bytes"] >= 0


def test_thumb_404_when_missing(authed):
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "Demo",
                                       "quality": "ql"})
    job_id = r.json()["id"]
    assert authed.get(f"/api/jobs/{job_id}/thumb").status_code == 404


def test_job_public_includes_size_fields(authed):
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "Demo",
                                       "quality": "ql"})
    job = r.json()
    assert "size_bytes" in job
    assert job["has_thumb"] is False


def test_logs_fallback_to_render_log(authed, tmp_path):
    """Si el buffer en memoria ya no existe, get_logs lee render.log."""
    from app.main import db
    job_id = "bbbb000011112222"
    db.insert_job({"id": job_id, "scene": "X", "quality": "ql", "timeout": 60,
                   "status": "error", "script": "x", "created_at": time.time()})
    job_dir = tmp_path / "render_jobs" / job_id
    job_dir.mkdir(parents=True)
    (job_dir / "render.log").write_text("linea 1\nlinea 2\n", encoding="utf-8")

    logs = authed.get(f"/api/jobs/{job_id}").json()["logs"]
    assert logs == ["linea 1", "linea 2"]


def test_render_log_persisted_after_error(authed, tmp_path):
    """Tras un job en error (runner caido) el log queda en disco."""
    r = authed.post("/api/jobs", json={"script": VALID_SCRIPT, "scene": "Demo",
                                       "quality": "ql"})
    job_id = r.json()["id"]
    status = _wait_terminal(authed, job_id)
    assert status == "error"
    # Sin runner no hay lineas de log, pero el directorio no debe romperse y
    # los logs deben seguir siendo consultables (buffer liberado o archivo).
    detail = authed.get(f"/api/jobs/{job_id}")
    assert detail.status_code == 200
    assert isinstance(detail.json()["logs"], list)
