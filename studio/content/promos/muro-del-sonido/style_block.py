# =====================================================================
# CO.DE Academy - promo "El muro del sonido" (curso 10, Aerodinamica).
#
# Cada circunferencia es el sonido que la fuente emitio k intervalos
# atras: nacio donde entonces estaba y ha crecido a k pasos de radio. Por
# debajo de Mach 1 los frentes se adelantan —el aire se entera de que
# vienes—; a Mach 1 son todos tangentes en la propia fuente (la pared); y
# por encima la envolvente es el cono de Mach, de semiangulo arcsen(1/M).
#
# Nada de esto se dibuja a ojo: la geometria sale de `frentes_moviles` y
# el angulo de `angulo_mach`. El dibujo se GIRA 90 grados para que la
# fuente suba y la estela caiga: asi llena el vertical.
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
from aerodinamica import (COLOR_CALCULO, COLOR_SUPERSONICO, angulo_mach,
                          frentes_moviles)

registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

FMT = _promo.formato()
GUIAS = os.environ.get("PROMO_GUIAS") == "1"

# --- La pieza --------------------------------------------------------
ONDAS = 4
PASO = 0.52                  # radio que gana una onda por intervalo
MACH_MAX = 1.8               # cono de 33.7 grados: abierto y legible

C_CIFRA = COLOR_CALCULO      # cian: las cifras
C_CONO = COLOR_SUPERSONICO   # rojo: el regimen supersonico


def cifra(mach, font_size=62):
    """Ancho fijo: de 0.00 a 1.80 sin que el numero se mueva."""
    return Text(f"{mach:4.2f}", font=FUENTE_HUD, font_size=font_size,
                color=C_CIFRA)


def frentes(mach, arriba):
    """El dibujo a ese Mach, girado para que la fuente suba, con la FUENTE
    en `arriba` (en la construccion la fuente esta en el origen, asi que
    girar alrededor del origen la deja quieta)."""
    f = frentes_moviles(mach=mach, n_ondas=ONDAS, paso=PASO)
    f.rotate(PI / 2, about_point=ORIGIN)
    return f.shift(arriba)
