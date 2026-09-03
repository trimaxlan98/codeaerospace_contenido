"""Laboratorio: ejecutar Python de validacion en el sandbox.

La brecha que cierra: **las sondas**. `studio/tools/sonda_*.py` son el guardian
de cada libreria del repo —cada invariante con su contraejemplo, y una tabla de
cifras medidas— y se corrian SOLO desde la terminal. En la app no habia forma
de «verificar la libreria» antes de escribir un clip, ni de calcular una cifra
con numpy, ni de dibujar un PNG con PIL. El unico Python que la app sabia
ejecutar era una escena de manim, y solo para producir un mp4.

Tres decisiones, con su porque:

1. **No entra en la cola de renders.** `JobManager._run_job` esta construido
   alrededor de `runner.render()`: transmite el log de manim linea a linea por
   SSE, busca un mp4 al terminar, saca miniatura y resolucion, y guarda todo en
   columnas de la tabla `jobs` (`scene`, `quality`, `formato`, `video_path`…)
   que un script de laboratorio no tiene. Meterlo ahi obligaria a partir el
   worker en dos caminos y a inventar valores para media docena de columnas.
   Se hace lo que ya hacen `mezclar_audio` y `verificar_promo`, que tampoco
   pasan por la cola por la misma razon: **son segundos, no minutos**. Una
   sonda tarda entre 1 y 3 s.
2. **Pero solo una a la vez** (un `asyncio.Lock` con respuesta inmediata si
   esta ocupado). El VPS tiene 2 vCPU y el contenedor esta capado a 1.5; con
   este turno unico, lo peor que puede coincidir es un render largo y una
   sonda corta, y el tope de compose sigue mandando.
3. **El registro es el disco, no la base de datos.** Cada ejecucion es un
   directorio (`render_jobs/lab/<id>/`) con `script.py`, `meta.json` y lo que
   el script haya dejado. Sin migracion de esquema, y el historial sobrevive a
   un reinicio del backend sin sincronizar dos fuentes de verdad. Borrar una
   ejecucion es borrar su directorio.

Lo que NO cambia: ejecutar Python no confiable ya era el trabajo del sandbox
(una escena de manim es Python arbitrario). Las garantias son las de
`docker-compose.yml` — sin red, repo read-only, `cap_drop: ALL`,
`no-new-privileges`, 1.5 vCPU / 2 GB / 256 pids, `--rm` — y el unico
directorio escribible es el de la propia ejecucion.
"""

import asyncio
import json
import re
import shutil
import time
import uuid
from pathlib import Path

# Los mismos rangos que valida el runner (si uno cambia, el otro tambien).
TIMEOUT_MIN, TIMEOUT_MAX = 30, 900
TIMEOUT_DEFECTO = 120
# Una sonda son 1-3 s de numpy. El techo generoso es para que un dia que se
# ponga pesada no falle por el reloj, no para esperarla cinco minutos.
TIMEOUT_SONDA = 300
SALIDA_MAX = 200 * 1024
HISTORIAL_MAX = 30

RE_LAB_ID = re.compile(r"^[a-f0-9]{16}$")
RE_SONDA = re.compile(r"^[a-z0-9_]{1,32}$")
# Nombre de archivo producido: mismo conjunto cerrado que enumera el runner.
RE_ARCHIVO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
EXT_ARCHIVO = {".png", ".jpg", ".jpeg", ".svg", ".wav", ".txt", ".json",
               ".csv", ".md", ".log"}
# Los dos archivos del propio laboratorio. `script.py` ya cae por la
# extension, pero `meta.json` NO: sin esta lista, la ruta de archivos
# producidos serviria el registro interno de la ejecucion (con su stdout
# entero) como si fuera un resultado del script.
RESERVADOS = {"script.py", "meta.json"}
TIPO_MIME = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml", ".wav": "audio/wav", ".txt": "text/plain",
    ".json": "application/json", ".csv": "text/csv", ".md": "text/markdown",
    ".log": "text/plain",
}

# Plantilla del editor: corta, real y verificable de un vistazo. Usa numpy,
# una libreria del repo y PIL, que es exactamente lo que un script de
# validacion necesita saber que tiene a mano.
PLANTILLA = '''"""Laboratorio — Python en el sandbox (sin red, repo de solo lectura).

Todo lo que dejes en este directorio (PNG, WAV, TXT, JSON, CSV) vuelve como
resultado. `import <libreria>` funciona igual que en una sonda: el PYTHONPATH
ya apunta a studio/content/manim_extensions.
"""
import numpy as np
from PIL import Image

from code_brand import CODE_ACCENT, CODE_BG

print("numpy", np.__version__)
print("paleta de la marca:", CODE_BG, CODE_ACCENT)

# Una figura minima: la senal que se mide, no la que se declara.
t = np.linspace(0, 1, 480, endpoint=False)
y = np.sin(2 * np.pi * 3 * t) * np.exp(-2 * t)
print(f"pico {y.max():.4f}   energia {np.sum(y ** 2):.4f}")

def rgb(css):
    return tuple(int(css[i:i + 2], 16) for i in (1, 3, 5))


alto = 240
lienzo = np.zeros((alto, t.size, 3), dtype=np.uint8)
lienzo[:, :] = rgb(CODE_BG)
fila = ((0.5 - 0.45 * y) * (alto - 1)).astype(int)
for x, f in enumerate(fila):
    lienzo[max(0, f - 1):f + 2, x] = rgb(CODE_ACCENT)
Image.fromarray(lienzo).save("figura.png")
print("figura.png escrita")
'''


class LaboratorioError(Exception):
    pass


def _resumen(stdout: str) -> str:
    """La ultima linea con contenido: en una sonda es el veredicto
    («18 invariantes ok, 0 fallos»), que es lo que se quiere ver en la lista
    del historial sin abrir la ejecucion."""
    for linea in reversed((stdout or "").splitlines()):
        limpio = linea.strip()
        if limpio and not set(limpio) <= set("=-_ "):
            return limpio[:160]
    return ""


class LaboratorioService:
    def __init__(self, cfg, runner) -> None:
        self.cfg = cfg
        self.runner = runner
        self.dir = Path(cfg.render_jobs_dir) / "lab"
        self._lock = asyncio.Lock()
        self._corriendo: str | None = None

    # ── sondas del repo ──────────────────────────────────────────────────────

    def sondas(self) -> list[dict]:
        """`studio/tools/sonda_*.py`, con la primera linea de su docstring.

        La lista sale del disco, no de una constante: una sonda nueva aparece
        en la app el dia que se escribe.
        """
        tools = Path(self.cfg.workspace) / "studio" / "tools"
        salida = []
        if not tools.is_dir():
            return salida
        for ruta in sorted(tools.glob("sonda_*.py")):
            nombre = ruta.stem[len("sonda_"):]
            if not RE_SONDA.match(nombre):
                continue
            salida.append({"nombre": nombre, "archivo": ruta.name,
                           "bytes": ruta.stat().st_size,
                           "que": self._titulo(ruta)})
        return salida

    @staticmethod
    def _titulo(ruta: Path) -> str:
        """Primera linea util del docstring (sin ejecutar nada)."""
        try:
            with ruta.open("r", encoding="utf-8", errors="replace") as fh:
                for linea in fh:
                    limpio = linea.strip()
                    if limpio.startswith(('"""', "'''")):
                        return limpio.strip('"\' ')[:120]
                    if limpio.startswith("#!") or not limpio:
                        continue
                    return ""
        except OSError:
            pass
        return ""

    def existe_sonda(self, nombre: str) -> bool:
        return bool(RE_SONDA.match(nombre or "")) and any(
            s["nombre"] == nombre for s in self.sondas())

    # ── registro en disco ────────────────────────────────────────────────────

    def _meta_path(self, lab_id: str) -> Path:
        return self.dir / lab_id / "meta.json"

    def _leer(self, lab_id: str) -> dict | None:
        if not RE_LAB_ID.match(lab_id):
            return None
        try:
            return json.loads(self._meta_path(lab_id).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def _escribir(self, meta: dict) -> None:
        ruta = self._meta_path(meta["id"])
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")

    def listar(self, limite: int = HISTORIAL_MAX) -> list[dict]:
        if not self.dir.is_dir():
            return []
        metas = []
        for hijo in self.dir.iterdir():
            if not hijo.is_dir():
                continue
            meta = self._leer(hijo.name)
            if meta:
                metas.append(publico(meta, breve=True))
        metas.sort(key=lambda m: m.get("creado") or 0, reverse=True)
        return metas[:limite]

    def obtener(self, lab_id: str) -> dict | None:
        meta = self._leer(lab_id)
        return publico(meta) if meta else None

    def borrar(self, lab_id: str) -> bool:
        if not RE_LAB_ID.match(lab_id):
            return False
        if lab_id == self._corriendo:
            raise LaboratorioError("Esa ejecución está en curso")
        destino = self.dir / lab_id
        if not destino.is_dir():
            return False
        shutil.rmtree(destino, ignore_errors=True)
        return True

    def archivo(self, lab_id: str, nombre: str) -> tuple[Path, str]:
        """Ruta de un archivo producido, con su tipo MIME.

        Defensa en profundidad identica a la de `/api/jobs/{id}/thumb`: el
        nombre pasa un regex anclado Y la ruta resuelta tiene que caer dentro
        del directorio de la ejecucion.
        """
        if not RE_LAB_ID.match(lab_id) or not RE_ARCHIVO.match(nombre):
            raise LaboratorioError("Archivo no disponible")
        ext = Path(nombre).suffix.lower()
        if nombre in RESERVADOS or ext not in EXT_ARCHIVO:
            raise LaboratorioError("Archivo no disponible")
        base = (self.dir / lab_id).resolve()
        ruta = (base / nombre).resolve()
        if not ruta.is_file() or ruta.parent != base:
            raise LaboratorioError("Archivo no disponible")
        return ruta, TIPO_MIME.get(ext, "application/octet-stream")

    # ── ejecucion ────────────────────────────────────────────────────────────

    @property
    def ocupado(self) -> bool:
        return self._corriendo is not None

    def crear(self, script: str | None, timeout: int,
              sonda: str | None = None, titulo: str = "") -> dict:
        """Valida, escribe el directorio y APARTA el turno. No ejecuta.

        Sincrono a proposito: reservar el turno dentro de una corrutina deja
        una ventana entre la comprobacion y el `await` por la que se cuelan
        dos ejecuciones a la vez. Aqui, entre el `if` y el `_corriendo = id`
        no hay ningun punto de suspension.
        """
        if sonda is not None:
            if not self.existe_sonda(sonda):
                raise LaboratorioError("Esa sonda no existe")
        elif not (script or "").strip():
            raise LaboratorioError("El script está vacío")
        if not (TIMEOUT_MIN <= timeout <= TIMEOUT_MAX):
            raise LaboratorioError(
                f"Timeout fuera de rango ({TIMEOUT_MIN}–{TIMEOUT_MAX}s)")
        if self._corriendo is not None:
            raise LaboratorioError("Ya hay una ejecución en curso")

        lab_id = uuid.uuid4().hex[:16]
        destino = self.dir / lab_id
        destino.mkdir(parents=True, exist_ok=True)
        if sonda is None:
            (destino / "script.py").write_text(script, encoding="utf-8")
        ahora = time.time()
        meta = {
            "id": lab_id, "creado": ahora, "timeout": timeout,
            "sonda": sonda,
            "titulo": (titulo or (f"sonda {sonda}" if sonda else "script"))[:80],
            "estado": "corriendo", "code": None, "timed_out": False,
            "stdout": "", "stderr": "", "archivos": [],
            "inicio": ahora, "fin": None,
        }
        self._escribir(meta)
        self._corriendo = lab_id
        return publico(meta)

    async def correr(self, lab_id: str) -> dict:
        """Ejecuta en el sandbox la ejecucion que `crear` dejo apartada."""
        meta = self._leer(lab_id)
        if meta is None:
            raise LaboratorioError("Esa ejecución no existe")
        async with self._lock:
            try:
                res = await self.runner.ejecutar(lab_id, meta["timeout"],
                                                 meta.get("sonda"))
                meta |= {
                    "code": res.get("code"),
                    "timed_out": bool(res.get("timed_out")),
                    "stdout": (res.get("stdout") or "")[:SALIDA_MAX],
                    "stderr": (res.get("stderr") or "")[:SALIDA_MAX],
                    "archivos": res.get("archivos") or [],
                }
                # `code != 0` no es un fallo del laboratorio: es el resultado.
                # Una sonda con invariantes rotos sale con 1 A PROPOSITO, y
                # tapar eso con un error rojo seria perder justo la senal.
                meta["estado"] = ("timeout" if meta["timed_out"]
                                  else "ok" if meta["code"] == 0
                                  else "salida")
            except Exception as e:  # noqa: BLE001 - runner caido, timeout…
                meta |= {"estado": "error", "stderr": str(e)}
            finally:
                if self._corriendo == lab_id:
                    self._corriendo = None
                meta["fin"] = time.time()
                self._escribir(meta)
        return publico(meta)

    async def ejecutar(self, script: str | None, timeout: int,
                       sonda: str | None = None, titulo: str = "") -> dict:
        """`crear` + `correr` en una sola espera (lo usan los tests)."""
        meta = self.crear(script, timeout, sonda, titulo)
        return await self.correr(meta["id"])


def publico(meta: dict, breve: bool = False) -> dict:
    """Vista para la API. En la lista, la salida NO viaja: 30 ejecuciones con
    200 KB de stdout cada una son 6 MB por cada refresco del historial."""
    base = {k: meta.get(k) for k in
            ("id", "creado", "estado", "code", "timed_out", "sonda", "titulo",
             "timeout", "inicio", "fin")}
    base["duracion_s"] = (round(meta["fin"] - meta["inicio"], 2)
                          if meta.get("fin") and meta.get("inicio") else None)
    base["resumen"] = _resumen(meta.get("stdout", ""))
    base["n_archivos"] = len(meta.get("archivos") or [])
    if breve:
        return base
    return base | {"stdout": meta.get("stdout", ""),
                   "stderr": meta.get("stderr", ""),
                   "archivos": meta.get("archivos") or []}
