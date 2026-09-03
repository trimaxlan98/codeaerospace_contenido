"""Hoja de contactos y fotograma como figura (sprint R3b).

La extraccion de verdad corre en el contenedor (`hoja_contactos.py`, ffmpeg);
aqui se prueba lo que la app hace con ella: validar lo que entra, no llamar
dos veces al contenedor por lo mismo, servir los PNG y no dejar salir del
directorio del job.
"""

import json
import time

import pytest

VALID_SCRIPT = (
    "from manim import *\n"
    "class Demo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle()))\n"
)

INDICE = {
    "ok": True, "n": 3, "duracion": 12.5, "ancho": 480,
    "frames": [{"archivo": "01.png", "t": 2.083, "ancho": 480, "alto": 270},
               {"archivo": "02.png", "t": 6.25, "ancho": 480, "alto": 270},
               {"archivo": "03.png", "t": 10.417, "ancho": 480, "alto": 270}],
    "final": {"archivo": "final.png", "t": 12.5, "ancho": 480, "alto": 270},
}

PNG = b"\x89PNG\r\n\x1a\n"


def _job_con_video(job_id="abcdef0000000001", status="done"):
    """Un job terminado con un mp4 en la ruta canonica (sin renderizar)."""
    from app.main import cfg, db
    media = cfg.render_jobs_dir / job_id / "media" / "videos" / "s" / "480p15"
    media.mkdir(parents=True, exist_ok=True)
    (media / "Demo.mp4").write_bytes(b"fake-mp4")
    ahora = time.time()
    db.insert_job({"id": job_id, "scene": "Demo", "quality": "ql",
                   "timeout": 600, "status": "queued", "script": VALID_SCRIPT,
                   "created_at": ahora, "project_id": None, "clip_id": None,
                   "content_hash": None, "formato": "horizontal"})
    db.update_job(job_id, status=status, started_at=ahora, finished_at=ahora,
                  video_path=str(media / "Demo.mp4"), size_bytes=8)
    return job_id


def _escribir_hoja(cfg, job_id, indice=INDICE):
    frames = cfg.render_jobs_dir / job_id / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    for f in indice["frames"]:
        (frames / f["archivo"]).write_bytes(PNG)
    (frames / indice["final"]["archivo"]).write_bytes(PNG)
    (frames / "indice.json").write_text(json.dumps(indice), encoding="utf-8")
    return frames


# ── hoja de contactos ────────────────────────────────────────────────────────

def test_la_hoja_llama_al_runner_y_devuelve_las_urls(authed, monkeypatch):
    from app.main import cfg, runner
    job_id = _job_con_video()
    llamadas = []

    async def falso(jid, n):
        llamadas.append((jid, n))
        _escribir_hoja(cfg, jid)
        return INDICE

    monkeypatch.setattr(runner, "frames", falso)
    d = authed.post(f"/api/jobs/{job_id}/frames", json={"n": 3}).json()
    assert llamadas == [(job_id, 3)]
    assert d["recalculada"] is True
    assert [f["t"] for f in d["frames"]] == [2.083, 6.25, 10.417]
    # Cada fotograma llega con su URL resuelta: la vista no compone rutas.
    assert d["frames"][0]["url"] == f"/api/jobs/{job_id}/frames/01.png"
    assert d["final"]["url"] == f"/api/jobs/{job_id}/frames/final.png"


def test_la_hoja_ya_hecha_no_arranca_otro_contenedor(authed, monkeypatch):
    """El mp4 de un job es inmutable: pedir la misma hoja dos veces no puede
    costar dos contenedores."""
    from app.main import cfg, runner
    job_id = _job_con_video("abcdef0000000002")
    _escribir_hoja(cfg, job_id)

    async def prohibido(jid, n):
        raise AssertionError("no debia llamarse al runner")

    monkeypatch.setattr(runner, "frames", prohibido)
    d = authed.post(f"/api/jobs/{job_id}/frames", json={"n": 3}).json()
    assert d["recalculada"] is False
    assert len(d["frames"]) == 3


def test_otro_n_si_recalcula(authed, monkeypatch):
    from app.main import cfg, runner
    job_id = _job_con_video("abcdef0000000003")
    _escribir_hoja(cfg, job_id)
    llamadas = []

    async def falso(jid, n):
        llamadas.append(n)
        return INDICE | {"n": n}

    monkeypatch.setattr(runner, "frames", falso)
    authed.post(f"/api/jobs/{job_id}/frames", json={"n": 8})
    assert llamadas == [8]


def test_un_png_borrado_invalida_la_hoja_en_disco(authed, monkeypatch):
    """El indice solo vale si sus archivos siguen ahi (borrar el job y volver
    a renderizar deja el indice viejo si nadie mira los PNG)."""
    from app.main import cfg, runner
    job_id = _job_con_video("abcdef0000000004")
    frames = _escribir_hoja(cfg, job_id)
    (frames / "02.png").unlink()
    llamadas = []

    async def falso(jid, n):
        llamadas.append(n)
        return INDICE

    monkeypatch.setattr(runner, "frames", falso)
    authed.post(f"/api/jobs/{job_id}/frames", json={"n": 3})
    assert llamadas == [3]


@pytest.mark.parametrize("n", [0, 25, -1, 100])
def test_n_fuera_de_rango(authed, n):
    job_id = _job_con_video(f"abcdef000000{abs(n) + 10:04d}")
    r = authed.post(f"/api/jobs/{job_id}/frames", json={"n": n})
    assert r.status_code == 422


def test_sin_video_no_hay_hoja(authed):
    from app.main import db
    job_id = _job_con_video("abcdef0000000005", status="error")
    db.update_job(job_id, video_path=None)
    assert authed.post(f"/api/jobs/{job_id}/frames",
                       json={"n": 4}).status_code == 409


def test_el_runner_caido_es_un_502(authed, monkeypatch):
    from app.main import runner
    from app.runner_client import RunnerError
    job_id = _job_con_video("abcdef0000000006")

    async def falso(jid, n):
        raise RunnerError("runner no disponible")

    monkeypatch.setattr(runner, "frames", falso)
    r = authed.post(f"/api/jobs/{job_id}/frames", json={"n": 4})
    assert r.status_code == 502


def test_los_fotogramas_no_dejan_salir_del_job(authed):
    from app.main import cfg
    job_id = _job_con_video("abcdef0000000007")
    _escribir_hoja(cfg, job_id)

    r = authed.get(f"/api/jobs/{job_id}/frames/01.png")
    assert r.status_code == 200 and r.content.startswith(PNG)
    assert authed.get(f"/api/jobs/{job_id}/frames/final.png").status_code == 200

    for malo in ("../scene.py", "..%2Fscene.py", "1.png", "otro.png",
                 "final.png.bak", "indice.json"):
        assert authed.get(
            f"/api/jobs/{job_id}/frames/{malo}").status_code in (404, 405)


# ── fotograma como figura ────────────────────────────────────────────────────

def test_la_figura_se_pide_a_la_resolucion_elegida(authed, monkeypatch):
    from app.main import cfg, runner
    job_id = _job_con_video("abcdef0000000008")
    llamadas = []

    async def falso(jid, t, ancho, formato):
        llamadas.append((jid, t, ancho, formato))
        nombre = f"t{int(round(t * 1000)):08d}_{ancho}.png"
        figuras = cfg.render_jobs_dir / jid / "figuras"
        figuras.mkdir(parents=True, exist_ok=True)
        (figuras / nombre).write_bytes(PNG)
        return {"ok": True, "archivo": nombre, "t": t, "ancho": ancho,
                "alto": 2160, "bytes": 8, "duracion": 12.5}

    monkeypatch.setattr(runner, "fotograma", falso)
    d = authed.post(f"/api/jobs/{job_id}/fotograma",
                    json={"t": 3.25, "ancho": 3840}).json()
    assert llamadas == [(job_id, 3.25, 3840, "png")]
    assert d["archivo"] == "t00003250_3840.png"
    assert d["url"] == f"/api/jobs/{job_id}/figuras/t00003250_3840.png"

    r = authed.get(d["url"])
    assert r.status_code == 200 and r.content.startswith(PNG)


@pytest.mark.parametrize("body", [
    {"t": -1.0, "ancho": 1920},          # instante negativo
    {"t": 100000.0, "ancho": 1920},      # mas alla de cualquier video
    {"t": 1.0, "ancho": 4096},           # por encima de 4K
    {"t": 1.0, "ancho": 8},              # por debajo del minimo
    {"ancho": 1920},                     # sin instante
])
def test_parametros_invalidos_de_la_figura(authed, body):
    job_id = _job_con_video("abcdef0000000009")
    r = authed.post(f"/api/jobs/{job_id}/fotograma", json=body)
    assert r.status_code == 422


def test_formato_distinto_de_png(authed):
    job_id = _job_con_video("abcdef000000000a")
    r = authed.post(f"/api/jobs/{job_id}/fotograma",
                    json={"t": 1.0, "ancho": 1920, "formato": "svg"})
    assert r.status_code == 422


def test_las_figuras_no_dejan_salir_del_job(authed):
    from app.main import cfg
    job_id = _job_con_video("abcdef000000000b")
    figuras = cfg.render_jobs_dir / job_id / "figuras"
    figuras.mkdir(parents=True, exist_ok=True)
    (figuras / "t00001000_1920.png").write_bytes(PNG)

    assert authed.get(
        f"/api/jobs/{job_id}/figuras/t00001000_1920.png").status_code == 200
    for malo in ("../scene.py", "..%2Fscene.py", "t1_1920.png", "otra.png",
                 "t00001000_1920.png.bak"):
        assert authed.get(
            f"/api/jobs/{job_id}/figuras/{malo}").status_code in (404, 405)


def test_fotogramas_requieren_sesion(client):
    assert client.post("/api/jobs/abcdef0000000001/frames",
                       json={"n": 4}).status_code == 401
    assert client.get(
        "/api/jobs/abcdef0000000001/frames/01.png").status_code == 401
    assert client.post("/api/jobs/abcdef0000000001/fotograma",
                       json={"t": 1.0, "ancho": 1920}).status_code == 401


# ── el runner y la herramienta no pueden separarse ───────────────────────────

def test_los_topes_del_runner_son_los_de_la_herramienta():
    """`hoja_contactos.py` valida n<=24 y ancho<=3840; el runner y la API
    tienen que juzgar con los mismos numeros, o la app ofreceria algo que el
    contenedor rechaza (o al reves)."""
    import ast
    from pathlib import Path

    from app import main as main_mod

    raiz = Path(__file__).resolve().parents[3]
    herramienta = ast.parse(
        (raiz / "studio" / "tools" / "hoja_contactos.py").read_text())
    runner_src = ast.parse(
        (raiz / "studio" / "runner" / "manim_runner.py").read_text())

    def const(arbol, nombre):
        for nodo in ast.walk(arbol):
            if (isinstance(nodo, ast.Assign)
                    and getattr(nodo.targets[0], "id", "") == nombre):
                return ast.literal_eval(nodo.value)
        return None

    assert const(herramienta, "N_MAX") == const(runner_src, "HOJA_MAX") \
        == main_mod.HOJA_MAX == 24
    assert const(herramienta, "ANCHO_MAX") == 3840
    assert const(herramienta, "ANCHO_TIRA") == const(runner_src, "ANCHO_TIRA")
