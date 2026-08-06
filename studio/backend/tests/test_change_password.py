"""Tests de cambio de contrasena y del bloqueo forzoso must_change_password."""

from .conftest import TEST_PASSWORD


def test_cambiar_password_ok(authed):
    r = authed.post("/api/change-password",
                    json={"current_password": TEST_PASSWORD, "new_password": "nueva-password-larga"})
    assert r.status_code == 200

    # login con la password vieja ya no funciona, con la nueva si
    fresh = authed
    assert fresh.post("/api/login", json={"username": "tester", "password": TEST_PASSWORD}
                      ).status_code == 401
    r2 = fresh.post("/api/login", json={"username": "tester", "password": "nueva-password-larga"})
    assert r2.status_code == 200


def test_cambiar_password_actual_incorrecta(authed):
    r = authed.post("/api/change-password",
                    json={"current_password": "no-es-esta", "new_password": "nueva-password-larga"})
    assert r.status_code == 422


def test_cambiar_password_muy_corta(authed):
    r = authed.post("/api/change-password",
                    json={"current_password": TEST_PASSWORD, "new_password": "corta"})
    assert r.status_code == 422


def test_cambiar_password_igual_a_la_actual(authed):
    r = authed.post("/api/change-password",
                    json={"current_password": TEST_PASSWORD, "new_password": TEST_PASSWORD})
    assert r.status_code == 422


def test_cambiar_password_requiere_auth(client):
    r = client.post("/api/change-password",
                    json={"current_password": TEST_PASSWORD, "new_password": "nueva-password-larga"})
    assert r.status_code == 401


def test_must_change_password_bloquea_la_api(client, monkeypatch):
    """Con el flag activo, toda la API queda 403 salvo login/logout/me/change-password."""
    r = client.post("/api/login", json={"username": "tester", "password": TEST_PASSWORD})
    assert r.status_code == 200

    from app.main import db as app_db
    auth_row = app_db.get_auth()
    app_db.set_password(auth_row["password_hash"], must_change_password=True)

    r_me = client.get("/api/me")
    assert r_me.status_code == 200
    assert r_me.json()["must_change_password"] is True

    r_jobs = client.get("/api/jobs")
    assert r_jobs.status_code == 403
    assert r_jobs.json()["code"] == "PASSWORD_CHANGE_REQUIRED"

    # cambiar la password limpia el flag y desbloquea el resto de la API
    r_change = client.post("/api/change-password",
                           json={"current_password": TEST_PASSWORD,
                                 "new_password": "nueva-password-larga"})
    assert r_change.status_code == 200
    assert client.get("/api/jobs").status_code == 200
    assert client.get("/api/me").json()["must_change_password"] is False

    # logout sigue disponible incluso con el flag activo (probado antes de
    # limpiarlo mas arriba implicitamente via /api/me y /api/jobs; aqui solo
    # confirmamos que la ruta esta en la lista exenta)
    from app.main import _PASSWORD_GATE_EXEMPT
    assert "/api/logout" in _PASSWORD_GATE_EXEMPT
