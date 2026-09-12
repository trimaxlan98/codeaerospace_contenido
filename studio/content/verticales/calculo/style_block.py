# =====================================================================
# CO.DE Academy — "Calculo visible" (curso 35, VERTICAL, estilo LIENZO,
# NARRADO).
#
# Bloque de estilo comun a las 20 piezas. Se antepone al script de cada
# una; las piezas NO repiten imports: solo definen su `Clip(Pieza)`.
#
# El lenguaje visual vive en `lienzo.py` y la materia en `calculo.py`
# (que a su vez se apoya en el sustrato de dibujo de `especiales.py`).
# Aqui queda lo que es de ESTE curso.
#
# QUE CAPA OCUPA (y por que importa al escribir una pieza):
#
#   Cada pieza es una afirmacion del calculo DE UNA VARIABLE cuya prueba
#   se puede MIRAR, y termina en una cifra que el render calcula. No es
#   un temario ordenado por capitulos: es el catalogo de las
#   demostraciones visuales del calculo.
#
#   Lo que NO se cuenta aqui, porque ya tiene curso: los campos y sus
#   operadores —gradiente, divergencia, rotacional, Green, Stokes— son
#   del curso 21; la dimension y la autosemejanza, del 26; el cambio de
#   dominio, del 32; los sistemas, del 33; y las funciones especiales,
#   del 34. Si una pieza necesita dos variables para contarse, se ha
#   salido de su capa. La unica que sale al plano es la campana (12), y
#   sale para volver a entrar: gira la curva para poder integrarla en una
#   sola variable, el radio.
#
#   Y el ZOOM se gasta UNA vez, en la pieza 03. El curso 34 zumbo cuatro
#   veces sobre Weierstrass para enseñar la excepcion; aqui se zumba para
#   enseñar la regla, y una sola vez.
#
# EL RITMO ES EL DEL CURSO MUDO, Y ES A PROPOSITO:
#
#   Este curso SI lleva voz (`es-MX-JorgeNeural`) y cama de SFX. Aun asi
#   `leer()` mantiene el suelo de 1.8 s que heredamos de los cursos 32,
#   33 y 34. Dos razones, las dos medidas:
#
#     1. La voz de esta casa PUNTUA, no narra de corrido. Se escribe
#        DESPUES del render, frase a frase, dentro de los huecos que deja
#        la animacion (`alinear_voz.py` las coloca en su instante exacto).
#        Un ritmo apretado no deja donde ponerlas.
#     2. La mitad de Instagram ve los reels sin sonido. Una pieza que solo
#        se entiende con voz esta a medio hacer.
#
#   Asi que se escribe como si fuera muda —portada con la tesis, UN verbo
#   visual, UNA cifra— y la voz se añade encima sin tocar el render.
#
# SIN NUMERACION: `Lienzo(modulo=None)`. Un "07" en la esquina de un reel
# suelto no significa nada para quien lo ve pasar.
#
# Y las cuatro reglas de siempre del lienzo:
#
#   1. El fondo es liso y azul marino. No se toca.
#   2. Un carril, un ocupante. `L.escena(...)` y `L.dato(...)` apagan
#      solos lo que hubiera. No uses `self.add` para nada que ocupe sitio.
#   3. Cuatro colores. AMBAR es EL acento; CIAN solo si hay DOS cosas a la
#      vez que hay que distinguir. En este curso el reparto natural es
#      AMBAR = lo que la pieza demuestra, CIAN = aquello con lo que se
#      compara (la secante, la escalera, la parabola, el caso conocido).
#   4. La cifra es tinta; la etiqueta dice de donde sale (ambar =
#      calculada aqui en el render, apagada = dada o elegida).
#
# Ninguna cifra en pantalla se inventa: todas salen de `calculo.py`
# durante el render, y los 231 invariantes de `sonda_calculo.py`
# demuestran que esa libreria calcula lo que dice calcular.
# =====================================================================
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import calculo as cal
import code_brand as _code_brand
import lienzo as lz

_code_brand.registrar_fuentes()

_TextBase = Text


class Text(_TextBase):
    """Sombra de Text que descarta los glifos vacios (espacios).

    Manim 0.20.1 deja el glifo del espacio anclado donde nacio el texto:
    al mover el mobject, el bounding box se infla y rompe next_to / Brace
    / SurroundingRectangle. Filtrarlos tras construir lo deja estable sin
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
BANDA = lz.alto_banda()          # 5.389: el alto de la franja del dibujo


# --- Atajos de rotulo -------------------------------------------------
def rot(texto, color=APAGADO, cuerpo=lz.ROTULO):
    """Etiqueta que nombra una parte del dibujo. Va DENTRO del grupo de
    la escena para que se mueva y se escale con ella."""
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


def soltar(dibujo, *futuros):
    """Saca del grupo los estados que solo sirven de DESTINO a un morfeo.

    El problema, y es de este curso porque aqui casi todas las piezas
    MUEVEN algo en vez de relevarlo: `Transform(a, b)` lleva `a` a donde
    esta `b` AHORA, asi que `b` tiene que estar ya en coordenadas de
    escena. Y un mobject construido con el mismo `P(x, y)` pero fuera del
    grupo no ha pasado por `encajar`: se queda centrado en el origen y el
    morfeo se va medio lienzo mas abajo.

    Asi que los destinos viajan DENTRO del grupo mientras se encaja —con
    el trazo apagado, para que no se vean ni cuenten como dibujo— y se
    sacan justo despues. Sus puntos ya estan donde tienen que estar.

    Ojo al orden: `L.escena` es quien llama a `encajar`, asi que esto va
    DESPUES de `L.escena` y nunca antes.

    Y hay un efecto de propina: mientras estan dentro, sus puntos fijan el
    bounding box del grupo, asi que el encaje no cambia de un estado a
    otro. Es la otra mitad de lo que hace `caja()`."""
    for f in futuros:
        dibujo.remove(f)
    return futuros


def caja(P):
    """El borde del cuadro, invisible: el ancla del encuadre.

    `encajar` centra y apoya el grupo por su bounding box, asi que dos
    estados del mismo dibujo con distinta extension se colocan en sitios
    distintos y el fotograma da un salto que nadie sabe explicar. Un
    recuadro con el trazo apagado fija la caja: tiene puntos (cuenta para
    el encuadre) y no pinta (no cuenta para el guardian de la fraccion,
    que mide lo que se VE).

    Si el cuadro tiene que verse, se pide `cal.recuadro(P)` normal y esto
    no hace falta."""
    r = cal.recuadro(P)
    r.set_stroke(opacity=0.0)
    return r


# --- La clase base de toda pieza --------------------------------------
class Pieza(Scene):
    """Toda pieza del curso empieza y termina EXACTAMENTE igual.

    Azul limpio -> marca de agua -> PORTADA -> lo suyo -> azul limpio.
    Que el fundido final se lleve tambien la marca no es un descuido: es
    lo que hace que la costura con la pieza siguiente valga cero (en el
    curso 28 el fundido dejaba el HUD encendido y habia parpadeo en las
    catorce uniones, invisible a ojo y evidente al medir).

    La portada NO es opcional en las piezas de contenido: es donde se
    dice, con palabras y una sola vez, de que va lo que se esta viendo.
    Por eso la exige `construct` en vez de dejarla a la disciplina de
    quien escribe el clip.

    Un clip solo escribe `pieza()`."""

    NOMBRE = None            # el nombre de la pieza, en la portada
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
                    f"que declarar NOMBRE y TESIS. La portada es la unica "
                    f"explicacion con palabras que recibe quien lo ve")
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

        El suelo de 1.8 s se mantiene AUNQUE el curso lleve voz: la voz
        se escribe despues del render y se coloca DENTRO de estos huecos
        (ver la cabecera). Un hueco de 0.6 s no admite ninguna frase, y
        una pieza sin huecos solo se puede narrar re-renderizandola."""
        t = self.LECTURA_MINIMA if t is None else float(t)
        if t < self.LECTURA_MINIMA:
            raise lz.FueraDelLienzo(
                f"leer({t}): un estado se sostiene al menos "
                f"{self.LECTURA_MINIMA} s. Si sobra tiempo, quita un plano "
                f"en vez de acortar este")
        self.wait(t)
