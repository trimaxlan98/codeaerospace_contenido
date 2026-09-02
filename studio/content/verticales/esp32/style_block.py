# =====================================================================
# CO.DE Academy — "ESP32: el chip por dentro" (curso 31, VERTICAL).
#
# Bloque de estilo comun a las 16 piezas. Se antepone al script de cada
# una; las piezas NO repiten imports: solo definen su `Clip(Pieza)`.
#
# Casi todo el estilo vive en `lienzo.py` (el lenguaje visual) y en
# `esp32.py` (las piezas de dibujo y las cifras). Aqui solo queda lo que
# es de ESTE curso: los atajos de paleta, la clase base que garantiza que
# toda pieza empieza y termina igual, y los rotulos de rol.
#
# Las cuatro reglas del lienzo, recordadas para quien escriba un clip:
#
#   1. El fondo es liso y azul marino. No se toca.
#   2. Un carril, un ocupante. `L.escena(...)` y `L.dato(...)` apagan solos
#      lo que hubiera antes. No uses `self.add` para nada que ocupe sitio.
#   3. Cuatro colores. AMBAR es EL acento; CIAN solo si hay DOS señales a
#      la vez que hay que distinguir.
#   4. La cifra es tinta; la etiqueta dice de donde sale (ambar = calculada
#      aqui en el render, apagada = hoja de datos de Espressif).
#
# Y la de siempre: ninguna cifra en pantalla se inventa. Todas salen de
# `esp32.py` durante el render.
# =====================================================================
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand as _code_brand
import esp32 as chip
import lienzo as lz

_code_brand.registrar_fuentes()

_TextBase = Text


class Text(_TextBase):
    """Sombra de Text que descarta los glifos vacios (espacios).

    Manim 0.20.1 deja el glifo del espacio anclado donde nacio el texto: al
    mover el mobject, el bounding box se infla y rompe next_to / Brace /
    SurroundingRectangle. Filtrarlos tras construir lo deja estable sin
    alterar la posicion de las letras (ya esta horneada)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submobjects = [s for s in self.submobjects if s.has_points()]


# --- El lienzo --------------------------------------------------------
# UNA sola llamada, a nivel de modulo: manim importa el archivo entero
# antes de instanciar la escena, asi que aqui todavia se puede cambiar el
# mundo. `render_vertical.py` pasa formato y calidad por entorno.
FMT = lz.formato()

AZUL = lz.AZUL
TINTA = lz.TINTA
APAGADO = lz.APAGADO
AMBAR = lz.AMBAR
CIAN = lz.CIAN
LINEA = lz.LINEA

ANCHO = lz.ANCHO_SEGURO          # 5.76: lo mas ancho que puede ir centrado
BANDA = lz.alto_banda()          # 5.59: el alto de la franja del dibujo


# --- Atajos de rotulo -------------------------------------------------
def rot(texto, color=APAGADO, cuerpo=lz.ROTULO):
    """Etiqueta que nombra una parte del dibujo. Va DENTRO del grupo de la
    escena para que se mueva y se escale con ella."""
    return lz.rotulo(texto, color=color, font_size=cuerpo)


def medido(x, n=2):
    """Formatea un numero calculado, sin ceros de adorno."""
    s = f"{float(x):.{n}f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-") else "0"


# --- La clase base de toda pieza --------------------------------------
class Pieza(Scene):
    """Toda pieza del curso empieza y termina EXACTAMENTE igual.

    Empieza en azul limpio, enciende numero y marca, hace lo suyo y vuelve
    al azul limpio. Que el fundido final se lleve TAMBIEN la capa fija no
    es un descuido: es lo que hace que la costura con la pieza siguiente
    valga cero. (En el curso 28 el fundido dejaba el HUD y la marca
    encendidos y la pieza siguiente los re-encendia de golpe: parpadeo en
    las catorce uniones, invisible a ojo y evidente al medir.)

    Un clip solo escribe `pieza()`. Ni `montar` ni `fundido` se repiten."""

    NUMERO = None            # el "01" de arriba a la izquierda
    ENTRADA = 0.7
    SALIDA = 0.9

    def construct(self):
        self.L = lz.Lienzo(self, modulo=self.NUMERO)
        self.L.montar(t=self.ENTRADA)
        self.pieza()
        self.L.fundido(t=self.SALIDA)
        self.wait(0.25)

    def pieza(self):
        raise NotImplementedError("cada clip escribe su pieza()")
