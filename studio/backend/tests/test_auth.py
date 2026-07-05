"""Pruebas de autenticacion, sesion y proteccion contra fuerza bruta."""

from .conftest import TEST_PASSWORD


def test_login_ok_sets_cookie(client):
    r = client.post("/api/login", json={"username": "tester", "password": TEST_PASSWORD})
    assert r.status_code == 200
    assert "ms_session" in r.cookies
    r2 = client.get("/api/me")
    assert r2.json() == {"authenticated": True, "user": "tester", "ai_enabled": False}


def test_login_bad_password(client):
    r = client.post("/api/login", json={"username": "tester", "password": "mala"})
    assert r.status_code == 401


def test_login_bad_user_same_response(client):
    r = client.post("/api/login", json={"username": "otro", "password": TEST_PASSWORD})
    assert r.status_code == 401


def test_all_api_routes_require_auth(client):
    protected = [
        ("GET", "/api/jobs"), ("GET", "/api/metrics"), ("GET", "/api/events"),
        ("POST", "/api/scenes"), ("POST", "/api/jobs"),
        ("GET", "/api/jobs/abcdef1234567890"),
        ("POST", "/api/jobs/abcdef1234567890/cancel"),
        ("GET", "/api/jobs/abcdef1234567890/video"),
        ("POST", "/api/logout"),
    ]
    for method, path in protected:
        r = client.request(method, path, json={})
        assert r.status_code == 401, f"{method} {path} -> {r.status_code}"


def test_bruteforce_lockout(client):
    for _ in range(5):
        r = client.post("/api/login", json={"username": "tester", "password": "mala"})
        assert r.status_code in (401, 429)
    # Al sexto intento debe estar bloqueado, incluso con la password correcta
    r = client.post("/api/login", json={"username": "tester", "password": TEST_PASSWORD})
    assert r.status_code == 429


def test_tampered_cookie_rejected(client):
    client.post("/api/login", json={"username": "tester", "password": TEST_PASSWORD})
    client.cookies.set("ms_session", "manipulada.invalida")
    r = client.get("/api/jobs")
    assert r.status_code == 401


def test_logout_clears_session(client):
    client.post("/api/login", json={"username": "tester", "password": TEST_PASSWORD})
    r = client.post("/api/logout")
    assert r.status_code == 200
    assert client.get("/api/me").json()["authenticated"] is False
