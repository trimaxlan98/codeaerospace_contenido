# =====================================================================
# CO.DE Academy - promo "Que es un determinante" (curso 22).
#
# El determinante no es una receta de calculo: es CUANTO estira o encoge
# el area una transformacion. Aqui se ve: el cuadrado unidad se convierte
# en un paralelogramo y la cifra es su area, calculada por la libreria
# como el area con signo de las columnas de la matriz.
#
# La familia de matrices es M(s) = [[1, s], [s, 1]], con det = 1 - s^2:
# va de la identidad (s=0, det 1) a una matriz singular (s=1, det 0) que
# aplasta TODO el plano sobre la recta y = x. Es un barrido continuo y
# monotono, y el estado inicial vuelve solo: por eso el bucle cierra.
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
from algebra_lineal import C_AREA, C_J, paralelogramo, plano

registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

FMT = _promo.formato()
GUIAS = os.environ.get("PROMO_GUIAS") == "1"

C_CIFRA = C_J                # cian: las cifras de la familia


def matriz(s):
    """M(s) = [[1, s], [s, 1]]. det = 1 - s^2, de 1 a 0."""
    return np.array([[1.0, float(s)], [float(s), 1.0]])


def cifra(valor, font_size=62):
    """Ancho fijo: la cifra baja de 1.00 a 0.00 sin moverse de sitio."""
    return Text(f"{valor:4.2f}", font=FUENTE_HUD, font_size=font_size,
                color=C_CIFRA)
