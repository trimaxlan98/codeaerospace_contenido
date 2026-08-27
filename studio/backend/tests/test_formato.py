"""Formato del lienzo (sprint P1 de promos): proporcion, tipo y lienzo.

Lo que se prueba aqui es la cadena entera de un dato que hasta ahora no
existia: el proyecto declara un formato, el job lo hereda y el cliente del
runner se lo manda al contenedor. Si cualquiera de los tres eslabones se
cae, un promo sale en 16:9 con bandas negras — que es exactamente lo que
este sprint viene a evitar.
"""

import asyncio
import json

import pytest

from app.db import Database
from app.projects import QUALITY_SPECS, ProjectService, specs

VALID_SCRIPT = (
    "from manim import *\n"
    "class Promo(Scene):\n"
    "    def construct(self):\n"
    "        self.play(Create(Circle()))\n"
)


@pytest.fixture()
def svc(tmp_path):
    db = Database(tmp_path / "t.db")
    yield ProjectService(db)
    db.close()


# ── la tabla de formatos ─────────────────────────────────────────────────────

def test_horizontal_es_la_tabla_de_manim():
    # En 16:9 mandan los numeros del flag -q: 854x480 no es exactamente
    # 16:9 y es lo que produce manim. Anunciar otra cosa seria mentir.
    for q, base in QUALITY_SPECS.items():
        s = specs(q, "horizontal")
        assert s["resolution"] == base["resolution"]
        assert s["fps"] == base["fps"]


def test_vertical_gira_el_lienzo_sin_encoger_el_lado_corto():
    # La calidad fija el LADO CORTO, no el alto: 1080p vertical son
    # 1080x1920, no 607x1080.
    assert specs("qh", "vertical")["resolution"] == "1080x1920"
    assert specs("qm", "vertical")["resolution"] == "720x1280"
    assert specs("qh", "vertical")["fps"] == 60


def test_cuadrado_y_lados_pares():
    assert specs("qh", "cuadrado")["resolution"] == "1080x1080"
    # libx264 exige lados pares: 480 * 16/9 = 853.33 -> 852, no 853.
    assert specs("ql", "vertical")["resolution"] == "480x852"
    for q in QUALITY_SPECS:
        for f in ("horizontal", "vertical", "cuadrado"):
            s = specs(q, f)
            assert s["width"] % 2 == 0 and s["height"] % 2 == 0


def test_specs_rechaza_lo_que_no_conoce():
    with pytest.raises(ValueError):
        specs("q4k", "vertical")
    with pytest.raises(ValueError):
        specs("qh", "panoramico")


# ── el proyecto ──────────────────────────────────────────────────────────────

def test_proyecto_por_defecto_sigue_siendo_un_curso_16_9(svc):
    p = svc.create_project("Curso", "", "qh", "")
    assert p["tipo"] == "curso"
    assert p["formato"] == "horizontal"
    assert svc.get_project_detail(p["id"])["specs"]["resolution"] == "1920x1080"


def test_promo_vertical(svc):
    p = svc.create_project("Promo", "", "qh", "", tipo="promo",
                           formato="vertical")
    detalle = svc.get_project_detail(p["id"])
    assert detalle["tipo"] == "promo"
    assert detalle["specs"]["resolution"] == "1080x1920"


def test_formato_se_bloquea_con_render_vigente(svc):
    p = svc.create_project("Promo", "", "qh", "", tipo="promo",
                           formato="vertical")
    # Sin render, el formato se cambia (es el punto del sprint: el mismo
    # archivo sale en 9:16 y en 16:9).
    svc.update_project(p["id"], formato="horizontal")
    assert svc.db.get_project(p["id"])["formato"] == "horizontal"

    clip = svc.add_clip(p["id"], "Uno", VALID_SCRIPT, "Promo")
    svc.db.update_clip(clip["id"], job_id="job1", rendered_hash="h")
    with pytest.raises(ValueError, match="formato"):
        svc.update_project(p["id"], formato="vertical")


# ── la API ───────────────────────────────────────────────────────────────────

def _crear_promo(authed):
    r = authed.post("/api/projects", json={
        "name": "Promo redes", "quality": "qh", "tipo": "promo",
        "formato": "vertical", "style_block": ""})
    assert r.status_code == 201
    return r.json()


def test_api_crea_promo_vertical(authed):
    p = _crear_promo(authed)
    assert p["tipo"] == "promo" and p["formato"] == "vertical"
    detalle = authed.get(f"/api/projects/{p['id']}").json()
    assert detalle["specs"] == {"resolution": "1080x1920", "fps": 60,
                                "width": 1080, "height": 1920, "corto": 1080,
                                "formato": "vertical"}


def test_api_rechaza_formato_y_tipo_desconocidos(authed):
    r = authed.post("/api/projects", json={"name": "X", "quality": "qh",
                                           "formato": "panoramico"})
    assert r.status_code == 422
    r = authed.post("/api/projects", json={"name": "X", "quality": "qh",
                                           "tipo": "pelicula"})
    assert r.status_code == 422


def test_el_job_hereda_el_formato_del_proyecto(authed):
    p = _crear_promo(authed)
    r = authed.post(f"/api/projects/{p['id']}/clips",
                    json={"title": "Bucle", "script": VALID_SCRIPT,
                          "scene": "Promo"})
    cid = r.json()["id"]
    job = authed.post(f"/api/projects/{p['id']}/clips/{cid}/render").json()
    assert job["formato"] == "vertical"
    # Y sobrevive al listado (viene de la fila, no del objeto en memoria).
    listado = {j["id"]: j for j in authed.get("/api/jobs").json()["jobs"]}
    assert listado[job["id"]]["formato"] == "vertical"
    # La resolucion se MIDE al terminar; mientras tanto es None, no un valor
    # supuesto a partir de la calidad.
    assert listado[job["id"]]["resolution"] is None


# ── el protocolo con el runner ───────────────────────────────────────────────

def test_el_cliente_del_runner_manda_el_lienzo(tmp_path):
    from app.runner_client import RunnerClient

    sock = tmp_path / "runner.sock"
    recibido: dict = {}

    async def correr():
        async def atender(reader, writer):
            recibido.update(json.loads(await reader.readline()))
            writer.write(b'{"type": "done", "exit_code": 0, "timed_out": false}\n')
            await writer.drain()
            writer.close()

        server = await asyncio.start_unix_server(atender, path=str(sock))
        try:
            cliente = RunnerClient(str(sock))
            return [e async for e in cliente.render(
                "abcdef0123456789", "Promo", "qh", 600,
                formato="vertical", corto=1080, largo=1920, fps=60)]
        finally:
            server.close()
            await server.wait_closed()

    eventos = asyncio.run(correr())
    assert eventos[-1]["type"] == "done"
    assert recibido["formato"] == "vertical"
    assert recibido["corto"] == 1080
    assert recibido["largo"] == 1920
    assert recibido["fps"] == 60
