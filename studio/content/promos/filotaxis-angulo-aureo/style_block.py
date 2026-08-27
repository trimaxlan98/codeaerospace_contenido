# =====================================================================
# CO.DE Academy - promo "El angulo que la naturaleza eligio".
# Bloque de estilo: se antepone al script de la escena.
#
# Aqui se fija el LIENZO (promo.formato lee PROMO_FORMATO del entorno), asi
# que la misma escena sale en 9:16 y en 16:9 sin tocar una linea.
# =====================================================================
import os
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand
import promo as _promo
from code_brand import (CODE_ACCENT, CODE_BG, CODE_INK, CODE_MUTED,
                        FUENTE_DISPLAY, FUENTE_HUD, etiqueta_hud,
                        registrar_fuentes)
from naturaleza import (ANGULO_AUREO_DEG, COLOR_CONSTANTE, COLOR_QUIMICA,
                        COLOR_REGLA, COLOR_VIDA, filotaxis)

registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

# El lienzo. Se resuelve al importar el modulo, antes de que exista la
# escena: es el unico momento en el que manim deja cambiarlo.
FMT = _promo.formato()
GUIAS = os.environ.get("PROMO_GUIAS") == "1"

# --- La pieza --------------------------------------------------------
SEMILLAS = 560                      # cuantas semillas tiene el disco
ANGULO = ANGULO_AUREO_DEG           # 137.5077640... (medido, no redondeado)
DESVIO = 1.15                       # cuanto se desafina el angulo en el barrido

# Las dos familias de espirales, y CUANTOS brazos de cada una se encienden.
# Que un brazo se LEA como espiral depende de cuanto gira por semilla:
#   m=8  -> +20.1 deg/semilla: 70 semillas, ~3.9 vueltas -> anillos.
#   m=13 -> -12.4 deg: ~1.5 vueltas -> todavia se lee como anillo.
#   m=21 -> +7.7 deg: 26 semillas, ~0.55 vueltas -> arco limpio del centro
#           al filo. ES el brazo que se ve en un girasol.
#   m=34 -> -4.7 deg: 16 semillas, ~0.21 vueltas, y gira AL REVES: es la
#           familia que cruza a la de 21.
# 21 y 34 son dos Fibonacci consecutivos, y son los que el ojo ve a este
# tamano de disco (~sqrt(560) = 24 semillas por vuelta en el filo).
FAMILIA_A, BRAZOS_A = 21, 5      # antihorario
FAMILIA_B, BRAZOS_B = 34, 8      # horario: cruza a la anterior

# --- Roles de color (heredados del curso 14) -------------------------
C_SEMILLA_CENTRO = COLOR_REGLA      # ambar: la regla, en el corazon del disco
C_SEMILLA_BORDE = COLOR_VIDA        # verde: lo vivo, en el filo
C_CIFRA = COLOR_CONSTANTE           # cian: TODA cifra calculada
C_ESPIRAL_A = COLOR_CONSTANTE       # la familia que gira a un lado
C_ESPIRAL_B = COLOR_QUIMICA         # la que gira al contrario


def cifra(valor, font_size=76):
    """El numero grande, en monoespaciada para que no baile al cambiar."""
    return Text(f"{valor:.1f}", font=FUENTE_HUD, font_size=font_size,
                color=C_CIFRA)
