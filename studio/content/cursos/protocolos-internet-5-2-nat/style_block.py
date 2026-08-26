# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 5.2 DHCP y NAT: casa prestada, puerta compartida".
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
# Todo valor que se rotule sale de aqui o de la libreria, NUNCA escrito a
# mano en el clip. Medido en el contenedor antes de escribir los clips
# (ver informe final del agente).

# Clip 1 - DORA: los cuatro mensajes REALES de dhcp_dora() (valores por
# defecto: red 192.168.1.0/24, arriendo 24 h).
DORA = dhcp_dora()


def _texto_dora(e):
    """Texto de la flecha de la Escalera, construido desde el dict REAL
    que entrega dhcp_dora() (nunca a mano)."""
    return "%s   %s -> %s" % (e["mensaje"], e["origen"], e["destino"])


# DISCOVER y REQUEST van "a todos" (broadcast, 255.255.255.255): la
# Escalera solo conoce actores, asi que la flecha se dibuja hacia el
# servidor (quien de verdad escucha), y el pie explica el broadcast.
EVENTOS_DORA = [dict(e, a=("servidor" if e["a"] == "todos" else e["a"]),
                     texto=_texto_dora(e)) for e in DORA["eventos"]]

# Clip 2 - una IP para todos: la casa comparte una direccion publica; las
# franjas RFC 1918 no salen de casa (es_privada() manda).
N_APARATOS = 8
IP_LAPTOP = "192.168.1.10"
IP_TELEFONO = "192.168.1.44"
NAT_IP_PUBLICA = "203.0.113.7"       # el mismo default de nat_traducir()
RFC1918_FILAS = [[p, cidr(p)["mascara"], "%s direcciones" % fmt(cidr(p)[
    "hosts"], 0)] for p in RFC1918]
IPS_PRUEBA = ["192.168.1.10", "10.5.5.5", "172.16.0.1", "93.184.216.34"]
PRIVADAS = [(ip, es_privada(ip)) for ip in IPS_PRUEBA]

# Clip 3 - la tabla de traduccion: tres sesiones salientes, DOS aparatos
# piden el MISMO puerto de origen (51000) y nat_traducir() los renumera.
DISPOSITIVOS_NAT = ["laptop", "telefono", "tv"]
SESIONES_NAT = [
    (IP_LAPTOP, 51000, "93.184.216.34", 443),
    (IP_TELEFONO, 51000, "93.184.216.34", 443),
    ("192.168.1.30", 52000, "198.51.100.9", 443),
]
NAT = nat_traducir(SESIONES_NAT, ip_publica=NAT_IP_PUBLICA)
FILAS_NAT = [[DISPOSITIVOS_NAT[i], f["ip_o"], str(f["pto_o"]),
             "%s:%d" % (f["ip_d"], f["pto_d"]), str(f["pto_publico"])]
            for i, f in enumerate(NAT["filas"])]
RENUMERADOS = NAT["renumerados"]            # 1: 51000 choca, sale 40000/40001
PUERTOS_USADOS = NAT["puertos_usados"]      # 3

# Clip 4 - lo que NAT rompio: intentos entrantes contra la MISMA tabla de
# NAT de arriba (la conversacion sigue: la fila de la laptop sigue viva).
INTENTOS_ENTRANTES = [22, 40000, 8080, 40001]
NAT_ENTRA = nat_entrante(INTENTOS_ENTRANTES, NAT["tabla"])
BLOQUEADOS = NAT_ENTRA["bloqueados"]        # 2
TOTAL_INTENTOS = NAT_ENTRA["total"]         # 4


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
