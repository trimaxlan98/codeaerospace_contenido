# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 4.3 Congestión: la cortesía que sostiene la red".
# Bloque de estilo del proyecto. Se antepone al script de CADA clip;
# los clips NO repiten imports: solo definen su ClipN(Scene).
#
# Copia del MOLDE de la familia (leccion 1.1): solo cambian esta
# cabecera y la tabla de numeros de la leccion.
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
from transiciones import (transicion_deslizar, transicion_persiana,
                          transicion_zoom)

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


_bloques.Text = Text
_code_brand.Text = Text

import algebra_lineal as _al  # noqa: E402  (tras definir la sombra)
from algebra_lineal import C_EJE, C_REJILLA, fmt, grafica  # noqa: E402

_al.Text = Text

import protocolos as _pr  # noqa: E402
from protocolos import (C_CAPA, C_CIFRA, C_CLAVE, C_COLA,  # noqa: E402
                        C_OK, C_PAQUETE, C_PERDIDA, C_RED,
                        CAMPOS_IPV4, CAPAS_TCPIP, agregar_rutas,
                        aimd, arp_resolver, arranque_lento, barra_bits,
                        bdp, cabecera, cabecera_ipv4, checksum_ip,
                        cidr, cola, cola_mm1, colapso_congestion,
                        conmutacion, crc32_trama, csma_cd, cubic,
                        encapsular, enlace, entero_a_ip, eui64,
                        fragmentar, ip_a_entero, ipv6_comprimir,
                        ipv6_expandir, little, mascara_bits,
                        mux_estadistico, nodo, paquete, pila,
                        prefijo_mas_largo, recuperacion_tras_perdida,
                        reloj, sierra, switch_aprende, tabla,
                        topologia, trama_ethernet, troceado, ttl_camino,
                        ventana, verificar_checksum, voltear_bit)

_pr.Text = Text

_RotulosBase = Rotulos


class Rotulos(_RotulosBase):
    """Relevo SECUENCIAL por zona: el rotulo anterior sale ANTES de que
    entre el nuevo (el original los cruza y se ven superpuestos)."""

    def mostrar(self, mobjeto, zona="abajo", run_time=0.45, salida=0.25,
                **kwargs):
        if self._zonas.get(zona) is not None:
            self.limpiar(zona, run_time=salida)
        return super().mostrar(mobjeto, zona=zona, run_time=run_time,
                               **kwargs)


config.background_color = CODE_BG

# --- Paleta del curso -------------------------------------------------
# Regla: EL COLOR DICE EL PAPEL. Ambar el paquete y el dato que viaja;
# cian TODA cifra calculada; azul la red (nodos, enlaces, topologia);
# rojo la perdida, el descarte y la congestion; verde lo entregado y
# confirmado; violeta las capas, cabeceras y jerarquias; fucsia la
# seguridad; naranja las colas y la espera; gris el mobiliario.
C_TITULO = CODE_INK          # #e8edf3 titulos
C_TENUE = CODE_MUTED         # #94a0b0 pies y elementos secundarios
C_ACENTO = CODE_ACCENT       # #f59e0b ambar
C_ACENTO_2 = CODE_ACCENT_2   # #ea580c naranja de cierre
C_CALCULO = C_CIFRA          # cian: cifras y resultados numericos

MARGEN_PIE = 0.68            # separacion del pie al borde inferior

# --- Numeros de la leccion --------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria `protocolos.py`,
# nunca escrito a mano en el clip: lo que se dibuja y lo que se escribe no
# pueden discrepar. Medido en el contenedor antes de escribir los clips.

# Clip 1 - el colapso de 1986: al pasar de la capacidad, el trabajo UTIL
# cae en vez de estancarse (cada perdida se retransmite y empuja mas).
COLAPSO = colapso_congestion()             # cargas 0.2 .. 3.0, capacidad 1.0
COL_X = [float(x) for x in COLAPSO["carga"]]
COL_U = [float(u) for u in COLAPSO["util"]]
COL_N = len(COL_X)                         # 15 puntos MEDIDOS
COL_CAP = COLAPSO["capacidad"]             # 1.0 = la capacidad del enlace
COL_CAIDA = COLAPSO["caida_pct"]           # 95.0 % de caida del trabajo util


def UTIL(x):
    """Trabajo util MEDIDO para la carga x (interpola entre los puntos).

    Con `muestras=COL_N` sobre (COL_X[0], COL_X[-1]) la grafica cae
    EXACTAMENTE en los 15 puntos medidos: no se dibuja nada interpolado.
    """
    return float(np.interp(float(x), COL_X, COL_U))


# La cola del router con la carga por encima de la capacidad (lambda = 1.4).
COLA_COLAPSO = cola_mm1(lmbda=1.4, mu=1.0, n_llegadas=4000, capacidad=8,
                        semilla=3)
COLA_CAP = COLA_COLAPSO["capacidad"]                 # 8 ranuras
OCUPACIONES = [0, 1, 2, 3, 4, 5, 6, 7, 8]            # el llenado en pantalla
BUCLE = ("la cola se llena", "se descarta", "se retransmite")

# Clip 2 - arranque lento: cwnd duplicandose hasta el umbral.
SLOW = arranque_lento(ssthresh=16, cwnd0=1, rtts=10)
SLOW_TRAZA = SLOW["traza"]                 # 1 2 4 8 16 17 18 19 20 21
SLOW_EXP = SLOW["rtts_hasta_umbral"]       # 4 RTT duplicando
SLOW_SSTHRESH = SLOW["ssthresh"]           # 16 segmentos
SLOW_LINEAL = SLOW_TRAZA[SLOW_EXP + 1:]   # 17 18 19 20 21: la parte de +1
# El tubo que hay que llenar: 100 Mb/s con 40 ms de ida y vuelta.
TUBO = bdp(100.0, 40.0)
TUBO_SEG = int(TUBO["segmentos_1460"])     # 342 segmentos de 1460 B en vuelo
TUBO_MBPS, TUBO_RTT = TUBO["mbps"], TUBO["rtt_ms"]

# Clip 3 - la sierra de TCP Reno: +1 por RTT, /2 al perder.
RENO = aimd(rtts=60, ssthresh0=32, perdidas=(18, 34, 50))
RENO_TRAZA = RENO["traza"]
RENO_PERDIDAS = RENO["perdidas"]           # 18, 34, 50
RENO_MEDIA = RENO["media"]                 # 27.63 segmentos EN ESTA VENTANA
RENO_PICO = RENO["pico"]                   # 45 segmentos
RENO_RTTS = len(RENO_TRAZA)                # 60 RTT dibujados
# cwnd justo ANTES y justo DESPUES de cada perdida, leidos de la traza.
RENO_CORTES = [(e["rtt"], RENO_TRAZA[e["rtt"]], e["cwnd_nuevo"])
               for e in RENO["eventos"]]

# Clip 4 - CUBIC frente a Reno, y BBR.
CUBIC = cubic(rtts=60, w_max=32.0, c=0.4, beta=0.7, perdidas=(18, 34, 50),
              rtt_s=0.04)
CUBIC_TRAZA = CUBIC["traza"]
CUBIC_MEDIA = CUBIC["media"]               # 21.06 EN ESTA MISMA VENTANA
CUBIC_PICO = CUBIC["pico"]
Y_MAX_SIERRA = RENO_PICO * 1.15            # MISMA escala para las dos sierras
# La media de una ventana corta hace parecer PEOR a CUBIC. Lo que de verdad
# los separa es el tiempo en volver a llenar el tubo tras una perdida, para
# la MISMA ventana de TUBO_SEG segmentos y tres RTT distintos.
RTTS_COMPARADOS = (20.0, 40.0, 200.0)
RECUP = [recuperacion_tras_perdida(TUBO_SEG, r) for r in RTTS_COMPARADOS]
RECUP_CUBIC_S = RECUP[0]["cubic_s"]        # 6.35 s: NO depende del RTT
RECUP_RENO_RTTS = RECUP[0]["reno_rtts"]    # 171 RTT de +1 segmento cada uno


def GANADOR(r):
    """Quien recupera antes y por cuanto, MEDIDO. Dentro del 10 % se
    declara empate en vez de fingir una diferencia que no se ve."""
    if r["reno_s"] < r["cubic_s"] * 0.90:
        return "Reno  %sx" % fmt(r["cubic_s"] / r["reno_s"], 1)
    if r["cubic_s"] < r["reno_s"] * 0.90:
        return "CUBIC %sx" % fmt(r["veces"], 1)
    return "empate"


# BBR no lo calcula la libreria: se nombra como lo que es (un algoritmo que
# ESTIMA el cuello de botella en vez de esperar la perdida) y no se le
# inventa ninguna cifra en pantalla.


# --- Rotulos ----------------------------------------------------------
def _con_fondo(mobjeto, buff=0.14, opacidad=0.82):
    """Rectangulo del color del fondo detras de un rotulo: el texto se lee
    limpio aunque haya piezas debajo."""
    fondo = BackgroundRectangle(mobjeto, color=CODE_BG, fill_opacity=opacidad,
                                buff=buff)
    return VGroup(fondo, mobjeto)


def titulo_curso(texto, font_size=34, color=None):
    """Titulo de clip (Rajdhani) anclado arriba. Zona 'arriba' de Rotulos."""
    t = titulo_marca(texto, font_size=font_size,
                     color=C_TITULO if color is None else color)
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


def panel_derecha(*mobjetos, buff=0.30):
    """Columna de mobjects (cifras, esquemas) en la esquina superior
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
