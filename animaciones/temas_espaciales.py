"""Temas (entornos) de las presentaciones espaciales: registro, plugins y temas derivados.

Un TEMA es un look completo y intercambiable de una presentación: fondo procedural por tipo de diapositiva,
tipografías, paleta, cómo se enmarca el video (fundido · monitor · tarjeta) y decoración. Las presentaciones
no saben de temas concretos: piden uno al registro, así que se puede
  · construir el mismo deck en cualquier tema,
  · mezclar varios temas en un deck (uno por sección),
  · agregar temas nuevos sin tocar el código del constructor.

Incluidos: orbita · mision · nebulosa · estacion. Para agregar más:
  1. JSON derivado — animaciones/temas/<id>.json (o en la carpeta de CODE_TEMAS_DIR):
       {"id": "aurora", "nombre": "Aurora", "base": "orbita", "tinte": 140,
        "descripcion": "Órbita girada al verde", "color": {"acento": "#7CFFB2"}, "fuentes": {"titulo": "Orbitron"}}
     Toma un tema existente (`base`), gira el matiz del fondo y de la paleta (`tinte`, en grados) y aplica los cambios.
  2. Plugin Python — animaciones/temas/<id>.py que llame `registrar(Tema(...))` (y, si trae fondo propio,
     `fondos_espaciales.registrar_generador("mi_fondo", funcion)`).
  Los archivos que empiezan con «_» se ignoran (plantillas).
  Crear desde la línea de comandos: python3 temas_espaciales.py --nuevo aurora --base orbita --tinte 140
  Listar:                           python3 temas_espaciales.py --lista
Reglas del tema con `video="fundido"`: el video se recolorea a `pantalla` y la diapositiva queda exacta en el
borde del video (los fondos de `fondos_espaciales.py` ya lo respetan con el parámetro `zona`).
"""
import importlib.util
import json
import os
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fondos_espaciales as F  # noqa: E402

DIR_TEMAS = Path(__file__).parent / "temas"
TEMA_OFICIAL = "orbita"  # elegido por el dueño (2026-09-30): lo que se construye si no se pide otro tema

# rectángulo del video (x, y, w, h en pulgadas) según cómo se enmarca
ZONA = {
    "fundido": (1.822, 1.5, 9.689, 5.45),
    "monitor": (2.133, 1.80, 9.067, 5.1),
    "tarjeta": (2.044, 1.72, 9.244, 5.2),
}
ALIAS = {"tema": "modo", "modo_video": "video"}  # compatibilidad con el acceso tipo dict del constructor


@dataclass
class Tema:
    id: str
    nombre: str
    fuentes: dict                      # titulo, display, cuerpo, etiqueta (nombres de fuente de Google Fonts)
    color: dict                        # tinta, tenue, acento, acento2, calido, linea, panel
    descripcion: str = ""
    modo: str = "oscuro"               # tema de los videos Manim que usa: oscuro | claro
    pantalla: str | None = None        # color al que se recolorea el fondo del video (None = no se toca)
    video: str = "fundido"             # fundido | monitor | tarjeta
    ancho_car: dict = field(default_factory=lambda: dict(titulo=0.5, cuerpo=0.52))  # ancho medio del carácter (em)
    k_titulo: float = 1.0              # factor de tamaño de títulos (Rajdhani es estrecha: >1)
    portada_ancho: float = 7.3         # ancho de la columna de texto de la portada (in)
    esquinas: bool = False             # escuadras de instrumento en esquinas, stickers y monitor; coordenadas en portada
    cierre_derecha: bool = False       # el texto del cierre va a la derecha (el fondo pone el arte a la izquierda)
    generador: object = "orbita"       # nombre en fondos_espaciales.GENERADORES o función(tipo, var, zona)
    tinte: float = 0.0                 # giro de matiz (grados) que se aplica al fondo (temas derivados)
    base: str | None = None            # id del tema del que deriva
    manim: dict | None = None          # fuente y paleta DENTRO de los videos Manim (ver code_lib.py, CODE_TEMA_VISUAL):
    #   FUENTE, FUENTE_CIFRA, PESO_CIFRA, ESCALA_TEXTO (vs Carlito), FONDO (= pantalla), TINTA, TENUE, C_EJE, C_TIERRA,
    #   C_TIERRA_2, C_SAT, C_ANT, C_CIELO, C_MAL, C_OK, C_PANEL. None = el video conserva Carlito y su paleta.

    def __getitem__(self, k):
        return getattr(self, ALIAS.get(k, k))

    @property
    def zona(self):
        return ZONA[self.video]

    def fondo(self, tipo, var=0, rehacer=False):
        z = self.zona if tipo == "video" else None
        return F.fondo(self.id, self.generador, tipo, var, z, self.tinte, rehacer)


TEMAS: dict[str, Tema] = {}


def registrar(tema: Tema, reemplazar=False):
    if tema.id in TEMAS and not reemplazar:
        raise ValueError(f"ya existe el tema {tema.id!r}")
    TEMAS[tema.id] = tema
    return tema


def obtener(id_) -> Tema:
    if id_ not in TEMAS:
        raise KeyError(f"tema {id_!r} no registrado; hay: {', '.join(TEMAS)}")
    return TEMAS[id_]


def ids():
    return list(TEMAS)


def derivar(base, id, nombre=None, tinte=0.0, **cambios) -> Tema:
    """Tema nuevo a partir de otro: gira matiz del fondo y de la paleta (salvo `tinta`) y aplica `cambios`
    (los dicts `color`, `fuentes` y `ancho_car` se mezclan con los de la base; lo demás reemplaza)."""
    b = obtener(base) if isinstance(base, str) else base
    col = {k: (v if k == "tinta" else F.rotar_hex(v, tinte)) for k, v in b.color.items()}
    col_extra = cambios.pop("color", {})
    fu = {**b.fuentes, **cambios.pop("fuentes", {})}
    ac = {**b.ancho_car, **cambios.pop("ancho_car", {})}
    pantalla = cambios.pop("pantalla", F.rotar_hex(b.pantalla, tinte) if b.pantalla else None)
    if pantalla and b.pantalla and b.color.get("panel", "").lower() == b.pantalla.lower():
        col["panel"] = pantalla  # el panel del video sigue al fondo recoloreado
    col.update(col_extra)
    mn = None
    if b.manim is not None:
        mn = {k: (F.rotar_hex(v, tinte) if k.startswith("C_") else v) for k, v in b.manim.items()}
        if pantalla:
            mn["FONDO"] = pantalla
        mn.update(cambios.pop("manim", {}))
    return replace(b, id=id, nombre=nombre or id.capitalize(), color=col, fuentes=fu, ancho_car=ac, pantalla=pantalla,
                   tinte=b.tinte + tinte, base=b.id, manim=mn, **cambios)


def desde_json(ruta):
    d = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if "base" in d:
        base = d.pop("base")
        id_, nombre, tinte = d.pop("id"), d.pop("nombre", None), d.pop("tinte", 0.0)
        return derivar(base, id_, nombre, tinte, **d)
    return Tema(**d)


def cargar_plugins(verbose=False):
    """Registra los temas de animaciones/temas/ y de las carpetas de CODE_TEMAS_DIR (separadas por «:»)."""
    carpetas = [DIR_TEMAS] + [Path(p) for p in os.environ.get("CODE_TEMAS_DIR", "").split(os.pathsep) if p]
    for c in carpetas:
        if not c.is_dir():
            continue
        for f in sorted(c.glob("*.json")) + sorted(c.glob("*.py")):
            if f.name.startswith("_"):
                continue
            try:
                if f.suffix == ".json":
                    t = desde_json(f)
                    if t.id not in TEMAS or TEMAS[t.id].base:  # un JSON puede reemplazar a otro JSON, no a un tema incluido
                        registrar(t, reemplazar=True)
                else:
                    spec = importlib.util.spec_from_file_location(f"tema_{f.stem}", f)
                    m = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(m)
                    if hasattr(m, "TEMA"):
                        registrar(m.TEMA, reemplazar=True)
                if verbose:
                    print("tema cargado:", f)
            except Exception as e:  # un tema roto no debe tumbar al resto
                print(f"[tema omitido] {f.name}: {e}", file=sys.stderr)


def crear_json(id, base="orbita", nombre=None, tinte=0.0, descripcion="", carpeta=None, **extra):
    """Escribe temas/<id>.json (tema derivado) y lo registra. Devuelve la ruta."""
    if not id.replace("_", "").isalnum() or id.startswith("_"):
        raise ValueError("el id debe ser alfanumérico (sin espacios ni «_» al inicio)")
    carpeta = Path(carpeta) if carpeta else DIR_TEMAS
    carpeta.mkdir(parents=True, exist_ok=True)
    spec = {"id": id, "nombre": nombre or id.capitalize(), "base": base, "tinte": float(tinte),
            "descripcion": descripcion or f"Derivado de {base}", **extra}
    ruta = carpeta / f"{id}.json"
    ruta.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    registrar(desde_json(ruta), reemplazar=True)
    return ruta


# ---------------------------------------------------------------- temas incluidos
registrar(Tema(
    id="orbita", nombre="Órbita", modo="oscuro", video="fundido", pantalla="#0a0e27", generador="orbita",
    descripcion="Marca codeaerospace.com: #0a0e27 y cian. Vía Láctea, horizonte planetario; el video se funde sin marco.",
    fuentes=dict(titulo="Rajdhani", display="Orbitron", cuerpo="DM Sans", etiqueta="Space Mono"),
    ancho_car=dict(titulo=0.44, cuerpo=0.52), k_titulo=1.14, portada_ancho=11.2,
    color=dict(tinta="#F1F5F9", tenue="#93A4BD", acento="#00D9FF", acento2="#37CFA0", calido="#F59E0B",
               linea="#00D9FF", panel="#0a0e27"),
    manim=dict(FUENTE="Rajdhani", FUENTE_CIFRA="Rajdhani", PESO_CIFRA="BOLD", ESCALA_TEXTO=1.0,
               FONDO="#0a0e27", TINTA="#F1F5F9", TENUE="#93A4BD", C_EJE="#2F4270", C_TIERRA="#2563EB", C_TIERRA_2="#1E3A8A",
               C_SAT="#F59E0B", C_ANT="#00D9FF", C_CIELO="#A78BFA", C_MAL="#FF3C6E", C_OK="#37CFA0", C_PANEL="#1A2847")))
registrar(Tema(
    id="mision", nombre="Control de misión", modo="oscuro", video="monitor", pantalla="#06121E", generador="mision",
    descripcion="Consola casi negra con rejilla, reglas, radar y globo de alambre; el video va en un monitor con escuadras.",
    fuentes=dict(titulo="Chakra Petch", display="Chakra Petch", cuerpo="IBM Plex Sans", etiqueta="IBM Plex Mono"),
    ancho_car=dict(titulo=0.5, cuerpo=0.52), k_titulo=0.96, portada_ancho=7.3, esquinas=True, cierre_derecha=True,
    color=dict(tinta="#E6EDF5", tenue="#7F8EA6", acento="#FFB020", acento2="#22D3EE", calido="#FF5A5F",
               linea="#22D3EE", panel="#06121E"),
    manim=dict(FUENTE="Chakra Petch", FUENTE_CIFRA="Chakra Petch", PESO_CIFRA="BOLD", ESCALA_TEXTO=0.87,
               FONDO="#06121E", TINTA="#E6EDF5", TENUE="#7F8EA6", C_EJE="#2E4B66", C_TIERRA="#2563EB", C_TIERRA_2="#1E3A8A",
               C_SAT="#FFB020", C_ANT="#22D3EE", C_CIELO="#A78BFA", C_MAL="#FF5A5F", C_OK="#34D399", C_PANEL="#10283F")))
registrar(Tema(
    id="nebulosa", nombre="Nebulosa", modo="oscuro", video="tarjeta", pantalla="#0C0820", generador="nebulosa",
    descripcion="Cinemático: nebulosa violeta, magenta y turquesa con paleta distinta por sección; planeta anillado al cierre.",
    fuentes=dict(titulo="Exo 2", display="Exo 2", cuerpo="Sora", etiqueta="Space Mono"),
    ancho_car=dict(titulo=0.5, cuerpo=0.58), k_titulo=0.98, portada_ancho=7.6,
    color=dict(tinta="#F7F4FF", tenue="#B9ADD9", acento="#F0ABFC", acento2="#5EEAD4", calido="#FFD6A5",
               linea="#C084FC", panel="#0C0820"),
    manim=dict(FUENTE="Exo 2", FUENTE_CIFRA="Exo 2", PESO_CIFRA="BOLD", ESCALA_TEXTO=0.9,
               FONDO="#0C0820", TINTA="#F7F4FF", TENUE="#B9ADD9", C_EJE="#4A3F7A", C_TIERRA="#6D5BD0", C_TIERRA_2="#3B2F8F",
               C_SAT="#FBBF77", C_ANT="#5EEAD4", C_CIELO="#F0ABFC", C_MAL="#FB7185", C_OK="#86EFAC", C_PANEL="#1B1240")))
registrar(Tema(
    id="estacion", nombre="Estación", modo="claro", video="tarjeta", pantalla=None, generador="estacion",
    descripcion="Claro: papel técnico azulado con órbitas de línea fina y globo de alambre; videos en tarjeta blanca.",
    fuentes=dict(titulo="Space Grotesk", display="Space Grotesk", cuerpo="IBM Plex Sans", etiqueta="Space Mono"),
    ancho_car=dict(titulo=0.55, cuerpo=0.52), k_titulo=0.98, portada_ancho=7.3, cierre_derecha=True,
    color=dict(tinta="#0B1530", tenue="#5B6B85", acento="#1D4ED8", acento2="#EA580C", calido="#EA580C",
               linea="#1D4ED8", panel="#FFFFFF"),
    manim=dict(FUENTE="Space Grotesk", FUENTE_CIFRA="Space Grotesk", PESO_CIFRA="BOLD", ESCALA_TEXTO=0.87,
               FONDO="#FFFFFF", TINTA="#0B1530", TENUE="#5B6B85", C_EJE="#B6C2D0", C_TIERRA="#1D4ED8", C_TIERRA_2="#93B4F5",
               C_SAT="#EA580C", C_ANT="#0E7490", C_CIELO="#6D28D9", C_MAL="#E11D48", C_OK="#059669", C_PANEL="#E8EEF8")))
cargar_plugins()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lista", action="store_true")
    ap.add_argument("--nuevo", metavar="ID")
    ap.add_argument("--base", default="orbita")
    ap.add_argument("--tinte", type=float, default=0.0)
    ap.add_argument("--nombre")
    ap.add_argument("--vista-previa", metavar="ID", help="genera el fondo de portada del tema (≈40 s)")
    a = ap.parse_args()
    if a.nuevo:
        print("creado:", crear_json(a.nuevo, a.base, a.nombre, a.tinte))
    if a.vista_previa:
        print(obtener(a.vista_previa).fondo("portada"))
    if a.lista or not (a.nuevo or a.vista_previa):
        for t in TEMAS.values():
            print(f"{t.id:10s} {t.nombre:18s} video={t.video:8s} modo={t.modo:6s} "
                  f"{'(deriva de ' + t.base + ', tinte ' + str(t.tinte) + ')' if t.base else ''}")
            print(f"           {t.descripcion}")
