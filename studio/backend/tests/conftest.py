import os
import sys
from pathlib import Path

import bcrypt
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

TEST_PASSWORD = "test-password-123"


def _set_env(tmp_path: Path) -> None:
    os.environ["MS_ADMIN_USER"] = "tester"
    os.environ["MS_ADMIN_PASSWORD_HASH"] = bcrypt.hashpw(
        TEST_PASSWORD.encode(), bcrypt.gensalt(rounds=4)
    ).decode()
    os.environ["MS_SECRET_KEY"] = "test-secret-key"
    os.environ["MS_WORKSPACE"] = str(tmp_path)
    os.environ["MS_DB_PATH"] = str(tmp_path / "test.db")
    os.environ["MS_RUNNER_SOCKET"] = str(tmp_path / "runner.sock")
    os.environ["MS_LESSONS_DIR"] = str(tmp_path / "lessons")
    os.environ["MS_ANIMATIONS_DIR"] = str(tmp_path / "animations")
    os.environ["MS_COOKIE_SECURE"] = "0"
    # El asistente IA queda deshabilitado en tests (la clave no existe en tmp);
    # los tests de IA que lo necesitan crean este archivo y mockean el cliente.
    os.environ["MS_GCP_KEY_PATH"] = str(tmp_path / "gcp-key.json")


@pytest.fixture()
def client(tmp_path):
    """TestClient con la app cargada limpia sobre un workspace temporal."""
    _set_env(tmp_path)
    # Recargar modulos que capturan settings en import
    for mod in list(sys.modules):
        if mod.startswith("app"):
            del sys.modules[mod]
    import app.config as config
    config.settings = None
    import app.auth as auth
    auth._rate_limiter = None

    from fastapi.testclient import TestClient
    from app.main import app as fastapi_app

    with TestClient(fastapi_app) as c:
        yield c


@pytest.fixture()
def authed(client):
    r = client.post("/api/login", json={"username": "tester", "password": TEST_PASSWORD})
    assert r.status_code == 200
    return client
