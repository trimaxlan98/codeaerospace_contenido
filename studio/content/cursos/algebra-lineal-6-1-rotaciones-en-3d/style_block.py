# =====================================================================
# CO.DE Academy - "Álgebra lineal · 6.1 Rotaciones en 3D: toda rotación tiene un eje". Bloque de estilo del proyecto. Se antepone al script de
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
# mano en el clip: la triada que se dibuja y la matriz que se escribe salen
# del MISMO array.
DEC_R = 2                       # decimales de las matrices 3x3 en pantalla

# --- Clip 1: una guiñada alrededor del eje z ---------------------------
# Los angulos NO son libres: la proyeccion oblicua de espacio3 (azimut -38,
# elevacion 24) aplasta unas direcciones y no otras, y dos flechas de la
# triada que caen a menos de ~20 grados en pantalla se leen como una sola.
# 50 y 40 grados separan las tres flechas en las tres actitudes del clip 2
# y dejan el eje de Euler lejos de todas ellas (comprobado direccion a
# direccion sobre la proyeccion antes de escribir los clips).
ANG_Z = 50.0
R_Z = rot3("z", ANG_Z)          # [[0.64, -0.77, 0], [0.77, 0.64, 0], [0, 0, 1]]
DET_RZ = determinante(R_Z)      # 1.0: girar no crea ni destruye volumen

# --- Clip 2: alabeo (eje x) y luego guiñada (eje z) --------------------
# `anim_matriz` toma el estado TOTAL desde la identidad: el segundo paso se
# anima con R_Z @ R_X (el producto), no con el incremento.
ANG_X = 40.0
R_X = rot3("x", ANG_X)
R_COMP = R_Z @ R_X              # primero alabeo, despues guiñada
DET_COMP = determinante(R_COMP)              # 1.0
ORTO_COMP = es_ortogonal(R_COMP)             # True: R^T R = I
LONG_COLS = np.linalg.norm(R_COMP, axis=0)   # (1.0, 1.0, 1.0)
LARGO_TRIADA = 2.0


def eje_y_angulo(R):
    """El par (eje, angulo) de un giro 3D que REPRODUCE R con `rot3_eje`.

    `eje_rotacion` normaliza el signo del eje (primera componente > 0), asi
    que el angulo positivo que sale de la traza puede corresponder al giro
    contrario. Aqui se elige el signo del eje que cumple
    `rot3_eje(eje, angulo) == R`: la cifra rotulada y el giro dibujado
    salen del mismo par.
    """
    eje, ang = eje_rotacion(R)
    if not np.allclose(rot3_eje(eje, ang), np.asarray(R, dtype=float),
                       atol=1e-8):
        eje = -eje
    return eje, float(ang)


# --- Clip 3: el eje de Euler del giro compuesto -----------------------
EJE_COMP, ANG_COMP = eje_y_angulo(R_COMP)   # (0.59, 0.28, 0.76) y 63.2 grados
FIJO_COMP = R_COMP @ EJE_COMP               # el MISMO vector: R e = e
DESVIO_EJE = float(np.linalg.norm(FIJO_COMP - EJE_COMP))   # 0.0
DEC_EJE = 2
LARGO_EJE = 2.6                 # largo en pantalla de la flecha fucsia


def abanico(eje, largos=(2.2, 1.8, 2.0), fase=80.0):
    """Tres flechas a 120 grados en el plano PERPENDICULAR al eje.

    Tres y no cuatro: cuatro a 90 grados caen en pantalla por pares
    opuestos y se leen como dos rectas cruzadas, no como cuatro flechas.
    Los largos son distintos para que parezcan flechas cualesquiera y no
    una figura. La fase (80 grados) esta elegida para que las tres, sus
    imagenes tras uno y dos giros, y el propio eje no se solapen en la
    proyeccion oblicua (separacion minima 39 grados).
    """
    e = np.asarray(eje, dtype=float)
    e = e / np.linalg.norm(e)
    aux = np.array([0.0, 0.0, 1.0]) if abs(e[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(e, aux)
    u = u / np.linalg.norm(u)
    n = len(largos)
    return [largos[k] * (rot3_eje(e, fase + 360.0 * k / n) @ u)
            for k in range(n)]


ABANICO = abanico(EJE_COMP)     # 3 flechas rojas en el plano del giro

# --- Clip 4: la actitud del satelite ----------------------------------
# Dos actitudes reales (guiñada y alabeo). Elegidas, como los angulos de
# arriba, para que las tres flechas del cuerpo se separen en pantalla en A,
# en B y durante todo el giro, y para que el eje de Euler no caiga sobre
# ninguna de ellas.
GUINADA_A, ALABEO_A = -30.0, -20.0
GUINADA_B, ALABEO_B = 20.0, 35.0
R_A = rot3("z", GUINADA_A) @ rot3("x", ALABEO_A)
R_B = rot3("z", GUINADA_B) @ rot3("x", ALABEO_B)
R_AB = R_B @ inversa(R_A)                   # el giro que lleva A hasta B
EJE_AB, ANG_AB = eje_y_angulo(R_AB)         # (0.77, -0.07, 0.63) y 73.0 grados
DESVIO_AB = float(np.linalg.norm(rot3_eje(EJE_AB, ANG_AB) @ R_A - R_B))  # 0.0
PASOS_AB = 12                   # pasos del giro interpolado A -> B
LARGO_EJE_AB = 2.8


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
