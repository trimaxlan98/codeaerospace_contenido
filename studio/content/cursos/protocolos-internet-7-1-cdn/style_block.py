# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 7.1 Acercar el contenido: CDN y anycast".
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
# Todo valor que se rotule sale de aqui o de la libreria, NUNCA escrito a
# mano en el clip. Todas las cifras se remidieron dentro del contenedor.

# Clip 1 - el viaje largo: un usuario en CDMX pide algo a un servidor en
# Madrid (el mismo sitio que en el 3 hara de "un solo origen"). El limite
# fisico (2c/3 en fibra, ida y vuelta) y lo medido de verdad, con saltos.
D_CDMX_MADRID = km_entre("CDMX", "Madrid")            # 9062.8 km
VIAJE_LARGO = ping(distancia_km=D_CDMX_MADRID)        # saltos=8 (defecto)
RTT_MIN_LARGO = VIAJE_LARGO["tope_luz_ms"]            # 90.7 ms: la luz, y ya
RTT_REAL_LARGO = VIAJE_LARGO["media"]                 # 97.7 ms: lo medido
PROCESO_LARGO = VIAJE_LARGO["proceso_ms"]             # 5.6 ms: los routers

# Clip 2 - la cache al borde: un PoP a 30 km, 2 saltos (la otra punta de la
# ciudad, o del mismo proveedor) frente al viaje del clip 1 hasta Madrid.
VIAJE_BORDE = ping(distancia_km=30.0, saltos=2, semilla=9)
RTT_BORDE = VIAJE_BORDE["media"]                      # 2.7 ms

# La tasa de acierto depende de la LOCALIDAD (zipf) y del TAMANO de cache.
CDN_ZIPF = {0.6: cdn(500, 40, zipf=0.6, tam_cache=8),
           1.1: cdn(500, 40, zipf=1.1, tam_cache=8),
           1.8: cdn(500, 40, zipf=1.8, tam_cache=8)}
CDN_CACHE = {4: cdn(500, 40, zipf=1.1, tam_cache=4),
            8: cdn(500, 40, zipf=1.1, tam_cache=8),
            20: cdn(500, 40, zipf=1.1, tam_cache=20)}
CDN_CACHEABLE_PCT = CDN_ZIPF[1.1]["cacheable_pct"]     # 80.0 % se puede guardar
CDN_NOCACHE_PCT = 100.0 - CDN_CACHEABLE_PCT            # 20.0 % siempre al origen


def ACIERTO_DE_ZIPF(z):
    """Tasa de acierto (cache de 8) en funcion de la localidad. Para la
    `Grafica`: la misma `cdn()` evaluada punto a punto, nunca interpolada
    a mano."""
    return cdn(500, 40, zipf=float(z), tam_cache=8)["tasa_acierto"]


# Clip 3 y 4 - anycast: la MISMA IP anunciada desde 8 PoP; las 12 ciudades
# de CIUDADES_PI como usuarios (todas, no una ventana).
IP_ANYCAST = "198.51.100.53"                           # TEST-NET-2, ficticia
SITIOS_ANYCAST = ["CDMX", "Nueva York", "Sao Paulo", "Madrid", "Lagos",
                 "Mumbai", "Tokio", "Sidney"]
USUARIOS_ANYCAST = list(CIUDADES_PI.keys())            # las 12, completas
ANYCAST_8 = anycast(SITIOS_ANYCAST, USUARIOS_ANYCAST)
ANYCAST_1 = anycast(["Madrid"], USUARIOS_ANYCAST)       # un solo origen
ANYCAST_FACTOR = ANYCAST_1["media_ms"] / ANYCAST_8["media_ms"]   # 5.6x
_FILA_8 = {f["usuario"]: f for f in ANYCAST_8["filas"]}
EJEMPLO_LOCAL = _FILA_8["CDMX"]              # cae en si misma: 4.8 ms
EJEMPLO_MEDIO = _FILA_8["Londres"]           # cae en Madrid: 17.4 ms
EJEMPLO_LEJOS = _FILA_8["Johannesburgo"]     # cae en Lagos: 49.9 ms

ANYCAST_CAIDA = anycast_caida(SITIOS_ANYCAST, USUARIOS_ANYCAST, "Madrid")
_FILA_DESPUES = {f["usuario"]: f for f in ANYCAST_CAIDA["despues"]["filas"]}
REENRUTADO_MADRID = _FILA_DESPUES["Madrid"]     # ahora cae en Lagos: 43.2 ms
REENRUTADO_LONDRES = _FILA_DESPUES["Londres"]   # ahora cae en Lagos: 55.0 ms

# Posiciones aproximadas del mapa (orden geografico este-oeste, NO a escala
# real: es un croquis, no una proyeccion cartografica).
POS_MUNDO = {"CDMX": (-4.6, 0.7), "Nueva York": (-3.4, 1.6),
            "Sao Paulo": (-2.4, -1.1), "Madrid": (-0.3, 1.6),
            "Londres": (0.7, 2.3), "Lagos": (0.9, 0.2),
            "Johannesburgo": (2.0, -1.3), "Mumbai": (3.3, 0.7),
            "Tokio": (5.8, 1.4), "Sidney": (6.3, -1.4)}


# Escalas de las barras de tiempo: la LONGITUD de la barra es el tiempo.
# `regla_viajes` codifica VIAJES, asi que con viajes=1 dos barras miden lo
# mismo aunque sus cifras difieran; el ancho de casilla lleva la escala.
MS_UD1 = 5.0 / RTT_REAL_LARGO            # clip 1: la mayor mide 5.0
MS_UD = 5.0 / ANYCAST_1["media_ms"]      # clip 3: idem


def tramo_corto(enl, hasta=0.86):
    """La trayectoria de un enlace RECORTADA antes del nodo: una ficha que
    termina su MoveAlongPath en el aparato se le monta encima."""
    a, b = enl.a, enl.b
    v = VMobject()
    v.set_points_as_corners([a, a + (b - a) * float(hasta)])
    return v


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
