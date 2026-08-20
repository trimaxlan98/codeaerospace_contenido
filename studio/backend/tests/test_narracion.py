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
        # 1 s de tono constante (amplitud 1000: por encima del umbral de
        # recorte de silencio, para que la duracion no cambie al recortar)
        return b"\xe8\x03" * 24_000


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

    # Hueco irreal en el guion (30 s): se acota a MAX_HUECO_S para no
    # desincronizar el final -> 1 + 2.5 + 1
    dur = sintetizar(fake, [{"t_inicio": 0, "texto": "a"},
                            {"t_inicio": 30, "texto": "b"}],
                     "Charon", tmp_path / "d.wav")
    assert abs(dur - 4.5) < 0.01

    # Sin tiempos: narracion de corrido (ambas secciones caben en un solo
    # trozo TTS, asi que es una sola llamada de 1 s)
    dur = sintetizar(fake, [{"texto": "a"}, {"texto": "b"}],
                     "Charon", tmp_path / "c.wav")
    assert dur == 1.0


def test_recortar_silencio():
    from app.narracion import TTS_RATE, _recortar_silencio

    voz = b"\xe8\x03" * TTS_RATE          # 1 s de amplitud 1000
    silencio = b"\x00\x00" * TTS_RATE     # 1 s de silencio
    audio = silencio + voz + silencio
    recortado = _recortar_silencio(audio)
    dur = len(recortado) / 2 / TTS_RATE
    # 1 s de voz + 0.12 s de margen a cada lado
    assert abs(dur - 1.24) < 0.01


def test_sintetizar_comprime_huecos_para_caber(tmp_path):
    """Con limite, los silencios entre secciones ceden antes de recortar voz:
    sin limite el alineado dura 4 s (1 + 2 de hueco + 1) y con 2.5 s de tope
    se comprime hasta caber sin perder ninguna seccion."""
    from app.narracion import sintetizar

    fake = FakeVertex()  # 1 s de audio por seccion
    secciones = [{"t_inicio": 0, "texto": "a"}, {"t_inicio": 3, "texto": "b"}]

    assert sintetizar(fake, secciones, "Charon", tmp_path / "sin.wav") == 4.0

    dur = sintetizar(fake, secciones, "Charon", tmp_path / "con.wav",
                     limite_s=2.5)
    assert 2.0 <= dur <= 2.5          # las 2 s de voz siguen completas
    # Aprovecha el hueco disponible en vez de pegarlas sin aire
    assert dur > 2.3

    # Ni pegadas caben (2 s de voz > 1.5 s): se entrega el minimo posible y
    # el ajuste fino queda para el reintento de guion / atempo del mux.
    dur = sintetizar(fake, secciones, "Charon", tmp_path / "min.wav",
                     limite_s=1.5)
    assert dur == 2.0


def test_generar_clip_conserva_el_mejor_intento(tmp_path):
    """Si el reintento sale peor que el guion original, se conserva el
    original (y no queda basura de intentos en el directorio)."""
    from app.narracion import generar_clip

    class VertexVariable(FakeVertex):
        """Cada intento pide una seccion mas: el 2o cabe, el 3o se pasa."""

        def __init__(self):
            super().__init__()
            self.duraciones = [3, 1, 4]  # segundos de voz por intento

        def guion(self, system, user):
            self.llamadas_guion += 1
            n = self.duraciones[self.llamadas_guion - 1]
            return {"secciones": [{"t_inicio": i, "t_fin": i + 1,
                                   "momento": "m", "texto": f"t{i}"}
                                  for i in range(n)]}

    fake = VertexVariable()
    clip = {"title": "Clip", "script": VALID_SCRIPT, "scene": "Demo",
            "notes": "", "position": 1}
    curso = {"name": "Curso", "description": "d", "total_clips": 1}
    entry = generar_clip(fake, curso, clip, VALID_SCRIPT, video_s=2.0,
                         voz="Charon", destino=tmp_path, etiqueta="01-clip",
                         log=lambda *a: None)

    # 1er intento 3 s (no cabe en 2 s + 5 %), 2o 1 s (cabe) -> para ahi
    assert fake.llamadas_guion == 2
    assert entry["audio_s"] == 1.0
    assert not list(tmp_path.glob("*.intento.wav"))
    # El wav en disco es el del intento elegido, no el del ultimo
    import wave
    with wave.open(str(tmp_path / "01-clip.wav")) as w:
        assert w.getnframes() / w.getframerate() == 1.0
    # md/txt/secciones describen ese mismo intento
    assert (tmp_path / "01-clip.txt").read_text().strip() == "t0"


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


def test_mux_concatena_los_clips_con_audio_no_los_originales():
    """Regresion: ffmpeg resuelve las rutas relativas de un concat.txt contra
    el directorio DEL ARCHIVO, no contra el cwd. Leer `../concat.txt` desde
    con_audio/ concatenaba los mp4 originales y el curso salia MUDO, sin que
    nada fallara. La lista tiene que vivir dentro de con_audio/."""
    from app.projects_api import MUX_SH

    assert "cp concat.txt con_audio/concat.txt" in MUX_SH
    assert "-i ../concat.txt" not in MUX_SH


def test_mux_ajusta_la_voz_que_no_cabe_en_vez_de_cortarla():
    """La voz mas larga que el video se acelera con atempo (preserva el tono);
    -shortest a secas le cortaria la cola."""
    from app.projects_api import MUX_SH

    assert "atempo=" in MUX_SH
    assert "ffprobe" in MUX_SH


def _stub_ffmpeg(bindir, log):
    """Stubs de ffmpeg/ffprobe en un dir que se antepone al PATH.

    `ffmpeg` apunta cada invocacion (cwd + args) en `log` y toca el archivo de
    salida (ultimo argumento) para que el `set -e` del script siga adelante;
    `ffprobe` finge que la voz dura 12 s y el video 10 s, para ejercitar
    tambien la rama de atempo (ratio 1.2, que el script capa a 1.15).
    """
    bindir.mkdir(parents=True, exist_ok=True)
    ffmpeg = bindir / "ffmpeg"
    ffmpeg.write_text(
        "#!/bin/sh\n"
        "{ printf '%s' \"$PWD\"\n"
        "  for a in \"$@\"; do printf '\\t%s' \"$a\"; done\n"
        f"  printf '\\n'; }} >> '{log}'\n"
        "out=\"\"\n"
        "for a in \"$@\"; do out=\"$a\"; done\n"
        "mkdir -p \"$(dirname \"$out\")\"\n"
        ": > \"$out\"\n"
    )
    ffprobe = bindir / "ffprobe"
    ffprobe.write_text(
        "#!/bin/sh\n"
        "f=\"\"\n"
        "for a in \"$@\"; do f=\"$a\"; done\n"
        "case \"$f\" in\n"
        "  *.wav) echo 12.0 ;;\n"
        "  *) echo 10.0 ;;\n"
        "esac\n"
    )
    for f in (ffmpeg, ffprobe):
        f.chmod(0o755)


def test_mux_sh_corre_de_verdad(tmp_path):
    """Ejecuta el mux.sh real con ffmpeg/ffprobe stubeados, en vez de mirar si
    ciertas cadenas siguen en el script.

    Cubre las dos regresiones que se comieron el audio del curso:

    1. El concat leia `../concat.txt` desde con_audio/, y como ffmpeg resuelve
       las rutas de un concat file respecto al directorio del propio fichero,
       unia los mp4 originales: el curso salia entero pero mudo.
    2. Con LANG=es_* el `printf "%.4f"` de mawk escribe el ratio con coma
       ("atempo=1,1500"), que ffmpeg rechaza. Solo pasa fuera del VPS, que
       corre en locale C — de ahi el `export LC_ALL=C` del script.
    """
    import os
    import re
    import shutil
    import subprocess
    from pathlib import Path

    from app.projects_api import MUX_SH

    sh = shutil.which("sh")
    assert sh, "hace falta un /bin/sh para este test"

    # Curso de dos clips: el primero con narracion, el segundo sin ella.
    (tmp_path / "001-intro.mp4").write_bytes(b"video")
    (tmp_path / "001-intro.wav").write_bytes(b"audio")
    (tmp_path / "002-cierre.mp4").write_bytes(b"video")
    (tmp_path / "concat.txt").write_text(
        "file '001-intro.mp4'\nfile '002-cierre.mp4'\n")
    (tmp_path / "mux.sh").write_text(MUX_SH)

    log = tmp_path / "ffmpeg.log"
    _stub_ffmpeg(tmp_path / "bin", log)
    # Locale con coma decimal (si la maquina lo tiene instalado); el script
    # tiene que imponer el suyo por dentro.
    env = {**os.environ,
           "PATH": f"{tmp_path / 'bin'}{os.pathsep}{os.environ['PATH']}",
           "LC_ALL": "es_ES.UTF-8"}
    r = subprocess.run([sh, "mux.sh"], cwd=tmp_path, env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

    invocaciones = [linea.split("\t") for linea in
                    log.read_text().splitlines() if linea]
    # Un mux por clip + el concat final
    assert len(invocaciones) == 3, invocaciones

    intro, cierre, concat = invocaciones
    # Clip con voz: se acelera lo justo (1.2 capado a 1.15) y se rellena con
    # apad. Con punto decimal, pase el locale que pase.
    assert "atempo=1.1500,apad" in intro
    # Clip sin voz: pista de silencio, para no mezclar clips con y sin audio
    assert any(a.startswith("anullsrc") for a in cierre)

    # El concat final: la lista que recibe ffmpeg debe apuntar a los mp4 de
    # con_audio/, resolviendo como lo hace ffmpeg (relativo a la lista, no al cwd).
    cwd_concat = Path(concat[0])
    assert "-f" in concat and concat[concat.index("-f") + 1] == "concat"
    lista = cwd_concat / concat[concat.index("-i") + 1]
    assert lista.is_file(), f"la lista del concat no existe: {lista}"

    entradas = re.findall(r"^file '(.+)'$", lista.read_text(), re.M)
    assert entradas == ["001-intro.mp4", "002-cierre.mp4"]
    muxeados = {(tmp_path / "con_audio" / n).resolve() for n in entradas}
    for entrada in entradas:
        resuelto = (lista.parent / entrada).resolve()
        assert resuelto in muxeados, (
            f"{entrada} resuelve a {resuelto}, que no es el mp4 muxeado")

    # Y la salida es el curso completo, un nivel por encima de con_audio/
    assert Path(concat[-1]).name == "curso_narrado.mp4"
    assert (cwd_concat / concat[-1]).resolve() == (
        tmp_path / "curso_narrado.mp4").resolve()


def test_audio_404_sin_narracion(authed):
    project = _create_project(authed)
    clip = _add_clip(authed, project["id"])
    r = authed.get(f"/api/projects/{project['id']}/narracion/{clip['id']}/audio")
    assert r.status_code == 404
    r = authed.get(f"/api/projects/{project['id']}/narracion/ajeno/audio")
    assert r.status_code == 404


def test_indice_de_cursos_dice_cuantos_clips_estan_narrados(authed, tmp_path,
                                                            monkeypatch):
    """`GET /api/projects` trae `narrated_count` y NO abre ningun mp4.

    El indice tiene que poder responder "que falta narrar" con ~60 cursos en
    catalogo; `estado_proyecto` no vale ahi porque necesita la duracion del
    video y `duracion_mp4` lee el archivo entero.
    """
    _enable(tmp_path, monkeypatch)
    project = _create_project(authed)
    pid = project["id"]
    clip = _add_clip(authed, pid, title="Clip uno")
    _add_clip(authed, pid, title="Clip dos")

    resumen = next(p for p in authed.get("/api/projects").json()["projects"]
                   if p["id"] == pid)
    assert resumen["clip_count"] == 2
    assert resumen["narrated_count"] == 0

    r = authed.post(f"/api/projects/{pid}/narracion",
                    json={"clips": [clip["id"]]})
    assert r.status_code == 202
    _wait_run(authed, pid)

    import app.main as main_mod
    llamadas = []
    monkeypatch.setattr(main_mod.narracion_service, "_video_s",
                        lambda clip: llamadas.append(clip) or None)

    resumen = next(p for p in authed.get("/api/projects").json()["projects"]
                   if p["id"] == pid)
    assert resumen["narrated_count"] == 1
    assert llamadas == [], "el indice no debe medir la duracion de los videos"


def test_el_indice_sobrevive_a_un_fallo_del_resumen_de_narracion(authed,
                                                                 monkeypatch):
    """Un error leyendo los guiones deja el indice sin el dato, no en 500."""
    project = _create_project(authed)
    import app.main as main_mod

    def explota(*_args, **_kwargs):
        raise OSError("disco de guiones no montado")

    monkeypatch.setattr(main_mod.narracion_service, "resumen_audio", explota)
    r = authed.get("/api/projects")
    assert r.status_code == 200
    resumen = next(p for p in r.json()["projects"] if p["id"] == project["id"])
    assert "narrated_count" not in resumen
