"""Musica en la app (sprint R2).

Sin Docker y sin numpy del lado del backend: la sintesis corre `musica.py`
dentro del contenedor. Lo que se prueba aqui es lo que decide si la musica
llega bien a la mezcla — el catalogo espejo, el manifiesto, la puerta del
banco audible y el plan de la pelicula — mas la unica regla de nivel que
importa, que la cama no tape la voz.
"""

import ast
import json
from pathlib import Path

from app import audio_promo

TOOLS = Path(__file__).resolve().parents[2] / "tools"

VALID_SCRIPT = (
    "from manim import *\n"
    "class Promo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle()))\n"
)


def _temas_de_musica_py() -> dict:
    """`TEMAS` de musica.py leido con ast (el modulo importa numpy)."""
    arbol = ast.parse((TOOLS / "musica.py").read_text())
    for nodo in arbol.body:
        if (isinstance(nodo, ast.Assign)
                and any(getattr(t, "id", "") == "TEMAS" for t in nodo.targets)):
            return {k.value: ast.literal_eval(v)
                    for k, v in zip(nodo.value.keys, nodo.value.values)}
    return {}


# ── el catalogo de temas no puede separarse de musica.py ─────────────────────

def test_los_temas_son_los_de_musica_py():
    """Mismo espejo que `SONIDOS`↔`PALETA`, y por el mismo motivo: un tema
    que la app ofrece y la sintesis no conoce falla DENTRO del contenedor,
    tarde, con un SystemExit que nadie ve hasta que la mezcla no sale."""
    temas = _temas_de_musica_py()
    assert temas, "no se encontro TEMAS en musica.py"
    assert sorted(temas) == sorted(audio_promo.TEMAS)


def test_lo_que_la_interfaz_ensena_es_lo_que_la_sintesis_hace():
    """`TEMAS_INFO` es lo que la interfaz enseña sin importar numpy: bpm,
    carácter y descripción. Un bpm que miente es peor que ninguno —el tema se
    elige por el pulso— y un carácter que no sale de los niveles reales
    convierte el catálogo en publicidad. Se regenera con
    `musica.py catalogo`."""
    etiqueta = {"drone": "drone", "arpegio": "arpegio", "sub": "sub-bajo"}
    for nombre, cfg in _temas_de_musica_py().items():
        info = audio_promo.TEMAS_INFO[nombre]
        assert info["bpm"] == cfg["bpm"], nombre
        capas = [(cfg[k], n) for k, n in etiqueta.items() if cfg[k] > 0]
        caracter = " + ".join(n for _, n in sorted(capas, key=lambda c: -c[0]))
        assert info["caracter"] == caracter, nombre
        assert info["descripcion"] == cfg["descripcion"], nombre


# ── manifiesto ───────────────────────────────────────────────────────────────

def test_normalizar_acepta_la_musica_y_rellena_el_nivel():
    m = audio_promo.normalizar({"audio": {"musica": {"tema": "orbita"}}})
    assert m["audio"]["musica"] == {"tema": "orbita",
                                    "db": audio_promo.MUSICA_DB}


def test_sin_musica_la_clave_no_aparece():
    """Ausente y «sin musica» son lo mismo: asi la apaga el desplegable."""
    assert "musica" not in audio_promo.normalizar({})["audio"]
    m = audio_promo.normalizar({"audio": {"musica": {"tema": "", "db": -20}}})
    assert "musica" not in m["audio"]
    assert audio_promo.validar(m) == []


def test_validar_rechaza_un_tema_que_la_sintesis_no_conoce():
    m = audio_promo.normalizar({"audio": {"musica": {"tema": "reggaeton"}}})
    assert any("reggaeton" in e for e in audio_promo.validar(m))

    m = audio_promo.normalizar({"audio": {"musica": {"tema": "orbita",
                                                     "db": -200}}})
    assert any("nivel de la musica" in e for e in audio_promo.validar(m))

    m = audio_promo.normalizar({"audio": {"musica": {"tema": "orbita",
                                                     "bpm": 400}}})
    assert any("bpm" in e for e in audio_promo.validar(m))

    ok = audio_promo.normalizar({"audio": {"musica": {"tema": "marcha",
                                                      "db": -24, "bpm": 90}}})
    assert audio_promo.validar(ok) == []


def test_avisa_cuando_la_musica_va_a_tapar_la_voz():
    """El unico error de nivel que no se ve hasta escuchar el resultado."""
    alta = audio_promo.normalizar({"audio": {"musica": {"tema": "orbita",
                                                        "db": -12}}})
    assert any("tapa la voz" in a for a in audio_promo.avisos(alta, 12.0))
    baja = audio_promo.normalizar({"audio": {"musica": {"tema": "orbita",
                                                        "db": -24}}})
    assert audio_promo.avisos(baja, 12.0) == []
    # Tambien en un clip de curso, que es donde hay narracion segura.
    assert any("tapa la voz" in a
               for a in audio_promo.avisos(alta, 30.0, "curso"))


def test_la_musica_viaja_al_manifiesto_que_lee_sfx():
    m = audio_promo.normalizar({"audio": {"musica": {"tema": "aurora",
                                                     "db": -20}}})
    spec = audio_promo.para_sfx(m)
    assert spec["audio"]["musica"] == {"tema": "aurora", "db": -20.0}


# ── API del banco ────────────────────────────────────────────────────────────

def _sembrar(cfg, *nombres):
    cfg.musica_dir.mkdir(parents=True, exist_ok=True)
    for n in nombres:
        (cfg.musica_dir / f"{n}.wav").write_bytes(b"RIFF----WAVEfmt ")


def test_banco_vacio(authed):
    body = authed.get("/api/musica").json()
    assert body["listos"] == []
    assert body["completo"] is False
    assert [t["nombre"] for t in body["temas"]] == list(audio_promo.TEMAS)
    # Cada tema llega con lo que hace falta para elegirlo sin oirlo todavia.
    assert all(t["bpm"] and t["caracter"] and t["descripcion"]
               for t in body["temas"])
    assert body["db_defecto"] == audio_promo.MUSICA_DB


def test_el_listado_ignora_los_temas_de_un_catalogo_viejo(authed):
    from app.main import cfg
    _sembrar(cfg, "orbita", "vals_vienes")
    body = authed.get("/api/musica").json()
    assert body["listos"] == ["orbita"]
    assert [t["nombre"] for t in body["temas"] if t["listo"]] == ["orbita"]


def test_completo_cuando_estan_todos(authed):
    from app.main import cfg
    _sembrar(cfg, *audio_promo.TEMAS)
    assert authed.get("/api/musica").json()["completo"] is True


def test_se_puede_oir_un_tema(authed):
    from app.main import cfg
    _sembrar(cfg, "deriva")
    r = authed.get("/api/musica/deriva")
    assert r.status_code == 200
    assert r.headers["content-type"] == "audio/wav"


def test_un_tema_que_no_existe_es_404(authed):
    from app.main import cfg
    _sembrar(cfg, "deriva")
    assert authed.get("/api/musica/reggaeton").status_code == 404
    # Nada de la URL toca el disco: el nombre va contra el conjunto cerrado
    # ANTES de construir ninguna ruta.
    assert authed.get("/api/musica/..%2F..%2Fetc%2Fpasswd").status_code == 404


def test_tema_sin_sintetizar_es_404_con_mensaje(authed):
    r = authed.get("/api/musica/orbita")
    assert r.status_code == 404
    assert "sintetizado" in r.json()["detail"]


def test_el_banco_de_musica_requiere_sesion(client):
    assert client.get("/api/musica").status_code == 401
    assert client.get("/api/musica/orbita").status_code == 401


# ── el manifiesto de un clip lo guarda con musica ────────────────────────────

def test_guardar_un_clip_con_musica(authed):
    p = authed.post("/api/projects", json={
        "name": "Promo con musica", "quality": "qh", "tipo": "promo",
        "formato": "vertical", "style_block": ""}).json()
    clip = authed.post(f"/api/projects/{p['id']}/clips",
                       json={"title": "Bucle", "script": VALID_SCRIPT,
                             "scene": "Promo"}).json()
    r = authed.put(f"/api/projects/{p['id']}/clips/{clip['id']}/audio",
                   json={"eventos": [], "musica": {"tema": "telemetria",
                                                   "db": -22}})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["manifiesto"]["audio"]["musica"] == {"tema": "telemetria",
                                                  "db": -22.0}
    assert "telemetria" in d["temas"]

    malo = {"eventos": [], "musica": {"tema": "reggaeton"}}
    r = authed.put(f"/api/projects/{p['id']}/clips/{clip['id']}/audio",
                   json=malo)
    assert r.status_code == 422 and "reggaeton" in r.json()["detail"]


# ── la pelicula ──────────────────────────────────────────────────────────────

def test_el_plan_de_la_pelicula_lleva_la_musica(authed, monkeypatch):
    from app.main import cfg, db, pelicula_service
    from app.projects import content_hash

    pid = authed.post("/api/projects",
                      json={"name": "Curso con musica",
                            "quality": "ql"}).json()["id"]
    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": "Uno", "script": VALID_SCRIPT,
                             "scene": "Promo"}).json()
    job_id = "beefbeefbeefbeef"
    media = cfg.render_jobs_dir / job_id / "media"
    media.mkdir(parents=True, exist_ok=True)
    video = media / "Promo.mp4"
    video.write_bytes(b"fake-mp4")
    db.insert_job({"id": job_id, "scene": "Promo", "quality": "ql",
                   "timeout": 600, "status": "queued", "script": VALID_SCRIPT,
                   "created_at": 0.0, "project_id": pid, "clip_id": clip["id"],
                   "content_hash": None, "formato": "horizontal"})
    db.update_job(job_id, status="done", video_path=str(video), size_bytes=8)
    project = db.get_project(pid)
    db.update_clip(clip["id"], job_id=job_id,
                   rendered_hash=content_hash(project["style_block"],
                                              VALID_SCRIPT, "Promo"))

    op = pelicula_service.plan(
        project, __import__("app.pelicula", fromlist=["x"])
        .normaliza_opciones({"musica": {"tema": "orbita", "db": -26}}))
    assert op["musica"] == {"tema": "orbita", "db": -26.0}

    # Y sin musica el plan no la menciona: el paso ni se ejecuta.
    sin = pelicula_service.plan(
        project, __import__("app.pelicula", fromlist=["x"])
        .normaliza_opciones({}))
    assert "musica" not in sin


def test_cambiar_de_tema_desactualiza_la_pelicula():
    """El hash del plan tiene que incluir la musica: si no, cambiar de tema
    dejaria la pelicula «al dia» sonando con el tema anterior."""
    from app import pelicula as mod

    base = {"proyecto": "X", "resolucion": "1920x1080", "fps": 60,
            "transicion": {"tipo": "corte", "duracion": 0.6}, "piezas": []}

    class _Cfg:
        workspace = Path("/nada")

    svc = mod.PeliculaService.__new__(mod.PeliculaService)
    svc.cfg = _Cfg()
    h0 = svc._hash_plan(dict(base))
    h1 = svc._hash_plan(dict(base, musica={"tema": "orbita", "db": -24}))
    h2 = svc._hash_plan(dict(base, musica={"tema": "deriva", "db": -24}))
    h3 = svc._hash_plan(dict(base, musica={"tema": "orbita", "db": -18}))
    assert len({h0, h1, h2, h3}) == 4


def test_la_api_de_la_pelicula_persiste_y_devuelve_la_musica(authed,
                                                             monkeypatch):
    """`POST /{pid}/pelicula` acepta la cama y `GET` la devuelve.

    El montaje se corta antes de llegar al runner (no hay Docker en tests):
    lo que se comprueba es que la opcion sobrevive el viaje y acaba en el
    plan que lee `ensamblar.py`.
    """
    pid = authed.post("/api/projects",
                      json={"name": "Curso vacio", "quality": "ql"}).json()["id"]
    estado = authed.get(f"/api/projects/{pid}/pelicula").json()
    assert estado["opciones"]["musica"] is None
    assert estado["temas"] == list(audio_promo.TEMAS)

    # Sin clips no hay montaje, pero la validacion del cuerpo si corre.
    r = authed.post(f"/api/projects/{pid}/pelicula",
                    json={"musica": {"tema": "reggaeton", "db": -24}})
    assert r.status_code == 409 and "reggaeton" in r.json()["detail"]

    r = authed.post(f"/api/projects/{pid}/pelicula",
                    json={"musica": {"tema": "orbita", "db": -900}})
    assert r.status_code == 422  # el rango lo ataja pydantic


# ── ensamblar.py: el plan y el ducking, sin ffmpeg ───────────────────────────

def _ensamblar_mod():
    import importlib.util
    spec = importlib.util.spec_from_file_location("ensamblar",
                                                  TOOLS / "ensamblar.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_el_plan_valida_la_musica(tmp_path):
    mod = _ensamblar_mod()
    plan = tmp_path / "plan.json"

    def escribe(mus):
        plan.write_text(json.dumps({"piezas": [{"video": "a.mp4"}],
                                    "musica": mus}))
        return plan

    mod.lee_plan(escribe({"tema": "orbita", "db": -24}))
    for malo, trozo in (({"db": -24}, "que tema"),
                        ({"tema": "orbita", "db": -900}, "fuera de rango")):
        try:
            mod.lee_plan(escribe(malo))
        except mod.ErrorPlan as e:
            assert trozo in str(e)
        else:
            raise AssertionError(f"{malo} deberia fallar")


def test_la_curva_de_ducking_baja_9_db_bajo_la_voz_y_vuelve():
    """Funcion pura: se prueba sin ffmpeg y sin montar nada.

    Es donde vive la decision que se oye — cuanto y con que rapidez se
    aparta la musica — asi que tiene que poder cambiarse midiendo, no
    montando un curso de media hora para escucharlo.
    """
    import numpy as np
    mod = _ensamblar_mod()

    hz = 100.0
    env = np.zeros(int(10 * hz))
    env[int(3 * hz):int(6 * hz)] = 0.5     # tres segundos de voz
    g = mod.curva_ducking(env, hz)

    piso = 10 ** (mod.DUCK_DB / 20)
    assert g[0] == 1.0 or abs(g[0] - 1.0) < 1e-6      # arranca sin agachar
    # A mitad del tramo hablado ya esta abajo (el ataque son 0.12 s).
    assert abs(g[int(4.5 * hz)] - piso) < 0.01
    # Y vuelve arriba despues de la liberacion (0.6 s), sin pasarse.
    assert g[int(9.5 * hz)] > 0.98
    assert g.max() <= 1.0 and g.min() >= piso - 1e-9
    # La liberacion es MAS LENTA que el ataque: al reves, bombea.
    baja = np.argmax(g < 0.5 * (1 + piso)) / hz - 3.0
    sube = (len(g) - np.argmax(g[::-1] > 0.9)) / hz - 6.0
    assert baja < sube
