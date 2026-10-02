"""Elementos orbitales reales (CelesTrak/18 SDS) con caché local y sello de época.

Reglas de CelesTrak que se respetan (comprobadas en su página el 2026-10-02): descargar solo cuando hace
falta (los datos cambian cada ~2 h), guardar una caché con sello de tiempo, identificarse con un
User-Agent y NO reintentar ante 403/404 (se usa la caché, aunque esté vieja, y se marca como tal).
Las piezas nunca llaman a la red durante el render: se descargan antes y se «congelan» en un JSON.
"""
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]                    # studio/content
CACHE = RAIZ / "datos_orbitales" / "cache"                    # ignorada en git
MUESTRAS = RAIZ / "datos_orbitales" / "muestras"              # datos congelados (versionados, para pruebas)
UA = "CoDeAerospace-contenido/1.0 (contacto@codeaerospace.com)"
URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR={norad}&FORMAT=json"


class EpocaCaducada(RuntimeError):
    """Los elementos son demasiado viejos para una pieza que promete una predicción."""


def _utc(texto):
    d = datetime.fromisoformat(texto)
    return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d.astimezone(timezone.utc)


@dataclass(frozen=True)
class Elementos:
    norad: int
    nombre: str
    epoca: datetime                 # UTC
    omm: dict                       # registro OMM tal cual lo entrega CelesTrak
    fuente: str                     # "celestrak"
    descargado: datetime            # UTC
    cache_vieja: bool = False       # True si se intentó refrescar y falló

    def edad_dias(self, ahora=None):
        return ((ahora or datetime.now(timezone.utc)) - self.epoca).total_seconds() / 86400


def _desde_registro(reg, descargado, fuente="celestrak", cache_vieja=False):
    return Elementos(int(reg["NORAD_CAT_ID"]), reg["OBJECT_NAME"], _utc(reg["EPOCH"]), reg, fuente, descargado, cache_vieja)


def cargar(ruta):
    """Lee elementos congelados con `congelar`."""
    d = json.loads(Path(ruta).read_text(encoding="utf-8"))
    return _desde_registro(d["omm"], _utc(d["descargado"]), d.get("fuente", "celestrak"))


def congelar(el, ruta):
    """Guarda los elementos tal cual, para reproducir una pieza igual más adelante."""
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    Path(ruta).write_text(json.dumps({"fuente": el.fuente, "descargado": el.descargado.isoformat(), "omm": el.omm},
                                     ensure_ascii=False, indent=1), encoding="utf-8")


def obtener(norad, max_edad_h=6.0, red=True, cache_dir=CACHE, ahora=None):
    """Elementos del objeto `norad`: de la caché si se descargaron hace menos de `max_edad_h` horas; si no,
    una descarga (y NO más si falla). Si no hay red ni caché lanza FileNotFoundError."""
    ahora = ahora or datetime.now(timezone.utc)
    ruta = Path(cache_dir) / f"celestrak_{int(norad)}.json"
    viejo = None
    if ruta.exists():
        viejo = cargar(ruta)
        if ahora - viejo.descargado < timedelta(hours=max_edad_h):
            return viejo
    if red:
        try:
            req = urllib.request.Request(URL.format(norad=int(norad)), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                datos = json.loads(r.read().decode("utf-8"))
            if datos and isinstance(datos, list):
                el = _desde_registro(datos[0], ahora)
                congelar(el, ruta)
                return el
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
            pass                                          # sin reintentos: se usa la caché, marcada como vieja
    if viejo is not None:
        return Elementos(viejo.norad, viejo.nombre, viejo.epoca, viejo.omm, viejo.fuente, viejo.descargado, True)
    raise FileNotFoundError(f"Sin caché ni red para el objeto {norad}")
