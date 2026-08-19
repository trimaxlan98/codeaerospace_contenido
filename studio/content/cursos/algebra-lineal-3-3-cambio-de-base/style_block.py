# =====================================================================
# CO.DE Academy - "Álgebra lineal · 3.3 Cambio de base: el mismo vector, otro idioma".
# Bloque de estilo del proyecto. Se antepone al script de
# CADA clip; los clips NO repiten imports: solo definen su ClipN(Scene).
#
# Copia del MOLDE de la familia (leccion 1.1): solo difieren esta cabecera
# y la tabla "Numeros de la leccion". Si difiere algo mas, es error de copia
# (comprobable con diff).
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
                            vector, vector3, vector_columna)

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
# mano en el clip: la flecha dibujada y la cifra escrita no pueden
# discrepar.
#
# La base nueva de la leccion: b1 y b2 (no ortogonales: la rejilla que
# generan es OBLICUA, que es de lo que va el cambio de base).
B1 = np.array([3.0, 1.0])                # b1: ambar (primera columna de P)
B2 = np.array([1.0, 2.0])                # b2: cian  (segunda columna de P)
P_BASE = np.column_stack([B1, B2])       # [[3, 1], [1, 2]]: P = [b1 | b2]
DET_P = determinante(P_BASE)             # 5.0: b1 y b2 no estan alineados
P_INV = inversa(P_BASE)                  # [[0.4, -0.2], [-0.2, 0.6]]

# El vector protagonista: el MISMO en los dos idiomas.
V_DEMO = np.array([4.0, 3.0])            # (4, 3) leido en la rejilla canonica
V_B = P_INV @ V_DEMO                     # (1, 1) leido en la rejilla oblicua

# La transformacion del clip 3: estira x2 a lo largo de b1 y encoge a la
# mitad a lo largo de b2. En el idioma canonico sus columnas no dicen nada;
# en el de b1 y b2 es diagonal (P^-1 A P = D_B).
D_B = escala(2.0, 0.5)                   # diag(2, 0.5)
A_MOV = P_BASE @ D_B @ P_INV             # [[2.3, -0.9], [0.6, 0.2]], det = 1
DET_A = determinante(A_MOV)              # 1.0: el area sobrevive
UNIDAD_3 = 0.70                          # clip 3: 2*b1 = (6, 2) tiene que caber

# El satelite del clip 4: actitud (guiñada 70 grados, alabeo -35) y el Sol.
# La direccion del Sol se elige fuera del plano del eje y: si no, la punta
# de la flecha aterriza sobre la etiqueta "y" que espacio3 clava al final
# del eje (y que no se puede mover ni apagar desde fuera). El alabeo es
# NEGATIVO a proposito: con alabeo positivo grande el eje z del cuerpo
# apunta hacia la camara y la proyeccion oblicua lo deja en un muñon.
GUINADA, ALABEO = 70.0, -35.0
R_SAT = rot3("z", GUINADA) @ rot3("x", ALABEO)  # ejes del cuerpo en el inercial
S_INERCIAL = np.array([1.5, 0.5, 2.5])      # la direccion del Sol, marco inercial
S_CUERPO = inversa(R_SAT) @ S_INERCIAL      # (0.98, -2.45, 1.34): la MISMA
                                            # direccion, en el marco cuerpo
DEC_SOL = 2                                 # decimales de las dos listas del Sol


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
