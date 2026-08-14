# =====================================================================
# CO.DE Academy - "Relatividad y el GPS"
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

import relatividad as _relatividad  # noqa: E402  (tras definir la sombra)
from relatividad import (ALTURA_ISS, ALTURA_MUON, BETA_MUON, C,  # noqa: E402
                         FREQ_GPS, GM_TIERRA, RADIO_GPS, RADIO_TIERRA,
                         TAU_MUON, altura_empate, carita_reloj,
                         curva_deriva, curva_gamma, curvas_muones,
                         deriva_us_dia, derivas_gps, error_metros,
                         fila_pulsos, frac_muones, frecuencia_fabrica,
                         gamma, mapa_error, metros_por_us, orbita_gps,
                         periodo_orbital, pozo_potencial, reloj_luz,
                         supervivencia_muones, trilateracion,
                         velocidad_orbital)

_relatividad.Text = Text

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
# Regla: la LUZ (pulsos, fotones) es ambar; el SATELITE y sus relojes
# (lo medido) cian; la TIERRA y el receptor verde; el ERROR que se
# acumula rojo; la GRAVEDAD (el pozo, la relatividad general) violeta.
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_ACENTO = CODE_ACCENT
C_ACENTO_2 = CODE_ACCENT_2
C_LUZ = "#f59e0b"            # ambar: la luz, los pulsos, el foton
C_SATELITE = "#22d3ee"       # cian: el satelite, sus relojes, lo medido
C_TIERRA = "#34d399"         # verde: la Tierra, el receptor, tu
C_ERROR = "#f43f5e"          # rojo: el error que se acumula
C_GRAVEDAD = "#a78bfa"       # violeta: el pozo, la relatividad general
C_EJE = "#31414f"            # gris azulado de mobiliario

MARGEN_PIE = 0.68

# --- Numeros del curso ------------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria (calculado o
# medido en pantalla), nunca escrito a mano en el clip.
V_GPS = velocidad_orbital()                 # 3874 m/s
PERIODO_GPS_H = periodo_orbital() / 3600.0  # 11.97 h
DERIVA_SR, DERIVA_GR, DERIVA_NETA = derivas_gps()   # -7.21 / +45.72 / +38.50
H_EMPATE = altura_empate()                  # ~3.186e6 m (medida)
DERIVA_ISS = deriva_us_dia(RADIO_TIERRA + ALTURA_ISS)   # -24.49 us/dia
F_FABRICA = frecuencia_fabrica()            # 10.22999999544 MHz
FRAC_CLASICA, FRAC_RELATIVISTA = frac_muones()          # ~0 / 0.102
GAMMA_MUON = gamma(BETA_MUON)               # 10.0
M_POR_US = metros_por_us()                  # 299.8 m
CM_POR_NS = metros_por_us(1e-3) * 100.0     # 30 cm
ERROR_HORA_M = error_metros(1.0)            # 481 m
ERROR_DIA_KM = error_metros(24.0) / 1000.0  # 11.54 km
BETA_EJEMPLO = 0.5                          # el punto que se rotula en
GAMMA_EJEMPLO = gamma(BETA_EJEMPLO)         # la curva gamma: 1.1547
BETA_RELOJ = 0.6                            # beta del reloj de luz (se ve)


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
             color=C_SATELITE if color is None else color)
    return t


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
