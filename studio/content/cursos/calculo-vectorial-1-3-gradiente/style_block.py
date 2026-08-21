# =====================================================================
# CO.DE Academy - "Cálculo vectorial · 1.3 El gradiente: la flecha que sube".
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
NIVELES = [0.25, 0.55, 0.9, 1.3, 1.7, 2.05]      # las curvas del mapa
P_PICO = np.array([1.2, 0.8])            # cima alta (f = 2.22)
P_PEQ = np.array([-1.8, -1.2])           # cima baja (f = 1.41)
Z_PICO = PAISAJE(P_PICO)
Z_PEQ = PAISAJE(P_PEQ)

# --- El punto protagonista y su gradiente (clips 1 y 2) ---------------
P_G = np.array([0.2, -0.1])              # entre las dos colinas, bien visible
G = grad_num(PAISAJE, P_G)               # (df/dx, df/dy) medido
GX, GY = float(G[0]), float(G[1])        # 0.51 y 0.58
G_MOD = float(np.linalg.norm(G))         # 0.77
G_DIR = G / G_MOD                        # la direccion unitaria del gradiente
ESC_GRAD = 2.0        # unidades de plano por unidad de gradiente (clips 1-2)
ESC_NIVEL = 1.0       # la misma escala, mas corta, para el mapa del clip 3

# El abanico del clip 2: 8 direcciones unitarias equiespaciadas que
# ARRANCAN en la del gradiente, asi que la ganadora es exactamente G_DIR y
# las dos perpendiculares miden 0.00 (el guino al clip 3).
N_ABANICO = 8
R_ABANICO = 1.25      # largo de las flechas del abanico (unidades de plano)
R_TAG = 1.95          # radio donde se posan las cifras (fuera de las puntas)
_ANG_G = float(np.arctan2(GY, GX))
DIRS_ABANICO = [np.array([np.cos(_ANG_G + k * 2 * np.pi / N_ABANICO),
                          np.sin(_ANG_G + k * 2 * np.pi / N_ABANICO)])
                for k in range(N_ABANICO)]
DERIV_ABANICO = [float(np.dot(G, u)) for u in DIRS_ABANICO]
K_GANA = int(np.argmax(DERIV_ABANICO))           # 0: la del gradiente
K_CERO = [k for k, d in enumerate(DERIV_ABANICO) if abs(d) < 1e-9]
K_BAJA = [k for k, d in enumerate(DERIV_ABANICO) if d < -1e-9]


# --- Los puntos del mapa del clip 3 -----------------------------------
def _punto_en_nivel(centro, grados, nivel, hi=4.5):
    """El punto del rayo (centro, grados) donde PAISAJE vale EXACTAMENTE
    `nivel`, por biseccion: asi el punto se apoya en la curva dibujada."""
    d = np.array([np.cos(np.radians(grados)), np.sin(np.radians(grados))])
    lo = 0.02
    for _ in range(80):
        r = (lo + hi) / 2
        if PAISAJE(centro + r * d) > nivel:
            lo = r
        else:
            hi = r
    return centro + ((lo + hi) / 2) * d


# (centro, angulo, nivel): 4 puntos repartidos por la colina alta y 1 en
# la baja; los 5 caen sobre curvas de NIVELES, que es lo que se dibuja.
# Los angulos y niveles estan elegidos para que las puntas de las flechas
# no se amontonen en la cima (sobra >= 0.45 unidades hasta el centro).
_SEMILLAS_NIVEL = [(P_PICO, 255, 0.9), (P_PICO, 20, 0.55),
                   (P_PICO, 300, 0.55), (P_PICO, 150, 0.55),
                   (P_PEQ, 200, 0.9)]
PUNTOS_NIVEL = [_punto_en_nivel(c, a, nv) for (c, a, nv) in _SEMILLAS_NIVEL]
NIVELES_PUNTO = [nv for (_, _, nv) in _SEMILLAS_NIVEL]
GRADS_NIVEL = [grad_num(PAISAJE, p) for p in PUNTOS_NIVEL]
TANS_NIVEL = [np.array([-g[1], g[0]]) / np.linalg.norm(g)
              for g in GRADS_NIVEL]     # tangente unitaria al nivel
DOTS_NIVEL = [float(np.dot(g, t)) for g, t in zip(GRADS_NIVEL, TANS_NIVEL)]
PERP_PEOR = max(abs(d) for d in DOTS_NIVEL)      # 0.00: la comprobacion
I_DEMO = 0                               # el punto que se explica despacio
R_TANGENTE = 0.95                        # medio largo del segmento tangente

# --- El ascenso por gradiente del clip 4 ------------------------------
P0_ASCENSO = np.array([2.9, -2.2])       # llano del sureste -> cima alta
T_ASCENSO = 18.0                         # la linea de flujo se para sola
P0_CERCA = np.array([1.0, -2.6])         # arranca al lado y acaba en la baja
T_CERCA = 22.0


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
