# =====================================================================
# CO.DE Academy - "Cálculo vectorial · 2.3 La integral de línea:
# el trabajo de un camino".
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
# mano en el clip: la flecha dibujada y la cifra escrita no pueden
# discrepar.
PAISAJE = paisaje_colinas                # de la familia (aqui no se usa)
Z_MAX = 2.2                              # tope de altura (para color_calor)

# El campo protagonista: el viento del catalogo,
#   F(x, y) = (1 + 0.35 sen(0.9 y),  0.45 sen(0.8 x))
# No es conservativo (su rotacional no es cero), asi que el camino y el
# sentido SI importan: justo lo que cuenta esta leccion.
CAMPO = campo_viento

# El camino protagonista: un arco de A a B combado hacia arriba. Cruza el
# viento casi de lado al principio y acaba yendo a favor.
A_CAM = (-3.4, -1.5)
B_CAM = (3.4, 1.5)
COMBA_CAM = 1.6
R_CAM = camino_arco(A_CAM, B_CAM, COMBA_CAM)     # r(t), t en [0, 1]


def R_INV(t):
    """El MISMO camino recorrido al reves (clip 4)."""
    return R_CAM(1.0 - t)


W_TOTAL = integral_linea(CAMPO, R_CAM)           # 7.22  (Simpson n=2000)
W_INV = integral_linea(CAMPO, R_INV)             # -7.22 (el mismo, negado)

# El circuito cerrado del clip 4: el rotor F = (-y, x) por el circulo de
# radio 1.5. Circulacion exacta 2*pi*1.5^2 = 14.137...
C_CIRC = circulo((0.0, 0.0), 1.5)
CIRC_ROTOR = circulacion(campo_rotor, C_CIRC)    # 14.14

# Instantes de muestreo (t del camino):
T_MUESTRA = (0.15, 0.45, 0.80)   # los tres pares F/dr del clip 1
T_LUPA = 0.45                    # el punto que se descompone (clip 2)
T_CRUZA = 0.15                   # el viento casi de lado: F.dr chico
T_FAVOR = 0.65                   # el viento a favor: F.dr entero
N_TRAMOS = 12                    # los tramitos dibujados en el clip 3

ESC_F = 1.15     # unidades del plano por unidad de |F| al dibujar F
ESC_T = 1.0      # largo del paso dr dibujado (la tangente es unitaria)
ESC_LUPA = 1.35  # la misma escala, agrandada para la lupa del clip 2

# Las sumas parciales del contador. integral_linea con n=200 da lo MISMO
# que el n=2000 por defecto (diferencia < 3e-9 medida en toda la lista de
# instantes), y cuesta diez veces menos por frame: el updater lo usa.
N_CONTADOR = 200


def trabajo_hasta(t):
    """Trabajo acumulado por el camino desde el inicio hasta r(t)."""
    t = float(np.clip(t, 0.0, 1.0))
    if t < 1e-6:
        return 0.0
    return integral_linea(CAMPO, R_CAM, 0.0, t, n=N_CONTADOR)


def trabajo_inv_hasta(t):
    """Lo mismo, recorriendo el camino al reves."""
    t = float(np.clip(t, 0.0, 1.0))
    if t < 1e-6:
        return 0.0
    return integral_linea(CAMPO, R_INV, 0.0, t, n=N_CONTADOR)


def circulacion_hasta(t):
    """Circulacion acumulada del rotor por el circulo hasta el angulo t."""
    t = float(np.clip(t, 0.0, 1.0))
    if t < 1e-6:
        return 0.0
    return integral_linea(campo_rotor, C_CIRC, 0.0, t, n=N_CONTADOR)


# --- Piezas repetidas de la leccion -----------------------------------
# La malla de flechas es la MISMA en los cuatro clips (mismo paso, misma
# escala y la misma magnitud de referencia medida sobre la malla): asi el
# viento se ve igual de fuerte en todos, y el color dice lo mismo.
PASO_CAMPO = 0.9
ESCALA_CAMPO = 0.62
ANCHO_CAMPO = 4.95       # medio ancho en x de la malla (unidades del plano)
ALTO_CAMPO = 2.25        # medio alto en y (deja libres pie y titulo)
MAG_VIENTO = float(max(
    np.linalg.norm(CAMPO((x, y)))
    for x in np.arange(-ANCHO_CAMPO, ANCHO_CAMPO + 1e-9, PASO_CAMPO)
    for y in np.arange(-ALTO_CAMPO, ALTO_CAMPO + 1e-9, PASO_CAMPO)))


def campo_leccion(pl, F=None, ancho=ANCHO_CAMPO, magnitud_max=MAG_VIENTO,
                  **kwargs):
    """La malla de flechas del viento (o del campo que se le pase) con los
    parametros fijos de la leccion. `ancho` se recorta cuando el panel de
    la derecha es ancho, para que no se toquen."""
    return campo_flechas(pl, CAMPO if F is None else F, paso=PASO_CAMPO,
                         escala=ESCALA_CAMPO, x0=-ancho, x1=ancho,
                         y0=-ALTO_CAMPO, y1=ALTO_CAMPO,
                         magnitud_max=magnitud_max, **kwargs)


def par_F_dr(pl, cam, t, esc_F=ESC_F, esc_T=ESC_T, angulo=False,
             radio_angulo=0.55):
    """En el punto r(t) del camino: el punto rojo, la flecha del CAMPO
    (azul) y el PASO dr (cian, la tangente unitaria), y si se pide el
    arco del angulo entre ambos con su cifra.

    Atributos: .p (coordenadas), .F (vector campo), .T (tangente unitaria),
    .escalar (F.dr por unidad de longitud), .punto .flecha_F .flecha_T
    .arco (o None)."""
    p = np.asarray(cam.coords(t), float)
    F = np.asarray(CAMPO(p), float)
    T = cam.tangente(t)
    g = VGroup()
    g.p, g.F, g.T = p, F, T
    g.escalar = float(np.dot(F, T))
    g.punto = Dot(pl.p(p), radius=0.075, color=C_VEC)
    g.flecha_F = flecha_libre(pl, p, p + F * esc_F, color=C_CAMPO,
                              grosor=6.0)
    g.flecha_T = flecha_libre(pl, p, p + T * esc_T, color=C_CIFRA,
                              grosor=4.6)
    g.arco = None
    g.add(g.punto, g.flecha_F, g.flecha_T)
    if angulo:
        arco = marca_angulo(pl, F, T, radio=radio_angulo, color=C_CIFRA,
                            font_size=16)
        arco.shift(pl.p(p) - pl.p(0, 0))
        # La cifra se recoloca SIEMPRE sobre la bisectriz: el offset que
        # trae marca_angulo (radio + 0.32) mide al CENTRO del texto, asi
        # que el arco le entra por la izquierda. Aqui se separa contando
        # el ancho del rotulo; y si el angulo es estrecho, el hueco entre
        # las dos flechas no da para la cifra: se manda mas alla de las
        # puntas, sobre la misma bisectriz, donde hay sitio libre.
        if arco.texto is not None:
            u = F / max(1e-12, float(np.linalg.norm(F)))
            bis = u + T
            bis = bis / max(1e-12, float(np.linalg.norm(bis)))
            fuera = radio_angulo + 0.28 + arco.texto.width / 2
            if arco.grados < 38.0:
                fuera = max(fuera, max(float(np.linalg.norm(F)) * esc_F,
                                       esc_T) * pl.unidad + 0.42)
            arco.texto.move_to(pl.p(p)
                               + fuera * np.array([bis[0], bis[1], 0.0]))
        g.arco = arco
        g.add(arco)
    return g


def contador(texto, valor, color=C_RES, font_size=40, decimales=2):
    """Rotulo + DecimalNumber en la esquina superior derecha (el patron
    del altimetro del molde). Devuelve (grupo, numero, etiqueta): el
    updater del numero lo pone el clip, y debe RE-ANCLARLO cada frame
    (el ancho cambia al cambiar de cifra o de signo)."""
    etiqueta = tag_hud(texto, font_size=18)
    num = DecimalNumber(float(valor), num_decimal_places=decimales,
                        color=color, font_size=font_size,
                        include_sign=False)
    grupo = VGroup(etiqueta, num).arrange(DOWN, buff=0.16)
    grupo.to_corner(UR, buff=0.55).shift(DOWN * 0.45)
    return grupo, num, etiqueta


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
