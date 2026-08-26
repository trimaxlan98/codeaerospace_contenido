# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 5.1 DNS: el directorio del mundo".
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
# Medido en el contenedor (protocolos.py, semillas fijas):
#   resolver_dns("www.ejemplo.org")   -> 4 viajes, RTT 2 -> 32 -> 77 -> 137 ms
#   la misma con cache caliente       -> 2 ms, 1 viaje  (68.5x mas rapido)
#   cache_dns(200, 12, ttl=N)         -> 39.5 % (ttl 4) / 54.0 % (ttl 8) /
#                                        71.5 % (ttl 20)

# Clip 1 - el arbol de nombres (JERARQUIA_DNS: raiz, TLD, dominio,
# subdominio). `Arbol` empareja padre/hijo por INDICE proporcional entre
# niveles consecutivos: si cada nivel no tiene el MISMO numero de
# hermanos, la rama que se dibuja no es la real (una etiqueta se queda
# sin hijo y otra cuelga del padre equivocado). Por eso los tres niveles
# no-raiz tienen 3 hermanos cada uno y el camino REAL (los valores
# exactos de JERARQUIA_DNS) va siempre en el indice 2, el ULTIMO: la
# rama real queda a la DERECHA en cada nivel y la raiz, con un unico
# hijo, queda centrada. Leer el camino de abajo (subdominio) hacia
# arriba (raiz) es entonces leer de derecha a izquierda: asi se resuelve
# un nombre de verdad.
_JD = dict(JERARQUIA_DNS)
ARBOL_NIVELES = [[_JD["raiz"]],
                 ["com", "net", _JD["TLD"]],
                 ["sitio.com", "sitio.net", _JD["dominio"]],
                 ["www.sitio.com", "www.sitio.net", _JD["subdominio"]]]
ARBOL_RAIZ = [(0, 0)]
ARBOL_TLD = ARBOL_RAIZ + [(1, 2)]
ARBOL_DOMINIO = ARBOL_TLD + [(2, 2)]
ARBOL_SUB = ARBOL_DOMINIO + [(3, 2)]      # camino completo marcado

# Clip 2 - la resolucion paso a paso (resolver_dns real, cache vacia: los
# CUATRO viajes de verdad, cliente incluido).
RESOLUCION = resolver_dns("www.ejemplo.org")
TOTAL_DNS_MS = RESOLUCION["total_ms"]           # 137.0 ms
VIAJES_DNS = RESOLUCION["viajes"]               # 4
ACTORES_DNS = ["cliente", "resolutor", "raiz", "TLD .org", "autoritativo"]


def _texto_paso_dns(p):
    """Texto de una flecha de la Escalera, tomado del dict REAL que
    entrega resolver_dns() (nunca escrito a mano)."""
    if p["responde"] is None:
        return "%s ?" % p["pregunta"]
    return p["respuesta"]


EVENTOS_DNS = [dict(de=p["de"], a=p["a"], t_ms=p["acumulado"],
                    texto=_texto_paso_dns(p)) for p in RESOLUCION["pasos"]]

# Clip 3 - la cache y el TTL. La misma consulta, con la cache ya caliente
# (el "cache" que devolvio la resolucion de arriba).
RESOLUCION_CACHE = resolver_dns("www.ejemplo.org", cache=RESOLUCION["cache"])
TOTAL_CACHE_MS = RESOLUCION_CACHE["total_ms"]    # 2.0 ms
VIAJES_CACHE = RESOLUCION_CACHE["viajes"]        # 1
ACELERACION_CACHE = TOTAL_DNS_MS / TOTAL_CACHE_MS   # 68.5x

TTLS = (4, 8, 20)
CACHES_TTL = {ttl: cache_dns(200, 12, ttl=ttl) for ttl in TTLS}
TASA_TTL = {ttl: CACHES_TTL[ttl]["tasa_acierto"] for ttl in TTLS}   # %

# Clip 4 - la raiz. 13 identidades de servidor raiz publicadas por IANA:
# es un dato PUBLICO, no lo calcula la libreria, y por eso se rotula en
# C_TENUE (nunca en C_CIFRA, para que el cian siga significando "esto lo
# midio la libreria"). `PING_IP` si es una medicion real de la libreria:
# la red entrega el paquete aunque el nombre no se resuelva.
RAIZ_LETRAS = list("ABCDEFGHIJKLM")
RAIZ_N = len(RAIZ_LETRAS)                        # 13 (dato publico)
PING_IP = ping()
PING_IP_MS = PING_IP["media"]                    # ~97 ms a la IP numerica


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
