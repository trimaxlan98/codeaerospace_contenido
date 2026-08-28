"""Pruebas de studio/tools/subir_promo.py: meter un promo del repo
(promo.json + style_block + escena) en la base del Studio.

Sin HTTP: se ejercitan cargar_promo() y sincronizar() directo contra una
Database temporal, que es exactamente lo que hace el CLI.
"""

import json
import sys
from pathlib import Path

import pytest

from app.db import Database
from app.projects import ProjectService, content_hash

TOOLS = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(TOOLS))

import subir_promo  # noqa: E402

STYLE = "from manim import *\n\nC_CIFRA = '#22d3ee'\n"
ESCENA = (
    "class Promo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle(color=C_CIFRA)))\n"
)
AUDIO = {"pico_db": -3.0, "fade_in": 0.35,
         "eventos": [["pulso", 5.3, -13], ["nebulosa", 0.1, -14]]}
VOZ = {"voz": "Charon", "secciones": [{"t_inicio": 0.8, "texto": "Una idea."}]}


def _promo_dir(tmp_path, **extra):
    d = tmp_path / "promo-demo"
    d.mkdir(parents=True)
    (d / "style_block.py").write_text(STYLE)
    (d / "escena.py").write_text(ESCENA)
    manifiesto = {"name": "El efecto mariposa", "curso": "Caos",
                  "description": "Promo de prueba", "scene": "Promo",
                  "file": "escena.py", "style_block": "style_block.py",
                  "formatos": ["vertical", "horizontal"],
                  "audio": AUDIO, "voz": VOZ}
    manifiesto.update(extra)
    (d / "promo.json").write_text(json.dumps(manifiesto))
    return d


def _service(tmp_path):
    db = Database(tmp_path / "db" / "manimstudio.db")
    return db, ProjectService(db)


def test_carga_el_promo_con_su_audio(tmp_path):
    promo = subir_promo.cargar_promo(_promo_dir(tmp_path))
    # El nombre lleva prefijo: el indice agrupa por lo que hay antes del "·".
    assert promo["name"] == "Promo · El efecto mariposa"
    assert promo["formato"] == "vertical" and promo["quality"] == "qh"
    # El curso al que pertenece entra en la descripcion.
    assert promo["description"].startswith("[Caos]")
    # Los eventos llegan ordenados por tiempo (el manifiesto los traia al reves).
    assert [e[0] for e in promo["audio"]["audio"]["eventos"]] == ["nebulosa", "pulso"]
    assert promo["audio"]["voz"]["secciones"][0]["texto"] == "Una idea."


def test_rechaza_lo_que_no_podria_renderizar_ni_mezclar(tmp_path):
    d = _promo_dir(tmp_path, scene="NoExiste")
    with pytest.raises(SystemExit):
        subir_promo.cargar_promo(d)

    d2 = _promo_dir(tmp_path / "otro",
                    audio={"eventos": [["trueno", 1.0, -12]]})
    with pytest.raises(SystemExit):
        subir_promo.cargar_promo(d2)

    d3 = _promo_dir(tmp_path / "tercero", formatos=["panoramico"])
    with pytest.raises(SystemExit):
        subir_promo.cargar_promo(d3)


def test_crea_proyecto_de_un_clip_y_es_idempotente(tmp_path):
    d = _promo_dir(tmp_path)
    db, service = _service(tmp_path)
    promo = subir_promo.cargar_promo(d)

    reporte = subir_promo.sincronizar(service, db, promo, dry_run=False)
    assert any("promo nuevo" in r for r in reporte)

    proyecto = db.list_projects()[0]
    assert proyecto["tipo"] == "promo" and proyecto["formato"] == "vertical"
    clips = db.list_clips(proyecto["id"])
    assert len(clips) == 1 and clips[0]["scene"] == "Promo"
    guardado = json.loads(clips[0]["audio_json"])
    assert guardado["audio"]["eventos"][0][0] == "nebulosa"

    # Segunda pasada: ni un cambio.
    reporte = subir_promo.sincronizar(service, db, promo, dry_run=False)
    assert any("sin cambios" in r for r in reporte)
    assert any("al dia" in r for r in reporte)
    assert len(db.list_projects()) == 1


def test_dry_run_no_escribe(tmp_path):
    db, service = _service(tmp_path)
    promo = subir_promo.cargar_promo(_promo_dir(tmp_path))
    subir_promo.sincronizar(service, db, promo, dry_run=True)
    assert db.list_projects() == []


def test_un_script_nuevo_deja_el_render_stale(tmp_path):
    d = _promo_dir(tmp_path)
    db, service = _service(tmp_path)
    promo = subir_promo.cargar_promo(d)
    subir_promo.sincronizar(service, db, promo, dry_run=False)
    proyecto = db.list_projects()[0]
    clip = db.list_clips(proyecto["id"])[0]
    db.update_clip(clip["id"], job_id="job1",
                   rendered_hash=content_hash(STYLE, ESCENA, "Promo"))

    (d / "escena.py").write_text(ESCENA + "        self.wait(1)\n")
    promo2 = subir_promo.cargar_promo(d)
    reporte = subir_promo.sincronizar(service, db, promo2, dry_run=False)
    assert any("STALE" in r for r in reporte)


def test_cambiar_solo_el_audio_avisa_de_la_mezcla_vieja(tmp_path):
    d = _promo_dir(tmp_path)
    db, service = _service(tmp_path)
    subir_promo.sincronizar(service, db, subir_promo.cargar_promo(d),
                            dry_run=False)
    proyecto = db.list_projects()[0]
    clip = db.list_clips(proyecto["id"])[0]
    db.update_clip(clip["id"], job_id="job1")

    (d / "promo.json").write_text(json.dumps({
        **json.loads((d / "promo.json").read_text()),
        "audio": {**AUDIO, "eventos": [["pulso", 2.0, -13]]}}))
    reporte = subir_promo.sincronizar(service, db, subir_promo.cargar_promo(d),
                                      dry_run=False)
    assert any("manifiesto de audio" in r for r in reporte)
    assert any("vuelve a mezclar" in r for r in reporte)
    guardado = json.loads(db.get_clip(clip["id"])["audio_json"])
    assert guardado["audio"]["eventos"] == [["pulso", 2.0, -13.0]]
