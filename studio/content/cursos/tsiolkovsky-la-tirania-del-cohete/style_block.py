# =====================================================================
# CO.DE Academy - "Tsiolkovsky: la tirania del cohete"
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

import cohete as _cohete  # noqa: E402  (tras definir la sombra)
from cohete import (COHETES_REALES, DV_LEO, EPS_ESTRUCTURA,  # noqa: E402
                    G0, GM_TIERRA, PERDIDAS_LEO, RADIO_TIERRA, VE_HIDROLOX,
                    VE_ION, VE_QUIMICO, VE_RP1, barras_carga, canon_newton,
                    carga_util, curva_tirania, delta_v, dv_leo,
                    fraccion_propelente, isp, llama_escape, patinador,
                    razon_masas, retroceso, silueta_cohete, v_orbital)

_cohete.Text = Text

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
# Regla: el PROPELENTE (lo que se quema, la llama) es ambar; la CARGA
# UTIL (lo que llega, lo medido) cian; la TIERRA y la orbita verde; la
# masa MUERTA y lo imposible (el SSTO) rojo; la ESTRUCTURA violeta.
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_ACENTO = CODE_ACCENT
C_ACENTO_2 = CODE_ACCENT_2
C_PROPELENTE = "#f59e0b"     # ambar: propelente, llama, la curva tirana
C_CARGA = "#22d3ee"          # cian: la carga util, lo que llega
C_TIERRA = "#34d399"         # verde: la Tierra, la orbita
C_MUERTO = "#f43f5e"         # rojo: masa muerta, el SSTO imposible
C_ESTRUCTURA = "#a78bfa"     # violeta: tanques, motores
C_EJE = "#31414f"            # gris azulado de mobiliario

MARGEN_PIE = 0.68

# --- Numeros del curso ------------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria (calculado o
# con cita), nunca escrito a mano en el clip.
V_ORB_KMS = v_orbital() / 1000.0            # 7.788 km/s (calculada)
DV_LEO_KMS = DV_LEO / 1000.0                # 9.39 km/s (orbital + cita)
PERDIDAS_KMS = PERDIDAS_LEO / 1000.0        # 1.6 km/s (cita)
RAZON_RP1 = razon_masas(DV_LEO, VE_RP1)         # 22.9
RAZON_QUIMICO = razon_masas(DV_LEO, VE_QUIMICO)  # 14.6
RAZON_HIDROLOX = razon_masas(DV_LEO, VE_HIDROLOX)  # 8.4
RAZON_ION = razon_masas(DV_LEO, VE_ION)         # 1.37
FRAC_PROP = fraccion_propelente(DV_LEO, VE_QUIMICO)  # 0.932
CARGA_SSTO = carga_util(DV_LEO, VE_QUIMICO, EPS_ESTRUCTURA, 1)  # -0.0126
CARGA_2ET = carga_util(DV_LEO, VE_QUIMICO, EPS_ESTRUCTURA, 2)   # +0.0389
CARGA_3ET = carga_util(DV_LEO, VE_QUIMICO, EPS_ESTRUCTURA, 3)   # +0.0457
ISP_QUIMICO = isp(VE_QUIMICO)               # 357 s
RETRO = retroceso()                         # 0.769 m/s
FRAC_PROP_ION = fraccion_propelente(DV_LEO, VE_ION)  # 0.269
# fracciones de la silueta del clip 1 (propelente / estructura / carga)
FRAC_CARGA_SIL = CARGA_2ET
FRAC_ESTRUCTURA_SIL = 1.0 - FRAC_PROP - FRAC_CARGA_SIL


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
             color=C_CARGA if color is None else color)
    return t


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
