# =====================================================================
# CO.DE Academy - promo "La tirania del cohete" (curso 17, Tsiolkovsky).
#
# La tesis se puede MEDIR y por eso se puede ver: con motor quimico y una
# sola etapa, el cohete se queda sin carga util ANTES de llegar a orbita.
# El impulso se detiene en 8840 m/s y la orbita pide 9388: faltan 548.
#
# Las tres franjas de la silueta son fracciones de la masa total y sus
# alturas SON esas fracciones (modelo del curso, eps = 8 % de la masa no
# util). A dv = 0 el cohete es 100 % carga; al final es 92 % combustible.
# =====================================================================
import os
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand
import promo as _promo
from code_brand import (CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD, etiqueta_hud,
                        registrar_fuentes)
from cohete import (COLOR_CARGA, COLOR_MUERTO, COLOR_PROPELENTE, DV_LEO,
                    EPS_ESTRUCTURA, VE_QUIMICO, carga_util,
                    fraccion_propelente, silueta_cohete)

registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

FMT = _promo.formato()
GUIAS = os.environ.get("PROMO_GUIAS") == "1"

# --- Los numeros (todos de la libreria, ver la sonda del plan) --------
VE = VE_QUIMICO             # 3500 m/s, el promedio quimico del curso
EPS = EPS_ESTRUCTURA        # 0.08
DV_CERO = -VE * np.log(EPS)  # 8840.1 m/s: aqui la carga util vale CERO
FALTAN = DV_LEO - DV_CERO    # 548.4 m/s que no hay de donde sacar

C_CIFRA = COLOR_CARGA        # cian: la cifra medida y la carga util
C_FALTA = COLOR_MUERTO       # el rojo del curso: lo que no llega


def cifra(valor, font_size=64):
    """Ancho fijo: el impulso sube de 0 a 8840 sin que el numero baile."""
    return Text(f"{valor:5.0f}", font=FUENTE_HUD, font_size=font_size,
                color=C_CIFRA)


def fracciones(dv):
    """(propelente, estructura, carga) de la masa total, sumando 1.

    La carga se recorta en cero: pasado DV_CERO el modelo la da NEGATIVA
    —esa es la tesis— pero una franja de altura negativa no se dibuja, y
    el barrido se para justo ahi.
    """
    p = fraccion_propelente(dv, VE)
    c = max(carga_util(dv, VE, EPS, 1), 0.0)
    return p, 1.0 - p - c, c
