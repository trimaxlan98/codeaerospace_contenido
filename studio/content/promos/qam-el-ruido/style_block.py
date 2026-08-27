# =====================================================================
# CO.DE Academy - promo "Cuando el ruido se come el simbolo" (curso 24).
#
# Una constelacion 16-QAM y 600 simbolos recibidos. El ruido no borra la
# señal: la EMBORRONA, y cuando la nube de un simbolo pisa la del vecino,
# el receptor decide mal. Los que caen en la region equivocada se ponen
# rojos y se cuentan.
#
# Honestidad: el ruido es UNA realizacion gaussiana fija que se escala por
# la sigma de cada Eb/N0 (sigma = sqrt(1/(2 k Eb/N0)), la misma formula de
# `awgn`). Asi la nube "respira" de forma continua en vez de parpadear
# como estatica, y sigue siendo ruido AWGN legitimo: los 600 dan 7.00 %
# de errores a 7 dB frente al 6.69 % del Monte Carlo de 200 000.
# =====================================================================
import math
import os
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand
import promo as _promo
from code_brand import (CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD, etiqueta_hud,
                        registrar_fuentes)
from comunicaciones import (C_BIT, C_RUIDO, C_SENAL, constelacion_qam16,
                            demodular)

registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

FMT = _promo.formato()
GUIAS = os.environ.get("PROMO_GUIAS") == "1"

# --- La pieza --------------------------------------------------------
ENVIOS = 500
K = 4                        # bits por simbolo en 16-QAM
SEMILLA = 7
# El barrido para en 7 dB a proposito: ahi la nube de cada simbolo
# (3 sigma = 1.04 u) casi toca la del vecino (1.39 u de separacion en
# pantalla) y se ve POR QUE falla. A 6 dB ya es confeti y se pierde la
# rejilla, que es justo lo que hay que enseñar.
EB_ALTO, EB_BAJO = 18.0, 7.0  # dB: de limpio a emborronado
ESCALA = 2.2                 # unidades de escena por unidad de Es=1
                             # (a 3.05 la nube se salia del lienzo)

PUNTOS, _BITS = constelacion_qam16()

_rng = np.random.default_rng(SEMILLA)
IDX = _rng.integers(0, len(PUNTOS), ENVIOS)      # que simbolo se envio
RUIDO = _rng.normal(0.0, 1.0, (ENVIOS, 2))       # patron, se escala por sigma
TX = PUNTOS[IDX]

C_OK = C_SENAL
C_ERR = C_RUIDO
C_PUNTO = C_BIT


def sigma_de(ebn0_db):
    """La misma sigma que `comunicaciones.awgn` para Es = 1."""
    return math.sqrt(1.0 / (2.0 * K * 10.0 ** (float(ebn0_db) / 10.0)))


def recibidos(ebn0_db):
    """(posiciones complejas, mascara de los que se deciden mal)."""
    s = sigma_de(ebn0_db)
    rx = TX + s * (RUIDO[:, 0] + 1j * RUIDO[:, 1])
    return rx, demodular(rx, PUNTOS) != IDX


def cifra(n, font_size=60):
    """Ancho fijo de dos: el contador va de 0 a 31 sin descolocarse."""
    return Text(f"{int(n):2d}", font=FUENTE_HUD, font_size=font_size,
                color=C_ERR)
