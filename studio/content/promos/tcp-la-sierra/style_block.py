# =====================================================================
# CO.DE Academy - promo "Nadie manda en Internet" (curso 25).
#
# La sierra de TCP: cada emisor sube su ventana +1 por RTT hasta que algo
# se pierde, y entonces la parte por la mitad. No hay autoridad que
# reparta el ancho de banda: la red se sostiene porque cada uno frena
# SOLO. La traza es la de `aimd`, con las perdidas donde dice la libreria,
# y la linea punteada es la media MEDIDA de esa traza.
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
from protocolos import C_CIFRA as _C_CIFRA
from protocolos import C_PAQUETE, C_PERDIDA, aimd, sierra

registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

FMT = _promo.formato()
GUIAS = os.environ.get("PROMO_GUIAS") == "1"

# --- La pieza --------------------------------------------------------
RTTS = 60
PERDIDAS = (18, 34, 50)
AIMD = aimd(rtts=RTTS, ssthresh0=32, perdidas=PERDIDAS)
TRAZA = AIMD["traza"]
MEDIA = float(np.mean(TRAZA))

C_CIFRA = _C_CIFRA
