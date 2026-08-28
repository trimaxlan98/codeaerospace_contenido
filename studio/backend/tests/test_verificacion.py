"""Verificacion del promo (sprint P3): el informe medido, dentro de la app.

La medicion de verdad corre en el contenedor (`promo_verifica.py`, ffmpeg);
aqui se prueba lo que la app hace con ella: guardarla, saber cuando deja de
valer, servir los frames y no dejar salir del directorio del job.
"""

import ast
import json
import time
from pathlib import Path

import pytest

from app import audio_promo
from app.projects import content_hash

VALID_SCRIPT = (
    "from manim import *\n"
    "class Promo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle()))\n"
)

INFORME = {
    "ok": True,
    "archivo": "promo_audio.mp4",
    "video": {"dur": 12.9, "ancho": 1080, "alto": 1920, "fps": 60.0,
              "resolucion": "1080x1920"},
    "duracion": {"ok": True, "min": 8.0, "max": 15.0, "s": 12.9},
    "bucle": {"ok": True, "media": 0.0, "pct": 0.0, "piso_media": 0.0002,
              "piso_pct": 0.0, "sobre_piso_media": 0.0, "sobre_piso_pct": 0.0},
    "audio": {"tiene_audio": True, "ok": True, "codec": "aac", "hz": 24000,
              "canales": 1, "dur": 12.93, "pico_db": -1.6,
              "entrada_db": -120.0, "salida_db": -120.0, "extremos_ok": True},
    "frames": ["f01.png", "f02.png"],
    "costura": "costura.png",
}


def test_el_rango_de_duracion_es_el_mismo_que_mide_la_herramienta():
    """`audio_promo` avisa con 8-15 s y `promo_verifica` juzga con 8-15 s.
    Si se separan, la app diria «cabe» de un promo que la medicion suspende."""
    tool = Path(__file__).resolve().parents[2] / "tools" / "promo_verifica.py"
    arbol = ast.parse(tool.read_text())
    valores = None
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Assign):
            continue
        destino = nodo.targets[0]
        if (isinstance(destino, ast.Tuple)
                and [getattr(t, "id", "") for t in destino.elts]
                == ["DUR_MIN", "DUR_MAX"]):
            valores = [c.value for c in nodo.value.elts]
    assert valores == [audio_promo.DUR_MIN, audio_promo.DUR_MAX]


def test_el_hash_de_verificacion_cambia_con_el_archivo():
    a = {"id": "job1", "audio_hash": None}
    b = {"id": "job1", "audio_hash": "mezcla1"}
    c = {"id": "job2", "audio_hash": None}
    # Medir el mudo y medir el mezclado no son lo mismo (la mitad del
    # informe es el audio), y otro render tampoco.
    assert audio_promo.hash_verificacion(a) != audio_promo.hash_verificacion(b)
    assert audio_promo.hash_verificacion(a) != audio_promo.hash_verificacion(c)
    assert audio_promo.hash_verificacion(b) == audio_promo.hash_verificacion(
        {"id": "job1", "audio_hash": "mezcla1"})


# ── la API ───────────────────────────────────────────────────────────────────

def _promo_con_render(authed, job_id="beefbeef00000001"):
    from app.main import cfg, db
    p = authed.post("/api/projects", json={
        "name": "Promo verificado", "quality": "qh", "tipo": "promo",
        "formato": "vertical", "style_block": ""}).json()
    clip = authed.post(f"/api/projects/{p['id']}/clips",
                       json={"title": "Bucle", "script": VALID_SCRIPT,
                             "scene": "Promo"}).json()
    media = cfg.render_jobs_dir / job_id / "media" / "videos" / "s" / "1920p60"
    media.mkdir(parents=True, exist_ok=True)
    (media / "Promo.mp4").write_bytes(b"fake-mp4")
    ahora = time.time()
    db.insert_job({"id": job_id, "scene": "Promo", "quality": "qh",
                   "timeout": 600, "status": "queued", "script": VALID_SCRIPT,
                   "created_at": ahora, "project_id": p["id"],
                   "clip_id": clip["id"], "content_hash": None,
                   "formato": "vertical"})
    db.update_job(job_id, status="done", started_at=ahora, finished_at=ahora,
                  video_path=str(media / "Promo.mp4"), size_bytes=8)
    db.update_clip(clip["id"], job_id=job_id,
                   rendered_hash=content_hash("", VALID_SCRIPT, "Promo"))
    return p, clip, job_id


def test_verificar_sin_render(authed):
    p = authed.post("/api/projects", json={
        "name": "Promo pelado", "quality": "qh", "tipo": "promo"}).json()
    clip = authed.post(f"/api/projects/{p['id']}/clips",
                       json={"title": "x", "script": VALID_SCRIPT,
                             "scene": "Promo"}).json()
    r = authed.post(f"/api/projects/{p['id']}/clips/{clip['id']}/verificar")
    assert r.status_code == 409


def test_verificar_guarda_el_informe_y_caduca(authed, monkeypatch):
    from app.main import db, manager
    p, clip, job_id = _promo_con_render(authed)

    async def falso(jid, frames=6, dur_min=8.0, dur_max=15.0):
        assert (jid, frames, dur_min, dur_max) == (job_id, 6, 8.0, 15.0)
        return INFORME

    monkeypatch.setattr(manager, "verificar_promo", falso)
    d = authed.post(f"/api/projects/{p['id']}/clips/{clip['id']}/verificar").json()
    assert d["verificacion"]["estado"] == "al_dia"
    assert d["verificacion"]["ok"] is True
    assert d["verificacion"]["informe"]["bucle"]["sobre_piso_pct"] == 0.0
    assert d["job_id"] == job_id

    # El detalle del proyecto lo resume sin cargar el informe entero.
    detalle = authed.get(f"/api/projects/{p['id']}").json()
    assert detalle["clips"][0]["verificacion"] == {"estado": "al_dia", "ok": True}

    # Mezclar despues cambia el archivo: el informe deja de valer.
    db.update_job(job_id, audio_path="/tmp/x.mp4", audio_hash="otra-mezcla")
    d = authed.get(f"/api/projects/{p['id']}/clips/{clip['id']}/audio").json()
    assert d["verificacion"]["estado"] == "desactualizada"


def test_un_informe_que_no_pasa_se_ve_rojo(authed, monkeypatch):
    from app.main import manager
    p, clip, _job = _promo_con_render(authed, job_id="beefbeef00000002")
    roto = json.loads(json.dumps(INFORME))
    roto["ok"] = False
    roto["bucle"] = {**roto["bucle"], "ok": False, "pct": 3.4,
                     "sobre_piso_pct": 3.4}

    async def falso(jid, **kw):
        return roto

    monkeypatch.setattr(manager, "verificar_promo", falso)
    d = authed.post(f"/api/projects/{p['id']}/clips/{clip['id']}/verificar").json()
    assert d["verificacion"]["ok"] is False
    assert d["verificacion"]["informe"]["bucle"]["sobre_piso_pct"] == 3.4


def test_los_frames_no_dejan_salir_del_job(authed):
    from app.main import cfg
    p, clip, job_id = _promo_con_render(authed, job_id="beefbeef00000003")
    verif = cfg.render_jobs_dir / job_id / "verificacion"
    verif.mkdir(parents=True, exist_ok=True)
    (verif / "costura.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    r = authed.get(f"/api/jobs/{job_id}/verificacion/costura.png")
    assert r.status_code == 200 and r.content.startswith(b"\x89PNG")

    # Nombres fuera del conjunto cerrado: ni traversal ni ficheros ajenos.
    for malo in ("../scene.py", "..%2Fscene.py", "otro.png", "f1.png",
                 "costura.png.bak"):
        assert authed.get(
            f"/api/jobs/{job_id}/verificacion/{malo}").status_code in (404, 405)
