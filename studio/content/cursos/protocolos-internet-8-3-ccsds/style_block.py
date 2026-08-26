# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 8.3 Internet interplanetario: CCSDS y Marte".
# Bloque de estilo del proyecto. Se antepone al script de CADA clip.
#
# Copia del MOLDE (leccion 1.1) con la API COMPLETA de protocolos.py
# ya importada. Solo cambian esta cabecera y la tabla de numeros.
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
    CAMPOS_IPV4, CAMPOS_IPV6, CAPAS_TCPIP, CIUDADES_PI,
    CODIGOS_HTTP, C_CAPA, C_CIFRA, C_CLAVE, C_COLA, C_OK, C_PAQUETE,
    C_PERDIDA, C_RED, H_GEO, H_LEO, ICMP_TIPOS, JERARQUIA_DNS,
    PILA_CCSDS, PILA_TCPIP, RFC1918, UA_KM, abr, abr_fijo,
    agregar_rutas, aimd, anycast, anycast_caida, arbol,
    archivo_a_marte, arp_resolver, arranque_lento, barra_bits, bdp,
    bellman_ford, bgp_mejor_ruta, buffer_reproduccion, bufferbloat,
    bus, cabecera, cabecera_ipv4, cabecera_ipv6, cache_condicional,
    cache_dns, cadena_certificados, camino_dijkstra, cdn,
    checksum_ip, cidr, codel, cola, cola_mm1, colapso_congestion,
    conmutacion, conteo_al_infinito, crc32_trama, csma_cd, cubic,
    demux, dh_pequeno, dhcp_dora, dijkstra, dtn_custodia,
    en_prefijo, encapsular, enlace, entero_a_ip, es_privada,
    escalera, espacio_direcciones, eui64, ficha, fragmentar,
    grafo_de, handshake_tcp, hol_bloqueo, http_peticion,
    http_transferencia, inundacion, ip_a_bytes, ip_a_entero,
    ipv6_comprimir, ipv6_expandir, jitter, km_entre,
    latencia_directo, little, malla_laser, mascara_bits,
    mux_estadistico, nat_entrante, nat_traducir, nodo, paquete,
    pila, pila_ccsds, ping, pmtud, prefijo_mas_largo,
    quic_migracion, rango_marte, ranuras, recuperacion_tras_perdida,
    regla_viajes, reloj, resolver_dns, retardo_marte, rtt_jacobson,
    rtt_orbital, secuestro_bgp, sierra, switch_aprende, tabla,
    tcp_en_orbita, tcp_sin_camino, tls_viajes, topologia,
    traceroute, trama_ethernet, troceado, ttl_camino, ventana,
    ventanas_contacto, verificar_checksum, voltear_bit)

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
# mano en el clip. Medido en el contenedor antes de escribir un solo clip.

# --- Clip 1: el retardo NO es un numero, es un rango ------------------
# `rango_marte` recorre el ano sintetico de oposicion (0.52 UA) a
# conjuncion (2.52 UA). El retardo es la distancia dividida por c: por eso
# la curva del retardo es la MISMA curva de la distancia, en otra unidad.
RANGO = rango_marte(13)
UA_CERCA = float(RANGO["uas"][0])
UA_LEJOS = float(RANGO["uas"][-1])
IDA_CERCA = RANGO["min_min"]              # 4.32 min luz
IDA_LEJOS = RANGO["max_min"]              # 20.96 min luz
RTT_CERCA = RANGO["rtt_min_min"]          # 8.65 min
RTT_LEJOS = RANGO["rtt_max_min"]          # 41.92 min
KM_CERCA = RANGO["filas"][0]["km"]
KM_LEJOS = RANGO["filas"][-1]["km"]
# El peor retardo de la Internet terrestre, para anclar la escala (8.1).
GEO_RTT_MS = rtt_orbital(H_GEO)["rtt_ms"]  # 238.7 ms
# Cuantas veces cabe el peor RTT terrestre en el mejor RTT marciano.
VECES_GEO = RTT_CERCA * 60_000.0 / GEO_RTT_MS


# Escala de las reglas del clip 1: unidades de pantalla por minuto luz.
# Las dos reglas comparten borde izquierdo, asi que la LONGITUD compara.
ESCALA_MIN = 0.145
X_REGLAS = -5.40                          # borde izquierdo comun


def tasa(mbps):
    """La tasa de un tramo en la unidad que le queda bien.

    `fmt(0.5, 0)` dice "0" y `fmt(1000.0, 1)` dice "1000.0": ninguna de las
    dos es la cifra que hay que leer en un rotulo de enlace.
    """
    m = float(mbps)
    if m >= 1000.0:
        return "%s Gb/s" % fmt(m / 1000.0, 0)
    if m >= 10.0:
        return "%s Mb/s" % fmt(m, 0)
    return "%s Mb/s" % fmt(m, 1)


def IDA_EN(ua):
    """Minutos luz de ida a `ua` unidades astronomicas (la curva)."""
    return retardo_marte(ua)["ida_min"]


# --- Clip 2: la pila del espacio frente a la de casa ------------------
# `Pila` pide capas de 3 campos (nombre, protocolo, cabecera) porque
# calcula el encapsulado; PILA_TCPIP y PILA_CCSDS son de 2. Se convierten
# aqui con cabecera 0 y se apagan los tamanos (ver `pila_desnuda`).
PILA = pila_ccsds()
CAPAS_CASA = PILA["tcpip"]
CAPAS_ESPACIO = PILA["ccsds"]
CAMBIOS = PILA["cambios"]
# Que capa de casa se corresponde con cual del espacio (indices).
PARES = [(0, 0), (1, 1), (2, 2), (3, 3)]
SE_VA = [1, 2, 3]              # capas de casa que se caen: TCP, IP, Ethernet
CAMBIOS_IDA = [0, 1, 2]        # sus razones en CAMBIOS
SE_ANADE = 4                   # la capa del espacio que en casa no existe
CAMBIO_NUEVO = 3               # su razon en CAMBIOS

# --- Clip 3: una imagen de 8 MB desde un rover ------------------------
VIAJE = archivo_a_marte(8.0, 1.5)
VIAJE_MB = VIAJE["tam_mb"]
VIAJE_UA = VIAJE["ua"]
TRAMOS = VIAJE["tramos"]
VIAJE_MIN = VIAJE["total_min"]             # 15.14 min
VIAJE_LUZ_MIN = VIAJE["luz_min"]           # 12.48 min: solo luz en camino
VIAJE_TX_S = sum(t["tx_s"] for t in TRAMOS)
VIAJE_TX_MIN = VIAJE_TX_S / 60.0           # 2.67 min de transmision
VIAJE_LUZ_PCT = 100.0 * VIAJE["luz_min"] * 60.0 / VIAJE["total_s"]   # 82.4
VIAJE_TX_PCT = 100.0 * VIAJE_TX_S / VIAJE["total_s"]                 # 17.6
LENTO = VIAJE["el_lento"]                  # "orbitador -> DSN"
# El contrafactual honesto: con banda X instantanea seguirian siendo...
SIN_CUELLO_MIN = (VIAJE["total_s"] - TRAMOS[1]["tx_s"]) / 60.0       # 13.01
# Minutos acumulados al final de cada tramo (las marcas de la escalera).
ACUM_MIN = []
_t = 0.0
for _tr in TRAMOS:
    _t += _tr["total_s"]
    ACUM_MIN.append(_t / 60.0)             # 0.53 / 15.14 / 15.14

# Los cuatro actores del viaje y los pares (de, a) de cada tramo.
ACTORES_VIAJE = ["rover", "orbitador", "DSN", "control"]
ACTORES_PARES = [("rover", "orbitador"), ("orbitador", "DSN"),
                 ("DSN", "control")]
X_MARCAS = -4.95              # columna de las marcas de tiempo (minutos)
ANCHO_BARRA = 9.0             # la barra de reparto del tiempo del clip 3


# --- Clip 4: el cierre del curso --------------------------------------
KM_VIAJE = retardo_marte(VIAJE_UA)["km"]   # 224 millones de km
MKM_VIAJE = KM_VIAJE / 1e6
# La linea entera del curso: de un cable de casa al suelo de Marte.
POS_LINEA = {"PC": (-5.5, 0.0), "Router": (-3.0, 0.0), "DSN": (-0.5, 0.0),
             "Orbitador": (2.2, 0.0), "Rover": (4.9, 0.0)}
ARISTAS_LINEA = {("PC", "Router"): None, ("Router", "DSN"): None,
                 ("DSN", "Orbitador"): None, ("Orbitador", "Rover"): None}
TIPOS_LINEA = {"PC": "host", "Router": "router", "DSN": "nube",
               "Orbitador": "satelite", "Rover": "host"}
CAMINO_LINEA = ["PC", "Router", "DSN", "Orbitador", "Rover"]
# Lo que sobrevive del Internet terrestre, y donde se aprendio.
PRINCIPIOS = [
    ("capas", "la pila cambia de piezas, no de idea"),
    ("direcciones", "el destino se nombra antes de saber el camino"),
    ("tolerar el fallo", "si no hay ruta, el dato espera y sigue"),
    ("acuerdos", "un comite escribe las reglas; nadie las manda"),
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


def pila_desnuda(capas2, **kw):
    """`Pila` con capas de DOS campos (nombre, protocolo).

    `PILA_TCPIP` y `PILA_CCSDS` son de dos campos, pero `Pila` pide tres
    porque calcula el encapsulado y rotula "N B" a la derecha de cada
    caja. Aqui no hay bytes que ensenar (una pila de la NASA no encapsula
    los mismos tamanos que una de casa): se completa con cabecera 0 y se
    quitan los tamanos, que ademas ensancharian la pieza y chocarian con
    la pila de al lado.
    """
    p = pila([(n, pr, 0) for n, pr in capas2], **kw)
    p.remove(p.tamanos)
    return p


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
