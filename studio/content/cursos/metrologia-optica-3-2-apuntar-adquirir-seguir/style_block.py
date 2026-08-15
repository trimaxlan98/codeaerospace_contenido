# =====================================================================
# CO.DE Academy - Familia "Metrologia optica" - MOLDE del style_block.
# Cada proyecto (leccion) lleva una COPIA identica de este bloque; solo
# cambia la cabecera `LECCION`. Se antepone al script de CADA clip; los
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

LECCION = "3.2"

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

import optica as _optica  # noqa: E402  (tras definir la sombra)
import isl as _isl  # noqa: E402
_TextSombra = Text
from optica import *  # noqa: E402,F401,F403  (trae piezas y numeros)
from isl import *  # noqa: E402,F401,F403
# El import * de las librerias re-trae `Text` de manim: se restaura la
# sombra y se inyecta en las librerias.
Text = _TextSombra
_code_brand.Text = Text
_optica.Text = Text
_isl.Text = Text

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

# --- Paleta de la familia (regla por ROL) -----------------------------
# Rojo emite (laser, pulso), ambar oscila (onda, fase), violeta es lo que
# la luz PINTA (franjas, Airy, manchas), cian es lo que se MIDE (cifras,
# detector, curvas de resultado), verde es el OBJETO medido o el satelite
# receptor. Gris: mobiliario, nunca el protagonista.
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_ACENTO = CODE_ACCENT
C_ACENTO_2 = CODE_ACCENT_2
C_HAZ = "#f43f5e"
C_ONDA = "#f59e0b"
C_FRANJA = "#a78bfa"
C_MEDIDA = "#22d3ee"
C_OBJETO = "#34d399"
C_EJE = "#31414f"

MARGEN_PIE = 0.68

# --- Numeros de la familia --------------------------------------------
# Todo valor que se rotule sale de aqui o de las librerias, nunca a mano.
F_HENE_THZ = frecuencia_de(LAMBDA_HENE) / 1e12            # 473.8
PASO_FRANJA_NM = paso_franja(LAMBDA_HENE) * 1e9           # 316.4
LC_LED_UM = longitud_coherencia(LAMBDA_HENE, 20e-9) * 1e6  # 20.0
LC_HENE_M = longitud_coherencia(LAMBDA_HENE, 1e-12)        # 0.40
FRANJAS_AIRE = franjas_indice(0.10, 2.7e-4, LAMBDA_HENE)   # 85.3
RAYLEIGH_HUBBLE_URAD = angulo_rayleigh(550e-9, 2.4) * 1e6  # 0.28
RAYLEIGH_OJO_URAD = angulo_rayleigh(550e-9, 3e-3) * 1e6    # 224
W0_ISL = 0.05                                              # m (cintura del haz)
DIV_ISL_URAD = divergencia_gauss(LAMBDA_ISL, W0_ISL) * 1e6  # 9.87
R_ISL_KM = 5000.0
HUELLA_ISL_M = huella(divergencia_gauss(LAMBDA_ISL, W0_ISL), R_ISL_KM * 1e3)  # 98.7
T_LUNA_S = tiempo_vuelo(384_400e3)                         # 2.564
T_LAGEOS_MS = tiempo_vuelo(5900e3) * 1e3                   # 39.4
PS_POR_MM = tiempo_vuelo(1e-3) * 1e12                      # 6.67 ps por mm (ida y vuelta)
AMBIG_10MHZ_M = ambiguedad_fase(10e6)                      # 15
AMBIG_100MHZ_M = ambiguedad_fase(100e6)                    # 1.5
STREHL_L14 = strehl_lineal(1 / 14)                         # 0.80 (criterio de Marechal; strehl() exacto da 0.82)
G_OPT_DBI = 10 * math.log10(ganancia_apertura(0.10, LAMBDA_ISL))     # 106.1
G_RF_DBI = 10 * math.log10(ganancia_apertura(1.0, C_LUZ / 30e9))    # 50.0
FSPL_ISL_DB = fspl_db(R_ISL_KM * 1e3, LAMBDA_ISL)          # 272.2
PT_DBM = 30.0
PR_DBM = potencia_recibida_dbm(PT_DBM, G_OPT_DBI, G_OPT_DBI, R_ISL_KM * 1e3, LAMBDA_ISL)  # -30
PR_W = 10 ** (PR_DBM / 10) * 1e-3                          # 1e-6
TASA_BPS = 10e9
FOTONES_BIT = fotones_por_bit(PR_W, LAMBDA_ISL, TASA_BPS)  # ~780
ADELANTO_URAD = angulo_adelanto(V_LEO_KMS * 1e3) * 1e6      # 50.7
DOPPLER_GHZ = doppler_optico(V_LEO_KMS * 1e3, LAMBDA_ISL) / 1e9  # 4.9
JITTER_1URAD_M = desplazamiento_por_jitter(1e-6, R_ISL_KM * 1e3)  # 5
T_GRACE_MS = tiempo_luz(SEP_GRACE_KM * 1e3) * 1e3           # 0.73
T_LISA_S = tiempo_luz(BRAZO_LISA_KM * 1e3)                  # 8.3
SENS_GRACE = sensibilidad_relativa(1e-9, SEP_GRACE_KM * 1e3)   # 4.5e-15
SENS_LISA = sensibilidad_relativa(1e-12, BRAZO_LISA_KM * 1e3)  # 4e-22


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
    """Cifra medida (Space Mono, ASCII puro) SIN posicion: el clip la
    coloca."""
    t = Text(texto, font=FUENTE_HUD, font_size=font_size,
             color=C_MEDIDA if color is None else color)
    return t


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
