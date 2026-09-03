"""La pelicula de un curso (sprint E1): plan, estado y API.

Sin Docker ni ffmpeg: el montaje real corre `studio/tools/ensamblar.py` dentro
del contenedor. Lo que se prueba aqui es lo que decide si la pelicula sale
bien — el plan que se le pasa al ensamblador, el hash que la caduca, y la
aritmetica de los empalmes, que es donde ya se rompio una vez (un offset
calculado sobre la suma cruda de duraciones deja el ultimo corte fuera del
video y ffmpeg lo pega sin fundir, sin fallar).
"""

import importlib.util
import json
import time
from pathlib import Path

import pytest

from app.projects import content_hash

VALID_SCRIPT = (
    "from manim import *\n"
    "class Demo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle()))\n"
)

TOOLS = Path(__file__).resolve().parents[2] / "tools"


def _peli():
    """`app.pelicula` reimportado.

    El fixture `client` borra los modulos `app*` y los vuelve a importar por
    cada test (ver conftest): una referencia de cabecera apunta a la clase
    ANTERIOR, y `pytest.raises(PeliculaError)` no la reconoce. Por eso el
    modulo se pide dentro de cada test.
    """
    from app import pelicula
    return pelicula


def _ensamblar_mod():
    """`ensamblar.py` importado por ruta: es una herramienta, no un modulo del
    paquete, y solo usa la libreria estandar (por eso se puede importar aqui,
    a diferencia de sfx.py, que necesita numpy)."""
    spec = importlib.util.spec_from_file_location("ensamblar", TOOLS / "ensamblar.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── las dos listas de transiciones no pueden separarse ───────────────────────

def test_las_transiciones_de_la_api_son_las_del_ensamblador():
    """La API ofrece un desplegable; el ensamblador es quien las sabe hacer.
    Si una crece sin la otra, el usuario elige un empalme que revienta en el
    contenedor (o deja de ver uno que ya funciona)."""
    pel = _peli()
    mod = _ensamblar_mod()
    assert sorted(pel.TRANSICIONES) == sorted(("corte",) + tuple(mod.TRANSICIONES))


# ── aritmetica del empalme ───────────────────────────────────────────────────

def test_el_offset_del_xfade_se_calcula_sobre_lo_acumulado():
    mod = _ensamblar_mod()
    filtro = mod.filtro_xfade([3.0, 2.5, 4.0], "fade", 0.5)
    # Primer empalme: 3.0 - 0.5. Segundo: (3.0 + 2.5 - 0.5) - 0.5 = 4.5.
    # Con la suma cruda saldria 5.0 y el fundido caeria fuera del clip.
    assert "offset=2.500" in filtro
    assert "offset=4.500" in filtro
    assert filtro.count("acrossfade") == 2
    assert filtro.endswith("[aout]")


def test_una_sola_pieza_no_admite_transicion():
    mod = _ensamblar_mod()
    with pytest.raises(mod.ErrorPlan):
        mod.filtro_xfade([3.0], "fade", 0.5)


def test_la_voz_se_acelera_solo_lo_justo():
    mod = _ensamblar_mod()
    assert mod.ratio_atempo(10.0, 10.0) == 1.0        # cabe
    assert mod.ratio_atempo(10.02, 10.0) == 1.0       # holgura: no se toca
    assert mod.ratio_atempo(11.0, 10.0) == pytest.approx(1.1)
    assert mod.ratio_atempo(30.0, 10.0) == mod.ATEMPO_MAX  # tope, no 3x
    assert mod.ratio_atempo(5.0, 0.0) == 1.0          # video sin duracion


def test_la_pieza_sin_voz_igual_lleva_pista_de_audio():
    """Un concat que mezcla clips con y sin audio sale roto y no falla: la
    pelicula se queda muda a partir del primer clip sin pista."""
    mod = _ensamblar_mod()
    argv = mod.args_pieza("a.mp4", None, "out.mp4")
    assert "anullsrc" in " ".join(argv)
    assert "-c:v" in argv and argv[argv.index("-c:v") + 1] == "copy"


def test_la_voz_se_MEZCLA_sobre_la_cama_de_sonido():
    """Sprint E3: un clip de curso puede llegar con su cama ya mezclada.

    Mapear solo la voz (`-map 1:a`) tiraba la cama por la borda sin que nada
    fallara: la pelicula salia con narracion y sin los efectos que se habian
    elegido clip a clip.

    Sprint R2: la suma dejo de ser `amix`. `amix=...:normalize=0` llego en
    ffmpeg 4.4 y la imagen trae 4.3.9 (Debian 11), asi que ese filtro fallaba
    con «Option 'normalize' not found» — y sin la opcion, amix divide cada
    entrada por el numero de entradas y la pieza entera bajaria 6 dB.
    """
    mod = _ensamblar_mod()
    argv = mod.args_pieza("a.mp4", "v.wav", "out.mp4", ratio=1.0, cama=True)
    filtro = argv[argv.index("-filter_complex") + 1]
    assert "amerge=inputs=2" in filtro and "pan=mono|c0=c0+c1" in filtro
    assert "amix" not in filtro                      # ver el docstring
    assert "[0:a]" in filtro and "[1:a]" in filtro   # cama Y voz
    assert argv[argv.index("-c:v") + 1] == "copy"


def test_la_cama_sola_se_recodifica_al_formato_comun():
    """Sin re-codificar, el `concat -c copy` puede encontrarse dos audios de
    formatos distintos (el de sfx.py y el del silencio) y salir roto."""
    mod = _ensamblar_mod()
    argv = mod.args_pieza("a.mp4", None, "out.mp4", cama=True)
    assert "anullsrc" not in " ".join(argv)
    assert argv[argv.index("-ar") + 1] == "24000"
    assert argv[argv.index("-c:v") + 1] == "copy"


def test_la_pieza_con_voz_copia_el_video():
    mod = _ensamblar_mod()
    argv = mod.args_pieza("a.mp4", "v.wav", "out.mp4", ratio=1.1)
    assert "atempo=1.1000,apad" in argv
    assert argv[argv.index("-c:v") + 1] == "copy"     # nunca se recodifica aqui
    assert "-shortest" in argv


# ── opciones ─────────────────────────────────────────────────────────────────

def test_opciones_por_defecto_no_recodifican():
    pel = _peli()
    op = pel.normaliza_opciones(None)
    assert op["transicion"] == "corte"
    assert op["narracion"] is True


def test_transicion_desconocida_y_duracion_fuera_de_rango():
    pel = _peli()
    with pytest.raises(pel.PeliculaError):
        pel.normaliza_opciones({"transicion": "espiral"})
    with pytest.raises(pel.PeliculaError):
        pel.normaliza_opciones({"transicion": "fundido", "duracion_transicion": 9})


# ── plan y estado ────────────────────────────────────────────────────────────

def _create_project(authed, **overrides):
    body = {"name": "Curso Pelicula", "description": "d", "quality": "ql",
            "style_block": ""}
    body.update(overrides)
    r = authed.post("/api/projects", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def _rendered_clip(authed, db, cfg, pid, title, job_id, resolution="854x480"):
    clip = authed.post(f"/api/projects/{pid}/clips",
                       json={"title": title, "script": VALID_SCRIPT,
                             "scene": "Demo"}).json()
    job_dir = cfg.render_jobs_dir / job_id / "media" / "videos" / "x" / "y"
    job_dir.mkdir(parents=True, exist_ok=True)
    video = job_dir / "Demo.mp4"
    video.write_bytes(b"fake-mp4")
    now = time.time()
    db.insert_job({"id": job_id, "scene": "Demo", "quality": "ql", "timeout": 120,
                   "status": "queued", "script": VALID_SCRIPT, "created_at": now,
                   "project_id": pid, "clip_id": clip["id"], "content_hash": None})
    db.update_job(job_id, status="done", started_at=now, finished_at=now,
                  video_path=str(video), size_bytes=10, resolution=resolution)
    project = db.get_project(pid)
    db.update_clip(clip["id"], job_id=job_id,
                   rendered_hash=content_hash(project["style_block"],
                                              VALID_SCRIPT, "Demo"))
    return clip


def test_plan_ordena_las_piezas_y_lista_lo_que_falta(authed):
    pel = _peli()
    from app.main import cfg, db, pelicula_service

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    _rendered_clip(authed, db, cfg, pid, "Dos", "cccc00002222dddd")
    authed.post(f"/api/projects/{pid}/clips",
                json={"title": "Sin render", "script": VALID_SCRIPT})

    project = db.get_project(pid)
    plan = pelicula_service.plan(project, pel.normaliza_opciones(None))
    assert [p["titulo"] for p in plan["piezas"]] == ["Uno", "Dos"]
    assert plan["faltan"] == ["Sin render"]
    # Las rutas son relativas al workspace: dentro del contenedor son /workspace/...
    assert all(not p["video"].startswith("/") for p in plan["piezas"])
    assert plan["raiz"] == "/workspace"


def test_el_plan_usa_el_video_que_la_app_sirve(authed):
    """Si el clip tiene su cama mezclada al lado del mudo, la pelicula usa
    ESA: montar con el mudo daria un curso que suena distinto a sus propios
    clips en la Biblioteca."""
    pel = _peli()
    from app.main import cfg, db, pelicula_service

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    sonoro = cfg.render_jobs_dir / "aaaa00001111bbbb" / "promo_audio.mp4"
    sonoro.write_bytes(b"con-cama")
    db.update_job("aaaa00001111bbbb", audio_path=str(sonoro))

    plan = pelicula_service.plan(db.get_project(pid), pel.normaliza_opciones(None))
    assert plan["piezas"][0]["video"].endswith("promo_audio.mp4")


def test_el_plan_engancha_la_narracion_que_exista(authed):
    pel = _peli()
    from app.main import cfg, db, narracion_service, pelicula_service

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    _rendered_clip(authed, db, cfg, pid, "Dos", "cccc00002222dddd")
    project = db.get_project(pid)

    destino = narracion_service.destino(project)
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "01-uno.wav").write_bytes(b"RIFF....")   # solo el primero

    plan = pelicula_service.plan(project, pel.normaliza_opciones(None))
    assert plan["piezas"][0]["voz"].endswith("01-uno.wav")
    assert "voz" not in plan["piezas"][1]

    # Con narracion apagada, la pelicula sale muda aunque el wav exista.
    muda = pelicula_service.plan(
        project, pel.normaliza_opciones({"narracion": False}))
    assert all("voz" not in p for p in muda["piezas"])


def test_la_marca_de_otro_tamano_no_se_pega(authed):
    pel = _peli()
    from app.main import cfg, db, pelicula_service

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    # Un intro vertical en un curso horizontal: el concat -c copy no pega dos
    # tamanos, y con xfade el resultado sale deformado.
    intro_pid = _create_project(authed, name="Marca")["id"]
    intro = _rendered_clip(authed, db, cfg, intro_pid, "Intro",
                           "eeee00003333ffff", resolution="1080x1920")
    project = db.get_project(pid)
    op = pel.normaliza_opciones({"intro_job_id": intro["job_id"]
                                  or "eeee00003333ffff"})
    with pytest.raises(pel.PeliculaError, match="1080x1920"):
        pelicula_service.plan(project, op)


def test_el_hash_caduca_la_pelicula_al_re_renderizar(authed):
    pel = _peli()
    from app.main import cfg, db, pelicula_service

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    project = db.get_project(pid)
    op = pel.normaliza_opciones(None)

    antes = pelicula_service._hash_plan(pelicula_service.plan(project, op))
    # Un re-render deja la MISMA ruta con otro contenido: por eso el hash mira
    # el mtime del archivo y no solo su nombre.
    video = Path(db.get_job("aaaa00001111bbbb")["video_path"])
    video.write_bytes(b"otro-render-distinto")
    despues = pelicula_service._hash_plan(pelicula_service.plan(project, op))
    assert antes != despues

    # Y cambiar el empalme tambien la caduca.
    otra = pelicula_service._hash_plan(
        pelicula_service.plan(project, pel.normaliza_opciones(
            {"transicion": "fundido"})))
    assert otra != despues


# ── verificacion de la pelicula ──────────────────────────────────────────────

def test_una_pelicula_sana_no_tiene_nada_que_decir():
    mod = _ensamblar_mod()
    assert mod.diagnostico(8.67, 8.5, [], "1920x1080", "1920x1080") == ([], [])


def test_la_duracion_que_no_cuadra_delata_material_perdido():
    """Si un offset de xfade deja la ultima pieza fuera, el video sale bien
    formado y mas corto. Es el unico sintoma."""
    mod = _ensamblar_mod()
    p, _ = mod.diagnostico(6.0, 8.5, [], "", "")
    assert len(p) == 1 and "-2.50 s" in p[0]


def test_la_tolerancia_absorbe_el_cuadre_a_frames():
    """El re-encode cuadra a frames enteros y a los fps del proyecto: exigir
    la duracion exacta marcaria como rota una pelicula sana."""
    mod = _ensamblar_mod()
    assert 0 < mod.TOLERANCIA_S <= 1.0
    assert mod.diagnostico(
        8.5 + mod.TOLERANCIA_S - 0.01, 8.5, [], "", "")[0] == []
    assert mod.diagnostico(
        8.5 + mod.TOLERANCIA_S + 0.01, 8.5, [], "", "")[0] != []


def test_las_piezas_que_perdieron_su_sonido_se_nombran():
    mod = _ensamblar_mod()
    p, _ = mod.diagnostico(8.5, 8.5, ["Uno", "Dos"], "", "")
    assert "2 piezas" in p[0] and "Uno, Dos" in p[0]
    # Con muchas, se nombran las primeras y se corta: el aviso es para leerlo.
    largo, _ = mod.diagnostico(8.5, 8.5, [f"C{i}" for i in range(9)], "", "")
    assert "…" in largo[0]


def test_solo_se_acusa_a_las_piezas_que_TRAIAN_sonido(tmp_path):
    """Un curso sin narrar es mudo A PROPOSITO. Acusarlo cada vez convertiria
    la medicion en ruido que se aprende a ignorar."""
    mod = _ensamblar_mod()
    inexistente = tmp_path / "no-esta.mp4"
    assert mod.espera_sonido({"voz": "guiones/x.wav"}, inexistente) is True
    assert mod.espera_sonido({}, inexistente) is False


def test_el_silencio_digital_esta_muy_por_debajo_del_suelo_del_codec():
    mod = _ensamblar_mod()
    assert mod.SILENCIO_DB <= -50


def test_la_resolucion_que_no_es_la_del_curso_se_delata():
    mod = _ensamblar_mod()
    p, _ = mod.diagnostico(8.5, 8.5, [], "1080x1920", "1920x1080")
    assert len(p) == 1 and "1080x1920" in p[0]


def test_el_estado_de_la_medicion_caduca_con_la_pelicula(authed):
    pel = _peli()
    from app.main import cfg, db, pelicula_service

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    project = db.get_project(pid)
    destino = pelicula_service.destino(project)
    destino.mkdir(parents=True, exist_ok=True)
    (destino / pel.NOMBRE_VIDEO).write_bytes(b"pelicula")

    h = pelicula_service._hash_plan(
        pelicula_service.plan(project, pel.normaliza_opciones(None)))
    escribir = lambda d: (destino / pel.NOMBRE_INFORME).write_text(  # noqa: E731
        json.dumps(d))

    escribir({"ok": True, "hash": h})
    assert pelicula_service.estado_verificacion(
        pelicula_service.informe(project)) == "sin_verificar"

    escribir({"ok": True, "hash": h, "verificacion": {"ok": True, "hash": h}})
    assert pelicula_service.estado_verificacion(
        pelicula_service.informe(project)) == "pasa"

    escribir({"ok": True, "hash": h, "verificacion": {"ok": False, "hash": h}})
    assert pelicula_service.estado_verificacion(
        pelicula_service.informe(project)) == "no_pasa"

    # Se volvio a montar: la medicion es de OTRA pelicula y no vale.
    escribir({"ok": True, "hash": "otro", "verificacion": {"ok": True, "hash": h}})
    assert pelicula_service.estado_verificacion(
        pelicula_service.informe(project)) == "vieja"


def test_medir_sin_pelicula_es_409(authed):
    from app.main import cfg, db

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    r = authed.post(f"/api/projects/{pid}/pelicula/verificar")
    assert r.status_code == 409
    assert "medir" in r.json()["detail"]


# ── API ──────────────────────────────────────────────────────────────────────

def test_estado_sin_material(authed):
    from app.main import db

    pid = _create_project(authed)["id"]
    r = authed.get(f"/api/projects/{pid}/pelicula")
    assert r.status_code == 200
    body = r.json()
    assert body["estado"] == "sin_clips"
    assert body["informe"] is None
    assert "corte" in body["transiciones"]

    authed.post(f"/api/projects/{pid}/clips", json={"title": "x",
                                                    "script": VALID_SCRIPT})
    assert authed.get(f"/api/projects/{pid}/pelicula").json()["estado"] \
        == "faltan_renders"


def test_montar_sin_renders_devuelve_409(authed):
    pid = _create_project(authed)["id"]
    r = authed.post(f"/api/projects/{pid}/pelicula", json={})
    assert r.status_code == 409
    assert "clips" in r.json()["detail"]


def test_transicion_invalida_es_422(authed):
    pid = _create_project(authed)["id"]
    r = authed.post(f"/api/projects/{pid}/pelicula",
                    json={"duracion_transicion": 99})
    assert r.status_code == 422


def test_el_video_falta_hasta_que_se_monta(authed):
    from app.main import cfg, db

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    assert authed.get(f"/api/projects/{pid}/pelicula")\
        .json()["estado"] == "sin_montar"
    assert authed.get(f"/api/projects/{pid}/pelicula/video").status_code == 404
    assert authed.delete(f"/api/projects/{pid}/pelicula").status_code == 404


def test_pelicula_montada_se_sirve_y_se_borra(authed):
    pel = _peli()
    from app.main import cfg, db, pelicula_service

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    project = db.get_project(pid)

    destino = pelicula_service.destino(project)
    destino.mkdir(parents=True, exist_ok=True)
    (destino / pel.NOMBRE_VIDEO).write_bytes(b"pelicula-falsa")
    plan = pelicula_service.plan(project, pel.normaliza_opciones(None))
    (destino / pel.NOMBRE_INFORME).write_text(
        '{"ok": true, "duracion": 12.0, "hash": "%s"}'
        % pelicula_service._hash_plan(plan))

    assert authed.get(f"/api/projects/{pid}/pelicula").json()["estado"] == "al_dia"
    r = authed.get(f"/api/projects/{pid}/pelicula/video")
    assert r.status_code == 200 and r.content == b"pelicula-falsa"
    assert "curso-pelicula.mp4" in r.headers["content-disposition"]

    assert authed.delete(f"/api/projects/{pid}/pelicula").status_code == 200
    assert authed.get(f"/api/projects/{pid}/pelicula/video").status_code == 404


def test_la_pelicula_de_otro_proyecto_no_se_ve(authed):
    r = authed.get("/api/projects/noexiste/pelicula")
    assert r.status_code == 404


def test_pelicula_requiere_sesion(client):
    assert client.get("/api/projects/x/pelicula").status_code == 401


def test_un_render_jobs_enlazado_a_otro_disco_sigue_dentro_del_workspace(
        authed, tmp_path):
    """`render_jobs/` y `exports/` pueden ser enlaces a otro disco (ver
    studio/docs/ARTEFACTOS-LOCALES.md). Resolver el enlace antes de comparar
    manda la ruta fuera del workspace y la pelicula no se puede ni planear,
    aunque el contenedor vea los videos perfectamente montados.
    """
    from app.main import pelicula_service
    ws = pelicula_service.cfg.workspace
    fuera = tmp_path.parent / "otro-disco-peli" / "render_jobs"
    fuera.mkdir(parents=True, exist_ok=True)
    enlace = ws / "render_jobs_enlazado"
    if enlace.is_symlink():
        enlace.unlink()
    enlace.symlink_to(fuera)

    assert pelicula_service._rel(enlace / "abc" / "Clip.mp4") == \
        "render_jobs_enlazado/abc/Clip.mp4"


def test_el_contenedor_recibe_montados_los_videos_de_los_jobs():
    """El repo va montado read-only, pero si `render_jobs` es un enlace, dentro
    del contenedor apunta a un destino que NO esta montado: `ensamblar.py` no
    puede leer un solo clip. Los dos comandos que leen renders (montar la
    pelicula y cortar una pieza) tienen que montarlo explicitamente.
    """
    import importlib.util
    ruta = Path(__file__).resolve().parents[3] / "studio" / "runner" / "manim_runner.py"
    fuente = ruta.read_text()
    # Se lee el fuente en vez de importar el runner: importarlo abre sockets y
    # arranca su bucle de servicio.
    # Se cuentan los USOS como argumento de docker, no la definicion.
    assert fuente.count('"-v", montaje_render_jobs()') == 2, (
        "handle_ensamblar y handle_piezas tienen que montar render_jobs")
    assert ':ro"' in fuente.split("def montaje_render_jobs")[1][:800], (
        "el montaje de los renders tiene que ser de solo lectura")


# ── R3c: costuras, picos y cola de la voz ────────────────────────────────────
#
# La costura se mide DENTRO del contenedor (es el unico sitio con ffmpeg), pero
# la aritmetica —de dos fotogramas a un numero, y de una fila de numeros a un
# diagnostico— es pura y se prueba aqui con imagenes sinteticas. Es la misma
# separacion que ya tenian `curva_ducking` y `diagnostico`: cambiar el criterio
# no puede exigir renderizar un curso.

def _lienzo(ancho=320, alto=180, hud=True):
    """Un fotograma de la casa en miniatura: fondo plano y capa fija."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (ancho, alto), (11, 17, 32))
    if hud:
        d = ImageDraw.Draw(img)
        # Las cuatro escuadras del HUD y el punto de la marca de agua: unos
        # pocos cientos de subpixeles sobre 57 600, que es mas o menos la
        # proporcion que ocupa la capa fija en un fotograma de curso.
        d.line((6, 6, 20, 6), fill=(245, 158, 11))
        d.line((ancho - 20, alto - 6, ancho - 6, alto - 6), fill=(245, 158, 11))
        d.rectangle((8, alto - 12, 12, alto - 8), fill=(245, 158, 11))
    return img


def test_dos_fotogramas_iguales_no_tienen_costura():
    pytest.importorskip("PIL")
    mod = _ensamblar_mod()
    a = _lienzo()
    assert mod.diferencia_media(a, a.copy()) == 0.0
    assert mod.veredicto_costura(0.0) == "bien"


def test_la_esquina_del_hud_apagada_da_un_valor_pequeno_pero_no_nulo():
    """El fallo del curso 28 en miniatura: la pieza termina con la capa fija
    apagada y la siguiente la enciende de golpe.

    Lo que hace peligroso a este defecto es justo que el numero sea PEQUENO
    —0,0552/255 en el curso real— y por eso a ojo no se ve. Tiene que salir
    distinto de cero y fuera de la banda limpia.
    """
    pytest.importorskip("PIL")
    mod = _ensamblar_mod()
    con = _lienzo(hud=True)
    sin = _lienzo(hud=False)
    d = mod.diferencia_media(sin, con)
    assert d > 0, "apagar la capa fija tiene que notarse en la medida"
    assert d < 1.0, "y tiene que ser un numero pequeno: por eso no se ve a ojo"
    assert mod.veredicto_costura(d) in ("aviso", "fallo")
    # El orden no importa: es una diferencia absoluta.
    assert mod.diferencia_media(con, sin) == pytest.approx(d)


def test_dos_fotogramas_de_distinto_tamano_no_se_comparan():
    pytest.importorskip("PIL")
    mod = _ensamblar_mod()
    with pytest.raises(mod.ErrorPlan, match="no miden lo mismo"):
        mod.diferencia_media(_lienzo(), _lienzo(ancho=321))


def test_los_umbrales_de_la_costura_salen_de_los_cursos_entregados():
    """0.0048 es la peor costura limpia medida (curso 28, catorce uniones de
    leccion) y 0.0552 la del defecto real. Los umbrales tienen que dejar la
    primera en verde y la segunda fuera de el."""
    mod = _ensamblar_mod()
    assert mod.veredicto_costura(0.0) == "bien"        # cursos 31 y 33
    assert mod.veredicto_costura(0.003) == "bien"      # curso 26
    assert mod.veredicto_costura(0.0048) == "bien"     # curso 28, limpio
    assert mod.veredicto_costura(0.0552) == "aviso"    # curso 28, el defecto
    assert mod.veredicto_costura(19.4) == "fallo"      # una pieza en negro
    assert mod.veredicto_costura(None) == "n/a"        # empalme xfade
    assert mod.COSTURA_OK < mod.COSTURA_AVISO


def test_tres_costuras_identicas_delatan_la_capa_fija():
    """La firma del curso 28: ninguna costura suelta acusaba a nadie, pero las
    catorce valian EXACTAMENTE lo mismo, y eso solo puede venir de un objeto
    que esta en todas las piezas."""
    mod = _ensamblar_mod()
    firma = mod.firma_capa_fija([0.0552, 0.0552, 0.0552])
    assert firma and "0.0552" in firma and "capa fija" in firma

    # Dos son coincidencia; tres son firma.
    assert mod.firma_capa_fija([0.0552, 0.0552]) is None
    # Cero no delata nada: un curso limpio tambien tiene todas las costuras
    # iguales, y valen cero.
    assert mod.firma_capa_fija([0.0, 0.0, 0.0, 0.0]) is None
    # Con una sola distinta ya no es la capa fija: es contenido.
    assert mod.firma_capa_fija([0.0552, 0.0552, 0.0553]) is None


def test_la_firma_de_la_capa_fija_sube_a_problema_solo_si_ya_avisaba():
    """El 0,0552 identico del curso 28 tiene que dejar la pelicula en rojo (es
    el defecto), pero unas costuras identicas dentro de la banda limpia son el
    suelo del codec y no rompen nada."""
    mod = _ensamblar_mod()
    sucias = [{"de": f"P{i}", "a": f"P{i + 1}", "valor": 0.0552,
               "veredicto": "aviso"} for i in range(3)]
    problemas, avisos = mod.diagnostico(8.5, 8.5, [], "", "", sucias)
    assert any("capa fija" in x for x in problemas)
    assert len(avisos) == 3          # y las tres costuras, una a una

    limpias = [{"de": f"P{i}", "a": f"P{i + 1}", "valor": 0.0009,
                "veredicto": "bien"} for i in range(3)]
    problemas, avisos = mod.diagnostico(8.5, 8.5, [], "", "", limpias)
    assert problemas == []
    assert any("capa fija" in x for x in avisos)


def test_una_costura_por_encima_del_techo_es_un_problema():
    mod = _ensamblar_mod()
    rota = [{"de": "Termina en negro", "a": "Sigue", "valor": 19.4252,
             "veredicto": "fallo"}]
    problemas, _ = mod.diagnostico(8.5, 8.5, [], "", "", rota)
    assert len(problemas) == 1
    assert "Termina en negro → Sigue" in problemas[0]


def test_el_pico_por_encima_del_techo_avisa_pero_no_rompe():
    """-0.5 dBFS es el techo de la casa (unir_vertical.py). Una pelicula que
    pica en -0.4 es entregable con reservas, no material roto."""
    mod = _ensamblar_mod()
    assert mod.PICO_MAX_DB == -0.5
    problemas, avisos = mod.diagnostico(8.5, 8.5, [], "", "", [], -0.4, [])
    assert problemas == []
    assert any("-0.4 dBFS" in x for x in avisos)
    assert mod.diagnostico(8.5, 8.5, [], "", "", [], -4.0, [])[1] == []
    # Sin audio no se inventa un veredicto.
    assert mod.diagnostico(8.5, 8.5, [], "", "", [], None, [])[1] == []


def test_la_voz_sin_cola_de_silencio_avisa_y_se_cuenta_bien():
    mod = _ensamblar_mod()
    assert mod.COLA_VOZ_S == 0.8 and mod.COLA_VOZ_DB == -50.0
    _, avisos = mod.diagnostico(8.5, 8.5, [], "", "", [], None, ["Uno"])
    assert "1 pieza cierra" in avisos[0] and "Uno" in avisos[0]
    _, muchos = mod.diagnostico(8.5, 8.5, [], "", "", [], None,
                                [f"C{i}" for i in range(9)])
    assert "9 piezas cierran" in muchos[0] and "…" in muchos[0]


def test_los_dos_topes_de_la_medicion_no_pueden_separarse():
    """El runner corta el contenedor y el cliente corta la espera. Si el del
    cliente fuera el mas corto, la medicion moriria por timeout mientras el
    contenedor sigue midiendo. Medir la pelicula dejo de ser leer su duracion:
    saca dos fotogramas por union y un volumedetect por pieza."""
    import app.runner_client as rc

    runner = Path(__file__).resolve().parents[3] / "studio" / "runner" \
        / "manim_runner.py"
    fuente = runner.read_text()
    assert "ENSAMBLAR_VERIFICA_TIMEOUT = 1800" in fuente
    assert "ENSAMBLAR_VERIFICA_TIMEOUT)" in fuente, \
        "el handler tiene que usar el tope nuevo, no el del promo"
    assert 'timeout=14700 if modo == "montar" else 1860' in \
        Path(rc.__file__).read_text()


# ── el veredicto global: verde, ambar y rojo ─────────────────────────────────

def test_el_veredicto_global_tiene_tres_colores(authed):
    """Sin el ambar, una costura de 0,055 o un pico en -0,4 tendrian que
    elegir entre mentir (verde) o ensenar a ignorar el rojo."""
    pel = _peli()
    from app.main import cfg, db, pelicula_service

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    project = db.get_project(pid)
    destino = pelicula_service.destino(project)
    destino.mkdir(parents=True, exist_ok=True)
    (destino / pel.NOMBRE_VIDEO).write_bytes(b"pelicula")
    h = pelicula_service._hash_plan(
        pelicula_service.plan(project, pel.normaliza_opciones(None)))

    def estado_con(verificacion):
        (destino / pel.NOMBRE_INFORME).write_text(json.dumps(
            {"ok": True, "hash": h, "verificacion": verificacion}))
        return pelicula_service.estado_verificacion(
            pelicula_service.informe(project))

    assert estado_con({"ok": True, "hash": h, "avisos": []}) == "pasa"
    assert estado_con({"ok": True, "hash": h,
                       "avisos": ["la pelicula pica en -0.4 dBFS"]}) == "avisos"
    assert estado_con({"ok": False, "hash": h, "avisos": ["algo"]}) == "no_pasa"
    # Una pelicula medida ANTES de R3c no trae `avisos`: sigue en verde, no se
    # le inventan avisos que nadie midio.
    assert estado_con({"ok": True, "hash": h}) == "pasa"


# ── el endpoint, con el runner mockeado ──────────────────────────────────────

def test_verificar_persiste_y_sirve_las_costuras(authed, monkeypatch):
    """`POST …/pelicula/verificar` guarda lo que midio el contenedor dentro de
    `pelicula.json` y `GET …/pelicula` lo devuelve entero. El runner se
    sustituye por un doble: aqui no hay ni Docker ni ffmpeg."""
    pel = _peli()
    from app.main import cfg, db, pelicula_service

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    _rendered_clip(authed, db, cfg, pid, "Dos", "cccc00002222dddd")
    project = db.get_project(pid)
    destino = pelicula_service.destino(project)
    destino.mkdir(parents=True, exist_ok=True)
    (destino / pel.NOMBRE_VIDEO).write_bytes(b"pelicula")
    h = pelicula_service._hash_plan(
        pelicula_service.plan(project, pel.normaliza_opciones(None)))
    (destino / pel.NOMBRE_INFORME).write_text(
        json.dumps({"ok": True, "duracion": 3.6, "hash": h}))

    medida = {
        "ok": True,
        "problemas": [],
        "avisos": ["la pelicula pica en -0.4 dBFS y el techo de la casa es "
                   "-0.5: va a recortar"],
        "duracion_medida": 3.6, "duracion_prevista": 3.6, "desfase": 0.0,
        "tolerancia": 0.5, "resolucion": "854x480",
        "resolucion_esperada": "854x480", "piezas": 2, "mudas": 0,
        "tramos": [{"titulo": "Uno", "pico_db": -10.5, "pico_alto": False,
                    "cola_voz_db": -91.0, "cola_voz_ok": True},
                   {"titulo": "Dos", "pico_db": -0.4, "pico_alto": True}],
        "costuras": [{"de": "Uno", "a": "Dos", "valor": 0.0048,
                      "veredicto": "bien"}],
        "costura_peor": 0.0048, "costura_diagnostico": None,
        "costura_umbrales": [0.01, 0.06],
        "pico_max_db": -0.4, "pico_techo_db": -0.5, "pico_veredicto": "aviso",
        "sin_cola_voz": [],
    }
    pedidos = []

    class RunnerDoble:
        async def ensamblar(self, project_id, modo="montar"):
            pedidos.append((project_id, modo))
            return dict(medida)

    monkeypatch.setattr(pelicula_service, "runner", RunnerDoble())

    r = authed.post(f"/api/projects/{pid}/pelicula/verificar")
    assert r.status_code == 200, r.text
    assert pedidos == [(pid, "verificar")]

    # Lo medido esta en el disco, dentro del informe del montaje y con SU hash:
    # una medicion de otra pelicula no vale.
    guardado = json.loads((destino / pel.NOMBRE_INFORME).read_text())
    assert guardado["verificacion"]["costuras"][0]["valor"] == 0.0048
    assert guardado["verificacion"]["hash"] == h

    # Y sale entero por la API, que es lo que pinta el panel.
    body = authed.get(f"/api/projects/{pid}/pelicula").json()
    v = body["informe"]["verificacion"]
    assert v["costuras"] == medida["costuras"]
    assert v["costura_umbrales"] == [0.01, 0.06]
    assert v["pico_max_db"] == -0.4 and v["pico_veredicto"] == "aviso"
    assert v["tramos"][0]["cola_voz_ok"] is True
    assert body["verificacion"] == "avisos"


def test_una_medicion_con_costuras_rotas_deja_la_pelicula_en_rojo(
        authed, monkeypatch):
    pel = _peli()
    from app.main import cfg, db, pelicula_service

    pid = _create_project(authed)["id"]
    _rendered_clip(authed, db, cfg, pid, "Uno", "aaaa00001111bbbb")
    project = db.get_project(pid)
    destino = pelicula_service.destino(project)
    destino.mkdir(parents=True, exist_ok=True)
    (destino / pel.NOMBRE_VIDEO).write_bytes(b"pelicula")
    h = pelicula_service._hash_plan(
        pelicula_service.plan(project, pel.normaliza_opciones(None)))
    (destino / pel.NOMBRE_INFORME).write_text(
        json.dumps({"ok": True, "hash": h}))

    class RunnerDoble:
        async def ensamblar(self, project_id, modo="montar"):
            return {"ok": False, "avisos": [],
                    "problemas": ["la costura Uno → Dos vale 19.4252/255: "
                                  "el corte entre las dos piezas se ve"],
                    "costuras": [{"de": "Uno", "a": "Dos", "valor": 19.4252,
                                  "veredicto": "fallo"}]}

    monkeypatch.setattr(pelicula_service, "runner", RunnerDoble())
    body = authed.post(f"/api/projects/{pid}/pelicula/verificar").json()
    assert body["verificacion"] == "no_pasa"
    assert "19.4252" in body["informe"]["verificacion"]["problemas"][0]


def test_costura_visible_es_aviso_en_horizontal():
    """Un curso 16:9 cierra cada clip con su propia composicion: la costura
    que en vertical es un problema aqui es un aviso (medido en prod: 2.23,
    5.55 y 5.96/255 en Sistemas ATP 3.3, un curso entregado y correcto)."""
    import importlib.util, sys
    from pathlib import Path
    ruta = Path(__file__).resolve().parents[2] / "tools" / "ensamblar.py"
    spec = importlib.util.spec_from_file_location("ensamblar_mod", ruta)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    costuras = [{"de": "a", "a": "b", "valor": 5.55, "veredicto": "fallo"}]
    prob, avi = mod.diagnostico(10, 10, [], "1920x1080", "1920x1080", costuras,
                                vertical=mod._es_vertical("1920x1080"))
    assert prob == [] and len(avi) == 1 and "por diseno" in avi[0]
    prob, avi = mod.diagnostico(10, 10, [], "1080x1920", "1080x1920", costuras,
                                vertical=mod._es_vertical("1080x1920"))
    assert len(prob) == 1 and avi == []
    assert mod._es_vertical("") is True
