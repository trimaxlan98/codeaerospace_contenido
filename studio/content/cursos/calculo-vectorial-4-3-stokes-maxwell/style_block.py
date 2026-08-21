# =====================================================================
# CO.DE Academy - "Cálculo vectorial · 4.3 Stokes y Maxwell: los campos que nos comunican".
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
UNIDAD = 0.9                 # tamaño en pantalla de una unidad del plano
CENTRO_PLANO = DOWN * 0.15   # el plano baja un pelo: el titulo respira

# --- Numeros de la leccion --------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria, nunca escrito a
# mano en el clip: lo dibujado y la cifra escrita no pueden discrepar.
PAISAJE = paisaje_colinas                # el paisaje de la familia
Z_MAX = 2.2                              # tope de altura (para color_calor)

# --- Clip 1: Stokes ---------------------------------------------------
# F = (-y, x, 0) en el espacio: rot F = (0, 0, 2) CONSTANTE. El circuito
# es el borde del rectangulo 2 x 1 en z = 0 (area 2), recorrido
# antihorario visto desde +z. Cualquier tapa que se apoye en ese borde da
# el MISMO flujo del rotacional, porque la componente z de Su x Sv vale 2
# se abombe lo que se abombe: los dos lados de Stokes son 4.0.
CAMPO_3D = campo_rotor3
ESQ_CIRCUITO = [np.array([-1.0, -0.5, 0.0]), np.array([1.0, -0.5, 0.0]),
                np.array([1.0, 0.5, 0.0]), np.array([-1.0, 0.5, 0.0])]


def BORDE3(t):
    """r(t) del circuito cerrado (t en [0, 1]), antihorario desde +z."""
    s = (t % 1.0) * 4
    i = min(int(s), 3)
    u = s - i
    A = ESQ_CIRCUITO[i]
    B = ESQ_CIRCUITO[(i + 1) % 4]
    return A + u * (B - A)


def S_PLANO(u, v):
    """La tapa PLANA que cierra el circuito (u, v en [0, 1])."""
    return np.array([2.0 * u - 1.0, v - 0.5, 0.0])


def S_DOMO(u, v):
    """La MISMA tapa, abombada: mismo borde, otra superficie."""
    return np.array([2.0 * u - 1.0, v - 0.5,
                     0.5 * np.sin(np.pi * u) * np.sin(np.pi * v)])


def ROT_3D(p):
    """El rotacional de CAMPO_3D como campo vectorial (para el flujo)."""
    return rot3_num(CAMPO_3D, p)


ROT3_CAMPO = rot3_num(CAMPO_3D, np.array([0.3, -0.2, 0.4]))   # (0, 0, 2)
CIRC_BORDE = integral_linea(CAMPO_3D, BORDE3, n=8000)         # 4.0
FLUJO_PLANO = flujo_parche(ROT_3D, S_PLANO, n=24)             # 4.0
FLUJO_DOMO = flujo_parche(ROT_3D, S_DOMO, n=24)               # 4.0
# Ocho muestras de F sobre el borde (las flechas azules del clip 1).
T_MUESTRAS_BORDE = [k / 8.0 + 1.0 / 16.0 for k in range(8)]
MAG_BORDE_MAX = max(float(np.linalg.norm(CAMPO_3D(BORDE3(t))))
                    for t in T_MUESTRAS_BORDE)

# --- Clip 2: las dos divergencias de Maxwell --------------------------
# Izquierda, el campo E de una carga puntual (campo_fuente trasladado):
# div = 0 FUERA, pero el flujo por una curva que la encierra vale 2*pi:
# ahi dentro hay fuente. Derecha, el campo B de un dipolo: div = 0 en
# todas partes, flujo 0 por cualquier cerrada y lineas de flujo CERRADAS.
P_CARGA = np.array([-2.3, 0.0])
P_IMAN = np.array([2.3, 0.0])


def CAMPO_E(p):
    return campo_fuente(np.asarray(p, dtype=float) - P_CARGA)


def CAMPO_B(p):
    return campo_dipolo(np.asarray(p, dtype=float) - P_IMAN)


R_GAUSS = 0.9
CURVA_E = circulo(P_CARGA, R_GAUSS)
CURVA_B = circulo(P_IMAN, R_GAUSS)
FLUJO_E = flujo_curva(CAMPO_E, CURVA_E)            # 6.28 = 2*pi
FLUJO_B = flujo_curva(CAMPO_B, CURVA_B)            # 0.0
P_DIV_E = P_CARGA + np.array([1.0, 0.6])
DIV_E_FUERA = div_num(CAMPO_E, P_DIV_E)            # 0.0 (fuera de la carga)
P_DIV_B = [P_IMAN + np.array([1.1, 1.7]),
           P_IMAN + np.array([-1.1, -1.7])]
DIV_B = [div_num(CAMPO_B, q) for q in P_DIV_B]     # 0.0 y 0.0
MALLA_E = dict(x0=-3.1, x1=-0.7, y0=-2.0, y1=1.6, paso=0.8)
MALLA_B = dict(x0=0.7, x1=3.1, y0=-2.0, y1=1.6, paso=0.8)
MAG_MAX_CAMPOS = 2.0                               # tope de tamano de flecha
# (semilla_y, T) de cada linea de flujo del dipolo: T medido para que la
# integracion RK4 CIERRE el lazo (vuelve a la semilla).
SEMILLAS_B = [(1.4, 7.5), (-1.4, 7.5), (2.0, 16.5), (-2.0, 16.5)]

# --- Clip 3: los dos rotacionales de Maxwell --------------------------
# Un B que crece (saliendo del plano) enrolla un E HORARIO: el signo
# menos de la ley de Faraday. Un E que crece enrolla un B ANTIHORARIO.
# Los dos remolinos son el mismo campo con signo opuesto y su rot medido
# lo dice: -2.0 y +2.0. La ruedecita gira a rot/2 radianes por segundo.
def REMOLINO_E(p):
    """El remolino de E alrededor de un B que crece: (y, -x), horario."""
    return -campo_rotor(p)


REMOLINO_B = campo_rotor                     # (-y, x), antihorario
P_ROT = np.array([1.1, 0.7])
ROT_E = rot_num(REMOLINO_E, P_ROT)           # -2.0
ROT_B = rot_num(REMOLINO_B, P_ROT)           # +2.0
VEL_E = ROT_E / 2.0                          # -1.0 rad/s
VEL_B = ROT_B / 2.0                          # +1.0 rad/s
MALLA_REMOLINO = dict(x0=-2.7, x1=2.7, y0=-1.8, y1=1.8, paso=0.9)
P_RUEDA_E = np.array([-2.0, -0.1])
P_RUEDA_B = np.array([2.0, -0.1])

# --- Clip 4: la onda --------------------------------------------------
# c no se escribe: sale de mu0 y eps0. Las fases estan elegidas para que
# ninguna flecha de la onda quede de longitud nula (una flecha nula seria
# un Dot y rompería el Transform entre gemelos de la MISMA malla).
ONDA = dict(x0=-2.6, x1=2.6, n=25, k=2.2, E0=1.5)
FASES = [0.6, 1.4, 2.2, 3.0, 3.8]
C_LUZ = velocidad_luz()                      # 299792458.08 m/s
C_LUZ_TXT = f"{C_LUZ:,.0f}".replace(",", " ")  # "299 792 458"


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


def flecha3(esp, a, b, color, grosor=2.6, punta=0.11, opacidad=1.0):
    """Flecha entre dos puntos 3D, proyectada sobre el espacio3.

    `calculo_vectorial` solo expone su version privada (`_flecha`), y esta
    leccion necesita dibujar el circuito y el campo sobre el borde a mano:
    misma receta (buff 0, punta proporcional) para que case con las
    flechas de la libreria.
    """
    A, B = esp.p(*a), esp.p(*b)
    largo = float(np.linalg.norm(B - A))
    if largo < 1e-6:
        return Dot(A, radius=0.02, color=color, fill_opacity=opacidad)
    fl = Arrow(A, B, buff=0.0, color=color, stroke_width=grosor,
               tip_length=min(punta, 0.55 * largo),
               max_tip_length_to_length_ratio=0.5,
               max_stroke_width_to_length_ratio=40)
    fl.set_opacity(opacidad)
    return fl


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
