# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 5.3 Ver la red: ICMP, ping y traceroute".
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
# Medido en el contenedor (ver informe final). Todo valor que se rotule
# sale de aqui o de una llamada directa a la libreria en el clip.

# Clip 1 - ICMP: el protocolo que se queja.
DATOS_NORMALES = [("Cabecera", 1.0, "20 B"), ("Datos de la app", 3.0,
                                              "1460 B")]
CADENA_TTL = ["R1", "R2", "R3"]
TTL_CAM = ttl_camino(ttl0=3, saltos=CADENA_TTL)          # muere en R3, ttl=0
CULPABLE = cabecera_ipv4(origen="10.0.0.7", destino="93.184.216.34",
                         ttl=0, protocolo=17, longitud=576, ident=0x2f19)
TIPO_TEXCEDIDO, CODIGO_TEXCEDIDO = 11, 0                 # ICMP_TIPOS[11]
ICMP_CAMPOS = [("Tipo", 1.0, str(TIPO_TEXCEDIDO)),
              ("Codigo", 1.0, str(CODIGO_TEXCEDIDO)),
              ("Cabecera original", 3.0, "el paquete culpable (20 B)")]
LISTA_ICMP = [("3", ICMP_TIPOS[3]), ("11", ICMP_TIPOS[11]),
             ("3/4", ICMP_TIPOS[(3, 4)])]     # tipo/codigo, ya en texto
CAB_ANCHO, CAB_ALTO, CAB_FS = 11.6, 0.55, 15             # medido en 2.1
PATH_TTL = ["origen"] + CADENA_TTL
POS_TTL1 = {"origen": (-4.4, 0.0), "R1": (-1.6, 0.0), "R2": (1.1, 0.0),
           "R3": (3.8, 0.0)}
ARISTAS_TTL1 = {("origen", "R1"): None, ("R1", "R2"): None,
               ("R2", "R3"): None}
TIPOS_TTL1 = {"origen": "host"}

# Clip 2 - Ping mide (propagacion vs cola, RTT MEDIDO).
PING_BASE = ping(9000.0, 8)                    # semilla=2, n=8 (de serie)
PING_CARGA = ping(9000.0, 8, carga=0.85)
RTT_MIN = PING_BASE["min"]                     # 96.4 ms
PROP_MS = PING_BASE["prop_ms"]                 # 90.1 ms: tope duro, 2c/3
RESTO_MS = RTT_MIN - PROP_MS                   # 6.3 ms: routers + jitter
MEDIA_BASE = PING_BASE["media"]                # 97.1 ms
MEDIA_CARGA = PING_CARGA["media"]              # 124.3 ms
DELTA_COLA = PING_CARGA["espera_ms"]           # +27.2 ms de cola, exacto
MUESTRAS_BASE = PING_BASE["muestras"]          # las 8 rondas dibujadas
MUESTRAS_CARGA = PING_CARGA["muestras"]

# Clip 3 - Traceroute: TTL 1..7, el salto 4 mudo.
CAMINO_TR = ["R1", "R2", "R3", "R4", "R5", "R6", "destino"]
TRACE = traceroute(CAMINO_TR, mudos=(4,), distancia_km=9000.0, semilla=4)
# Columnas GENERICAS por TTL (no por nombre de router): el salto mudo
# necesita su PROPIA columna, o el evento se queda con de==a (arco de
# longitud cero, invisible).
ACTORES_TR = ["origen"] + ["salto %d" % i for i in range(1, len(CAMINO_TR))
                          ] + ["destino"]


def _texto_evento_tr(s):
    if s["mudo"]:
        return "*   sin respuesta"
    if s["icmp"] == "respuesta de eco":
        return "%s   llegue: eco" % s["nodo"]
    return "%s   tiempo excedido" % s["nodo"]


EVENTOS_TR = [
    {"de": "origen", "a": ACTORES_TR[s["ttl"]], "texto": _texto_evento_tr(s),
     "t_ms": s["ms"],
     "color": (C_PERDIDA if s["mudo"] else
              (C_OK if s["icmp"] == "respuesta de eco" else C_CAPA))}
    for s in TRACE["saltos"]]

# Clip 4 - El MTU escondido (pmtud MEDIDO, con y sin agujero negro).
MTUS_CAMINO = [1500, 1500, 1400, 1500]
PMTU_OK = pmtud(MTUS_CAMINO)                   # mtu_camino=1400, red=100
PMTU_NEGRO = pmtud(MTUS_CAMINO, filtra_icmp=True)   # agujero_negro=True
FRAG_CAMINO = fragmentar(1500 - 20, mtu=1400)  # contraste: fragmentar SI
                                               # se hiciera en el camino
POS_MTU = {"origen": (-5.4, 0.0), "R1": (-2.6, 0.0), "R2": (0.2, 0.0),
          "R3": (3.0, 0.0), "destino": (5.6, 0.0)}
ARISTAS_MTU = {("origen", "R1"): 1500, ("R1", "R2"): 1500,
              ("R2", "R3"): 1400, ("R3", "destino"): 1500}
TIPOS_MTU = {"origen": "host", "destino": "servidor"}
TABLA_MTU_CAB = ["salto", "MTU", "intento", "resultado"]
TABLA_MTU_FILAS = [
    [str(p["salto"]), str(p["mtu"]), str(p["intento"]),
     ("cabe" if p["cabe"] else p["icmp"])]
    for p in PMTU_OK["pasos"]]


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
