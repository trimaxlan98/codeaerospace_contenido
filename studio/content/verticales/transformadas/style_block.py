# =====================================================================
# CO.DE Academy — "Transformadas: cambiar de dominio" (curso 32, VERTICAL).
#
# Bloque de estilo comun a las 20 piezas. Se antepone al script de cada
# una; las piezas NO repiten imports: solo definen su `Clip(Pieza)`.
#
# Casi todo vive en `lienzo.py` (el lenguaje visual) y en
# `transformadas.py` (las transformadas y sus dibujos). Aqui queda lo que
# es de ESTE curso.
#
# Lo que hace distinto a este curso de los tres verticales anteriores:
#
#   1. SE PUBLICA MUDO. Sin voz y sin cama de efectos: la musica la pone
#      quien lo sube. Eso quita el narrador, y como el estilo prohibe la
#      frase en pantalla, la explicacion se concentra en la PORTADA de
#      tres segundos (nombre + que vuelve facil) y no vuelve a aparecer.
#      El resto del clip es dibujo y cifra.
#   2. SIN NUMERACION. `Lienzo(modulo=None)`: la esquina de arriba queda
#      vacia. Lo pidio el dueño y tiene razon — un "07" en la esquina de
#      un reel suelto no significa nada para quien lo ve pasar.
#   3. EL RITMO LO SOSTIENE LA ANIMACION. Sin voz nadie avisa de cuando
#      hay que mirar, asi que todo estado importante se sostiene con
#      `self.leer()`, que no admite menos de 1.8 s.
#
# Y las cuatro reglas de siempre del lienzo:
#
#   1. El fondo es liso y azul marino. No se toca.
#   2. Un carril, un ocupante. `L.escena(...)` y `L.dato(...)` apagan
#      solos lo que hubiera. No uses `self.add` para nada que ocupe sitio.
#   3. Cuatro colores. AMBAR es EL acento; CIAN solo si hay DOS señales a
#      la vez que hay que distinguir.
#   4. La cifra es tinta; la etiqueta dice de donde sale (ambar =
#      calculada aqui en el render, apagada = dada).
#
# Ninguna cifra en pantalla se inventa: todas salen de `transformadas.py`
# durante el render, y 83 invariantes de `sonda_transformadas.py`
# demuestran que esa libreria calcula lo que dice calcular.
# =====================================================================
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand as _code_brand
import lienzo as lz
import transformadas as tf

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
    """Formatea un numero calculado, sin ceros de adorno.

    El `rstrip("0")` SOLO se aplica si hay punto decimal. Sin esa guarda,
    `medido(40.0, 0)` devolvia "4": el strip se comia el cero de las
    decenas y ponia en pantalla una cifra falsa que ningun render habria
    marcado como error (lo cazo el curso 31)."""
    s = f"{float(x):.{n}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s if s not in ("", "-") else "0"


# --- La clase base de toda pieza --------------------------------------
class Pieza(Scene):
    """Toda pieza del curso empieza y termina EXACTAMENTE igual.

    Azul limpio -> marca de agua -> PORTADA -> lo suyo -> azul limpio. Que
    el fundido final se lleve tambien la marca no es un descuido: es lo
    que hace que la costura con la pieza siguiente valga cero (en el curso
    28 el fundido dejaba el HUD encendido y habia parpadeo en las catorce
    uniones, invisible a ojo y evidente al medir).

    La portada NO es opcional en las piezas de contenido: sin voz, es el
    unico sitio donde se dice de que va lo que se esta viendo. Por eso la
    exige `construct` en vez de dejarla a la disciplina de quien escribe
    el clip.

    Un clip solo escribe `pieza()`."""

    NOMBRE = None            # el nombre de la transformada, en la portada
    TESIS = None             # que vuelve facil (<= 5 palabras)
    ES_MARCA = False         # intro y cierre: sin portada
    ENTRADA = 0.7
    SALIDA = 0.9

    def construct(self):
        # Sin numeracion: `modulo=None` deja vacia la esquina de arriba.
        self.L = lz.Lienzo(self, modulo=None)
        self.L.montar(t=self.ENTRADA)
        if not self.ES_MARCA:
            if not self.NOMBRE or not self.TESIS:
                raise lz.FueraDelLienzo(
                    f"{type(self).__name__}: una pieza de contenido tiene "
                    f"que declarar NOMBRE y TESIS. Sin voz, la portada es "
                    f"la unica explicacion que recibe quien lo ve")
            self.L.portada(self.NOMBRE, self.TESIS)
        self.pieza()
        self.L.fundido(t=self.SALIDA)
        self.wait(0.25)

    def pieza(self):
        raise NotImplementedError("cada clip escribe su pieza()")

    # --- ritmo ---------------------------------------------------------
    LECTURA_MINIMA = 1.8

    def leer(self, t=None):
        """Sostiene el estado que hay en pantalla el tiempo de leerlo.

        Con voz, el silencio lo llenaba la frase y bastaba `wait(0.6)`
        entre planos. Mudo, ese hueco es el unico momento en que el
        espectador puede entender lo que acaba de pasar, y 0.6 s no dan.
        El minimo es duro por el mismo motivo que los demas guardianes de
        la casa: una regla de ritmo que dependa de acordarse no sobrevive
        a dieciocho piezas."""
        t = self.LECTURA_MINIMA if t is None else float(t)
        if t < self.LECTURA_MINIMA:
            raise lz.FueraDelLienzo(
                f"leer({t}): sin voz, un estado se sostiene al menos "
                f"{self.LECTURA_MINIMA} s. Si sobra tiempo, quita un plano "
                f"en vez de acortar este")
        self.wait(t)
