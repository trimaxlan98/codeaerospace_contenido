# =====================================================================
# CO.DE Academy - promo "El secreto que se grita en publico" (curso 19).
#
# Diffie-Hellman de 1976 con numeros de juguete REALES (p=23, g=5): Ana y
# Beto no se conocen, se gritan numeros por un canal que ve todo el mundo
# y acaban los dos con el mismo secreto — que nunca cruzo el canal.
#
# Roles de color (los del curso): ambar lo PRIVADO (no se mueve nunca),
# cian lo PUBLICO (es lo unico que cruza), verde el SECRETO compartido.
# Que el verde no cruce la linea es todo el mensaje del clip.
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
from cripto import (A_DH, B_DH, COLOR_CIFRADO, COLOR_CLARO, COLOR_LLAVE,
                    G_DH, P_DH, diffie_hellman)

registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

FMT = _promo.formato()
GUIAS = os.environ.get("PROMO_GUIAS") == "1"

# --- Los numeros, calculados por la libreria -------------------------
DH = diffie_hellman()        # {'A': 8, 'B': 19, 's_ana': 2, 's_beto': 2}
PUB_A, PUB_B = DH["A"], DH["B"]
SECRETO = DH["s_ana"]
assert DH["s_ana"] == DH["s_beto"], "el acuerdo no cierra"

C_PRIVADO = COLOR_CLARO      # ambar: lo que nunca sale de casa
C_PUBLICO = COLOR_CIFRADO    # cian: lo que cruza el canal a la vista
C_SECRETO = COLOR_LLAVE      # verde: el secreto compartido


def numero(valor, color, font_size=52):
    return Text(f"{int(valor)}", font=FUENTE_HUD, font_size=font_size,
                color=color)
