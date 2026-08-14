# =====================================================================
# CO.DE Academy - "Caos: el orden escondido"
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

# --- Tipografia de marca ---------------------------------------------
registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

_TextBase = Text


class Text(_TextBase):
    """Sombra de Text que descarta los glifos vacios (espacios).

    Manim 0.20.1 deja el glifo del espacio anclado donde nacio el texto:
    al mover el mobject, el bounding box se infla y rompe next_to / Brace.
    Filtrarlos tras construir lo deja estable.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submobjects = [s for s in self.submobjects if s.has_points()]


_code_brand.Text = Text

import caos as _caos  # noqa: E402  (tras definir la sombra)
from caos import (FEIGENBAUM_DELTA, LORENZ_BETA, LORENZ_RHO,  # noqa: E402
                  LORENZ_SIGMA, R_BIFURCACIONES, VENTANA_P3, Abanico,
                  PenduloDoble, abanico_pendulos, cobweb, curva_lorenz,
                  curva_separacion, energia_pendulo, feigenbaum_cocientes,
                  imagen_bifurcacion, mapa_retorno, orbita_logistica,
                  par_lorenz, pendulo_doble, ruido_uniforme,
                  trayectoria_lorenz)

_caos.Text = Text

_RotulosBase = Rotulos


class Rotulos(_RotulosBase):
    """Relevo SECUENCIAL por zona: el rotulo anterior sale ANTES de que
    entre el nuevo (el original los cruza ~0.5 s)."""

    def mostrar(self, mobjeto, zona="abajo", run_time=0.45, salida=0.25,
                **kwargs):
        if self._zonas.get(zona) is not None:
            self.limpiar(zona, run_time=salida)
        return super().mostrar(mobjeto, zona=zona, run_time=run_time,
                               **kwargs)

config.background_color = CODE_BG

# --- Paleta del curso -------------------------------------------------
# Regla: el SISTEMA es ambar, su GEMELO casi identico (y lo medido: delta,
# lambda) cian, el ERROR que crece rojo, el ORDEN verde, el ESPACIO DE
# FASES (el atractor como objeto, el ruido) violeta.
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_ACENTO = CODE_ACCENT
C_ACENTO_2 = CODE_ACCENT_2
C_SISTEMA = "#f59e0b"        # ambar: la trayectoria, la parabola
C_GEMELO = "#22d3ee"         # cian: el gemelo; delta y lambda medidos
C_ERROR = "#f43f5e"          # rojo: la separacion que crece
C_ORDEN = "#34d399"          # verde: equilibrios, ciclos, ventanas
C_FASE = "#a78bfa"           # violeta: el atractor como objeto, el ruido
C_EJE = "#31414f"            # gris azulado de mobiliario

MARGEN_PIE = 0.68

# --- Numeros del curso ------------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria (medido o con
# cita), nunca escrito a mano en el clip.
R_EQUILIBRIO = 2.9                    # la telarana converge
R_CICLO2 = 3.3                        # el vals de dos pasos
R_CAOS = 3.9                          # no se repite jamas
EPS_LORENZ = 1e-6                     # la millonesima del clip 5
EPS_PENDULO_DEG = 0.01                # la centesima de grado del clip 6
N_PENDULOS = 25
COCIENTES_FEIG = feigenbaum_cocientes()   # (4.751, 4.656, 4.668)
ZOOM_P3 = (3.80, 3.88)                # encuadre del zoom a la ventana
# Horizontes de prediccion (segundos, orden de magnitud, con cita):
# pendulo doble ~10 s (laboratorio), clima ~2 semanas (Lorenz/ECMWF),
# sistema solar ~5 millones de años (Laskar 1989).
HORIZONTES = (("péndulo doble", 10.0), ("clima", 1.2e6),
              ("sistema solar", 1.6e14))


# --- Rotulos ----------------------------------------------------------
def titulo_curso(texto, font_size=34, color=None):
    t = titulo_marca(texto, font_size=font_size,
                     color=C_TITULO if color is None else color)
    if t.width > config.frame_width - 2.0:
        t.scale_to_fit_width(config.frame_width - 2.0)
    t.to_edge(UP, buff=0.52)
    return t


def pie_curso(texto, font_size=25, color=None):
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    if t.width > config.frame_width - 2.6:
        t.scale_to_fit_width(config.frame_width - 2.6)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return t


def formula_pie(tex, font_size=34, color=None):
    m = MathTex(tex, font_size=font_size,
                color=C_ACENTO if color is None else color)
    if m.width > config.frame_width - 3.0:
        m.scale_to_fit_width(config.frame_width - 3.0)
    m.to_edge(DOWN, buff=MARGEN_PIE)
    return m


def hud_modulo(texto):
    t = etiqueta_hud(texto)
    t.to_corner(UL, buff=0.5)
    return t


def tag_junto(mobjeto, texto, direccion=DOWN, buff=0.16, font_size=18,
              color=None):
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    t.set_opacity(0.85)
    t.next_to(mobjeto, direccion, buff=buff)
    return t


def tag_hud(texto, font_size=15, color=None):
    """Cifra medida (Space Mono) SIN posicion: el clip la coloca."""
    t = Text(texto, font=FUENTE_HUD, font_size=font_size,
             color=C_GEMELO if color is None else color)
    return t


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
