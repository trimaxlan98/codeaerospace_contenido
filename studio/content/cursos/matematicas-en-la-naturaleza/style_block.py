# =====================================================================
# CO.DE Academy - "Matematicas en la naturaleza"
# Bloque de estilo del proyecto. Se antepone al script de CADA clip; los
# clips NO repiten imports: solo definen su clase ClipN(Scene).
# =====================================================================
import math
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand as _code_brand
from code_brand import (CODE_ACCENT, CODE_ACCENT_2, CODE_BG, CODE_INK,
                        CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD, Rotulos,
                        esquinas_hud, etiqueta_hud, marca_agua,
                        registrar_fuentes, titulo_marca)
from transiciones import (transicion_deslizar, transicion_persiana,
                          transicion_zoom)

# --- Tipografia de marca ---------------------------------------------
# El default se fija sobre el Text ORIGINAL de Manim (antes de la sombra)
# para que tambien lo hereden los helpers de las librerias.
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

import naturaleza as _naturaleza  # noqa: E402  (tras definir la sombra)
from naturaleza import (ANGULO_AUREO_DEG, B_AUREA, B_NAUTILUS,  # noqa: E402
                        E, FIB, MAPAS_HELECHO, OMEGA_PI_DEG, PHI,
                        TURING_MANCHAS, TURING_RAYAS, arbol_fractal,
                        campo_turing, curva_crecimiento, escalera_compuesta,
                        espiral_log, filotaxis, gato_dormido, gato_sentado,
                        imagen_helecho, imagen_turing, mapas_helecho_marcos,
                        onda_circular, panal, perimetro_por_area,
                        rectangulos_fibonacci, red_micelio, rio_meandro,
                        secuencia_turing, tesela_unidad)

_naturaleza.Text = Text

_RotulosBase = Rotulos


class Rotulos(_RotulosBase):
    """Relevo SECUENCIAL por zona: el rotulo anterior sale ANTES de que
    entre el nuevo (el original los cruza y durante ~0.5 s se ven dos)."""

    def mostrar(self, mobjeto, zona="abajo", run_time=0.45, salida=0.25,
                **kwargs):
        if self._zonas.get(zona) is not None:
            self.limpiar(zona, run_time=salida)
        return super().mostrar(mobjeto, zona=zona, run_time=run_time,
                               **kwargs)

config.background_color = CODE_BG

# --- Paleta del curso -------------------------------------------------
# Regla: la REGLA matematica es ambar, lo VIVO verde, la CONSTANTE que la
# regla produce (phi, pi, e, 137.5) cian, el MITO y el desperdicio rojos,
# la QUIMICA que calcula violeta. Mobiliario gris azulado.
C_TITULO = CODE_INK          # #e8edf3 titulos
C_TENUE = CODE_MUTED         # #94a0b0 pies y elementos secundarios
C_ACENTO = CODE_ACCENT       # #f59e0b ambar
C_ACENTO_2 = CODE_ACCENT_2   # #ea580c naranja de cierre
C_REGLA = "#f59e0b"          # ambar: la regla, la curva, el angulo
C_VIDA = "#34d399"           # verde: lo vivo (semillas, helecho, micelio)
C_CONSTANTE = "#22d3ee"      # cian: phi, pi, e, el resultado
C_MITO = "#f43f5e"           # rojo: el desperdicio, el mito
C_QUIMICA = "#a78bfa"        # violeta: morfogenos, decaimiento
C_EJE = "#31414f"            # gris azulado de mobiliario
C_PELAJE = "#d9a05a"         # base del pelaje del gato (arena)
C_TINTA = "#20160c"          # la mancha/raya sobre el pelaje

MARGEN_PIE = 0.68            # separacion del pie al borde inferior

# --- Numeros del curso ------------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria, nunca escrito a
# mano en el clip: el codigo del curso y el codigo de la naturaleza que
# cuenta son la misma cuenta.
N_SEMILLAS = 600                       # semillas del girasol del curso
ANGULO_MALO_1 = 90.0                   # el reparto en cuatro rayos
ANGULO_MALO_2 = 120.0                  # el reparto en tres rayos
PARASTICAS = (21, 34)                  # las dos familias visibles (Fibonacci)
COCIENTES_FIB = tuple(FIB[i + 1] / FIB[i] for i in range(1, 7))
                                       # 2.0, 1.5, 1.667, 1.6, 1.625, 1.615
OMEGA_JOVEN = 30.0                     # el rio casi recto
OMEGA_MEDIO = 80.0                     # el rio que ya serpentea
N_COMPUESTA = (1, 4, 12, 52)           # capitalizaciones de la escalera
PERIMETROS = {n: perimetro_por_area(n) for n in (3, 4, 6)}
                                       # 4.559, 4.000, 3.722 (area 1)
TURING_PASOS = 7000                    # pasos del campo (los presets)
HALES = 1999                           # el año del teorema del panal


# --- Rotulos ----------------------------------------------------------
def titulo_curso(texto, font_size=34, color=None):
    """Titulo de clip (Rajdhani) anclado arriba. Zona 'arriba' de Rotulos."""
    t = titulo_marca(texto, font_size=font_size,
                     color=C_TITULO if color is None else color)
    if t.width > config.frame_width - 2.0:
        t.scale_to_fit_width(config.frame_width - 2.0)
    t.to_edge(UP, buff=0.52)
    return t


def pie_curso(texto, font_size=25, color=None):
    """Pie narrativo anclado abajo. Zona 'abajo' de Rotulos."""
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    if t.width > config.frame_width - 2.6:
        t.scale_to_fit_width(config.frame_width - 2.6)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return t


def formula_pie(tex, font_size=34, color=None):
    """MathTex corto que ocupa la MISMA zona que el pie (nunca se suman)."""
    m = MathTex(tex, font_size=font_size,
                color=C_ACENTO if color is None else color)
    if m.width > config.frame_width - 3.0:
        m.scale_to_fit_width(config.frame_width - 3.0)
    m.to_edge(DOWN, buff=MARGEN_PIE)
    return m


def hud_modulo(texto):
    """Etiqueta de telemetria del modulo, esquina superior izquierda."""
    t = etiqueta_hud(texto)
    t.to_corner(UL, buff=0.5)
    return t


def tag_junto(mobjeto, texto, direccion=DOWN, buff=0.16, font_size=18,
              color=None):
    """Etiqueta corta de mobiliario pegada a un mobject (no narrativa)."""
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    t.set_opacity(0.85)
    t.next_to(mobjeto, direccion, buff=buff)
    return t


def tag_hud(texto, font_size=15, color=None):
    """Texto corto de telemetria (Space Mono) SIN posicion: el clip lo
    coloca. Para cifras medidas (sinuosidad, F/k, (1+1/n)^n)."""
    t = Text(texto, font=FUENTE_HUD, font_size=font_size,
             color=C_CONSTANTE if color is None else color)
    return t


def llave(mobjeto, texto=None, direccion=UP, font_size=22, color=None,
          buff=0.12):
    """Brace opcionalmente etiquetado (etiquetas de 1-2 palabras)."""
    col = C_ACENTO if color is None else color
    b = Brace(mobjeto, direction=direccion, color=col)
    if texto is None:
        return VGroup(b)
    t = Text(texto, font_size=font_size, color=col)
    t.next_to(b, direccion, buff=buff)
    return VGroup(b, t)


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
