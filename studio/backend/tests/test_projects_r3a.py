"""Sprint R3a — paridad con la terminal: un proyecto es un directorio.

Cuatro capacidades que solo existian en la terminal y ahora tambien en la
app: exportar las fuentes de un proyecto, importarlas (zip o directorio del
repo), renderizar un lote a la calidad que se elija y duplicar.

Sin runner real: los renders quedan en la cola y el worker los marca `error`
al no haber contenedor. Lo que se valida aqui es la capa API/DB, y para el
progreso del lote se siembran jobs directamente en la Database (mismo patron
que `test_projects_export.py`).
"""

import io
import json
import time
import zipfile

from app import importar
from app.narracion import etiqueta_clip, slugify
from app.projects import content_hash

VALID_SCRIPT = (
    "from manim import *\n"
    "class Demo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle()))\n"
)
STYLE = "from manim import *\n\nC_ACENTO = '#f59e0b'\n"


def _create_project(authed, **overrides):
    body = {"name": "Curso R3a", "description": "desc", "quality": "ql",
            "style_block": STYLE}
    body.update(overrides)
    r = authed.post("/api/projects", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def _add_clip(authed, pid, title, scene="Demo", **extra):
    body = {"title": title, "script": VALID_SCRIPT, "scene": scene}
    body.update(extra)
    r = authed.post(f"/api/projects/{pid}/clips", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def _marcar_renderizado(db, pid, cid, job_id, quality="ql", **extra):
    """Un clip con render vigente, sin pasar por la cola."""
    clip = db.get_clip(cid)
    project = db.get_project(pid)
    ahora = time.time()
    db.insert_job({"id": job_id, "scene": clip["scene"], "quality": quality,
                   "timeout": 120, "status": "queued", "script": VALID_SCRIPT,
                   "created_at": extra.get("created_at", ahora - 10),
                   "project_id": pid, "clip_id": cid, "content_hash": None})
    db.update_job(job_id, status="done",
                  started_at=extra.get("started_at", ahora - 10),
                  finished_at=extra.get("finished_at", ahora - 4),
                  video_path="/tmp/x.mp4", size_bytes=1)
    db.update_clip(cid, job_id=job_id,
                   rendered_hash=content_hash(project["style_block"],
                                              clip["script"], clip["scene"]))


# ── nombres de archivo ───────────────────────────────────────────────────

def test_el_slug_del_importador_es_el_de_narracion():
    """Los guiones se buscan por nombre de archivo: si `importar.slug` se
    separara de `narracion.slugify`, el zip los exportaria con un nombre y
    la app los buscaria con otro, en silencio."""
    titulos = ["1 · El número de Mach", "Señales y sistemas", "ÑU/ÁRBOL",
               "   ", "a" * 80, "Clip (copia)", "3.1 — Fourier"]
    for t in titulos:
        assert importar.slug(t) == slugify(t), t
        assert importar.etiqueta(0, t) == etiqueta_clip(0, t)


# ── exportar las fuentes ─────────────────────────────────────────────────

def test_fuentes_zip_tiene_el_layout_que_lee_el_cli(authed):
    project = _create_project(authed)
    pid = project["id"]
    _add_clip(authed, pid, "1 · Intro")
    _add_clip(authed, pid, "2 · Cierre")

    r = authed.get(f"/api/projects/{pid}/fuentes.zip")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"
    assert "fuentes.zip" in r.headers["content-disposition"]

    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        nombres = zf.namelist()
        assert nombres == ["curso.json", "style_block.py",
                           "clips/01-1-intro.py", "clips/02-2-cierre.py"]
        assert zf.read("style_block.py").decode() == STYLE
        manifiesto = json.loads(zf.read("curso.json"))
    assert manifiesto["name"] == "Curso R3a"
    assert manifiesto["quality"] == "ql"
    assert manifiesto["style_block"] == "style_block.py"
    assert [c["file"] for c in manifiesto["clips"]] == [
        "clips/01-1-intro.py", "clips/02-2-cierre.py"]
    assert manifiesto["clips"][0]["scene"] == "Demo"


def test_round_trip_de_fuentes_es_byte_a_byte(authed, tmp_path):
    """Exportar -> borrar -> importar -> exportar da los MISMOS bytes."""
    project = _create_project(authed, name="Curso ida y vuelta")
    pid = project["id"]
    c1 = _add_clip(authed, pid, "1 · Intro")
    _add_clip(authed, pid, "2 · Cierre")
    authed.patch(f"/api/projects/{pid}/clips/{c1['id']}",
                 json={"final_state": "queda el círculo", "notes": "nota 1"})
    # Un guion escrito a mano: tiene que viajar dentro del zip.
    r = authed.put(f"/api/projects/{pid}/narracion/{c1['id']}/guion",
                   json={"secciones": [{"t_inicio": 0.5, "texto": "Hola."},
                                       {"t_inicio": 4.0, "texto": "Adiós."}]})
    assert r.status_code == 200, r.text

    primero = authed.get(f"/api/projects/{pid}/fuentes.zip").content
    with zipfile.ZipFile(io.BytesIO(primero)) as zf:
        assert "guiones/01-1-intro.secciones.json" in zf.namelist()
        assert "guiones/01-1-intro.txt" in zf.namelist()

    assert authed.delete(f"/api/projects/{pid}").status_code == 200

    r = authed.post("/api/projects/importar", content=primero,
                    headers={"Content-Type": "application/zip"})
    assert r.status_code == 200, r.text
    res = r.json()
    assert res["creado"] is True and res["clips"] == 2 and res["creados"] == 2
    assert res["guiones"] == 1
    nuevo_pid = res["project_id"]

    detalle = authed.get(f"/api/projects/{nuevo_pid}").json()
    assert [c["title"] for c in detalle["clips"]] == ["1 · Intro", "2 · Cierre"]
    assert detalle["clips"][0]["final_state"] == "queda el círculo"
    assert detalle["clips"][0]["notes"] == "nota 1"
    guion = authed.get(
        f"/api/projects/{nuevo_pid}/narracion/{detalle['clips'][0]['id']}/guion").json()
    assert [s["texto"] for s in guion["secciones"]] == ["Hola.", "Adiós."]

    segundo = authed.get(f"/api/projects/{nuevo_pid}/fuentes.zip").content
    assert segundo == primero


def test_reimportar_el_mismo_zip_no_cambia_nada(authed):
    project = _create_project(authed, name="Curso idempotente")
    pid = project["id"]
    _add_clip(authed, pid, "1 · Intro")

    fuentes = authed.get(f"/api/projects/{pid}/fuentes.zip").content
    r = authed.post("/api/projects/importar", content=fuentes,
                    headers={"Content-Type": "application/zip"})
    assert r.status_code == 200, r.text
    res = r.json()
    assert res["creado"] is False and res["project_id"] == pid
    assert res["actualizados"] == 0 and res["creados"] == 0
    assert all(l.startswith("=") for l in res["reporte"]), res["reporte"]
    assert len(authed.get("/api/projects").json()["projects"]) == 1


def test_el_zip_rechaza_lo_que_no_es_un_curso(authed):
    # No es un zip
    r = authed.post("/api/projects/importar", content=b"no soy un zip",
                    headers={"Content-Type": "application/zip"})
    assert r.status_code == 422

    # Zip con una ruta que se sale del proyecto
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("curso.json", "{}")
        zf.writestr("../evil.py", "import os")
    r = authed.post("/api/projects/importar", content=buf.getvalue(),
                    headers={"Content-Type": "application/zip"})
    assert r.status_code == 422 and "no toca" in r.json()["detail"]

    # Zip sin curso.json
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("style_block.py", "x = 1")
    r = authed.post("/api/projects/importar", content=buf.getvalue(),
                    headers={"Content-Type": "application/zip"})
    assert r.status_code == 422 and "curso.json" in r.json()["detail"]

    # Escena que no existe en el script compuesto
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("curso.json", json.dumps({
            "name": "Roto", "quality": "ql", "style_block": "style_block.py",
            "clips": [{"file": "clips/01-x.py", "title": "X",
                       "scene": "NoExiste"}]}))
        zf.writestr("style_block.py", STYLE)
        zf.writestr("clips/01-x.py", VALID_SCRIPT)
    r = authed.post("/api/projects/importar", content=buf.getvalue(),
                    headers={"Content-Type": "application/zip"})
    assert r.status_code == 422 and "NoExiste" in r.json()["detail"]


# ── importar del repo ────────────────────────────────────────────────────

def _curso_en_el_repo(tmp_path, slug="curso-demo", name="Curso del repo"):
    d = tmp_path / "content" / "cursos" / slug
    (d / "clips").mkdir(parents=True)
    (d / "style_block.py").write_text(STYLE)
    (d / "clips" / "01-uno.py").write_text(VALID_SCRIPT)
    (d / "clips" / "02-dos.py").write_text(
        VALID_SCRIPT.replace("Circle", "Square"))
    (d / "curso.json").write_text(json.dumps({
        "name": name, "description": "de git", "quality": "qm",
        "style_block": "style_block.py",
        "clips": [
            {"file": "clips/01-uno.py", "title": "1 · Uno", "scene": "Demo",
             "final_state": "queda uno"},
            {"file": "clips/02-dos.py", "title": "2 · Dos", "scene": "Demo"},
        ]}, ensure_ascii=False))
    return d


def test_importar_un_curso_del_repo(authed, tmp_path):
    _curso_en_el_repo(tmp_path)

    # El listado dice que esta ahi.
    listado = authed.get("/api/projects/importables").json()
    assert listado["origenes"]["cursos"] == ["curso-demo"]

    # dry_run no escribe.
    r = authed.post("/api/projects/importar?dry_run=1",
                    json={"slug": "curso-demo", "origen": "cursos"})
    assert r.status_code == 200, r.text
    assert r.json()["creado"] is True and r.json()["dry_run"] is True
    assert authed.get("/api/projects").json()["projects"] == []

    r = authed.post("/api/projects/importar",
                    json={"slug": "curso-demo", "origen": "cursos"})
    assert r.status_code == 200, r.text
    res = r.json()
    assert res["creado"] is True and res["clips"] == 2
    detalle = authed.get(f"/api/projects/{res['project_id']}").json()
    assert detalle["quality"] == "qm"
    assert [c["title"] for c in detalle["clips"]] == ["1 · Uno", "2 · Dos"]
    assert detalle["clips"][0]["final_state"] == "queda uno"

    # Segunda pasada: idempotente por nombre exacto.
    r = authed.post("/api/projects/importar",
                    json={"slug": "curso-demo", "origen": "cursos"})
    assert r.json()["creado"] is False
    assert r.json()["project_id"] == res["project_id"]
    assert len(authed.get("/api/projects").json()["projects"]) == 1


def test_el_slug_del_repo_no_deja_salirse_del_directorio(authed, tmp_path):
    _curso_en_el_repo(tmp_path)
    for malo in ("../cursos/curso-demo", "..", "/etc", "Curso-Demo",
                 "curso demo", "curso-demo/../../..", ""):
        r = authed.post("/api/projects/importar",
                        json={"slug": malo, "origen": "cursos"})
        assert r.status_code == 422, (malo, r.status_code)
    r = authed.post("/api/projects/importar",
                    json={"slug": "curso-demo", "origen": "etc"})
    assert r.status_code == 422
    r = authed.post("/api/projects/importar",
                    json={"slug": "no-existe", "origen": "cursos"})
    assert r.status_code == 422


def test_importar_un_vertical_convierte_cada_pieza_en_un_clip(authed, tmp_path):
    raiz = tmp_path / "content" / "verticales" / "vert-demo"
    (raiz).mkdir(parents=True)
    (raiz / "style_block.py").write_text(STYLE)
    for i, nombre in enumerate(["00-intro", "01-la-costa"], start=0):
        d = raiz / "clips" / nombre
        d.mkdir(parents=True)
        (d / "escena.py").write_text(VALID_SCRIPT)
        pieza = {"name": f"{i:02d} · Pieza {i}", "scene": "Demo",
                 "file": "escena.py", "description": f"la pieza {i}",
                 "duracion_objetivo": 35.57 + i, "modulo": "M1 · Uno"}
        if i == 1:
            pieza["audio"] = {"pico_db": -4.0, "fade_in": 0.4,
                              "eventos": [["pulso", 5.3, -13],
                                          ["nebulosa", 0.1, -14]]}
            pieza["voz"] = {"voz": "Charon",
                            "secciones": [{"t_inicio": 1.6,
                                           "texto": "Esto es una costa."}]}
        (d / "clip.json").write_text(json.dumps(pieza, ensure_ascii=False))
    (raiz / "curso.json").write_text(json.dumps({
        "name": "Vertical demo", "slug": "vert-demo", "formato": "vertical",
        "estilo": "lienzo", "description": "curso 9:16",
        "style_block": "style_block.py",
        "piezas": [{"dir": "clips/00-intro", "tipo": "marca"},
                   {"dir": "clips/01-la-costa"}]}, ensure_ascii=False))

    r = authed.post("/api/projects/importar",
                    json={"slug": "vert-demo", "origen": "verticales"})
    assert r.status_code == 200, r.text
    pid = r.json()["project_id"]

    detalle = authed.get(f"/api/projects/{pid}").json()
    assert detalle["formato"] == "vertical" and detalle["quality"] == "qh"
    assert detalle["estilo"] == "lienzo"
    assert [c["title"] for c in detalle["clips"]] == ["00 · Pieza 0",
                                                      "01 · Pieza 1"]
    # Modulo y duracion objetivo viajan en las notas, en formato fijo.
    assert detalle["clips"][0]["notes"] == (
        "Módulo: M1 · Uno\nDuración objetivo: 35.57 s\nla pieza 0")
    # La cama de sonido de la pieza queda como manifiesto del clip.
    assert detalle["clips"][0]["has_audio"] is False
    assert detalle["clips"][1]["has_audio"] is True
    audio = authed.get(
        f"/api/projects/{pid}/clips/{detalle['clips'][1]['id']}/audio").json()
    manifiesto = audio["manifiesto"]
    eventos = manifiesto["audio"]["eventos"]
    assert [e[0] for e in eventos] == ["nebulosa", "pulso"]  # ordenados por t
    assert manifiesto["voz"]["secciones"][0]["texto"] == "Esto es una costa."


def test_importar_un_promo_del_repo(authed, tmp_path):
    d = tmp_path / "content" / "promos" / "promo-demo"
    d.mkdir(parents=True)
    (d / "style_block.py").write_text(STYLE)
    (d / "escena.py").write_text(VALID_SCRIPT)
    (d / "promo.json").write_text(json.dumps({
        "name": "El determinante", "curso": "Álgebra", "scene": "Demo",
        "file": "escena.py", "description": "un promo",
        "formatos": ["vertical"],
        "audio": {"pico_db": -3.0, "eventos": [["pulso", 5.3, -13]]},
        "voz": {"voz": "Charon",
                "secciones": [{"t_inicio": 0.8, "texto": "Una idea."}]},
    }, ensure_ascii=False))

    r = authed.post("/api/projects/importar",
                    json={"slug": "promo-demo", "origen": "promos"})
    assert r.status_code == 200, r.text
    detalle = authed.get(f"/api/projects/{r.json()['project_id']}").json()
    assert detalle["name"] == "Promo · El determinante"
    assert detalle["tipo"] == "promo" and detalle["formato"] == "vertical"
    assert detalle["quality"] == "qh"
    assert detalle["description"].startswith("[Álgebra]")
    assert len(detalle["clips"]) == 1 and detalle["clips"][0]["has_audio"]


# ── render en lote ───────────────────────────────────────────────────────

def test_render_lote_salta_los_al_dia_salvo_force(authed):
    from app.main import db

    project = _create_project(authed)
    pid = project["id"]
    hecho = _add_clip(authed, pid, "1 · Hecho")
    pendiente = _add_clip(authed, pid, "2 · Pendiente")
    _marcar_renderizado(db, pid, hecho["id"], "aaaa000011112222")

    r = authed.post(f"/api/projects/{pid}/render-lote", json={})
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["queued"]) == 1
    assert body["saltados"] == [{"clip_id": hecho["id"], "error": "al dia"}]
    assert body["lote_id"] and body["calidad_cambiada"] is None

    lote = authed.get(f"/api/projects/{pid}/lote").json()["lote"]
    assert lote["total"] == 1 and lote["lote_id"] == body["lote_id"]
    assert lote["saltados"] == 1

    # force encola tambien el que estaba al dia (el otro sigue en vuelo).
    r = authed.post(f"/api/projects/{pid}/render-lote",
                    json={"clips": [hecho["id"]], "force": True})
    assert r.status_code == 200, r.text
    assert len(r.json()["queued"]) == 1

    # Un clip que no es del proyecto -> 404.
    r = authed.post(f"/api/projects/{pid}/render-lote",
                    json={"clips": ["deadbeefdeadbeef"]})
    assert r.status_code == 404
    assert pendiente["id"]


def test_render_lote_cambia_la_calidad_del_proyecto(authed):
    from app.main import db

    project = _create_project(authed, quality="ql")
    pid = project["id"]
    uno = _add_clip(authed, pid, "1 · Uno")
    dos = _add_clip(authed, pid, "2 · Dos")
    _marcar_renderizado(db, pid, uno["id"], "bbbb000011112222")
    _marcar_renderizado(db, pid, dos["id"], "cccc000011112222")

    # PATCH normal: con renders vigentes la calidad esta bloqueada.
    assert authed.patch(f"/api/projects/{pid}",
                        json={"quality": "qh"}).status_code == 409

    # El lote SI la cambia: es el acto deliberado de rehacer el curso entero.
    r = authed.post(f"/api/projects/{pid}/render-lote", json={"calidad": "qh"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["calidad_cambiada"] == {"de": "ql", "a": "qh"}
    assert body["calidad"] == "qh"
    # La calidad no entra en el hash: sin el `force` implicito los dos clips
    # se habrian saltado por estar "al dia" con un video del tamano viejo.
    assert len(body["queued"]) == 2 and body["saltados"] == []
    assert authed.get(f"/api/projects/{pid}").json()["quality"] == "qh"

    # Con clips elegidos a dedo se rechaza: dejaria el curso con dos tamanos.
    r = authed.post(f"/api/projects/{pid}/render-lote",
                    json={"calidad": "ql", "clips": [uno["id"]]})
    assert r.status_code == 409
    r = authed.post(f"/api/projects/{pid}/render-lote", json={"calidad": "4k"})
    assert r.status_code == 422


def test_lote_derivado_de_los_jobs_tras_un_reinicio(authed):
    from app.main import db

    project = _create_project(authed)
    pid = project["id"]
    clip = _add_clip(authed, pid, "1 · Uno")

    ahora = time.time()
    # El pendiente es el MAS VIEJO: el corte del lote derivado es su
    # created_at, asi que los tres entran en el conteo.
    db.insert_job({"id": "dddd000011112222", "scene": "Demo", "quality": "ql",
                   "timeout": 120, "status": "queued", "script": VALID_SCRIPT,
                   "created_at": ahora - 300, "project_id": pid,
                   "clip_id": clip["id"], "content_hash": None})
    for i, (jid, dur) in enumerate([("eeee000011112222", 20.0),
                                    ("ffff000011112222", 40.0)]):
        db.insert_job({"id": jid, "scene": "Demo", "quality": "ql",
                       "timeout": 120, "status": "queued",
                       "script": VALID_SCRIPT, "created_at": ahora - 200 + i,
                       "project_id": pid, "clip_id": clip["id"],
                       "content_hash": None})
        db.update_job(jid, status="done", started_at=ahora - 100,
                      finished_at=ahora - 100 + dur, video_path="/tmp/x.mp4")

    lote = authed.get(f"/api/projects/{pid}/lote").json()["lote"]
    assert lote["derivado"] is True
    assert lote["total"] == 3 and lote["hechos"] == 2 and lote["pendientes"] == 1
    assert lote["activo"] is True
    assert lote["media_s"] == 30.0     # (20 + 40) / 2
    assert lote["eta_s"] == 30.0       # un job pendiente, ninguno corriendo


def test_lote_vacio_sin_jobs(authed):
    project = _create_project(authed)
    assert authed.get(
        f"/api/projects/{project['id']}/lote").json()["lote"] is None


# ── duplicar ─────────────────────────────────────────────────────────────

def test_duplicar_proyecto(authed):
    from app.main import db

    project = _create_project(authed, name="Curso original", quality="qm",
                              formato="vertical")
    pid = project["id"]
    uno = _add_clip(authed, pid, "1 · Uno")
    _add_clip(authed, pid, "2 · Dos")
    authed.patch(f"/api/projects/{pid}/clips/{uno['id']}",
                 json={"final_state": "queda esto", "notes": "nota"})
    db.update_clip(uno["id"], audio_json='{"audio": {"eventos": []}}')
    _marcar_renderizado(db, pid, uno["id"], "1111000011112222", quality="qm")

    r = authed.post(f"/api/projects/{pid}/duplicar",
                    json={"name": "Curso copia"})
    assert r.status_code == 201, r.text
    copia = r.json()
    assert copia["id"] != pid and copia["quality"] == "qm"
    assert copia["formato"] == "vertical"
    assert copia["style_block"] == STYLE

    detalle = authed.get(f"/api/projects/{copia['id']}").json()
    assert [c["title"] for c in detalle["clips"]] == ["1 · Uno", "2 · Dos"]
    assert detalle["clips"][0]["final_state"] == "queda esto"
    assert detalle["clips"][0]["notes"] == "nota"
    assert detalle["clips"][0]["has_audio"] is True
    # El render NO se copia: un video es de UN clip.
    assert detalle["clips"][0]["status"] == "no_render"
    assert detalle["clips"][0]["job_id"] is None

    # El nombre es la clave de emparejamiento del importador: no se repite.
    r = authed.post(f"/api/projects/{pid}/duplicar",
                    json={"name": "Curso copia"})
    assert r.status_code == 409


def test_duplicar_clip_lo_deja_justo_detras(authed):
    project = _create_project(authed)
    pid = project["id"]
    uno = _add_clip(authed, pid, "1 · Uno")
    _add_clip(authed, pid, "2 · Dos")
    authed.patch(f"/api/projects/{pid}/clips/{uno['id']}",
                 json={"final_state": "queda esto"})

    r = authed.post(f"/api/projects/{pid}/clips/{uno['id']}/duplicar")
    assert r.status_code == 201, r.text
    copia = r.json()
    assert copia["title"] == "1 · Uno (copia)"
    assert copia["position"] == 1

    detalle = authed.get(f"/api/projects/{pid}").json()
    assert [c["title"] for c in detalle["clips"]] == [
        "1 · Uno", "1 · Uno (copia)", "2 · Dos"]
    assert detalle["clips"][1]["final_state"] == "queda esto"
    assert detalle["clips"][1]["scene"] == "Demo"

    assert authed.post(
        f"/api/projects/{pid}/clips/deadbeef/duplicar").status_code == 404


# ── autenticacion ────────────────────────────────────────────────────────

def test_las_rutas_nuevas_piden_sesion(client):
    assert client.post("/api/projects/importar",
                       json={"slug": "x"}).status_code == 401
    assert client.get("/api/projects/importables").status_code == 401
    assert client.get("/api/projects/abc/fuentes.zip").status_code == 401
    assert client.post("/api/projects/abc/render-lote",
                       json={}).status_code == 401
    assert client.get("/api/projects/abc/lote").status_code == 401
    assert client.post("/api/projects/abc/duplicar",
                       json={"name": "x"}).status_code == 401
