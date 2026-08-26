# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 8.1 Internet en órbita: GEO, LEO y la malla láser".
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

# `pase_leo` vive en la libreria del curso 24 (comunicaciones
# digitales): la 8.1 la reutiliza tal cual para la duracion del
# pase y el traspaso, como manda el contrato de protocolos.py.
import comunicaciones as _com  # noqa: E402
from comunicaciones import pase_leo  # noqa: E402

_com.Text = Text

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
# discrepar. Medido en el contenedor ANTES de escribir los clips.

# --- La escala DECLARADA de la geometria (clips 1 y 3) ---------------
# Una sola escala para las dos orbitas: si el GEO se dibujara comodo y el
# LEO tambien, la leccion mentiria. A esta escala el LEO roza el suelo.
ESCALA_KM = 12000.0                 # km por unidad de pantalla
R_TIERRA_KM = 6371.0
R_TIERRA_U = R_TIERRA_KM / ESCALA_KM        # 0.531
GEO_U = H_GEO / ESCALA_KM                   # 2.982
LEO_U = H_LEO / ESCALA_KM                   # 0.046

# --- Clip 1: el retardo que impone la luz -----------------------------
GEO = rtt_orbital(H_GEO)                    # 35 786 km, elevacion 90
GEO_KM = GEO["d_km"]                        # 35786.0
GEO_IDA = GEO["ida_ms"]                     # 119.4 ms un tramo suelo-satelite
GEO_RTT = GEO["rtt_ms"]                     # 238.7 ms subir y bajar
GEO_USR = GEO["rtt_usuario_ms"]             # 477.5 ms de usuario a usuario
# La misma ida y vuelta por un cable submarino de 9 000 km (fibra, no
# vacio: `ping` usa la velocidad en fibra y suma el proceso de 8 saltos).
CABLE_KM = 9000.0
CABLE = ping(CABLE_KM, saltos=8)
CABLE_MS = CABLE["media"]                   # 97.1 ms ida y vuelta

# --- Clip 2: TCP con 477 ms de ida y vuelta ---------------------------
CAP_MBPS = 50.0                             # el enlace CONTRATADO
TUBO = bdp(CAP_MBPS, GEO_USR)
TUBO_KB = TUBO["kb"]                        # 2914.3 kB en vuelo
TUBO_SEG = int(TUBO["segmentos_1460"])      # 2043 segmentos de 1460 B
VENT_CHICA, VENT_GRANDE = 64, 256           # kB de ventana
T64 = tcp_en_orbita(GEO_USR, VENT_CHICA, CAP_MBPS, pep=True)
T256 = tcp_en_orbita(GEO_USR, VENT_GRANDE, CAP_MBPS, pep=True)
PRECIO_PEP = T64["precio_pep"]              # lo dice la libreria, no yo
# Llenar el tubo con arranque lento: cwnd duplicandose cada RTT hasta
# cubrir los TUBO_SEG segmentos. El umbral se pone alto a proposito para
# medir la exponencial entera.
SLOW = arranque_lento(ssthresh=4096, cwnd0=1, rtts=14)
SLOW_RTTS = next(i for i, c in enumerate(SLOW["traza"]) if c >= TUBO_SEG)
SLOW_CWND = SLOW["traza"][SLOW_RTTS]        # 2048 segmentos
SLOW_S = SLOW_RTTS * GEO_USR / 1000.0       # 5.25 s solo para arrancar
SLOW_S_LEO = SLOW_RTTS * rtt_orbital(H_LEO)["rtt_usuario_ms"] / 1000.0
# El enganche con la 4.3: alli la diferencia Reno/CUBIC era teorica porque
# el RTT era corto. Con el RTT orbital deja de serlo.
RTT_TIERRA = 40.0
RECUP = [recuperacion_tras_perdida(TUBO_SEG, r)
         for r in (RTT_TIERRA, GEO_USR)]
RECUP_CUBIC_S = RECUP[0]["cubic_s"]         # 11.53 s: NO depende del RTT
RECUP_RENO_RTTS = RECUP[1]["reno_rtts"]     # 1021.5 RTT de +1 segmento
RECUP_GEO_MIN = RECUP[1]["reno_s"] / 60.0   # 8.13 minutos de Reno


def GANADOR(r):
    """Quien recupera antes y por cuanto, MEDIDO (la misma regla de la
    4.3: dentro del 10 % se declara empate en vez de fingir)."""
    if r["reno_s"] < r["cubic_s"] * 0.90:
        return "Reno  %sx" % fmt(r["cubic_s"] / r["reno_s"], 1)
    if r["cubic_s"] < r["reno_s"] * 0.90:
        return "CUBIC %sx" % fmt(r["veces"], 1)
    return "empate"


# --- Clip 3: LEO y el pase --------------------------------------------
LEO = rtt_orbital(H_LEO)                    # 550 km, elevacion 90
LEO_KM = LEO["d_km"]
LEO_IDA = LEO["ida_ms"]                     # 1.8 ms un tramo
LEO_RTT = LEO["rtt_ms"]                     # 3.7 ms
LEO_USR = LEO["rtt_usuario_ms"]             # 7.3 ms de usuario a usuario
VECES_LEO = GEO_USR / LEO_USR               # 65.1 veces menos
# El pase sobre la estacion (Tierra sin rotar: se declara en el pie).
PASE = pase_leo(H_LEO, elev_max=60.0)
PASE_S = float(PASE["t_total_s"])           # 727.6 s horizonte a horizonte
PASE_MIN = PASE_S / 60.0                    # 12.13 min
ELEV_MAX = 60.0
ELEV_UMBRAL = 25.0                          # por debajo, la antena lo suelta
_M = np.asarray(PASE["elev_deg"]) >= ELEV_UMBRAL
PASE_UTIL_S = float(np.asarray(PASE["t_s"])[_M].max() -
                    np.asarray(PASE["t_s"])[_M].min())   # 254.7 s
PASE_UTIL_MIN = PASE_UTIL_S / 60.0          # 4.24 min
PASE_T0 = float(np.asarray(PASE["t_s"]).min())           # -363.8 s
PASE_T1 = float(np.asarray(PASE["t_s"]).max())           # +363.8 s
# El retardo NO es constante durante el pase: cambia con la elevacion.
# (elevacion 0 = horizonte: 2703.8 km, el mismo d_km que mide `pase_leo`.)
LEO_IDA_CENIT = rtt_orbital(H_LEO, elevacion_deg=ELEV_MAX)["ida_ms"]   # 2.09
LEO_IDA_HORIZ = rtt_orbital(H_LEO, elevacion_deg=0.0)["ida_ms"]        # 9.02
LEO_D_HORIZ = rtt_orbital(H_LEO, elevacion_deg=0.0)["d_km"]            # 2703.8
TRASPASOS_HORA = 3600.0 / PASE_S            # 4.95 pases por hora


def ELEV(t):
    """Elevacion MEDIDA (grados) en el segundo t del pase."""
    return float(np.interp(float(t), np.asarray(PASE["t_s"]),
                           np.asarray(PASE["elev_deg"])))


# --- Clip 4: la malla optica ------------------------------------------
MALLA = malla_laser(4, 6)                   # 4 planos de 6 satelites
MALLA_N = MALLA["satelites"]                # 24
MALLA_ENLACES = len(MALLA["aristas"])       # 42 enlaces opticos
MALLA_PLANOS, MALLA_POR_PLANO = MALLA["planos"], MALLA["por_plano"]
ORIGEN_MALLA = MALLA["origen"]              # S0-0
DESTINO_A = MALLA["destino"]                # S3-3: el que ve Londres ahora
RUTA_A = MALLA["ruta"]                      # 6 saltos
SALTOS_A, COSTE_A = MALLA["saltos"], MALLA["coste"]
DESTINO_B = "S3-1"                          # 10 min despues lo ve otro
RUTA_B = camino_dijkstra(MALLA["dijkstra"], DESTINO_B)
SALTOS_B = len(RUTA_B) - 1                  # 4 saltos
COSTE_B = MALLA["dijkstra"]["dist"][DESTINO_B]
# Cada plano es un anillo (el satelite habla con el de delante y el de
# atras) inclinado 18 grados; los planos se ven de canto y separados 2.9.
# Parametros hallados por barrido en el contenedor: con ellos ninguna
# arista pasa a menos de 0.58 de un nodo que no sea suyo (a ojo se
# encimaban).
_MALLA_AX, _MALLA_AY, _MALLA_GAP = 1.10, 1.85, 2.90
_MALLA_TILT = math.radians(18.0)


def _pos_malla():
    ct, st = math.cos(_MALLA_TILT), math.sin(_MALLA_TILT)
    x0 = -_MALLA_GAP * (MALLA_PLANOS - 1) / 2.0
    pos = {}
    for p in range(MALLA_PLANOS):
        for i in range(MALLA_POR_PLANO):
            a = 2.0 * math.pi * i / MALLA_POR_PLANO
            dx, dy = _MALLA_AX * math.sin(a), _MALLA_AY * math.cos(a)
            pos["S%d-%d" % (p, i)] = (x0 + p * _MALLA_GAP + dx * ct - dy * st,
                                      dx * st + dy * ct)
    return pos


POS_MALLA = _pos_malla()
TIPOS_MALLA = {k: "satelite" for k in POS_MALLA}


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


def miles(x):
    """Entero con separador de millares en ESPACIO (ASCII puro): 35 786.
    `fmt` no separa millares, y "35786 km" junto a un pie que dice
    "35 786 km" se lee como dos cifras distintas."""
    return "{:,}".format(int(round(float(x)))).replace(",", " ")


def apagar_camino(topo, camino, color=C_RED, grosor=2.4, grosor_nodo=2.2):
    """Deshace `Topologia.resaltar_camino`: la pieza recolorea aristas Y
    nodos y no trae inversa, asi que sin esto la segunda ruta del clip 4
    se dibujaria ENCIMA de la primera y se verian las dos a la vez."""
    for a, b in zip(camino[:-1], camino[1:]):
        topo.enlace(a, b).linea.set_stroke(color, width=grosor)
    for k in camino:
        topo.nodo(k).forma.set_stroke(color, width=grosor_nodo)
    return topo


def cifra_ms(regla, ms, dec=1, font_size=20, color=None, buff=0.30):
    """La cifra en ms pegada al final de una `regla_viajes`, con los
    decimales que quiero (la pieza solo rotula enteros)."""
    t = tag_hud("%s ms" % fmt(ms, dec), font_size=font_size,
                color=C_CALCULO if color is None else color)
    t.next_to(regla.cajas[-1], RIGHT, buff=buff)
    return t


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
