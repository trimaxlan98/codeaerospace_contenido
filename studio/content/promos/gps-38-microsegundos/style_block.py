# =====================================================================
# CO.DE Academy - promo "Los 38 microsegundos del GPS" (curso 16).
#
# La cadena que se ve: el reloj del satelite adelanta 38.5 us al dia
# (SR -7.21 + GR +45.72), y como el GPS mide distancias con el tiempo de
# vuelo de la luz, cada microsegundo son 300 metros. Sin corregir, en un
# dia el error llega a 11.5 km.
#
# El satelite da DOS vueltas exactas (un dia de GPS son dos orbitas), asi
# que termina donde empezo: eso es lo que cierra el bucle.
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
from relatividad import (COLOR_ERROR, COLOR_SATELITE, derivas_gps,
                         error_metros, orbita_gps)

registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

FMT = _promo.formato()
GUIAS = os.environ.get("PROMO_GUIAS") == "1"

# --- Los numeros (de la libreria; sonda en el plan) -------------------
DERIVA_SR, DERIVA_GR, DERIVA = derivas_gps()   # -7.21, +45.72, +38.50 us/dia
HORAS_DIA = 24.0
ERROR_DIA_KM = error_metros(HORAS_DIA) / 1000.0  # 11.543 km
VUELTAS = 2                  # un dia de GPS son dos orbitas exactas
ALPHA0 = 0.125               # de donde sale (y a donde vuelve) el satelite
COLA = 0.22                  # vueltas de estela detras del satelite

C_CIFRA = COLOR_ERROR        # rojo: el error que se acumula
C_SAT = COLOR_SATELITE


def cifra(km, font_size=58):
    """El error acumulado. Ancho fijo para que no baile al pasar de una
    cifra a dos: ' 0.0 KM' -> '11.5 KM'."""
    return Text(f"{km:4.1f} KM", font=FUENTE_HUD, font_size=font_size,
                color=C_CIFRA)
