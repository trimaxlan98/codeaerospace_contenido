# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 4.1 Dos contratos: UDP y TCP".
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
                        demux, encapsular, enlace, entero_a_ip, eui64,
                        escalera, ficha, fragmentar, handshake_tcp,
                        ip_a_entero, ipv6_comprimir,
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
# Todo valor que se rotule sale de aqui o de la libreria, nunca escrito a
# mano en el clip. Medido en el contenedor (ver informe final del agente).

# Clip 1 - demux: la 4-tupla decide el socket. Un host, tres programas
# escuchando y CUATRO paquetes: el cuarto apunta a un puerto sin nadie
# escuchando y no se entrega.
IP_HOST = "203.0.113.10"
SOCKETS = {(IP_HOST, 443): "Navegador", (IP_HOST, 53): "DNS",
          (IP_HOST, 25): "Correo"}
PAQUETES_DEMUX = [
    {"ip_o": "198.51.100.5", "pto_o": 51000, "ip_d": IP_HOST, "pto_d": 443},
    {"ip_o": "198.51.100.7", "pto_o": 51500, "ip_d": IP_HOST, "pto_d": 53},
    {"ip_o": "198.51.100.9", "pto_o": 52000, "ip_d": IP_HOST, "pto_d": 25},
    {"ip_o": "198.51.100.11", "pto_o": 52500, "ip_d": IP_HOST,
     "pto_d": 9999},
]
DEMUX = demux(PAQUETES_DEMUX, SOCKETS)
SOCKET_DE = {443: "Navegador", 53: "DNS", 25: "Correo"}
SOCKET_Y = {443: 1.15, 53: 0.0, 25: -1.15}          # fila de cada socket

# Clip 2/3 - las cabeceras REALES de transporte (campos = [(nombre, bits)],
# RFC 768 / RFC 793 sin opciones). No hay `CAMPOS_UDP`/`CAMPOS_TCP` en la
# libreria (a diferencia de `CAMPOS_IPV4`): se definen aqui, con los MISMOS
# anchos de bit que el estandar, para que `cabecera()` los dibuje.
CAMPOS_UDP = (("Puerto origen", 16), ("Puerto destino", 16),
             ("Longitud", 16), ("Checksum", 16))
CAMPOS_TCP = (("Puerto origen", 16), ("Puerto destino", 16),
             ("Numero de secuencia", 32), ("Numero de ACK", 32),
             ("Offset y flags", 16), ("Ventana", 16),
             ("Checksum", 16), ("Puntero urgente", 16))

# El sobrecosto MEDIDO con `encapsular`: la misma carga (una consulta
# chica de 32 B) por UDP y por TCP. Los 8 B / 20 B de transporte se leen
# directo de `CAPAS_UDP`/`CAPAS_TCPIP`; el resto (IP + Ethernet) es igual
# en los dos casos, asi el contraste es limpio.
DATOS_EJEMPLO = 32
CAPAS_UDP = (("Aplicacion", "DNS", 0), ("Transporte", "UDP", 8),
            ("Red", "IP", 20), ("Enlace", "Ethernet", 18))
ENC_UDP = encapsular(DATOS_EJEMPLO, capas=CAPAS_UDP)
ENC_TCP = encapsular(DATOS_EJEMPLO, capas=CAPAS_TCPIP)

# Valores de ejemplo de la cabecera UDP: puertos ilustrativos (el mismo
# estilo que las IP de ejemplo en 1.2/2.1), y la Longitud tomada del
# propio `ENC_UDP` (el tamano tras la capa de Transporte: 8 + 32 = 40).
CAB_UDP_VAL = {"Puerto origen": "51500", "Puerto destino": "53",
              "Longitud": str(ENC_UDP["pasos"][1]["tamano"]),
              "Checksum": "0x1a2f"}

# Valores de ejemplo de la cabecera TCP: los numeros de secuencia y de ACK
# NO se inventan, salen del evento ACK real de `handshake_tcp()` (misma
# funcion que da el costo del apreton mas abajo).
HS = handshake_tcp()
_ACK_EV = HS["eventos"][2]                    # el tercer mensaje: ACK
CAB_TCP_VAL = {"Puerto origen": "51500", "Puerto destino": "443",
              "Numero de secuencia": str(_ACK_EV["seq"]),
              "Numero de ACK": str(_ACK_EV["ack"]),
              "Offset y flags": "20 B / ACK", "Ventana": "64240",
              "Checksum": "0x8f3c", "Puntero urgente": "0"}

# Clip 2/3 - los mismos tres datagramas/segmentos, la misma perdida (el
# numero 2), para que el contraste UDP/TCP sea la MISMA historia dos
# veces, no dos historias distintas.
NUMEROS_ENVIADOS = [1, 2, 3]
PERDIDO = 2

# Clip 4 - la tabla comparada y el costo del primer byte. El apreton
# ENTERO (ISN, SYN/ACK paso a paso) es de la 4.2: aqui solo se cita el
# costo en tiempo, ya calculado arriba en `HS`.
ANTES_PRIMER_BYTE_TCP = HS["antes_del_primer_byte_ms"]     # 40.0 ms
ANTES_PRIMER_BYTE_UDP = 0.0
FILAS_TABLA = [
    ["Cabecera", "8 B", "20 B"],
    ["Antes del primer byte", "0 ms", "%d ms" % ANTES_PRIMER_BYTE_TCP],
    ["Si se pierde un dato", "nadie se entera", "se detecta y se rellena"],
]
CASOS_USO = [
    ("DNS: una pregunta y una respuesta cortas", "UDP"),
    ("Voz o video en vivo: mejor tarde que repetido", "UDP"),
    ("Una pagina o un archivo: tiene que llegar completo", "TCP"),
]


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
