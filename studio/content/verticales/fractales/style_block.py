# =====================================================================
# CO.DE Academy — "Fractales: la forma del infinito" (curso VERTICAL).
#
# Bloque de estilo compartido por las 16 piezas. Se antepone al script de
# cada una; las piezas NO repiten imports: solo definen su Clip(Scene).
#
# Este curso estrena formato. Tres reglas mandan sobre todas las demas:
#
#   1. **9:16 de verdad.** `promo.formato()` reconfigura el mundo de manim
#      (no basta con -r): 1080x1920 con 135 px por unidad, los mismos que
#      en 16:9, asi que los font_size de los cursos horizontales valen tal
#      cual y lo unico que cambia es la COLOCACION (columna, no fila).
#   2. **Sin subtitulos.** No hay pies de frase. Solo se escribe: la CIFRA
#      medida, su etiqueta HUD de una o dos palabras, y el identificador de
#      la pieza. Si una idea necesita una frase, la imagen esta mal hecha.
#   3. **Zona segura.** La app se come 10 % arriba, 20 % abajo y 14 % a la
#      derecha. El dibujo puede llenar el lienzo; lo que IMPORTA vive
#      dentro de la zona util (`Y_HUD`, `Y_ESCENA`, `Y_CIFRA`, `X_SEGURO`).
#
# Y la de siempre: **ninguna cifra en pantalla se inventa**. Todas salen de
# `fractales.py` con numpy y semilla fija.
# =====================================================================
import math
import os
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand as _code_brand
import fractales as fr
import promo as _promo
from code_brand import (CODE_ACCENT, CODE_ACCENT_2, CODE_BG, CODE_INK,
                        CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD,
                        esquinas_hud, registrar_fuentes)

# --- Tipografia de marca ---------------------------------------------
registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

_TextBase = Text


class Text(_TextBase):
    """Sombra de Text que descarta los glifos vacios (espacios).

    Manim 0.20.1 deja el glifo del espacio anclado donde nacio el texto: al
    mover el mobject, el bounding box se infla y rompe next_to / Brace /
    SurroundingRectangle. Filtrarlos tras construir lo deja estable sin
    alterar la posicion de las letras (ya esta horneada).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submobjects = [s for s in self.submobjects if s.has_points()]


_code_brand.Text = Text

# --- El lienzo vertical ----------------------------------------------
# UNA sola llamada, a nivel de modulo: manim importa el archivo entero
# antes de instanciar la escena, asi que aqui todavia se puede cambiar el
# mundo. `render_vertical.py` pasa formato y calidad por entorno.
FMT = _promo.formato()
GUIAS = os.environ.get("PROMO_GUIAS") == "1"

config.background_color = CODE_BG

# --- Renglones de la composicion vertical ----------------------------
# Todo lo que importa cae entre Y_SUELO y Y_TECHO. La escena grande vive
# arriba (donde el pulgar no tapa) y la cifra abajo, sobre el suelo util.
Y_TECHO = FMT.tope                    #  5.69: borde util de arriba
Y_SUELO = FMT.suelo                   # -4.27: borde util de abajo
# 0.78 y no menos: la marca de agua vive pegada al techo util y con 0.42
# el HUD de la pieza le quedaba rozando (se vio en el primer render).
Y_HUD = Y_TECHO - 0.78                #  4.91: la etiqueta de la pieza
Y_ESCENA = 1.25                       # centro del dibujo grande
Y_CIFRA = Y_SUELO + 1.05              # base del bloque de cifra
X_SEGURO = FMT.ancho / 2 - FMT.margen["der"]      # 2.88: columna de botones
ALTO_ESCENA = 8.2                     # alto tipico de una imagen a pantalla
ANCHO_UTIL = FMT.ancho - 0.9          # 7.1: margen de aire a los lados

# Ancho maximo de una pieza CENTRADA que no puede taparse. El margen
# derecho (la columna de botones) es mas ancho que el izquierdo, asi que
# manda el, y va doblado porque el texto se centra en x=0.
ANCHO_SEGURO = 2.0 * min(FMT.ancho / 2 - FMT.margen["izq"],
                         FMT.ancho / 2 - FMT.margen["der"])   # 5.76

# --- Paleta por ROL (un color = un significado en TODO el curso) -----
C_MEDIDO = fr.COLOR_MEDIDO        # #22d3ee cian: TODA cifra calculada aqui
C_REGLA = fr.COLOR_REGLA          # #f59e0b ambar: la regla, el instrumento
C_ESCAPA = fr.COLOR_ESCAPA        # #ea580c naranja: lo que se va al infinito
C_ATRAPADO = fr.COLOR_ATRAPADO    # #7c3aed violeta: lo que queda preso
C_VIDA = fr.COLOR_VIDA            # #34d399 verde: costa, helecho, terreno
C_EJE = fr.COLOR_EJE              # #31414f mobiliario
C_EXTERNO = fr.COLOR_EXTERNO      # #94a0b0 gris: dato de la literatura
C_TINTA = CODE_INK


# --- Piezas de texto (las UNICAS permitidas) -------------------------
def cabe(mob, que="texto"):
    """Aborta el render si la pieza se sale de la zona que la app no tapa.

    En vertical la columna derecha se la comen los botones de la app, y un
    rotulo de 6.7 unidades centrado se mete ahi sin que se note en el
    frame de validacion (paso en el clip 02: "VECES EL TRIANGULO"). Mejor
    que el render falle con el ancho medido que publicar texto tapado.
    """
    if mob.width > ANCHO_SEGURO + 1e-6:
        raise ValueError(
            f"{que} mide {mob.width:.2f} de ancho y la zona segura son "
            f"{ANCHO_SEGURO:.2f}: acortalo o baja el font_size")
    return mob


def hud(texto, font_size=19, color=CODE_MUTED):
    """Etiqueta de telemetria: Space Mono, MAYUSCULAS con aire.

    SOLO ASCII: Space Mono no trae acentos ni superindices, y un glifo que
    falta sale como caja. Los acentos viven en el clip.json, que nadie
    renderiza. El ancho se comprueba contra la zona segura.
    """
    t = Text(" ".join(str(texto).upper()), font=FUENTE_HUD,
             font_size=font_size, color=color)
    return cabe(t, f'HUD "{texto}"')


def hud_pieza(texto, color=CODE_MUTED):
    """El identificador de la pieza, arriba y dentro de la zona util."""
    t = hud(texto, font_size=19, color=color)
    t.move_to(UP * Y_HUD)
    t.set_z_index(900)
    return t


def cifra(texto, font_size=104, color=C_MEDIDO):
    """LA cifra. Monoespaciada para que no baile al cambiar de valor."""
    t = Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)
    return cabe(t, f'cifra "{texto}"')


def bloque_cifra(valor, etiqueta, font_size=104, color=C_MEDIDO,
                 color_etiqueta=None, buff=0.30):
    """La cifra con su etiqueta encima, anclada al suelo util.

    Es el unico "texto" que lleva un clip aparte del HUD de la pieza: un
    numero y de que es. El grupo trae `.numero` y `.etiqueta` sueltos para
    poder animar solo uno de los dos.
    """
    et = hud(etiqueta, font_size=20,
             color=color_etiqueta if color_etiqueta else CODE_MUTED)
    num = cifra(valor, font_size=font_size, color=color)
    g = VGroup(et, num).arrange(DOWN, buff=buff)
    g.move_to(UP * (Y_CIFRA + g.height / 2 - 0.5))
    g.numero = num
    g.etiqueta = et
    g.set_z_index(800)
    return g


# Los tres renglones del pie de cifra. Se fijan aqui (no a ojo en cada
# clip) para que la cifra caiga SIEMPRE en el mismo sitio: en vertical, el
# ojo vuelve al mismo punto de la pantalla y un numero que se mueve entre
# clips se lee como otro numero.
Y_ETIQUETA = -2.55       # que se esta midiendo (gris)
Y_NUMERO = -3.22         # LA cifra (cian si la calculo la libreria)
Y_SUB = -4.02            # la condicion de la medida (ambar: el instrumento)


def medida(valor, etiqueta=None, sub=None, color=C_MEDIDO,
           color_sub=C_REGLA, font_size=104, font_etiqueta=20,
           font_sub=18):
    """El pie de cifra completo: etiqueta / CIFRA / condicion.

    Devuelve un VGroup con `.numero`, `.etiqueta` y `.sub` sueltos, cada uno
    ya en su renglon, para poder cambiar solo uno sin mover los otros.
    Ninguna de las tres piezas se sale de la zona segura: la etiqueta y la
    condicion son de una o dos palabras a proposito.
    """
    g = VGroup()
    num = cifra(valor, font_size=font_size, color=color)
    num.move_to(UP * Y_NUMERO)
    g.numero = num
    g.add(num)
    g.etiqueta = None
    g.sub = None
    if etiqueta is not None:
        et = hud(etiqueta, font_size=font_etiqueta, color=CODE_MUTED)
        et.move_to(UP * Y_ETIQUETA)
        g.etiqueta = et
        g.add(et)
    if sub is not None:
        sb = hud(sub, font_size=font_sub, color=color_sub)
        sb.move_to(UP * Y_SUB)
        g.sub = sb
        g.add(sb)
    g.set_z_index(800)
    return g


def cambiar(escena, fuera, dentro, salida=0.30, entrada=0.36):
    """Relevo LIMPIO de rotulos: lo viejo se apaga ANTES de que entre lo
    nuevo, nunca a la vez.

    Un fundido cruzado en el mismo sitio deja los dos textos superpuestos
    medio segundo. En un curso con pies de texto eso se perdona; en uno SIN
    subtitulos, ese medio segundo es justo el que el espectador esta usando
    para leer la cifra. Se vio en el clip 05: "24" y "200000" encimados.
    """
    def lista(x):
        if x is None:
            return []
        if isinstance(x, (list, tuple)):
            return [m for m in x if m is not None]
        return [x]

    fuera, dentro = lista(fuera), lista(dentro)
    if fuera:
        escena.play(*[FadeOut(m, scale=0.92) for m in fuera],
                    run_time=salida)
    if dentro:
        escena.play(*[FadeIn(m, scale=1.06) for m in dentro],
                    run_time=entrada)


def relevo(escena, viejo, nuevo, run_time=0.4):
    """Cambia una pieza de texto por otra en el MISMO sitio, sin que las dos
    coexistan ni un frame (la regla dura: nada encimado)."""
    nuevo.move_to(viejo.get_center())
    escena.play(FadeOut(viejo, scale=0.9), FadeIn(nuevo, scale=1.05),
                run_time=run_time)
    return nuevo


def titulo(texto, font_size=52, color=CODE_INK):
    """Titulo display. Solo para la intro y el cierre: una pieza de curso
    no lleva titulo en pantalla, lleva imagen."""
    return Text(texto, weight="SEMIBOLD", font_size=font_size, color=color)


def nota_externa(texto, font_size=18):
    """Un dato que NO calcula la libreria (literatura), en gris.

    El cian significa "medido aqui": si un numero viene de un articulo, va
    en gris y con su fuente. Se usa contadisimas veces.
    """
    return hud(texto, font_size=font_size, color=C_EXTERNO)


# --- Colocacion ------------------------------------------------------
def a_escena(mob, alto=None, y=Y_ESCENA):
    """Coloca un mobject como 'el dibujo grande' de la pieza."""
    if alto is not None:
        mob.height = alto
    if mob.width > ANCHO_UTIL:
        mob.width = ANCHO_UTIL
    mob.move_to(UP * y)
    return mob


def marco_escena(alto=ALTO_ESCENA, y=Y_ESCENA, ancho=None):
    """Rectangulo guia (invisible en el render) del hueco del dibujo."""
    r = Rectangle(width=ancho or ANCHO_UTIL, height=alto,
                  stroke_opacity=0.0, fill_opacity=0.0)
    r.move_to(UP * y)
    return r


def poli(pts, color=C_VIDA, grosor=2.6, opacidad=1.0):
    """Poligonal (n,2) de la libreria -> VMobject en coordenadas de escena."""
    return fr.poligonal(pts, color=color, grosor=grosor, opacidad=opacidad)


def encajar(mob, alto, y=Y_ESCENA, x=0.0):
    """Escala por ALTO (conservando proporcion) y centra donde se pida."""
    mob.height = alto
    mob.move_to(np.array([x, y, 0.0]))
    return mob


# --- Marca de la escena (sombra de Scene) ----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    """Fondo de marca + esquinas HUD + marca de agua recolocada.

    En vertical la esquina inferior derecha es la columna de botones de
    Instagram: `promo.marca_promo` sube la marca al borde superior. El
    fondo opaco cubre el lienzo entero para que ningun re-encodeo de la app
    deje una linea negra en el borde.

    Las piezas de IDENTIDAD (la intro y el cierre) ponen `marca_chica` y
    `esquinas` a False: alli el wordmark grande ES la marca, y repetirla
    pequeña arriba la duplica.
    """

    marca_chica = True
    esquinas = True

    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(_promo.fondo_seguro(FMT))
        if self.esquinas:
            self.add(esquinas_hud(opacidad=0.14))
        if self.marca_chica:
            self.add(_promo.marca_promo(FMT, opacidad=0.34))
        if GUIAS:
            self.add(_promo.guias(FMT))


def reticula(paso=0.9, opacidad=0.10, color=C_EJE):
    """Reticula HUD tenue a pantalla completa. Nace invisible (la opacidad
    se enciende al paso del escaneo de la intro)."""
    ancho = FMT.ancho / 2
    alto = FMT.alto / 2
    lineas = VGroup()
    x = -ancho
    while x <= ancho + 1e-6:
        lineas.add(Line([x, -alto, 0], [x, alto, 0], stroke_width=1.0))
        x += paso
    y = -alto
    while y <= alto + 1e-6:
        lineas.add(Line([-ancho, y, 0], [ancho, y, 0], stroke_width=1.0))
        y += paso
    lineas.set_stroke(color=color, opacity=opacidad)
    return lineas


def wordmark(font_size=84):
    """CO.DE en grande, centrado en el origen.

    Devuelve (grupo, co, punto, de): las letras en tinta y el punto en
    ambar, sueltos para poder animarlos por separado.
    """
    co = Text("CO", weight="SEMIBOLD", font_size=font_size, color=CODE_INK)
    pt = Text(".", weight="BOLD", font_size=font_size, color=CODE_ACCENT)
    de = Text("DE", weight="SEMIBOLD", font_size=font_size, color=CODE_INK)
    g = VGroup(co, pt, de).arrange(buff=0.10, aligned_edge=DOWN)
    g.move_to(ORIGIN)
    return g, co, pt, de


def academy(font_size=27):
    """ACADEMY con tracking amplio (las letras van espaciadas a mano: la
    sombra de Text descarta los glifos de espacio, pero su posicion ya
    quedo horneada)."""
    return Text("A C A D E M Y", weight="MEDIUM", font_size=font_size,
                color=CODE_MUTED)


def subrayado_marca(referencia, margen=0.14, grosor=3.5):
    """Linea con el degradado de marca (ambar -> naranja) bajo un mobject."""
    linea = Line(referencia.get_corner(DL), referencia.get_corner(DR),
                 stroke_width=grosor)
    linea.set_color(color_gradient([CODE_ACCENT, CODE_ACCENT_2], 2))
    linea.shift(DOWN * margen)
    return linea
