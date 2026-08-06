"""Narracion de proyectos: estado por clip, generacion en segundo plano
(Vertex mockeado, sin red) y descarga de audio/texto. Las partes puras del
generador (mvhd, hash, slug) se cubren en test_guiones.py."""

import time

VALID_SCRIPT = (
    "from manim import *\n"
    "class Demo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle()))\n"
)


def _create_project(authed, **overrides):
    body = {"name": "Curso narrado", "description": "desc", "quality": "ql",
            "style_block": ""}
    body.update(overrides)
    r = authed.post("/api/projects", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def _add_clip(authed, pid, title="Clip uno"):
    r = authed.post(f"/api/projects/{pid}/clips",
                    json={"title": title, "script": VALID_SCRIPT,
                          "scene": "Demo"})
    assert r.status_code == 201, r.text
    return r.json()


class FakeVertex:
    model_tts = "tts-de-prueba"

    def __init__(self, tts_delay=0.0):
        self.tts_delay = tts_delay
        self.llamadas_guion = 0

    def guion(self, system, user):
        self.llamadas_guion += 1
        return {"secciones": [{"t_inicio": 0, "t_fin": 5, "momento": "intro",
                               "texto": "Hola, esto es una prueba."}]}

    def tts(self, texto, voz):
        if self.tts_delay:
            time.sleep(self.tts_delay)
        return b"\x00\x00" * 24_000  # 1 s de silencio PCM


def _enable(tmp_path, monkeypatch, fake=None):
    (tmp_path / "gcp-key.json").write_text('{"project_id": "test"}')
    import app.main as main_mod
    fake = fake or FakeVertex()
    monkeypatch.setattr(main_mod.narracion_service, "_vertex", lambda: fake)
    return fake


def _wait_run(authed, pid, timeout=5.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        d = authed.get(f"/api/projects/{pid}/narracion").json()
        run = d.get("run")
        if run and run["finished"]:
            return d
        time.sleep(0.05)
    raise AssertionError("la narracion no termino a tiempo")


def test_estado_sin_credenciales(authed):
    project = _create_project(authed)
    clip = _add_clip(authed, project["id"])

    r = authed.get(f"/api/projects/{project['id']}/narracion")
    assert r.status_code == 200
    d = r.json()
    assert d["enabled"] is False
    assert d["run"] is None
    assert d["clips"][0]["clip_id"] == clip["id"]
    assert d["clips"][0]["estado"] == "sin_narracion"
    assert d["clips"][0]["has_audio"] is False

    r = authed.post(f"/api/projects/{project['id']}/narracion", json={})
    assert r.status_code == 503

    assert authed.get("/api/projects/nope/narracion").status_code == 404


def test_generacion_en_segundo_plano(authed, tmp_path, monkeypatch):
    fake = _enable(tmp_path, monkeypatch)
    project = _create_project(authed)
    clip = _add_clip(authed, project["id"])
    pid = project["id"]

    r = authed.post(f"/api/projects/{pid}/narracion", json={})
    assert r.status_code == 202, r.text
    assert r.json()["queued"] == [clip["id"]]

    d = _wait_run(authed, pid)
    assert d["run"]["done"] == 1
    assert d["run"]["errores"] == []
    c = d["clips"][0]
    assert c["estado"] == "al_dia"
    assert c["has_audio"] and c["has_texto"]
    assert c["audio_s"] == 1.0
    assert c["voz"] == "Charon"

    # Audio y texto descargables
    r = authed.get(f"/api/projects/{pid}/narracion/{clip['id']}/audio")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("audio/wav")
    r = authed.get(f"/api/projects/{pid}/narracion/{clip['id']}/texto")
    assert r.status_code == 200
    assert "Clip uno" in r.json()["md"]
    assert "prueba" in r.json()["txt"]

    # Al dia: relanzar no encola nada
    r = authed.post(f"/api/projects/{pid}/narracion", json={})
    assert r.status_code == 202
    assert r.json()["queued"] == []

    # Cambiar el script deja la narracion desactualizada
    r = authed.patch(f"/api/projects/{pid}/clips/{clip['id']}",
                     json={"script": VALID_SCRIPT + "\n# cambio\n"})
    assert r.status_code == 200
    d = authed.get(f"/api/projects/{pid}/narracion").json()
    assert d["clips"][0]["estado"] == "desactualizada"

    # force regenera aunque este al dia
    llamadas = fake.llamadas_guion
    r = authed.post(f"/api/projects/{pid}/narracion",
                    json={"clips": [clip["id"]], "force": True})
    assert r.status_code == 202
    assert r.json()["queued"] == [clip["id"]]
    _wait_run(authed, pid)
    assert fake.llamadas_guion > llamadas


def test_corrida_unica_y_cancelacion(authed, tmp_path, monkeypatch):
    _enable(tmp_path, monkeypatch, FakeVertex(tts_delay=0.3))
    project = _create_project(authed)
    for i in range(2):
        _add_clip(authed, project["id"], title=f"Clip {i + 1}")
    pid = project["id"]

    r = authed.post(f"/api/projects/{pid}/narracion", json={})
    assert r.status_code == 202
    # Segunda corrida mientras la primera sigue activa -> 409
    r = authed.post(f"/api/projects/{pid}/narracion", json={})
    assert r.status_code == 409

    r = authed.post(f"/api/projects/{pid}/narracion/cancel")
    assert r.status_code == 200
    d = _wait_run(authed, pid)
    # Cancelada entre clips: no llego a narrar los dos
    assert d["run"]["done"] < 2

    # Sin corrida activa, cancelar avisa
    r = authed.post(f"/api/projects/{pid}/narracion/cancel")
    assert r.status_code == 409


def test_audio_404_sin_narracion(authed):
    project = _create_project(authed)
    clip = _add_clip(authed, project["id"])
    r = authed.get(f"/api/projects/{project['id']}/narracion/{clip['id']}/audio")
    assert r.status_code == 404
    r = authed.get(f"/api/projects/{project['id']}/narracion/ajeno/audio")
    assert r.status_code == 404
