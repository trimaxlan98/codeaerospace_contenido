"""Audio del promo (sprint P2): manifiesto, avisos y API.

Sin Docker ni Vertex: la mezcla real se prueba fuera (el runner corre
`sfx.py` en el contenedor). Lo que se prueba aqui es lo que decide si el
promo suena bien — el manifiesto que se le pasa a sfx.py y los avisos que
evitan los dos errores que ya se cometieron a mano: la frase que no cabe y
la voz pegada al ultimo frame.
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


# ── el catalogo de sonidos no puede separarse de sfx.py ──────────────────────

def test_los_sonidos_son_los_de_sfx():
    """`SONIDOS` es un espejo de `PALETA`. Si alguien añade un sonido a
    sfx.py y no aparece en la app, el desplegable miente; si lo quita, la
    mezcla falla en el contenedor con un KeyError. Se comparan leyendo el
    archivo (sfx.py importa numpy y no se puede importar aqui)."""
    sfx = Path(__file__).resolve().parents[2] / "tools" / "sfx.py"
    arbol = ast.parse(sfx.read_text())
    paleta = None
    for nodo in arbol.body:
        if (isinstance(nodo, ast.Assign)
                and any(getattr(t, "id", "") == "PALETA" for t in nodo.targets)):
            paleta = [k.value for k in nodo.value.keys]
    assert paleta, "no se encontro PALETA en sfx.py"
    assert sorted(paleta) == sorted(audio_promo.SONIDOS)


# ── manifiesto ───────────────────────────────────────────────────────────────

def test_normalizar_ordena_y_rellena():
    m = audio_promo.normalizar({
        "audio": {"eventos": [["pulso", 5.0, -12], ["aire", 1.0, -18]]},
        "voz": {"secciones": [{"t_inicio": 6.0, "texto": "dos"},
                              {"t_inicio": 1.0, "texto": "uno"},
                              {"t_inicio": 9.0, "texto": "   "}]},
    })
    # Los eventos y las frases se ordenan por tiempo: el ensamblador de voz
    # empuja la frase siguiente si una llega fuera de orden.
    assert [e[0] for e in m["audio"]["eventos"]] == ["aire", "pulso"]
    assert [s["texto"] for s in m["voz"]["secciones"]] == ["uno", "dos"]
    assert m["audio"]["pico_db"] == audio_promo.PICO_DB
    assert m["audio"]["pico_db_con_voz"] == audio_promo.PICO_DB_CON_VOZ
    assert "fade_out" not in m["audio"]  # ausente = automatico


def test_validar_rechaza_lo_que_sfx_no_sabria_leer():
    m = audio_promo.normalizar({"audio": {"eventos": [["trueno", 1.0, -12]]}})
    assert any("trueno" in e for e in audio_promo.validar(m))

    m = audio_promo.normalizar({"audio": {"eventos": [["pulso", 1.0, 40]]}})
    assert any("nivel" in e for e in audio_promo.validar(m))

    m = audio_promo.normalizar({"voz": {"voz": "rm -rf /"}})
    assert any("voz" in e for e in audio_promo.validar(m))

    assert audio_promo.validar(audio_promo.vacio()) == []


def test_silabas_aproximadas():
    # "Cada semilla nace girando igual" (del promo de filotaxis): 12 grupos
    # de vocales. La cuenta agrupa diptongos, que es como suenan.
    assert audio_promo.silabas("Cada semilla nace girando igual") == 12
    assert audio_promo.silabas("") == 0
    # A 2.45 sil/s, esa frase pide ~5 s.
    assert 4.5 < audio_promo.duracion_voz("Cada semilla nace girando igual") < 5.5


# ── avisos: los dos errores que ya se cometieron ─────────────────────────────

def test_avisa_cuando_una_frase_no_cabe():
    m = audio_promo.normalizar({"voz": {"secciones": [
        {"t_inicio": 0.5, "texto": "Una frase larguisima que no cabe de ninguna"
                                   " manera en el hueco que se le ha dejado"},
        {"t_inicio": 2.0, "texto": "La siguiente"},
    ]}})
    avisos = audio_promo.avisos(m, 12.0)
    assert any("empujara" in a for a in avisos)


def test_avisa_cuando_la_voz_se_pega_al_final():
    m = audio_promo.normalizar({"voz": {"secciones": [
        {"t_inicio": 10.5, "texto": "Justo al final del video"},
    ]}})
    avisos = audio_promo.avisos(m, 12.0)
    assert any("chasquea" in a for a in avisos)
    # Con aire de sobra, ni un aviso.
    m = audio_promo.normalizar({"voz": {"secciones": [
        {"t_inicio": 1.0, "texto": "Con tiempo de sobra"},
    ]}})
    assert audio_promo.avisos(m, 12.0) == []


def test_avisa_de_un_sonido_despues_del_final():
    m = audio_promo.normalizar({"audio": {"eventos": [["pulso", 30.0, -12]]}})
    assert any("no se oira" in a for a in audio_promo.avisos(m, 12.0))


def test_el_hash_de_voz_ignora_la_cama():
    a = audio_promo.normalizar({"voz": {"secciones": [{"t_inicio": 1, "texto": "hola"}]}})
    b = audio_promo.normalizar({
        "audio": {"eventos": [["pulso", 1.0, -12]]},
        "voz": {"secciones": [{"t_inicio": 1, "texto": "hola"}]}})
    # Mover un sonido no debe volver a gastar TTS...
    assert audio_promo.hash_voz(a) == audio_promo.hash_voz(b)
    # ...pero si cambia la mezcla completa.
    assert audio_promo.hash_mezcla(a, "job1") != audio_promo.hash_mezcla(b, "job1")
    # Y el mismo manifiesto sobre otro render tampoco vale.
    assert audio_promo.hash_mezcla(a, "job1") != audio_promo.hash_mezcla(a, "job2")


def test_para_sfx_no_reescala():
    """sfx.py reescala los tiempos si el manifiesto declara otra duracion.
    Aqui los tiempos se escriben sobre un video que ya existe: sin
    `duracion_objetivo` no se toca nada."""
    m = audio_promo.normalizar({"audio": {"eventos": [["pulso", 3.0, -12]]}})
    spec = audio_promo.para_sfx(m)
    assert "duracion_objetivo" not in spec
    assert spec["audio"]["eventos"] == [["pulso", 3.0, -12.0]]


# ── API ──────────────────────────────────────────────────────────────────────

def _promo(authed):
    r = authed.post("/api/projects", json={
        "name": "Promo con sonido", "quality": "qh", "tipo": "promo",
        "formato": "vertical", "style_block": ""})
    assert r.status_code == 201, r.text
    p = r.json()
    clip = authed.post(f"/api/projects/{p['id']}/clips",
                       json={"title": "Bucle", "script": VALID_SCRIPT,
                             "scene": "Promo"}).json()
    return p, clip


MANIFIESTO = {
    "eventos": [{"sonido": "nebulosa", "t": 0.1, "db": -14},
                {"sonido": "pulso", "t": 3.0, "db": -12}],
    "secciones": [{"t_inicio": 0.8, "texto": "Una idea que cabe."}],
    "voz": "Charon",
}


def test_guardar_y_leer_el_manifiesto(authed):
    p, clip = _promo(authed)
    r = authed.put(f"/api/projects/{p['id']}/clips/{clip['id']}/audio",
                   json=MANIFIESTO)
    assert r.status_code == 200, r.text
    d = r.json()
    assert [e[0] for e in d["manifiesto"]["audio"]["eventos"]] == ["nebulosa", "pulso"]
    assert d["estado"]["estado"] == "sin_render"  # hay manifiesto, no hay video
    assert "nebulosa" in d["sonidos"]

    d2 = authed.get(f"/api/projects/{p['id']}/clips/{clip['id']}/audio").json()
    assert d2["manifiesto"] == d["manifiesto"]

    # El clip lo anuncia en el detalle del proyecto, sin cargar el manifiesto.
    detalle = authed.get(f"/api/projects/{p['id']}").json()
    assert detalle["clips"][0]["has_audio"] is True
    assert detalle["clips"][0]["audio"]["estado"] == "sin_render"
    assert "audio_json" not in detalle["clips"][0]


def test_un_curso_lleva_cama_pero_no_voz(authed):
    """Sprint E3: la cama de sonido dejo de ser exclusiva de los promos.

    Lo que un curso NO puede llevar aqui es voz: su narracion sale de
    «Generar narracion» y la pelicula la pega al montar. Aceptar las frases
    en silencio pegaria DOS voces sobre el mismo clip.
    """
    r = authed.post("/api/projects", json={"name": "Curso", "quality": "ql"})
    pid = r.json()["id"]
    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": "Uno", "script": VALID_SCRIPT,
                             "scene": "Promo"}).json()

    r = authed.put(f"/api/projects/{pid}/clips/{clip['id']}/audio", json=MANIFIESTO)
    assert r.status_code == 422
    assert "narracion" in r.json()["detail"]

    solo_cama = {k: v for k, v in MANIFIESTO.items() if k != "secciones"}
    r = authed.put(f"/api/projects/{pid}/clips/{clip['id']}/audio", json=solo_cama)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["tipo"] == "curso"
    assert body["voz_aqui"] is False
    assert [e[0] for e in body["manifiesto"]["audio"]["eventos"]] == ["nebulosa", "pulso"]


def test_la_verificacion_es_cosa_de_promos(authed):
    """Mide la costura del bucle y 8-15 s: en un curso no significa nada."""
    pid = authed.post("/api/projects",
                      json={"name": "Curso V", "quality": "ql"}).json()["id"]
    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": "Uno", "script": VALID_SCRIPT,
                             "scene": "Promo"}).json()
    r = authed.post(f"/api/projects/{pid}/clips/{clip['id']}/verificar")
    assert r.status_code == 409
    assert "bucle" in r.json()["detail"]


def test_manifiesto_invalido(authed):
    p, clip = _promo(authed)
    malo = dict(MANIFIESTO, eventos=[{"sonido": "trueno", "t": 1, "db": -12}])
    r = authed.put(f"/api/projects/{p['id']}/clips/{clip['id']}/audio", json=malo)
    assert r.status_code == 422
    assert "trueno" in r.json()["detail"]


def test_mezclar_sin_manifiesto_y_sin_render(authed):
    p, clip = _promo(authed)
    r = authed.post(f"/api/projects/{p['id']}/clips/{clip['id']}/audio/mezclar")
    assert r.status_code == 422  # todavia no hay nada que mezclar

    authed.put(f"/api/projects/{p['id']}/clips/{clip['id']}/audio", json=MANIFIESTO)
    r = authed.post(f"/api/projects/{p['id']}/clips/{clip['id']}/audio/mezclar")
    assert r.status_code == 409  # hay manifiesto, pero no hay video
    assert "renderízalo" in r.json()["detail"]


def _fake_render(db, cfg, pid, clip, job_id="a1b2c3d4e5f60718"):
    """Un render 'done' con mp4 falso, como en test_projects_export."""
    media = cfg.render_jobs_dir / job_id / "media" / "videos" / "scene" / "1920p60"
    media.mkdir(parents=True, exist_ok=True)
    video = media / "Promo.mp4"
    video.write_bytes(b"fake-mp4-data")
    ahora = time.time()
    db.insert_job({"id": job_id, "scene": "Promo", "quality": "qh", "timeout": 600,
                   "status": "queued", "script": VALID_SCRIPT, "created_at": ahora,
                   "project_id": pid, "clip_id": clip["id"], "content_hash": None,
                   "formato": "vertical"})
    db.update_job(job_id, status="done", started_at=ahora, finished_at=ahora,
                  video_path=str(video), size_bytes=13)
    project = db.get_project(pid)
    db.update_clip(clip["id"], job_id=job_id,
                   rendered_hash=content_hash(project["style_block"],
                                              VALID_SCRIPT, "Promo"))
    return job_id, video


def test_con_render_pide_voz_pero_no_hay_vertex(authed):
    from app.main import cfg, db
    p, clip = _promo(authed)
    authed.put(f"/api/projects/{p['id']}/clips/{clip['id']}/audio", json=MANIFIESTO)
    _fake_render(db, cfg, p["id"], clip)

    d = authed.get(f"/api/projects/{p['id']}/clips/{clip['id']}/audio").json()
    assert d["estado"]["estado"] == "sin_mezclar"
    assert d["voz_disponible"] is False  # sin gcp-key.json en el tmp de tests

    # El manifiesto lleva una frase: sin Vertex se dice claro, no se mezcla
    # a medias ni se descarta la voz en silencio.
    r = authed.post(f"/api/projects/{p['id']}/clips/{clip['id']}/audio/mezclar")
    assert r.status_code == 503
    assert "Vertex" in r.json()["detail"]


def test_estado_al_dia_y_desactualizado(authed):
    from app.main import cfg, db
    from app import audio_promo as ap
    p, clip = _promo(authed)
    authed.put(f"/api/projects/{p['id']}/clips/{clip['id']}/audio", json=MANIFIESTO)
    job_id, _video = _fake_render(db, cfg, p["id"], clip)

    # Se simula una mezcla ya hecha (el runner no corre en tests).
    m = json.loads(db.get_clip(clip["id"])["audio_json"])
    salida = cfg.render_jobs_dir / job_id / "promo_audio.mp4"
    salida.write_bytes(b"fake-mp4-con-audio")
    db.update_job(job_id, audio_path=str(salida),
                  audio_hash=ap.hash_mezcla(m, job_id))
    d = authed.get(f"/api/projects/{p['id']}/clips/{clip['id']}/audio").json()
    assert d["estado"]["estado"] == "al_dia"

    # El video que sirve la app pasa a ser el sonorizado.
    r = authed.get(f"/api/jobs/{job_id}/video")
    assert r.status_code == 200 and r.content == b"fake-mp4-con-audio"

    # Cambiar el manifiesto lo desactualiza (sin tocar el render).
    authed.put(f"/api/projects/{p['id']}/clips/{clip['id']}/audio",
               json=dict(MANIFIESTO, pico_db=-6.0))
    d = authed.get(f"/api/projects/{p['id']}/clips/{clip['id']}/audio").json()
    assert d["estado"]["estado"] == "desactualizado"


def test_avisos_viajan_con_la_duracion_real(authed, monkeypatch):
    from app.main import cfg, db
    p, clip = _promo(authed)
    # Una frase que empieza a 10.5 s en un video de 12 s: el bucle chasquea.
    authed.put(f"/api/projects/{p['id']}/clips/{clip['id']}/audio",
               json=dict(MANIFIESTO,
                         secciones=[{"t_inicio": 10.5, "texto": "Se pega al final"}]))
    _fake_render(db, cfg, p["id"], clip)
    monkeypatch.setattr("app.audio_api.duracion_mp4", lambda _p: 12.0)
    d = authed.get(f"/api/projects/{p['id']}/clips/{clip['id']}/audio").json()
    assert d["duracion_video"] == 12.0
    assert any("chasquea" in a for a in d["avisos"])
