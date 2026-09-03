"""Laboratorio: ejecutar Python de validacion en el sandbox (sprint R3b).

La ejecucion de verdad corre en el contenedor (comando `ejecutar` del runner);
aqui se prueba lo que decide la app: que entra, que turno hay, que se guarda,
que se sirve y que NO se sirve.
"""

import json
import time

import pytest

SCRIPT = "print('hola')\n"

SALIDA = {
    "code": 0, "timed_out": False,
    "stdout": "numpy 2.5.2\n18 invariantes ok, 0 fallos\n",
    "stderr": "",
    "archivos": [{"nombre": "figura.png", "bytes": 812}],
}


def _esperar(authed, lab_id, intentos=60):
    """La ejecucion se lanza en segundo plano: se pregunta hasta que acabe.

    TestClient corre el bucle en otro hilo; sin este bucle el test leeria
    'corriendo' y no probaria nada.
    """
    for _ in range(intentos):
        d = authed.get(f"/api/laboratorio/{lab_id}").json()
        if d["estado"] != "corriendo":
            return d
        time.sleep(0.05)
    raise AssertionError(f"la ejecucion {lab_id} no termino")


@pytest.fixture()
def con_tools(authed):
    """Las herramientas REALES del repo dentro del workspace de prueba.

    El servicio busca las sondas en `<workspace>/studio/tools` porque esa es
    la ruta que el runner ejecuta dentro del contenedor
    (`/workspace/studio/tools/sonda_<x>.py`): las dos tienen que mirar al
    mismo sitio o la app ofreceria una sonda que el runner no encuentra. En
    los tests el workspace es un tmp_path, asi que se enlazan los archivos de
    verdad —sondas y herramientas que NO lo son, para que el filtro tenga algo
    que descartar.
    """
    from pathlib import Path

    from app.main import cfg
    origen = Path(__file__).resolve().parents[2] / "tools"
    destino = Path(cfg.workspace) / "studio" / "tools"
    destino.mkdir(parents=True, exist_ok=True)
    for ruta in origen.glob("*.py"):
        enlace = destino / ruta.name
        if not enlace.exists():
            enlace.symlink_to(ruta)
    return authed


def _falso_runner(monkeypatch, salida=None, registro=None):
    from app.main import runner

    async def ejecutar(lab_id, timeout, sonda=None):
        if registro is not None:
            registro.append({"lab_id": lab_id, "timeout": timeout,
                             "sonda": sonda})
        return dict(salida or SALIDA)

    monkeypatch.setattr(runner, "ejecutar", ejecutar)


# ── ejecutar un script ───────────────────────────────────────────────────────

def test_un_script_se_guarda_corre_y_devuelve_su_salida(authed, monkeypatch):
    from app.main import cfg
    registro = []
    _falso_runner(monkeypatch, registro=registro)

    r = authed.post("/api/laboratorio", json={"script": SCRIPT, "timeout": 60,
                                              "titulo": "prueba"})
    assert r.status_code == 202
    lab_id = r.json()["id"]
    # El script se escribe en la ruta canonica que el runner espera.
    guardado = cfg.render_jobs_dir / "lab" / lab_id / "script.py"
    assert guardado.read_text() == SCRIPT

    d = _esperar(authed, lab_id)
    assert registro == [{"lab_id": lab_id, "timeout": 60, "sonda": None}]
    assert d["estado"] == "ok" and d["code"] == 0
    assert "18 invariantes ok" in d["stdout"]
    # El resumen del historial es la ultima linea util, que en una sonda es
    # justamente el veredicto.
    assert d["resumen"] == "18 invariantes ok, 0 fallos"
    assert d["archivos"] == [{"nombre": "figura.png", "bytes": 812}]
    assert d["titulo"] == "prueba"


def test_un_exit_1_no_es_un_error_del_laboratorio(authed, monkeypatch):
    """Una sonda con invariantes rotos sale con 1 A PROPOSITO: pintar eso
    como fallo del sistema seria perder justo la señal que se buscaba."""
    _falso_runner(monkeypatch, salida={**SALIDA, "code": 1,
                                       "stdout": "3 invariantes ok, 2 fallos\n"})
    lab_id = authed.post("/api/laboratorio", json={"script": SCRIPT}).json()["id"]
    d = _esperar(authed, lab_id)
    assert d["estado"] == "salida" and d["code"] == 1
    assert d["resumen"] == "3 invariantes ok, 2 fallos"


def test_el_timeout_se_distingue_de_una_salida_distinta_de_cero(authed, monkeypatch):
    _falso_runner(monkeypatch, salida={**SALIDA, "code": 124, "timed_out": True})
    lab_id = authed.post("/api/laboratorio", json={"script": SCRIPT}).json()["id"]
    assert _esperar(authed, lab_id)["estado"] == "timeout"


def test_el_runner_caido_deja_la_ejecucion_en_error(authed, monkeypatch):
    from app.main import runner
    from app.runner_client import RunnerError

    async def ejecutar(lab_id, timeout, sonda=None):
        raise RunnerError("runner no disponible")

    monkeypatch.setattr(runner, "ejecutar", ejecutar)
    lab_id = authed.post("/api/laboratorio", json={"script": SCRIPT}).json()["id"]
    d = _esperar(authed, lab_id)
    assert d["estado"] == "error" and "no disponible" in d["stderr"]


@pytest.mark.parametrize("body", [
    {"script": ""},                       # vacio
    {"timeout": 60},                      # sin script
    {"script": SCRIPT, "timeout": 29},    # por debajo del minimo
    {"script": SCRIPT, "timeout": 901},   # por encima del maximo
    {"script": SCRIPT, "timeout": "mucho"},
])
def test_parametros_invalidos(authed, body):
    assert authed.post("/api/laboratorio", json=body).status_code == 422


def test_un_script_de_solo_espacios_tampoco_vale(authed):
    r = authed.post("/api/laboratorio", json={"script": "   \n\t\n"})
    assert r.status_code == 409  # pasa el min_length, lo caza el servicio


def test_un_script_enorme_es_413(authed):
    from app.main import cfg
    grande = "x = 1\n" * (cfg.max_script_bytes // 6 + 100)
    assert authed.post("/api/laboratorio",
                       json={"script": grande}).status_code == 413


def test_solo_una_ejecucion_a_la_vez(authed, monkeypatch):
    """2 vCPU: el turno es unico, y quien llega segundo lo sabe al instante."""
    import asyncio

    from app.main import runner
    puerta = asyncio.Event()

    async def ejecutar(lab_id, timeout, sonda=None):
        await puerta.wait()
        return dict(SALIDA)

    monkeypatch.setattr(runner, "ejecutar", ejecutar)
    primera = authed.post("/api/laboratorio", json={"script": SCRIPT})
    assert primera.status_code == 202
    segunda = authed.post("/api/laboratorio", json={"script": SCRIPT})
    assert segunda.status_code == 409
    assert authed.get("/api/laboratorio").json()["ocupado"] is True


# ── sondas ───────────────────────────────────────────────────────────────────

def test_la_lista_de_sondas_son_las_del_repo(con_tools):
    d = con_tools.get("/api/laboratorio/sondas").json()
    nombres = [s["nombre"] for s in d["sondas"]]
    # Salen del disco, no de una constante: una sonda nueva aparece sola.
    assert "sistemas" in nombres and "atp" in nombres
    # Solo `sonda_*.py`: ni las herramientas ni los modulos del paquete.
    for s in d["sondas"]:
        assert s["archivo"] == f"sonda_{s['nombre']}.py"
    for prohibido in ("render_local", "ensamblar", "sfx", "hoja_contactos"):
        assert prohibido not in nombres
    # La descripcion es la primera linea del docstring, leida sin ejecutar.
    sistemas = next(s for s in d["sondas"] if s["nombre"] == "sistemas")
    assert "sistemas.py" in sistemas["que"]


def test_correr_una_sonda_la_ejecuta_tal_cual(con_tools, monkeypatch):
    """La sonda no se copia al directorio: se corre el archivo del repo, que
    va montado read-only. Del exterior solo llega su nombre."""
    registro = []
    _falso_runner(monkeypatch, registro=registro)
    r = con_tools.post("/api/laboratorio/sondas/sistemas")
    assert r.status_code == 202
    lab_id = r.json()["id"]
    d = _esperar(con_tools, lab_id)
    assert registro[0]["sonda"] == "sistemas"
    assert d["sonda"] == "sistemas" and d["titulo"] == "sonda sistemas"


@pytest.mark.parametrize("nombre", [
    "noexiste", "sistemas.py", "../ensamblar", "SISTEMAS", "",
])
def test_una_sonda_que_no_existe_es_404(authed, nombre):
    r = authed.post(f"/api/laboratorio/sondas/{nombre}")
    assert r.status_code in (404, 405)


# ── archivos producidos ──────────────────────────────────────────────────────

def test_los_archivos_producidos_se_sirven_y_no_dejan_salir(authed, monkeypatch):
    from app.main import cfg
    _falso_runner(monkeypatch)
    lab_id = authed.post("/api/laboratorio", json={"script": SCRIPT}).json()["id"]
    _esperar(authed, lab_id)
    base = cfg.render_jobs_dir / "lab" / lab_id
    (base / "figura.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (base / "medidas.json").write_text('{"pico": -1.6}')

    r = authed.get(f"/api/laboratorio/{lab_id}/archivos/figura.png")
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"
    r = authed.get(f"/api/laboratorio/{lab_id}/archivos/medidas.json")
    assert r.status_code == 200 and json.loads(r.content)["pico"] == -1.6

    # Ni traversal, ni el propio script, ni extensiones fuera de la lista.
    for malo in ("../scene.py", "..%2Fmeta.json", "script.py", "figura.exe",
                 "meta.json", "no-esta.png"):
        assert authed.get(
            f"/api/laboratorio/{lab_id}/archivos/{malo}").status_code in (404, 405)


def test_el_historial_no_arrastra_la_salida(authed, monkeypatch):
    """30 ejecuciones con 200 KB de stdout serian 6 MB por refresco."""
    _falso_runner(monkeypatch)
    lab_id = authed.post("/api/laboratorio", json={"script": SCRIPT}).json()["id"]
    _esperar(authed, lab_id)
    fila = authed.get("/api/laboratorio").json()["ejecuciones"][0]
    assert fila["id"] == lab_id
    assert "stdout" not in fila and "stderr" not in fila
    assert fila["resumen"] and fila["n_archivos"] == 1


def test_borrar_una_ejecucion_borra_su_directorio(authed, monkeypatch):
    from app.main import cfg
    _falso_runner(monkeypatch)
    lab_id = authed.post("/api/laboratorio", json={"script": SCRIPT}).json()["id"]
    _esperar(authed, lab_id)
    assert authed.delete(f"/api/laboratorio/{lab_id}").status_code == 200
    assert not (cfg.render_jobs_dir / "lab" / lab_id).exists()
    assert authed.get(f"/api/laboratorio/{lab_id}").status_code == 404
    assert authed.delete(f"/api/laboratorio/{lab_id}").status_code == 404


def test_un_id_inventado_no_toca_el_disco(authed):
    for malo in ("..", "../../etc", "zzzz", "0" * 64):
        assert authed.get(f"/api/laboratorio/{malo}").status_code in (404, 405)


def test_la_plantilla_del_editor_llega_con_el_listado(authed):
    d = authed.get("/api/laboratorio").json()
    assert "import numpy as np" in d["plantilla"]
    assert "from PIL import Image" in d["plantilla"]
    assert d["timeout"] == {"min": 30, "max": 900, "defecto": 120}


def test_laboratorio_requiere_sesion(client):
    assert client.get("/api/laboratorio").status_code == 401
    assert client.get("/api/laboratorio/sondas").status_code == 401
    assert client.post("/api/laboratorio",
                       json={"script": SCRIPT}).status_code == 401
    assert client.post("/api/laboratorio/sondas/sistemas").status_code == 401


# ── el servicio y el runner no pueden separarse ──────────────────────────────

def test_los_rangos_de_timeout_son_los_del_runner():
    import ast
    from pathlib import Path

    from app import laboratorio as lab_mod

    ruta = Path(__file__).resolve().parents[3] / "studio" / "runner" / "manim_runner.py"
    arbol = ast.parse(ruta.read_text())
    valores = None
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.Assign)
                and isinstance(nodo.targets[0], ast.Tuple)
                and [getattr(t, "id", "") for t in nodo.targets[0].elts]
                == ["LAB_TIMEOUT_MIN", "LAB_TIMEOUT_MAX"]):
            valores = ast.literal_eval(nodo.value)
    assert valores == (lab_mod.TIMEOUT_MIN, lab_mod.TIMEOUT_MAX)


def test_el_laboratorio_corre_en_el_contenedor_sin_red_y_con_el_repo_ro():
    """Las garantias del sandbox no son opcionales para el comando nuevo:
    tiene que usar el MISMO servicio de compose que un render (`manim-render`,
    `network_mode: none`, repo read-only) y montar rw SOLO su directorio."""
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[3]
    fuente = (raiz / "studio" / "runner" / "manim_runner.py").read_text()
    bloque = fuente.split("async def handle_ejecutar")[1].split("\n# ──")[0]
    assert '"manim-render"' in bloque
    assert 'COMPOSE_FILE' in bloque and '"--profile", "render"' in bloque
    assert ':rw"' in bloque and "lab_mount" in bloque
    # Nada de montar el repo entero con escritura ni el resto de render_jobs.
    assert "montaje_render_jobs()" not in bloque
    compose = (raiz / "docker-compose.yml").read_text()
    assert 'network_mode: "none"' in compose
    assert "- .:/workspace:ro" in compose
