# =====================================================================
# CO.DE Academy - "Marca · Intro y cierre". Bloque de estilo del
# proyecto. Se antepone al script de CADA clip; los clips NO repiten
# imports: solo definen su ClipN(Scene).
#
# Proyecto ESPECIAL de identidad: dos clips cortos (~10 s) que se pegan
# en posproduccion al inicio y al final de cada curso nuevo. A
# diferencia de las lecciones, aqui la sombra de Scene NO añade
# marca_agua ni esquinas: el wordmark grande ES la marca y cada clip
# coreografia su propia identidad.
# =====================================================================
import math
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand as _code_brand
from code_brand import (CODE_ACCENT, CODE_ACCENT_2, CODE_BG, CODE_INK,
                        CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD,
                        esquinas_hud, etiqueta_hud, registrar_fuentes,
                        titulo_marca)

# --- Tipografia de marca ---------------------------------------------
registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

_TextBase = Text


class Text(_TextBase):
    """Sombra de Text que descarta los glifos vacios (espacios).

    Manim 0.20.1 deja el glifo del espacio anclado donde nacio el texto: al
    mover el mobject, el bounding box se infla y rompe next_to / Brace /
    SurroundingRectangle. Filtrarlos tras construir lo deja estable sin
    alterar la posicion de las letras (ya esta horneada).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submobjects = [s for s in self.submobjects if s.has_points()]


_code_brand.Text = Text

config.background_color = CODE_BG

# --- Paleta -----------------------------------------------------------
C_TITULO = CODE_INK          # #e8edf3 tinta
C_TENUE = CODE_MUTED         # #94a0b0 secundario
C_ACENTO = CODE_ACCENT       # #f59e0b ambar
C_ACENTO_2 = CODE_ACCENT_2   # #ea580c naranja (cierre del degradado)
C_EJE = "#31414f"            # gris azulado de mobiliario / reticula


# --- Piezas del wordmark ----------------------------------------------
def wordmark(font_size=96):
    """CO.DE en grande, centrado en el origen.

    Devuelve (grupo, co, punto, de): las letras en tinta y el punto en
    ambar, ya arreglados; las partes se devuelven sueltas para poder
    animarlas por separado (el punto llega al final, parpadea, etc.).
    """
    co = Text("CO", weight="SEMIBOLD", font_size=font_size, color=CODE_INK)
    punto = Text(".", weight="BOLD", font_size=font_size, color=CODE_ACCENT)
    de = Text("DE", weight="SEMIBOLD", font_size=font_size, color=CODE_INK)
    grupo = VGroup(co, punto, de).arrange(buff=0.10, aligned_edge=DOWN)
    grupo.move_to(ORIGIN)
    return grupo, co, punto, de


def academy(font_size=30):
    """ACADEMY en muted con tracking amplio (letras espaciadas a mano:
    la sombra de Text descarta los glifos de espacio pero la posicion de
    las letras ya queda horneada)."""
    return Text("A C A D E M Y", weight="MEDIUM", font_size=font_size,
                color=CODE_MUTED)


def subrayado(referencia, margen=0.12, grosor=3.5):
    """Linea con el degradado de marca (ambar -> naranja) bajo un mobject,
    del mismo ancho que el."""
    linea = Line(referencia.get_corner(DL), referencia.get_corner(DR),
                 stroke_width=grosor)
    linea.set_color(color_gradient([CODE_ACCENT, CODE_ACCENT_2], 2))
    linea.shift(DOWN * margen)
    return linea


def tag_hud(texto, font_size=17, color=None):
    """Etiqueta de telemetria en Space Mono (SOLO ASCII: sin acentos ni
    superindices — Space Mono no los trae)."""
    return Text(texto, font=FUENTE_HUD, font_size=font_size,
                color=C_TENUE if color is None else color)


def reticula(paso=0.9, opacidad=0.10):
    """Reticula HUD tenue a pantalla completa, en C_EJE. Nace invisible
    (opacidad de linea aparte) para poder encenderla al paso del escaneo."""
    ancho = config.frame_width / 2
    alto = config.frame_height / 2
    lineas = VGroup()
    x = -ancho
    while x <= ancho + 1e-6:
        lineas.add(Line([x, -alto, 0], [x, alto, 0], stroke_width=1.0))
        x += paso
    y = -alto
    while y <= alto + 1e-6:
        lineas.add(Line([-ancho, y, 0], [ancho, y, 0], stroke_width=1.0))
        y += paso
    lineas.set_stroke(color=C_EJE, opacity=opacidad)
    return lineas


# --- Marca de la escena (sombra de Scene) -----------------------------
# Solo el fondo: NADA de marca_agua ni esquinas automaticas en este
# proyecto (ver cabecera).
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
