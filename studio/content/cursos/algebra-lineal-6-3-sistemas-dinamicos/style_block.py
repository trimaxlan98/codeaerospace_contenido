# =====================================================================
# CO.DE Academy - "Álgebra lineal · 6.3 Sistemas dinámicos: la matriz que mueve el tiempo". Bloque de estilo del proyecto. Se antepone al script de
# CADA clip; los clips NO repiten imports: solo definen su ClipN(Scene).
#
# Este bloque es el MOLDE de la familia "Álgebra lineal": las 11 lecciones
# restantes copian este archivo y solo cambian la cabecera y la tabla de
# numeros de su leccion. Por eso la paleta, los rotulos y los helpers
# viven aqui y no en un clip.
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
from algebra_lineal import (C_AREA, C_EJE, C_I, C_IMG, C_J, C_K,  # noqa: E402
                            C_PROPIO, C_REJILLA, C_VEC, C_VIVA, PHI,
                            angulo_entre, autos, caja3, celdas, cizalla,
                            combinacion, determinante, diagonalizar,
                            ejes_principales, escala, espacio3,
                            fibonacci_matriz, flecha_libre, fmt, grafica,
                            imagen_base, inversa, marca_angulo,
                            matriz_columnas, matriz_tex, minimos_cuadrados,
                            nube, nucleo, paralelogramo, paralelogramo_de,
                            plano, plano_generado, potencia, proyeccion,
                            proyeccion_dibujo, proyeccion_matriz,
                            puntos_nube, rango, recta, reflexion, resolver,
                            rot2, rot3, satelite3, span_recta, telemetria,
                            vector, vector3, vector_columna,
                            gram_schmidt, qr, es_ortogonal, svd,  # modulos 5-6
                            aproximacion_rango, numero_condicion, elipse_de,
                            imagen_sintetica, markov_estacionario, iterar,
                            autos_complejos, eje_rotacion, rot3_eje, muestrear,
                            base_fourier, coeficientes, circulo_unidad,
                            pixeles, barras, trayectoria, triada3)

_al.Text = Text

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
# Regla: EL COLOR DICE EL PAPEL. Ambar i-sombrero / primera columna; cian
# j-sombrero / segunda columna y las CIFRAS; violeta k-sombrero (en 2D, el
# segundo vector protagonista); rojo el vector del que se habla; verde lo
# que sale de la cuenta (Mv, la suma, b); fucsia las direcciones propias;
# naranja el area del determinante; azul la rejilla que se MUEVE; gris la
# rejilla fija.
C_TITULO = CODE_INK          # #e8edf3 titulos
C_TENUE = CODE_MUTED         # #94a0b0 pies y elementos secundarios
C_ACENTO = CODE_ACCENT       # #f59e0b ambar
C_ACENTO_2 = CODE_ACCENT_2   # #ea580c naranja de cierre
C_CALCULO = C_J              # cian: cifras y resultados numericos
C_VEC_2 = C_K                # violeta: el segundo vector protagonista (2D)

MARGEN_PIE = 0.68            # separacion del pie al borde inferior
UNIDAD = 0.9                 # tamaño en pantalla de una unidad del plano
CENTRO_PLANO = DOWN * 0.15   # el plano baja un pelo: el titulo respira

# --- Numeros de la leccion --------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria, nunca escrito a
# mano en el clip: la trayectoria que se dibuja y la cifra que se lee salen
# del MISMO array.
#
# El sistema: la desviacion respecto al nominal de la temperatura de los dos
# modulos de un satelite. El estado es un vector de dos numeros y un paso de
# tiempo es una matriz:  x_{k+1} = A x_k.

# --- Clips 1 y 4: el paso ESTABLE -------------------------------------
# Encoge un 10 % y gira 25 grados: el estado cae en espiral hacia el cero
# (el satelite vuelve al nominal).
A_CONTRAE = 0.9 * rot2(25.0)
VAL_CONTRAE, MOD_CONTRAE, ANG_CONTRAE = autos_complejos(A_CONTRAE)  # 0.90, 25.0
X0 = np.array([2.6, 1.4])                # el estado de hoy (modulo A, modulo B)
X1 = A_CONTRAE @ X0                      # el estado de manana
PASOS_1 = 8
TRAY_1 = iterar(A_CONTRAE, X0, PASOS_1)  # 9 estados: el rastro del clip 1

# --- La SILLA (clips 2 y 3) -------------------------------------------
# diag(1.15, 0.80) escrita en una base girada 30 grados. Los autovalores son
# los del guion (1.15 estira, 0.80 encoge) pero sus ejes propios NO caen
# encima de los ejes grises del dibujo, donde el fucsia se confundiria con
# el mobiliario (cosecha de trampas: C_TENUE == C_EJE).
GIRO_SILLA = rot2(30.0)
D_SILLA = np.diag([1.15, 0.80])
A_SILLA = GIRO_SILLA @ D_SILLA @ GIRO_SILLA.T      # [[1.06, 0.15], [0.15, 0.89]]
LAM_SILLA, EJES_SILLA = autos(A_SILLA)             # [1.15, 0.80]
DIR_ESTIRA = EJES_SILLA[:, 0]                      # 30 grados:  lambda = 1.15
DIR_ENCOGE = EJES_SILLA[:, 1]                      # -60 grados: lambda = 0.80
VAL_SILLA, MOD_SILLA, ANG_SILLA = autos_complejos(A_SILLA)   # 1.15, 0.0

# --- La ROTACION pura (clip 2) ----------------------------------------
A_GIRA = rot2(40.0)
VAL_GIRA, MOD_GIRA, ANG_GIRA = autos_complejos(A_GIRA)       # 1.00, 40.0


def en_ejes(a, b):
    """El estado que tiene `a` sobre el eje que estira y `b` sobre el que
    encoge. Iterar la silla multiplica a por 1.15 y b por 0.80: por eso las
    trayectorias se pegan al primero y huyen por el."""
    return a * DIR_ESTIRA + b * DIR_ENCOGE


# --- Clip 2: tres mini-planos -----------------------------------------
# plano_leccion() usa el alcance de la familia (12 unidades) y tres rejillas
# asi se cruzarian en el centro del cuadro: aqui se llama a plano() directo.
UNIDAD_MINI = 0.40
ALCANCE_MINI = 3
CENTROS_MINI = (LEFT * 4.6 + CENTRO_PLANO, CENTRO_PLANO,
                RIGHT * 4.6 + CENTRO_PLANO)
ALTO_MATRIZ_MINI = UP * 2.45          # la matriz, encima de cada mini-plano
ALTO_CIFRA_MINI = DOWN * 2.20         # las cifras |lambda| y angulo, debajo
X0_CONTRAE_MINI = np.array([2.4, 0.0])
X0_GIRA_MINI = np.array([2.2, 0.0])
# El arranque de la silla se elige con mas peso del que se apaga que del
# que crece: asi la trayectoria ENTRA acercandose al eje que encoge, dobla,
# y SALE mas lejos de donde empezo (r: 1.71 -> 1.23 -> 2.12). Con un
# arranque muy pegado al eje que encoge la iteracion solo acorta y la silla
# se leeria como una contraccion.
X0_SILLA_MINI = (en_ejes(0.60, 1.60), en_ejes(-0.60, -1.60))
PASOS_MINI = 10
PASOS_SILLA_MINI = 9
PASOS_GIRA_MINI = 9                   # 9 x 40 grados = una vuelta entera
TRAY_CONTRAE_MINI = iterar(A_CONTRAE, X0_CONTRAE_MINI, PASOS_MINI)
TRAY_SILLA_MINI = tuple(iterar(A_SILLA, x, PASOS_SILLA_MINI)
                        for x in X0_SILLA_MINI)
TRAY_GIRA_MINI = iterar(A_GIRA, X0_GIRA_MINI, PASOS_GIRA_MINI)

# --- Clip 3: la silla a tamano completo -------------------------------
V_ESTIRA = 2.2 * DIR_ESTIRA           # las dos flechas propias (fucsia)
V_ENCOGE = 2.4 * DIR_ENCOGE
PASOS_3 = 12
# Mismo criterio que la silla mini: r pasa de 2.66 a 1.44 y vuelve a 2.95.
ARRANQUES_3 = ((0.55, 2.6), (-0.55, 2.6), (0.55, -2.6), (-0.55, -2.6))
TRAYS_3 = tuple(iterar(A_SILLA, en_ejes(a, b), PASOS_3)
                for a, b in ARRANQUES_3)

# --- Clip 4: converger, y el recap de la familia ----------------------
PASOS_4 = 20
TRAY_4 = iterar(A_CONTRAE, X0, PASOS_4)
A_POTENCIA = potencia(A_CONTRAE, PASOS_4)     # A^20: la rejilla al 12 %
MOD_POTENCIA = MOD_CONTRAE ** PASOS_4         # 0.90^20 = 0.12
# La matriz del recap: simetrica, area x2 y ejes propios a 45 y 135 grados.
M_RECAP = np.array([[1.5, 0.5], [0.5, 1.5]])
DET_RECAP = determinante(M_RECAP)             # 2.0
LAM_RECAP, EJES_RECAP = autos(M_RECAP)        # [2.0, 1.0]
V_RECAP_1 = 1.6 * EJES_RECAP[:, 0]            # 45 grados:  se duplica
V_RECAP_2 = 1.9 * EJES_RECAP[:, 1]            # 135 grados: no se mueve


# --- El plano de la leccion ------------------------------------------
def plano_leccion(unidad=UNIDAD, vivo=True, centro=None):
    """El plano estandar de la familia, ya colocado. Crear ANTES que los
    vectores (los localizadores leen la posicion actual)."""
    pl = plano(unidad=unidad, vivo=vivo)
    pl.move_to(CENTRO_PLANO if centro is None else centro)
    return pl


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
