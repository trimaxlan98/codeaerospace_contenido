# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 6.2 TLS: el candado de la web".
# Bloque de estilo del proyecto. Se antepone al script de CADA clip;
# los clips NO repiten imports: solo definen su ClipN(Scene).
#
# Copia del MOLDE de la familia (leccion 1.1) con la API COMPLETA de
# protocolos.py ya importada: en el lote 2 cada leccion tuvo que
# ampliar el import a mano. Solo cambian esta cabecera y la tabla de
# numeros de la leccion.
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
from protocolos import (  # noqa: E402  (la API completa)
    CAMPOS_IPV4, CAMPOS_IPV6, CAPAS_TCPIP, CODIGOS_HTTP, C_CAPA,
    C_CIFRA, C_CLAVE, C_COLA, C_OK, C_PAQUETE, C_PERDIDA, C_RED,
    ICMP_TIPOS, JERARQUIA_DNS, RFC1918, agregar_rutas, aimd, arbol,
    arp_resolver, arranque_lento, barra_bits, bdp, bellman_ford,
    bgp_mejor_ruta, bus, cabecera, cabecera_ipv4, cabecera_ipv6,
    cache_condicional, cache_dns, cadena_certificados,
    camino_dijkstra, checksum_ip, cidr, cola, cola_mm1,
    colapso_congestion, conmutacion, conteo_al_infinito,
    crc32_trama, csma_cd, cubic, demux, dh_pequeno, dhcp_dora,
    dijkstra, en_prefijo, encapsular, enlace, entero_a_ip,
    es_privada, escalera, espacio_direcciones, eui64, ficha,
    fragmentar, grafo_de, handshake_tcp, hol_bloqueo, http_peticion,
    http_transferencia, inundacion, ip_a_bytes, ip_a_entero,
    ipv6_comprimir, ipv6_expandir, little, mascara_bits,
    mux_estadistico, nat_entrante, nat_traducir, nodo, paquete,
    pila, ping, pmtud, prefijo_mas_largo, quic_migracion, ranuras,
    recuperacion_tras_perdida, reloj, resolver_dns, rtt_jacobson,
    secuestro_bgp, sierra, switch_aprende, tabla, tls_viajes,
    topologia, traceroute, trama_ethernet, troceado, ttl_camino,
    ventana, verificar_checksum, voltear_bit)

_pr.Text = Text

from cripto import rsa_cifrar  # noqa: E402  (abrir una firma con la publica: es lo que hace la casa)

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
# mano en el clip: lo que se dibuja y lo que se escribe no pueden
# discrepar. Medido en el contenedor antes de escribir un solo clip.

RTT_MS = 40.0                  # el RTT de la leccion, el mismo en los 4 clips

# --- Clip 1: el apreton. TCP primero, TLS ENCIMA; los RTT se SUMAN ----
HS = handshake_tcp(rtt_ms=RTT_MS)
RTT_TCP_MS = HS["rtt_ms"]                        # 40.0 ms
TCP_ANTES_MS = HS["antes_del_primer_byte_ms"]    # 40.0 ms: TCP cuesta 1 RTT
TCP_RTTS = TCP_ANTES_MS / RTT_MS                 # 1.0
TLS12 = tls_viajes("1.2")                        # 2 RTT, 4 mensajes
TLS13 = tls_viajes("1.3")                        # 1 RTT, 2 mensajes
TLS13R = tls_viajes("1.3", reanudado=True)       # 0 RTT, 1 mensaje
AVISO_0RTT = TLS13R["aviso"]                     # la letra chica, de la libreria

# El apreton COMPLETO (TCP + TLS) no se suma a mano: `http_transferencia`
# ya lo define como 1 RTT de transporte mas los de TLS. Se lo pedimos.
APRETON_12 = http_transferencia(1, "keepalive", RTT_MS,
                                version_tls="1.2")["apreton_rtts"]   # 3.0
APRETON_13 = http_transferencia(1, "keepalive", RTT_MS,
                                version_tls="1.3")["apreton_rtts"]   # 2.0
APRETON_0RTT = TCP_RTTS + TLS13R["rtt"]                              # 1.0
MS_12 = APRETON_12 * RTT_MS        # 120 ms antes del primer byte de HTTP
MS_13 = APRETON_13 * RTT_MS        # 80 ms
MS_0RTT = APRETON_0RTT * RTT_MS    # 40 ms
AHORRO_13_MS = MS_12 - MS_13       # 40 ms: justo un viaje

_MEDIO = RTT_MS / 2.0              # media vuelta: lo que tarda un mensaje

# Los tres mensajes de TCP salen TAL CUAL de handshake_tcp(); los cinco de
# TLS 1.2 van encima, a media vuelta de distancia cada uno, y el ultimo
# evento es el primer byte de HTTP: ahi es donde se lee la suma.
_TEXTO_TCP = {"SYN": "SYN", "SYN-ACK": "SYN-ACK", "ACK": "ACK  (TCP listo)"}
EVENTOS_TLS12 = [
    dict(e, texto=_TEXTO_TCP[e["flags"]], color=C_RED)
    for e in HS["eventos"][:3]
] + [
    {"de": "cliente", "a": "servidor", "texto": "ClientHello",
     "t_ms": TCP_ANTES_MS, "color": C_CLAVE},
    {"de": "servidor", "a": "cliente", "texto": "ServerHello + Certificado",
     "t_ms": TCP_ANTES_MS + _MEDIO, "color": C_CLAVE},
    {"de": "cliente", "a": "servidor", "texto": "ClaveIntercambio + Finished",
     "t_ms": TCP_ANTES_MS + 2 * _MEDIO, "color": C_CLAVE},
    {"de": "servidor", "a": "cliente", "texto": "Finished",
     "t_ms": TCP_ANTES_MS + 3 * _MEDIO, "color": C_CLAVE},
    {"de": "cliente", "a": "servidor", "texto": "GET /index.html",
     "t_ms": MS_12, "color": C_PAQUETE},
]
IDX_TCP = (0, 1, 2)                # que eventos son de TCP
IDX_TLS_1 = (3, 4)                 # primer viaje de TLS 1.2
IDX_TLS_2 = (5, 6)                 # segundo viaje
IDX_HTTP = (7,)                    # el primer byte util

# --- Clip 2: la clave que nadie mando (dh_pequeno -> cripto) ---------
# Numeros de juguete a proposito: el curso 19 ya explico la matematica
# modular. Aqui solo se ensena el GESTO.
DH_P, DH_G, DH_A, DH_B = 23, 5, 6, 15       # p y g publicos; a y b privados
DH = dh_pequeno(DH_P, DH_G, DH_A, DH_B)
DH_PUB_C, DH_PUB_S = DH["A"], DH["B"]       # 8 y 19: lo que se grita
DH_SECRETO = DH["s_ana"]                    # 2
DH_IGUALES = bool(DH["iguales"]) and DH["s_ana"] == DH["s_beto"]
DH_EN_EL_CABLE = (DH_P, DH_G, DH_PUB_C, DH_PUB_S)   # lo que oye el espia
DH_EN_CASA = (DH_A, DH_B, DH_SECRETO)               # lo que nunca viaja

# --- Clip 3: el certificado y su cadena (firmas RSA de verdad) -------
CERT = cadena_certificados("ejemplo.org")
CERT_MAL = cadena_certificados("ejemplo.org", alterar=True)
RSA_E, RSA_N = CERT["e"], CERT["n"]         # 17 y 3233
ESL = CERT["eslabones"]                     # raiz -> intermedia -> sitio
ESL_MAL = CERT_MAL["eslabones"][-1]         # el eslabon del sitio, alterado


def ABRIR(firma):
    """Abrir una firma con la clave publica de la CA. La libreria ya dice
    si `verifica`; esto recupera el NUMERO que sale al abrirla, que es lo
    que hay que poner en pantalla al lado del hash para que se vea por que
    la firma falla."""
    return rsa_cifrar(int(firma), RSA_E, RSA_N)


CERT_ABRE = [ABRIR(x["firma"]) for x in ESL]        # 834, 731, 60
CERT_HASH_MAL = ESL_MAL["hash"]                     # 2840: el cuerpo cambio
CERT_ABRE_MAL = ABRIR(ESL_MAL["firma"])             # 60: la firma no cambio
CERT_VALIDA = CERT["cadena_valida"]                 # True
CERT_VALIDA_MAL = CERT_MAL["cadena_valida"]         # False

# --- Clip 4: las tres barras (1.2, 1.3, 1.3 reanudado) ---------------
# Cada barra es el tiempo ANTES del primer byte de HTTP: un tramo azul de
# TCP mas un tramo fucsia de TLS. La escala es la misma en las tres.
BARRAS_TLS = (
    ("TLS 1.2", TLS12["rtt"], APRETON_12, MS_12),
    ("TLS 1.3", TLS13["rtt"], APRETON_13, MS_13),
    ("1.3 reanudado", TLS13R["rtt"], APRETON_0RTT, MS_0RTT),
)
UNIDAD_RTT = 1.45              # unidades de pantalla por RTT (escala unica)


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
