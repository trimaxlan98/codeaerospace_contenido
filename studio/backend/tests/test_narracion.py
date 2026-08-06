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


def test_sintetizar_alineado(tmp_path):
    """Con t_inicio por seccion, la voz cae en su momento visual: silencio
    hasta el offset y cascada si la seccion anterior se pasa de largo."""
    from app.narracion import sintetizar

    fake = FakeVertex()  # 1 s de audio por seccion

    # Secciones en 0 s y 3 s -> 1 s de voz + 2 s de silencio + 1 s de voz
    dur = sintetizar(fake, [{"t_inicio": 0, "texto": "a"},
                            {"t_inicio": 3, "texto": "b"}],
                     "Charon", tmp_path / "a.wav")
    assert dur == 4.0

    # La segunda seccion pediria 0.5 s pero la primera ocupa 1 s: cede en
    # cascada con la pausa minima (0.35 s) -> 1 + 0.35 + 1
    dur = sintetizar(fake, [{"t_inicio": 0, "texto": "a"},
                            {"t_inicio": 0.5, "texto": "b"}],
                     "Charon", tmp_path / "b.wav")
    assert abs(dur - 2.35) < 0.01

    # Sin tiempos: narracion de corrido (ambas secciones caben en un solo
    # trozo TTS, asi que es una sola llamada de 1 s)
    dur = sintetizar(fake, [{"texto": "a"}, {"texto": "b"}],
                     "Charon", tmp_path / "c.wav")
    assert dur == 1.0


def _make_rendered_clip(authed, db, cfg, pid, title, job_id):
    """Clip con render 'done' vigente y mp4 falso (patron de test_projects_export)."""
    import time as _t

    from app.projects import content_hash

    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": title, "script": VALID_SCRIPT,
                             "scene": "Demo"}).json()
    job_dir = cfg.render_jobs_dir / job_id / "media"
    job_dir.mkdir(parents=True, exist_ok=True)
    video_path = job_dir / "Demo.mp4"
    video_path.write_bytes(b"fake-mp4-data")
    now = _t.time()
    db.insert_job({"id": job_id, "scene": "Demo", "quality": "ql", "timeout": 120,
                   "status": "queued", "script": VALID_SCRIPT, "created_at": now,
                   "project_id": pid, "clip_id": clip["id"], "content_hash": None})
    db.update_job(job_id, status="done", started_at=now - 5, finished_at=now,
                  video_path=str(video_path), size_bytes=13)
    project = db.get_project(pid)
    chash = content_hash(project["style_block"], VALID_SCRIPT, "Demo")
    db.update_clip(clip["id"], job_id=job_id, rendered_hash=chash)
    return clip


def test_archive_y_manifest_con_narracion(authed, tmp_path, monkeypatch):
    import io
    import zipfile

    from app.main import cfg, db

    _enable(tmp_path, monkeypatch)
    project = _create_project(authed)
    pid = project["id"]
    clip = _make_rendered_clip(authed, db, cfg, pid, "Intro", "cafe0000aaaabeef")

    r = authed.post(f"/api/projects/{pid}/narracion", json={})
    assert r.status_code == 202
    _wait_run(authed, pid)

    # El manifest expone el estado de narracion por clip
    manifest = authed.get(f"/api/projects/{pid}/export").json()
    n = manifest["clips"][0]["narracion"]
    assert n["has_audio"] is True and n["estado"] == "al_dia"

    # El zip trae mp4 + wav + txt emparejados, mux.sh y LEEME
    r = authed.get(f"/api/projects/{pid}/archive")
    assert r.status_code == 200
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    names = set(zf.namelist())
    assert {"001-intro.mp4", "001-intro.wav", "001-intro.txt",
            "concat.txt", "manifest.json", "mux.sh", "LEEME.txt"} <= names
    assert clip["id"] is not None


def test_audio_404_sin_narracion(authed):
    project = _create_project(authed)
    clip = _add_clip(authed, project["id"])
    r = authed.get(f"/api/projects/{project['id']}/narracion/{clip['id']}/audio")
    assert r.status_code == 404
    r = authed.get(f"/api/projects/{project['id']}/narracion/ajeno/audio")
    assert r.status_code == 404
