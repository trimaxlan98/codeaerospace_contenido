# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 2.1 IP: la dirección y el datagrama".
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
                        arp_resolver, barra_bits, cabecera,
                        cabecera_ipv4, checksum_ip, cidr, cola,
                        cola_mm1, conmutacion, crc32_trama, csma_cd,
                        encapsular, enlace, entero_a_ip, eui64,
                        fragmentar, ip_a_entero, ipv6_comprimir,
                        ipv6_expandir, little, mascara_bits,
                        mux_estadistico, nodo, paquete, pila,
                        prefijo_mas_largo, reloj, switch_aprende,
                        tabla, topologia, trama_ethernet, troceado,
                        ttl_camino, verificar_checksum, voltear_bit)

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
# NUNCA escrito a mano en el clip: lo que se dibuja y lo que se escribe no
# pueden discrepar. Medido en el contenedor antes de escribir los clips.

# Clip 1 - la cabecera IPv4 REAL de 20 bytes y su checksum calculado.
IP_ORIGEN = "10.0.0.7"
IP_DESTINO = "93.184.216.34"
CAB = cabecera_ipv4(origen=IP_ORIGEN, destino=IP_DESTINO, ttl=64,
                    protocolo=6, longitud=1500, ident=0x1c46, banderas=2)
CAB_BYTES = CAB["bytes"]
CAB_VAL = CAB["valores"]
CAB_N_CAMPOS = len(CAMPOS_IPV4)                  # 12
CAB_HEX = " ".join("%02x" % b for b in CAB_BYTES)
# Los cuatro campos que DECIDEN algo (el resto es burocracia del formato).
CAMPOS_DECIDEN = ("Direccion origen", "Direccion destino", "TTL",
                  "Protocolo")
# Geometria de la pieza `cabecera` MEDIDA (sonda de anchos en el
# contenedor): con estos tres numeros ningun rotulo de los 12 campos se
# encoge ni se encima, ni siquiera Banderas (3 bits) ni IHL (4 bits).
CAB_ANCHO = 11.6
CAB_ALTO = 0.55
CAB_FS = 15

# El checksum, paso a paso y en pantalla: las diez palabras de 16 bits con
# el propio campo de checksum a cero, su suma, el pliegue del acarreo y el
# complemento a uno. CK_FINAL tiene que salir igual que CAB["checksum"].
CAB_CERO = bytes(CAB_BYTES[:10]) + b"\x00\x00" + bytes(CAB_BYTES[12:])
CK_PALABRAS = [(CAB_CERO[i] << 8) | CAB_CERO[i + 1] for i in range(0, 20, 2)]
CK_SUMA = sum(CK_PALABRAS)                       # 0x22709
CK_BAJA = CK_SUMA & 0xFFFF                       # 0x2709
CK_ACARREO = CK_SUMA >> 16                       # 0x2
CK_PLEGADA = CK_BAJA + CK_ACARREO                # 0x270b
CK_FINAL = checksum_ip(CAB_CERO)                 # 0xd8f4
assert CK_FINAL == CAB["checksum"] == (~CK_PLEGADA) & 0xFFFF

# Verificar: sumar la cabecera ENTERA da 0 si esta intacta (la regla real).
CK_INTACTA = verificar_checksum(CAB_BYTES)       # 0
BIT_ROTO = 8 * 8 + 3                             # un bit del byte del TTL
CAB_ROTA = voltear_bit(CAB_BYTES, BIT_ROTO)
TTL_ROTO = CAB_ROTA[8]                           # 64 -> 80
CK_ROTA = verificar_checksum(CAB_ROTA)           # 61439: corrupta

# Clip 2 - el mejor esfuerzo: cinco redes en fila y tres fracasos legales.
POS_CAMINO = {"A": (-5.55, 0.0), "R1": (-3.25, 0.0), "R2": (-0.95, 0.0),
              "R3": (1.35, 0.0), "R4": (3.55, 0.0), "B": (5.55, 0.0)}
ARISTAS_CAMINO = {("A", "R1"): "cobre", ("R1", "R2"): "fibra",
                  ("R2", "R3"): "radio", ("R3", "R4"): "satelite",
                  ("R4", "B"): "fibra"}
TIPOS_CAMINO = {"A": "host", "B": "servidor", "R3": "satelite"}
CAMINO = ["A", "R1", "R2", "R3", "R4", "B"]
N_REDES = len(ARISTAS_CAMINO)                    # 5
FRACASOS = ("perder", "duplicar", "desordenar")
ORDEN_SALIDA = [1, 2, 3]
ORDEN_LLEGADA = [2, 3, 1]                        # el desorden que se ve

# Clip 3 - TTL: el seguro contra los bucles.
TTL0 = 64
CICLO = ["R1", "R2", "R3", "R4"]
TTL_CAM = ttl_camino(TTL0, CICLO, bucle=True)
TTL_RUTA = TTL_CAM["ruta"]
TTL_SALTOS = TTL_CAM["saltos"]                   # 64
TTL_MUERTO = TTL_CAM["muerto"]                   # True
TTL_VUELTAS = TTL_SALTOS // len(CICLO)           # 16
TTL_NODO_FINAL = TTL_RUTA[-1]["nodo"]            # R4


def TTL_EN(salto):
    """El TTL medido tras el salto `salto` (1-based) del camino circular."""
    i = min(max(int(salto), 1), TTL_SALTOS) - 1
    return TTL_RUTA[i]["ttl"]


POS_BUCLE = {"A": (-5.30, 1.30), "R1": (-2.30, 1.30), "R2": (1.40, 1.30),
             "R3": (1.40, -1.30), "R4": (-2.30, -1.30)}
ARISTAS_BUCLE = {("A", "R1"): None, ("R1", "R2"): None, ("R2", "R3"): None,
                 ("R3", "R4"): None, ("R4", "R1"): None}
TIPOS_BUCLE = {"A": "host"}

# Clip 4 - fragmentar 4000 B por un enlace de MTU 1500.
CARGA_BYTES = 4000
MTU = 1500
FRAG = fragmentar(CARGA_BYTES, mtu=MTU)
FRAGS = FRAG["fragmentos"]
FRAG_N = FRAG["n"]                               # 3
FRAG_UTIL = FRAG["util"]                         # 1480
FRAG_EXTRA = FRAG["bytes_extra"]                 # 40 B de cabeceras de mas
FRAG_PERDIDO = 2                                 # el que se cae (1-based)
FRAG_ESCALA = 8.0 / CARGA_BYTES                  # unidades por byte
FILAS_FRAG = [["%d" % (i + 1), "%d" % f["offset_campo"],
               "%d B" % f["datos"], "%d" % f["mf"]] for i, f in
              enumerate(FRAGS)]


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


def ruta_de(topo, nombres):
    """Camino poligonal por los centros de una lista de nodos de la
    topologia, listo para `MoveAlongPath`. La libreria dibuja la topologia
    y sabe resaltar un camino, pero no lo expone como trayectoria."""
    v = VMobject()
    v.set_points_as_corners([topo.punto(k) for k in nombres])
    return v


def ficha(texto="", lado=0.40, color=C_PAQUETE, fs=16):
    """Un datagrama como ficha cuadrada rotulada: el objeto que viaja
    cuando no toca abrirle la cabecera."""
    c = Square(lado, stroke_color=color, stroke_width=2.4,
               fill_color=color, fill_opacity=0.22)
    if str(texto) == "":
        return VGroup(c)
    t = tag_hud(str(texto), font_size=fs, color=color)
    t.move_to(c.get_center())
    return VGroup(c, t)


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
