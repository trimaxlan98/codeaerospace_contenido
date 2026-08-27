# =====================================================================
# CO.DE Academy - promo "Por que 137.5" (curso 14).
# Segundo promo de redes, formato INFORMATIVO: el espectador tiene que
# salir sabiendo algo, no preguntandose que era esa cifra.
#
# La leccion no se cuenta con texto: se enseña el CONTRAEJEMPLO. A 90
# grados las semillas se alinean en cuatro rayos y dejan cuñas vacias; al
# barrer el angulo hasta el aureo los huecos se cierran. Y el hueco no se
# rotula: se DIBUJA, con el circulo vacio mas grande que cabe en el disco,
# medido por la libreria.
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
from naturaleza import (ANGULO_AUREO_DEG, COLOR_CONSTANTE, COLOR_MITO,
                        COLOR_REGLA, COLOR_VIDA, filotaxis, hueco_maximo)

registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

FMT = _promo.formato()
GUIAS = os.environ.get("PROMO_GUIAS") == "1"

# --- La pieza --------------------------------------------------------
SEMILLAS = 560
ANGULO = ANGULO_AUREO_DEG           # 137.5077640... (medido, no redondeado)
ANGULO_MALO = 90.0                  # una vuelta exacta entre cuatro: rayos

# --- Roles de color (heredados del curso 14) -------------------------
C_SEMILLA_CENTRO = COLOR_REGLA      # ambar: la regla, en el corazon del disco
C_SEMILLA_BORDE = COLOR_VIDA        # verde: lo vivo, en el filo
C_CIFRA = COLOR_CONSTANTE           # cian: TODA cifra calculada
C_HUECO = COLOR_MITO                # rojo: el desperdicio (idioma del curso)


def cifra(valor, font_size=68):
    """El numero grande, en monoespaciada para que no baile al cambiar."""
    return Text(f"{valor:.1f}", font=FUENTE_HUD, font_size=font_size,
                color=C_CIFRA)


def anillo(hueco, centro, color, grosor=3.0, opacidad=1.0):
    """El hueco medido, dibujado donde esta: un circulo del radio que la
    libreria calculo, en el punto que la libreria encontro."""
    # num_components alto por prudencia (el circulo de manim son 9 tramos
    # de bezier); a 20 px de radio los 9 de fabrica tambien salen limpios.
    # Si el aro parece una flor, no es el aro: son las semillas que lo
    # tocan. Un circulo vacio maximo es tangente a sus vecinas.
    c = Circle(radius=hueco["radio"], stroke_color=color,
               stroke_width=grosor, stroke_opacity=opacidad,
               num_components=64)
    c.move_to(centro + np.array([hueco["centro"][0], hueco["centro"][1], 0.0]))
    c.set_z_index(20)
    return c
