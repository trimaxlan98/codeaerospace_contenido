# =====================================================================
# CO.DE Academy - "Cerrar el enlace: la cuenta en decibelios"
# Bloque de estilo del proyecto. Se antepone al script de CADA clip; los
# clips NO repiten imports: solo definen su clase ClipN(Scene).
# =====================================================================
import math
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import bloques as _bloques
import code_brand as _code_brand
from bloques import bloque, conectar, flujo
from brillo import con_brillo, punto_brillante
from code_brand import (CODE_ACCENT, CODE_ACCENT_2, CODE_BG, CODE_INK,
                        CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD, Rotulos,
                        esquinas_hud, etiqueta_hud, marca_agua,
                        registrar_fuentes, titulo_marca)
from senal import destello
from transiciones import (transicion_deslizar, transicion_persiana,
                          transicion_zoom)

# --- Tipografia de marca ---------------------------------------------
# El default se fija sobre el Text ORIGINAL de Manim (antes de la sombra)
# para que tambien lo hereden los helpers de bloques.py / code_brand.py.
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


# Los helpers de las librerias tambien deben usar la sombra.
_bloques.Text = Text
_code_brand.Text = Text

import enlace as _enlace  # noqa: E402  (tras definir la sombra)
from enlace import (barra_margen, cascada_db, curva_fspl,  # noqa: E402
                    curva_shannon, escalera_modcod, frente_esferico,
                    fspl_db, nube_simbolos, patron_ganancia, piso_ruido,
                    regla_db, termometro_ruido)

_enlace.Text = Text

_RotulosBase = Rotulos


class Rotulos(_RotulosBase):
    """Relevo SECUENCIAL por zona: el rotulo anterior sale ANTES de que
    entre el nuevo.

    El original cruza ambos en la misma animacion y durante ~0.5 s se ven
    superpuestos (dos frases a la vez en el pie). Aqui nunca coinciden.
    """

    def mostrar(self, mobjeto, zona="abajo", run_time=0.45, salida=0.25,
                **kwargs):
        if self._zonas.get(zona) is not None:
            self.limpiar(zona, run_time=salida)
        return super().mostrar(mobjeto, zona=zona, run_time=run_time,
                               **kwargs)

config.background_color = CODE_BG

# --- Paleta del curso -------------------------------------------------
# Regla: lo que SUMA es verde, lo que RESTA es rojo, la SEÑAL es ambar, el
# RUIDO violeta y el RESULTADO (saldo, margen, techo) cian.
C_TITULO = CODE_INK          # #e8edf3 titulos
C_TENUE = CODE_MUTED         # #94a0b0 pies y elementos secundarios
C_ACENTO = CODE_ACCENT       # #f59e0b ambar
C_ACENTO_2 = CODE_ACCENT_2   # #ea580c naranja de cierre
C_SENAL = "#f59e0b"          # ambar: la señal, la potencia util, la PIRE
C_GANANCIA = "#34d399"       # verde: lo que suma (ganancia, G/T, -k)
C_PERDIDA = "#f43f5e"        # rojo: lo que resta (FSPL, atmosfera, lluvia)
C_RUIDO = "#a78bfa"          # violeta: el ruido, N0, la temperatura
C_MARGEN = "#22d3ee"         # cian: el saldo, el margen, el techo del canal
C_EJE = "#31414f"            # gris azulado de mobiliario

MARGEN_PIE = 0.68            # separacion del pie al borde inferior

# --- Numeros del curso ------------------------------------------------
# Un enlace de television directa a casa, el mismo de principio a fin: los
# ocho clips cuentan ESTE enlace y no ocho enlaces distintos. Todo valor que
# se rotule sale de aqui o de la libreria, nunca escrito a mano en el clip.
P_TX_W = 20.0                       # potencia del transmisor a bordo
P_TX_DBW = 10 * math.log10(P_TX_W)  # 13.0 dBW
G_TX_DB = 45.0                      # ganancia de la antena del satelite
PIRE_DBW = P_TX_DBW + G_TX_DB       # 58.0 dBW
D_KM = 36000.0                      # altura del arco geoestacionario
F_GHZ = 12.0                        # banda Ku de bajada
L_ATM_DB = 1.5                      # atmosfera clara
G_RX_DB = 35.0                      # antena domestica de 60 cm
T_SIS_K = 150.0                     # temperatura de ruido del sistema
K_DBW = 228.6                       # -10log10(k), la constante de Boltzmann
RB_BPS = 50e6                       # tasa util del portador

FSPL_DB = fspl_db(D_KM, F_GHZ)                       # 205.2 dB
GT_DB = G_RX_DB - 10 * math.log10(T_SIS_K)           # 13.2 dB/K
C_RX_DBW = PIRE_DBW - FSPL_DB - L_ATM_DB + G_RX_DB   # -113.6 dBW
C_RX_W = 10 ** (C_RX_DBW / 10)                       # 4.3e-12 W
CN0_DBHZ = PIRE_DBW - FSPL_DB - L_ATM_DB + GT_DB + K_DBW   # 93.1 dBHz
EBN0_DB = CN0_DBHZ - 10 * math.log10(RB_BPS)               # 16.1 dB

# Escalera DVB-S2X del clip 8: (etiqueta, Es/N0 requerido dB, bits/s/Hz).
MODCODS = (("QPSK 1/2", 1.00, 0.99), ("QPSK 3/4", 4.03, 1.49),
           ("8PSK 3/4", 7.91, 2.23), ("16APSK 3/4", 10.21, 2.97),
           ("32APSK 4/5", 13.64, 3.95))


# --- Rotulos ----------------------------------------------------------
def titulo_curso(texto, font_size=34, color=None):
    """Titulo de clip (Rajdhani) anclado arriba. Zona 'arriba' de Rotulos."""
    t = titulo_marca(texto, font_size=font_size,
                     color=C_TITULO if color is None else color)
    if t.width > config.frame_width - 2.0:
        t.scale_to_fit_width(config.frame_width - 2.0)
    t.to_edge(UP, buff=0.52)
    return t


def pie_curso(texto, font_size=25, color=None):
    """Pie narrativo anclado abajo. Zona 'abajo' de Rotulos."""
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    if t.width > config.frame_width - 2.6:
        t.scale_to_fit_width(config.frame_width - 2.6)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return t


def formula_pie(tex, font_size=34, color=None):
    """MathTex corto que ocupa la MISMA zona que el pie (nunca se suman)."""
    m = MathTex(tex, font_size=font_size,
                color=C_ACENTO if color is None else color)
    if m.width > config.frame_width - 3.0:
        m.scale_to_fit_width(config.frame_width - 3.0)
    m.to_edge(DOWN, buff=MARGEN_PIE)
    return m


def hud_modulo(texto):
    """Etiqueta de telemetria del modulo, esquina superior izquierda."""
    t = etiqueta_hud(texto)
    t.to_corner(UL, buff=0.5)
    return t


def tag_junto(mobjeto, texto, direccion=DOWN, buff=0.16, font_size=18,
              color=None):
    """Etiqueta corta de mobiliario pegada a un mobject (no narrativa)."""
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    t.set_opacity(0.85)
    t.next_to(mobjeto, direccion, buff=buff)
    return t


def llave(mobjeto, texto=None, direccion=UP, font_size=22, color=None,
          buff=0.12):
    """Brace opcionalmente etiquetado (etiquetas de 1-2 palabras)."""
    col = C_ACENTO if color is None else color
    b = Brace(mobjeto, direction=direccion, color=col)
    if texto is None:
        return VGroup(b)
    t = Text(texto, font_size=font_size, color=col)
    t.next_to(b, direccion, buff=buff)
    return VGroup(b, t)


def antena(escala=1.0, color=None, mirando=RIGHT):
    """Antena parabolica esquematica: plato, foco en su brazo y pie.

    Vive en el style_block y no en la libreria porque es puro mobiliario
    narrativo (el "quien habla"), no una pieza que calcule nada.

    Se construye SIEMPRE mirando a la derecha y luego se gira el plato solo,
    no el pie: una antena inclinada al cielo sigue teniendo el mastil
    vertical y la base horizontal, y girar el grupo entero la tumbaba.
    """
    col = C_TENUE if color is None else color
    # Arco centrado en ORIGIN que ocupa el lado -x: su concavidad (y por
    # tanto la direccion en que "mira" el plato) queda hacia +x.
    plato = Arc(radius=0.5, start_angle=PI - 0.62, angle=1.24, color=col,
                stroke_width=3.2)
    foco = Dot(RIGHT * 0.26, radius=0.045, color=col)
    brazo = Line(plato.point_from_proportion(0.5), foco.get_center(),
                 stroke_width=1.5, color=col).set_opacity(0.8)
    cabeza = VGroup(plato, brazo, foco)
    cabeza.rotate(angle_of_vector(mirando), about_point=ORIGIN)

    mastil = Line(ORIGIN + DOWN * 0.10, DOWN * 0.66, stroke_width=2.6,
                  color=col)
    base = Line(mastil.get_end() + LEFT * 0.20, mastil.get_end() + RIGHT * 0.20,
                stroke_width=2.6, color=col)
    return VGroup(cabeza, mastil, base).scale(escala)


def satelite(escala=1.0, color=None):
    """Satelite esquematico: cuerpo con dos paneles."""
    col = C_TENUE if color is None else color
    cuerpo = Rectangle(width=0.42, height=0.34, stroke_width=2.4, color=col)
    paneles = VGroup(*[
        Rectangle(width=0.46, height=0.22, stroke_width=1.8, color=col)
        .set_opacity(0.75) for _ in range(2)])
    paneles[0].next_to(cuerpo, LEFT, buff=0.10)
    paneles[1].next_to(cuerpo, RIGHT, buff=0.10)
    return VGroup(paneles[0], cuerpo, paneles[1]).scale(escala)


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
