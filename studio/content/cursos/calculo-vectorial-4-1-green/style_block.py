# =====================================================================
# CO.DE Academy - "Cálculo vectorial · 4.1 El teorema de Green: el borde cuenta lo de dentro".
# Bloque de estilo del proyecto. Se antepone al script de
# CADA clip; los clips NO repiten imports: solo definen su ClipN(Scene).
#
# Copia del MOLDE de la familia (leccion 1.1): solo cambian la cabecera
# y la tabla de numeros de la leccion. Paleta, rotulos y helpers son
# identicos en las 12 lecciones.
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

import algebra_lineal as _al  # noqa: E402  (tras definir la sombra)
from algebra_lineal import (C_EJE, C_I, C_J, C_K, C_REJILLA,  # noqa: E402
                            C_VIVA, fmt, flecha_libre, grafica, marca_angulo,
                            matriz_tex, plano, espacio3, recta, vector,
                            vector_columna)

_al.Text = Text

import calculo_vectorial as _cv  # noqa: E402
from calculo_vectorial import (C_CAMPO, C_CIFRA, C_FLUJO,  # noqa: E402
                               C_GRAD, C_REGION, C_RES, C_VEC, EPS0, MU0,
                               F_demo, caja_conteo, camino, camino_arco,
                               camino_escalera, camino_recta, campo_cizalla,
                               campo_dipolo, campo_flechas, campo_fuente,
                               campo_gradiente, campo_gravedad,
                               campo_radial, campo_radial3, campo_remolino,
                               campo_rotor, campo_rotor3, campo_silla,
                               campo_viento, circulacion, circulo,
                               color_calor, cubo_flujo3, curva_corte3,
                               curva_nivel3, curvas_nivel, div_num,
                               flechas3, flujo_caja3, flujo_curva,
                               flujo_parche, grad_num, integral_doble,
                               integral_linea, integral_linea_escalar,
                               linea_flujo, mosaico_circulaciones,
                               normales_borde, onda_em, paisaje_colinas,
                               paisaje_silla, paisaje_valle, parcial,
                               parche3, phi_demo, phi_gravedad,
                               plano_corte3, potencial_comprobado,
                               region_rect, rot3_num, rot_num, rueda,
                               superficie3, velocidad_luz)

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
# Regla: EL COLOR DICE EL PAPEL. Ambar la direccion privilegiada (el
# gradiente, la normal); cian las CIFRAS y las tangentes; azul las
# flechas del campo (la magnitud las gradua frio->calido); rojo la
# particula o el camino protagonista; verde lo que sale de la cuenta
# (trabajo, flujo, los dos lados de un teorema); fucsia las lineas de
# flujo; naranja la region de integracion y su borde; gris la rejilla.
C_TITULO = CODE_INK          # #e8edf3 titulos
C_TENUE = CODE_MUTED         # #94a0b0 pies y elementos secundarios
C_ACENTO = CODE_ACCENT       # #f59e0b ambar
C_ACENTO_2 = CODE_ACCENT_2   # #ea580c naranja de cierre
C_CALCULO = C_CIFRA          # cian: cifras y resultados numericos

MARGEN_PIE = 0.68            # separacion del pie al borde inferior
UNIDAD = 1.5                 # tamaño en pantalla de una unidad del plano
CENTRO_PLANO = DOWN * 0.15   # el plano baja un pelo: el titulo respira
# UNIDAD grande (1.5 en vez de 0.9): la region de esta leccion es el
# cuadrado [-1, 1]^2 y con 0.9 se veria del tamaño de un sello. Asi ocupa
# 3 x 3 unidades de pantalla y sus nueve baldosas siguen siendo legibles.

# --- Numeros de la leccion --------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria, nunca escrito a
# mano en el clip: lo dibujado y la cifra escrita no pueden discrepar.
# Green dice que ambos lados coinciden; aqui se MIDEN los dos por
# separado y se comparan en pantalla.


def F_GREEN(p):
    """El campo de la leccion: F = (x^2 - y, x + y^2).

    Su rotacional vale 2 en TODO el plano (ROT_G lo mide), asi que Green
    predice circulacion = 2 * area = 8 sobre la region R."""
    x, y = float(p[0]), float(p[1])
    return np.array([x ** 2 - y, x + y ** 2])


def F_AREA(p):
    """El campo del planimetro: F = (-y/2, x/2), rotacional 1. Con
    rotacional 1 la integral doble de Green ES el area, de modo que la
    circulacion por cualquier cerrada mide lo que encierra."""
    x, y = float(p[0]), float(p[1])
    return np.array([-y / 2.0, x / 2.0])


# La region R: el cuadrado [-1, 1]^2 (area 4).
X0, X1, Y0, Y1 = -1.0, 1.0, -1.0, 1.0
AREA_REG = (X1 - X0) * (Y1 - Y0)
P_TEST = np.array([0.37, -0.21])         # un punto cualquiera: rot es constante
ROT_G = rot_num(F_GREEN, P_TEST)         # 2.0
ROT_A = rot_num(F_AREA, P_TEST)          # 1.0
LADO_DENTRO = integral_doble(lambda p: rot_num(F_GREEN, p),
                             X0, X1, Y0, Y1, n=60)      # 8.0 (el lado ∬)

# El mosaico del clip 1: 3 x 3 baldosas con hueco entre ellas.
NX, NY = 3, 3
MARGEN_BALDOSA = 0.09
DX_B, DY_B = (X1 - X0) / NX, (Y1 - Y0) / NY
# Baldosas vecinas (0, 1) y (1, 1) de la fila central y el lado que
# comparten: la de la izquierda lo sube, la de la derecha lo baja.
CENTRO_B_IZQ = (X0 + 0.5 * DX_B, Y0 + 1.5 * DY_B)
CENTRO_B_DER = (X0 + 1.5 * DX_B, Y0 + 1.5 * DY_B)
X_COMPARTIDO = X0 + DX_B
Y_COMP_A, Y_COMP_B = Y0 + DY_B, Y0 + 2 * DY_B


def tramo_izq(t):
    """El lado compartido tal y como lo recorre la baldosa IZQUIERDA
    (es su lado derecho: antihorario, hacia ARRIBA)."""
    return np.array([X_COMPARTIDO,
                     Y_COMP_A + t * (Y_COMP_B - Y_COMP_A)])


def tramo_der(t):
    """El mismo segmento tal y como lo recorre la baldosa DERECHA (es su
    lado izquierdo: antihorario, hacia ABAJO)."""
    return np.array([X_COMPARTIDO,
                     Y_COMP_B + t * (Y_COMP_A - Y_COMP_B)])


W_IZQ = integral_linea(F_GREEN, tramo_izq)      # -0.198
W_DER = integral_linea(F_GREEN, tramo_der)      # +0.198
W_PAR = W_IZQ + W_DER                           # 0.0: el par se cancela

# El planimetro del clip 4.
R_CIRC = 1.2
CURVA_CIRC = circulo((0.0, 0.0), R_CIRC)
AREA_CIRC = float(np.pi * R_CIRC ** 2)                    # 4.524 (la formula)
CIRC_CIRCULO = circulacion(F_AREA, CURVA_CIRC)            # 4.524 (medido)


def tabla_acumulada(F, curva, n=41, nsimpson=600):
    """(ts, valores) de la integral de linea PARCIAL sobre curva(t), de 0
    a t. El contador que corre interpola en esta tabla: rehacer Simpson
    en cada frame costaria minutos de render."""
    ts = np.linspace(0.0, 1.0, n)
    vals = [0.0] + [integral_linea(F, curva, 0.0, float(t), n=nsimpson)
                    for t in ts[1:]]
    return ts, np.array(vals)


def tabla_barrido(g, x0, x1, y0, y1, n=41, nmalla=60):
    """(xs, valores) de la integral doble PARCIAL sobre [x0, x] x [y0, y1]:
    la cortina que barre la region mientras el contador sube."""
    xs = np.linspace(x0, x1, n)
    vals = [0.0] + [integral_doble(g, x0, float(x), y0, y1, n=nmalla)
                    for x in xs[1:]]
    return xs, np.array(vals)


# --- El plano y el espacio de la leccion ------------------------------
def plano_leccion(unidad=UNIDAD, vivo=False, centro=None):
    """El plano estandar de la familia, ya colocado (sin rejilla viva: en
    esta familia la rejilla es mobiliario). Crear ANTES que las piezas
    (los localizadores leen la posicion actual)."""
    pl = plano(unidad=unidad, vivo=vivo)
    pl.move_to(CENTRO_PLANO if centro is None else centro)
    return pl


def espacio_leccion(unidad=0.78, centro=None, **kwargs):
    """El espacio3 estandar de la familia, ya colocado."""
    esp = espacio3(unidad=unidad, **kwargs)
    esp.move_to((CENTRO_PLANO + DOWN * 0.35) if centro is None else centro)
    return esp


# --- Rotulos ----------------------------------------------------------
def _con_fondo(mobjeto, buff=0.14, opacidad=0.82):
    """Rectangulo del color del fondo detras de un rotulo: el texto se lee
    limpio aunque la rejilla pase por debajo."""
    fondo = BackgroundRectangle(mobjeto, color=CODE_BG, fill_opacity=opacidad,
                                buff=buff)
    return VGroup(fondo, mobjeto)


def titulo_curso(texto, font_size=34, color=None):
    """Titulo de clip (Rajdhani) anclado arriba. Zona 'arriba' de Rotulos."""
    t = titulo_marca(texto, font_size=font_size,
                     color=C_TITULO if color is None else color)
    # Tope por el HUD "MODULO 0K" de la esquina: el titulo centrado no debe
    # pasar de ~7.6 u de ancho o pisa la etiqueta (titulos de >40 caracteres).
    if t.width > 7.6:
        t.scale_to_fit_width(7.6)
    t.to_edge(UP, buff=0.52)
    return _con_fondo(t)


def pie_curso(texto, font_size=25, color=None):
    """Pie narrativo anclado abajo. Zona 'abajo' de Rotulos."""
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    if t.width > config.frame_width - 2.6:
        t.scale_to_fit_width(config.frame_width - 2.6)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(t)


def formula_pie(tex, font_size=34, color=None):
    """MathTex corto que ocupa la MISMA zona que el pie (nunca se suman)."""
    m = MathTex(tex, font_size=font_size,
                color=C_CALCULO if color is None else color)
    if m.width > config.frame_width - 3.0:
        m.scale_to_fit_width(config.frame_width - 3.0)
    m.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(m)


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


def tag_hud(texto, font_size=17, color=None):
    """Cifra o etiqueta tecnica en Space Mono (SOLO ASCII: sin acentos ni
    superindices — Space Mono no los trae)."""
    t = Text(texto, font=FUENTE_HUD, font_size=font_size,
             color=C_CALCULO if color is None else color)
    return t


def panel_derecha(*mobjetos, buff=0.35):
    """Columna de mobjects (matrices, cifras) en la esquina superior
    derecha, con fondo, sin pisar el titulo ni el HUD."""
    g = VGroup(*mobjetos).arrange(DOWN, buff=buff)
    g.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
    return _con_fondo(g, buff=0.18, opacidad=0.75)


def llave(mobjeto, texto=None, direccion=UP, font_size=22, color=None,
          buff=0.12):
    """Brace opcionalmente etiquetado (etiquetas de 1-2 palabras)."""
    col = C_CALCULO if color is None else color
    b = Brace(mobjeto, direction=direccion, color=col)
    if texto is None:
        return VGroup(b)
    t = Text(texto, font_size=font_size, color=col)
    t.next_to(b, direccion, buff=buff)
    return VGroup(b, t)


def cierre_leccion(escena, rot, linea_blanca, linea_cian, pie=None,
                   *apagar, espera=4.6):
    """El cierre a pantalla limpia de la leccion (clip 4): apaga lo que se
    le pase, limpia el titulo y muestra dos lineas (blanca y cian)."""
    if apagar:
        escena.play(*[FadeOut(m) for m in apagar], run_time=0.8)
    rot.limpiar("arriba", run_time=0.4)
    l1 = Text(linea_blanca, font_size=40, color=C_TITULO)
    l2 = Text(linea_cian, font_size=40, color=C_CALCULO)
    l1.move_to(UP * 0.42)
    l2.move_to(DOWN * 0.42)
    if pie is not None:
        rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
    escena.play(FadeIn(l1, shift=0.2 * UP), run_time=0.7)
    escena.play(FadeIn(l2, shift=0.2 * UP), run_time=0.7)
    escena.wait(espera)
    return VGroup(l1, l2)


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
