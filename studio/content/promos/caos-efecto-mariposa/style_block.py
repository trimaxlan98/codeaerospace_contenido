# =====================================================================
# CO.DE Academy - promo "El efecto mariposa" (curso 15, Caos).
#
# Dos copias del mismo sistema, separadas por una millonesima. Se dibujan
# a la vez y durante trece segundos son LA MISMA LINEA; luego se abren.
# La cifra de abajo es la distancia real entre las dos, paso a paso: se
# queda en 0.000 un buen rato y despues se dispara.
# =====================================================================
import os
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand
import promo as _promo
from code_brand import (CODE_ACCENT, CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD,
                        etiqueta_hud, registrar_fuentes)
from caos import (COLOR_EJE, COLOR_ERROR, COLOR_GEMELO, COLOR_SISTEMA,
                  par_lorenz, curva_lorenz)

registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

FMT = _promo.formato()
GUIAS = os.environ.get("PROMO_GUIAS") == "1"

# --- La pieza --------------------------------------------------------
EPS = 1e-6                  # la diferencia inicial, en x
PASOS = 4400                # 22 s simulados a dt = 0.005
DT = 0.005
SUBM = 2400                 # puntos del trazo (submuestreo del trazado)

# Medido con la libreria (sonda del plan): la separacion pasa de 1 a los
# 13.2 s simulados y el trazo se corta en t=22 s, donde las dos van por
# alas OPUESTAS y la separacion vale 25.90 (elegido midiendo: en otros
# cortes vuelven a coincidir de casualidad y el remate se desinfla).
T_RUPTURA = 13.2
D_FINAL = 25.90

C_A = COLOR_SISTEMA         # ambar: el sistema
C_B = COLOR_GEMELO          # cian: el gemelo
C_CIFRA = COLOR_GEMELO
C_ERROR = COLOR_ERROR


def cifra(valor, font_size=62):
    """Monoespaciada y de ancho fijo: la cifra crece de 0.000 a decenas y
    no puede bailar de sitio mientras lo hace."""
    return Text(f"{valor:7.3f}", font=FUENTE_HUD, font_size=font_size,
                color=C_CIFRA)
