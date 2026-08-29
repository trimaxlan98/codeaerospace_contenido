# =====================================================================
# CO.DE Academy - presentacion.py
# El lienzo, la paleta y los PASOS de una PRESENTACION de presentacion.
#
# Una presentacion no es un clip de curso ni un promo de redes:
#   - vive dentro de un slide de PowerPoint, no en un reproductor;
#   - la narra una persona EN VIVO, asi que no lleva voz ni subtitulos;
#   - avanza cuando el ponente hace clic, no cuando el reloj lo dice;
#   - y el fondo del slide lo elige quien presenta, no la marca: una
#     plantilla de tesis suele ser BLANCA.
#
# Los dos primeros puntos ya los cubre el estudio. Los dos ultimos son
# lo que este modulo agrega.
#
#   import presentacion
#   PZA = presentacion.lienzo()              # lee el entorno; horizontal + marca
#
#   class MiPresentacion(Scene):
#       def setup(self):
#           presentacion.aplicar(self, PZA)
#
#       def construct(self):
#           self.play(...)
#           presentacion.paso(self, "El planteamiento")   # <- aqui se hace clic
#           self.play(...)
#           presentacion.paso(self, "El resultado")
#           self.play(...)
#
# `paso()` NO parte el render. Anota el instante en `pasos.json` y deja
# la escena quieta un momento; quien corta es ffmpeg, despues, con esos
# tiempos. Un solo render produce los N fragmentos, y el ultimo fotograma
# de cada uno ES el primero del siguiente: el empalme entre slides no se
# ve. Renderizar N veces la misma escena costaria N veces mas en un VPS
# de 2 vCPU y ademas no garantizaria esa continuidad.
# =====================================================================
import json
import os
from pathlib import Path

from manim import DR, DOWN, LEFT, RIGHT, UP, Rectangle, Text, VGroup, config

import code_brand
from code_brand import (CODE_ACCENT, CODE_BG, CODE_INK, CODE_MUTED,
                        FUENTE_DISPLAY, FUENTE_HUD, registrar_fuentes)

# El mundo de manim mide SIEMPRE 8 unidades de alto, en los tres formatos.
# Asi 1 unidad = 135 px con el lado corto en 1080, y un font_size=40 se ve
# igual de grande en 16:9 que en 4:3: una presentacion bien compuesta solo
# necesita RECOLOCAR presentaciones al cambiar de formato, no re-dimensionarlas.
ALTO_MUNDO = 8.0

# Ninguno es vertical: en un slide el lado corto es SIEMPRE el alto.
PROPORCIONES = {
    "horizontal": 16 / 9,   # pantalla completa, proyector moderno
    "clasico": 4 / 3,       # auditorios viejos y plantillas de tesis
    "cuadrado": 1.0,        # panel al lado del texto
}

ALTO_PX = {"ql": 480, "qm": 720, "qh": 1080}
FPS = {"ql": 30, "qm": 30, "qh": 60}

# Un slide no tiene barra de app que se coma los bordes, pero un proyector
# mal ajustado si recorta un poco: 3.5% de holgura por lado.
HOLGURA = 0.035

# Fondos con nombre. Cualquier otro valor se toma como color: "#1e293b".
FONDOS = {
    "marca": CODE_BG,        # el casi-negro del canal
    "blanco": "#ffffff",     # plantilla institucional / tesis
    "pizarra": "#0f172a",    # azul muy oscuro, mas suave que el negro
}

# Paleta para fondo CLARO. La de la marca no sirve aqui y no es opinion:
# el ambar #f59e0b sobre blanco da 2.15:1 de contraste (ilegible), y la
# tinta #e8edf3 da 1.18:1 (invisible). Medidos con WCAG 2.1.
#   tinta  #0f172a sobre blanco -> 17.85:1
#   apoyo  #475569 sobre blanco ->  7.58:1
#   acento #b45309 sobre blanco ->  5.02:1
TINTA_CLARA = "#0f172a"
APOYO_CLARO = "#475569"
ACENTO_CLARO = "#b45309"

# Rajdhani tiene dos defectos MEDIDOS en renders ya publicados: parte
# palabras a 16-17 px ("retardada" -> "ret ardada") y las JUNTA por debajo
# de 22 px ("por separado" -> "porseparado"). En un curso eso es un
# borron; en la defensa de una tesis, proyectado a tres metros, es un
# error que el jurado lee. Aqui es un error duro, no un aviso.
MIN_DISPLAY = 22

_REGISTRO: list[dict] = []
_LIENZO: dict = {}


# ── luminancia: quien decide si un fondo es claro ────────────────────────────

def _luminancia(hex_color: str) -> float:
    """Luminancia relativa WCAG de un "#rrggbb"."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    canales = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        canales.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canales[0] + 0.7152 * canales[1] + 0.0722 * canales[2]


def contraste(a: str, b: str) -> float:
    """Razon de contraste WCAG entre dos colores (1:1 a 21:1)."""
    la, lb = _luminancia(a), _luminancia(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _color_fondo(nombre: str) -> str:
    color = FONDOS.get(nombre, nombre)
    if not (isinstance(color, str) and color.startswith("#")
            and len(color.lstrip("#")) in (3, 6)):
        raise ValueError(f"fondo desconocido: {nombre!r} "
                         f"(usa {', '.join(FONDOS)} o un #rrggbb)")
    return color


# ── el lienzo ────────────────────────────────────────────────────────────────

class Lienzo:
    """El lienzo de la presentacion: mundo, pixeles y la paleta que ese fondo
    admite. La paleta VOLTEA con el fondo — no es decoracion, es lo unico
    que hace legible la misma escena sobre blanco y sobre negro."""

    def __init__(self, nombre, fondo, px_ancho, px_alto, fps):
        self.nombre = nombre
        self.fondo = fondo
        self.px_ancho = px_ancho
        self.px_alto = px_alto
        self.fps = fps
        self.alto = ALTO_MUNDO
        self.ancho = ALTO_MUNDO * PROPORCIONES[nombre]
        self.es_claro = _luminancia(fondo) > 0.35
        if self.es_claro:
            self.tinta, self.apoyo, self.acento = (TINTA_CLARA, APOYO_CLARO,
                                                   ACENTO_CLARO)
        else:
            self.tinta, self.apoyo, self.acento = (CODE_INK, CODE_MUTED,
                                                   CODE_ACCENT)

    # --- bordes del lienzo -------------------------------------------
    @property
    def borde_arriba(self):
        return self.alto / 2

    @property
    def borde_abajo(self):
        return -self.alto / 2

    # --- bordes con la holgura del proyector -------------------------
    @property
    def tope(self):
        return self.borde_arriba - HOLGURA * self.alto

    @property
    def suelo(self):
        return self.borde_abajo + HOLGURA * self.alto

    @property
    def izquierda(self):
        return -self.ancho / 2 + HOLGURA * self.ancho

    @property
    def derecha(self):
        return self.ancho / 2 - HOLGURA * self.ancho

    def radio_max(self, holgura=0.78):
        """Radio de la presentacion redonda mas grande que cabe centrada."""
        return holgura * min(self.ancho, self.alto) / 2

    def contraste_tinta(self):
        """Contraste real de la tinta contra este fondo. Sirve para que un
        script con fondo a medida compruebe que su color se lee."""
        return contraste(self.tinta, self.fondo)

    def __repr__(self):
        return (f"<Lienzo {self.nombre} {self.px_ancho}x{self.px_alto} "
                f"fondo {self.fondo} {'claro' if self.es_claro else 'oscuro'} "
                f"@{self.fps}fps>")


def lienzo(nombre=None, fondo=None, calidad=None, alto_px=None, ancho_px=None,
           fps=None) -> Lienzo:
    """Configura manim para el lienzo pedido y devuelve el `Lienzo`.

    Se llama UNA vez, a nivel de modulo, antes de que exista la escena:
    manim importa el archivo entero antes de instanciarla, asi que aqui
    todavia se puede cambiar el lienzo.

    Sin argumentos lee el entorno (lo que pone el runner de ManimStudio):
    PRESENTACION_FORMATO, PRESENTACION_FONDO, PRESENTACION_CALIDAD, PRESENTACION_ALTO, PRESENTACION_ANCHO,
    PRESENTACION_FPS. Como respaldo acepta las PROMO_* del lienzo de promos, para
    que una presentacion pueda renderizarse por la cola normal antes de que la
    interfaz sepa de presentaciones.
    """
    ent = os.environ.get
    nombre = nombre or ent("PRESENTACION_FORMATO") or ent("PROMO_FORMATO") or "horizontal"
    if nombre not in PROPORCIONES:
        raise ValueError(f"formato de presentacion desconocido: {nombre!r} "
                         f"(usa {', '.join(PROPORCIONES)})")
    fondo = _color_fondo(fondo or ent("PRESENTACION_FONDO") or "marca")
    calidad = calidad or ent("PRESENTACION_CALIDAD") or ent("PROMO_CALIDAD") or "qh"
    if calidad not in ALTO_PX:
        raise ValueError(f"calidad desconocida: {calidad!r}")
    alto_px = int(alto_px or ent("PRESENTACION_ALTO") or ent("PROMO_CORTO")
                  or ALTO_PX[calidad])
    ancho_px = int(ancho_px or ent("PRESENTACION_ANCHO") or ent("PROMO_LARGO") or 0)
    fps = int(fps or ent("PRESENTACION_FPS") or ent("PROMO_FPS") or FPS[calidad])

    alto_px -= alto_px % 2                       # libx264 exige pares
    ancho_px = ancho_px or int(round(alto_px * PROPORCIONES[nombre]))
    ancho_px -= ancho_px % 2

    # ORDEN OBLIGATORIO: al fijar frame_height manim copia el valor a las
    # DOS dimensiones; frame_width tiene que ir despues o el mundo se queda
    # en 16:9 y el contenido sale encajonado con bandas negras.
    config.pixel_width = ancho_px
    config.pixel_height = alto_px
    config.frame_height = ALTO_MUNDO
    config.frame_width = ALTO_MUNDO * PROPORCIONES[nombre]
    config.frame_rate = fps
    config.background_color = fondo

    lz = Lienzo(nombre, fondo, ancho_px, alto_px, fps)
    if abs(config.frame_width - lz.ancho) > 1e-6:
        raise RuntimeError("el mundo no quedo en el formato pedido: "
                           f"{config.frame_width} != {lz.ancho}")
    _REGISTRO.clear()
    # El lienzo REALMENTE usado queda anotado junto a los pasos. Asi el
    # paquete se describe a si mismo y quien lo arma no tiene que volver a
    # deducir el color de fondo: lo lee del render. Importa cuando la
    # escena elige su propio fondo en el codigo en vez de heredarlo del
    # entorno — el slide se pinta del color que se vio, no del que se pidio.
    _LIENZO.clear()
    _LIENZO.update({"formato": lz.nombre, "fondo": lz.fondo,
                    "ancho_px": lz.px_ancho, "alto_px": lz.px_alto,
                    "fps": lz.fps, "es_claro": lz.es_claro})
    _volcar()
    return lz


# ── identidad, adaptada al fondo ─────────────────────────────────────────────

def marca(lz: Lienzo, opacidad=0.34):
    """El wordmark del canal, recoloreado para que se lea sobre ESTE fondo.

    Sobre blanco la marca de agua original es literalmente invisible
    (1.18:1): hay que teñirla de tinta oscura, no solo bajarle la opacidad.
    """
    m = code_brand.marca_agua()
    co, punto, de, academy = m
    for parte in (co, de):
        parte.set_color(lz.tinta)
    academy.set_color(lz.apoyo)
    punto.set_color(lz.acento)
    m.set_opacity(opacidad)
    m.to_corner(DR, buff=0.28)
    m.set_z_index(1000)
    return m


def aplicar(escena, lz: Lienzo, marca_agua=True, esquinas=None) -> None:
    """Fondo y marca de la presentacion. Llamar en `setup()`.

    Las esquinas HUD son de la estetica de consola del canal y sobre un
    fondo claro se ven como suciedad: por defecto solo salen en oscuro.
    """
    registrar_fuentes()
    escena.camera.background_color = lz.fondo
    if esquinas is None:
        esquinas = not lz.es_claro
    if esquinas:
        escena.add(code_brand.esquinas_hud(color=lz.acento))
    if marca_agua:
        escena.add(marca(lz))
    type(escena)._code_brand = True    # la presentacion ya trae identidad propia


# ── mobiliario con la paleta del lienzo ──────────────────────────────────────

def _display(texto, font_size, weight, color):
    if font_size < MIN_DISPLAY:
        raise ValueError(
            f"font_size={font_size} en Rajdhani: por debajo de {MIN_DISPLAY} px"
            f" junta las palabras ({texto!r} saldria mal). Sube el tamano, o"
            " usa presentacion.dato() si lo que quieres es una etiqueta chica.")
    registrar_fuentes()
    return Text(texto, font=FUENTE_DISPLAY, weight=weight,
                font_size=font_size, color=color)


def titulo(texto, lz: Lienzo, font_size=40, color=None):
    """Titulo display, en la tinta que ese fondo admite."""
    return _display(texto, font_size, "SEMIBOLD", color or lz.tinta)


def rotulo(texto, lz: Lienzo, font_size=26, color=None):
    """Etiqueta corta junto a una figura."""
    return _display(texto, font_size, "MEDIUM", color or lz.apoyo)


def dato(texto, lz: Lienzo, font_size=20, color=None):
    """Cifra medida, en la mono de telemetria y en MAYUSCULAS."""
    registrar_fuentes()
    return Text(str(texto).upper(), font=FUENTE_HUD, font_size=font_size,
                color=color or lz.acento)


def guias(lz: Lienzo):
    """Rectangulo de la holgura del proyector. Solo para validar encuadre;
    no va en el render final."""
    util = Rectangle(width=lz.derecha - lz.izquierda, height=lz.tope - lz.suelo,
                     stroke_width=2, stroke_color=lz.acento, stroke_opacity=0.5)
    borde = Rectangle(width=lz.ancho, height=lz.alto, stroke_width=2,
                      stroke_color=lz.apoyo, stroke_opacity=0.4)
    etiqueta = dato(f"{lz.nombre} {lz.px_ancho}x{lz.px_alto} {lz.fondo}", lz,
                    font_size=18)
    etiqueta.next_to(util, DOWN, buff=0.12)
    g = VGroup(util, borde, etiqueta)
    g.set_z_index(2000)
    return g


# ── los pasos ────────────────────────────────────────────────────────────────

def _ruta_pasos() -> Path:
    """`pasos.json` va DENTRO de media_dir.

    Es el unico sitio escribible en los dos montajes que existen: el runner
    monta `<job>/media` y la herramienta de linea de comandos monta `/media`
    a secas — ahi el padre es `/`, que es de solo lectura.
    """
    return Path(config.media_dir).resolve() / "pasos.json"


def _volcar() -> None:
    """Escribe el registro tras CADA paso, no al final: si la escena
    revienta a la mitad, los pasos que si ocurrieron siguen ahi y el
    diagnostico dice hasta donde llego."""
    try:
        _ruta_pasos().write_text(
            json.dumps({"lienzo": _LIENZO, "pasos": _REGISTRO},
                       ensure_ascii=False, indent=2),
            encoding="utf-8")
    except OSError as e:                # anotar los pasos nunca tumba un render
        print(f"[presentacion] no pude escribir pasos.json: {e}")


def paso(escena, etiqueta=None, espera=0.4) -> float:
    """Marca un punto de clic y devuelve el instante en que cae.

    La escena se queda QUIETA `espera` segundos alrededor del corte, con el
    instante justo en medio. Asi el fragmento que termina se congela un
    momento en su estado final y el que empresentacion arranca del mismo cuadro:
    en el slide siguiente, la imagen ya estaba ahi antes de que el video
    arrancara, y el empalme no se nota.
    """
    escena.wait(espera / 2)
    t = float(escena.renderer.time)
    escena.wait(espera / 2)
    _REGISTRO.append({"t": round(t, 3),
                      "etiqueta": etiqueta or f"Paso {len(_REGISTRO) + 1}"})
    _volcar()
    return t


def pasos() -> list[dict]:
    """Los pasos anotados hasta ahora (para pruebas)."""
    return list(_REGISTRO)
