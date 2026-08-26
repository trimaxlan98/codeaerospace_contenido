# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 6.3 HTTP/2 y QUIC: el fin de la fila india".
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
# Todo valor que se rotule sale de aqui o de la libreria, nunca escrito a
# mano en el clip: lo que se dibuja y lo que se escribe no pueden
# discrepar. Medido en el contenedor antes de escribir los clips.

# La pagina de la leccion: 40 objetos, RTT de 40 ms, TLS 1.3 siempre.
N_OBJETOS = 40
RTT_MS = 40.0

# La escalera completa: la MISMA pagina pedida de seis maneras. Los tres
# primeros escalones los conto la leccion 6.1 (punto de partida, no se
# vuelven a explicar); los tres ultimos son los de esta leccion.
MODOS = ("serie", "keepalive", "paralelo", "h2", "h3", "h3-0rtt")
ESCALERA = dict((m, http_transferencia(N_OBJETOS, modo=m, rtt_ms=RTT_MS))
                for m in MODOS)
NOMBRE_MODO = {
    "serie":     "HTTP/1.0  una conexion por objeto",
    "keepalive": "HTTP/1.1  una conexion, fila india",
    "paralelo":  "HTTP/1.1  seis conexiones",
    "h2":        "HTTP/2    una conexion multiplexada",
    "h3":        "HTTP/3    QUIC sobre UDP",
    "h3-0rtt":   "HTTP/3    reanudado con 0-RTT",
}


def MS(modo):
    """Milisegundos MEDIDOS de la pagina completa en ese modo."""
    return ESCALERA[modo]["ms"]


def VIAJES(modo):
    """RTT (viajes de ida y vuelta) que cuesta la pagina en ese modo."""
    return ESCALERA[modo]["rtts"]


# Los saltos que rotula la leccion (division de cifras ya medidas).
GANANCIA_H2 = MS("paralelo") / MS("h2")        # 3.0x sobre 6 conexiones
GANANCIA_H2_FILA = MS("keepalive") / MS("h2")  # 14x sobre la fila india
GANANCIA_H3 = MS("h2") / MS("h3")              # 1.5x sobre HTTP/2
AHORRO_H3_MS = MS("h2") - MS("h3")             # 40 ms = un viaje entero
GANANCIA_0RTT = MS("serie") / MS("h3-0rtt")    # 120x sobre HTTP/1.0

# Clip 1 - lo que HTTP/1.1 repetia en cada objeto (HPACK lo comprime; la
# libreria no modela la compresion, asi que solo se cuenta lo repetido).
PET = http_peticion()
CABECERAS_REPETIDAS = N_OBJETOS * PET["bytes_peticion"]

# El apreton, escalon a escalon. En HTTP/2 son dos viajes (TCP y luego
# TLS 1.3); QUIC funde los dos en uno; reanudando, ninguno.
TLS13 = tls_viajes("1.3")
TLS0 = tls_viajes("1.3", reanudado=True)
AVISO_0RTT = TLS0["aviso"]
APRETON_H2 = ESCALERA["h2"]["apreton_rtts"]    # 2.0 viajes
APRETON_H3 = VIAJES("h3") - 1.0                # 1.0 viaje
APRETON_0RTT = VIAJES("h3-0rtt") - 1.0         # 0.0 viajes

# Las reglas de viajes que se dibujan: (etiqueta, color) por viaje.
# Naranja = espera de protocolo; ambar = el viaje que trae los datos.
VIAJES_H2 = (("TCP", C_COLA), ("TLS 1.3", C_COLA), ("datos", C_PAQUETE))
VIAJES_H3 = (("QUIC+TLS", C_COLA), ("datos", C_PAQUETE))
VIAJES_0RTT = (("datos", C_PAQUETE),)

# Clips 2 y 3 - el bloqueo de cabeza de linea.
HOL = hol_bloqueo(4, 6, perdida_en=2)
HOL_FLUJOS = HOL["n_flujos"]
HOL_PARADOS_TCP = HOL["parados_tcp"]           # 4 de 4
HOL_PARADOS_QUIC = HOL["parados_quic"]         # 1 de 4
HOL_FLUJO_PERDIDO = HOL["perdida_en"]          # indice 0..3
# Se dibujan las 3 PRIMERAS rondas de las 6 (12 partes entrelazadas): la
# estadistica de partes se mide sobre la ventana dibujada, no sobre la
# corrida entera.
HOL_RONDAS = 3
PATRON_MUX = [f for _ in range(HOL_RONDAS) for f in range(HOL_FLUJOS)]
PATRON_FILA = [f for f in range(HOL_FLUJOS) for _ in range(HOL_RONDAS)]
HOL_PARTES = len(PATRON_MUX)                   # 12 partes en el cable
IDX_PERDIDO = PATRON_MUX.index(HOL_FLUJO_PERDIDO)   # la primera del flujo 3
# Sobre TCP solo sube lo que llego ANTES del hueco: en cuanto falta una
# parte, todo lo que viene detras espera en el bufer aunque ya este ahi.
TCP_LLEGADAS = HOL_PARTES - 1
TCP_ENTREGADAS = IDX_PERDIDO
TCP_ESPERANDO = HOL_PARTES - 1 - IDX_PERDIDO
# Sobre QUIC cada flujo tiene su propio orden: solo el flujo del segmento
# perdido espera; los demas suben a la aplicacion.
QUIC_ENTREGADAS = sum(1 for i, f in enumerate(PATRON_MUX)
                      if f != HOL_FLUJO_PERDIDO and i != IDX_PERDIDO)
QUIC_ESPERANDO = HOL_PARTES - 1 - QUIC_ENTREGADAS


def ETIQUETA_FLUJO(f):
    """El flujo f (0-based) rotulado como lo ve el espectador."""
    return "%d" % (f + 1)


# Clip 4 - la mudanza de red: la misma conexion vista desde las dos redes.
QMIG = quic_migracion()
IP_WIFI = "192.168.1.37"
IP_MOVIL = "10.44.9.212"
PTO_CLIENTE = 51514
IP_SITIO = "93.184.216.34"
PTO_SITIO = 443
SOCKETS = {(IP_SITIO, PTO_SITIO): "servidor web"}
MUDANZA = demux(
    [{"ip_o": IP_WIFI, "pto_o": PTO_CLIENTE,
      "ip_d": IP_SITIO, "pto_d": PTO_SITIO},
     {"ip_o": IP_MOVIL, "pto_o": PTO_CLIENTE,
      "ip_d": IP_SITIO, "pto_d": PTO_SITIO}],
    SOCKETS)
TUPLA_WIFI = MUDANZA["pasos"][0]["tupla"]
TUPLA_MOVIL = MUDANZA["pasos"][1]["tupla"]
CAMPOS_TUPLA = ("IP origen", "Puerto origen", "IP destino", "Puerto destino")
# Fila a fila: campo, valor en wifi, valor en movil. La quinta fila no es
# de la 4-tupla: es el ID de conexion de QUIC, que no cambia.
FILAS_MUDANZA = [[CAMPOS_TUPLA[i], str(TUPLA_WIFI[i]), str(TUPLA_MOVIL[i])]
                 for i in range(4)]
FILAS_MUDANZA.append(["ID de conexion QUIC", QMIG["id"], QMIG["id"]])
CAMBIA_FILA = [i for i in range(5)
               if FILAS_MUDANZA[i][1] != FILAS_MUDANZA[i][2]]   # solo la 0
POR_QUE_TCP = QMIG["tcp"]["por_que"]
POR_QUE_QUIC = QMIG["quic"]["por_que"]


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


def fila_viajes(viajes, etiqueta, ms, y=0.0, x0=-3.60, ancho_viaje=1.55,
                alto=0.50, fs=14):
    """Una linea de tiempo medida en VIAJES de ida y vuelta.

    Un rectangulo por RTT, pegados y con el borde izquierdo comun en `x0`:
    dos filas se comparan a ojo y la longitud ES el tiempo. Naranja los
    viajes que solo son protocolo (el apreton), ambar el que trae los
    datos. `protocolos.py` no trae una regla de RTT (`ranuras` numera del
    0 y aqui las casillas tienen nombre, no numero), asi que vive aqui.
    """
    cajas = VGroup()
    for k, (texto, col) in enumerate(viajes):
        r = Rectangle(width=ancho_viaje, height=alto, stroke_color=col,
                      stroke_width=2.6, fill_color=col, fill_opacity=0.20)
        r.move_to(np.array([x0 + ancho_viaje * (k + 0.5), y, 0.0]))
        t = tag_hud(texto, font_size=fs, color=col)
        if t.width > ancho_viaje * 0.86:
            t.scale_to_fit_width(ancho_viaje * 0.86)
        t.move_to(r.get_center())
        cajas.add(r, t)
    et = tag_hud(etiqueta, font_size=20, color=C_TENUE)
    et.next_to(cajas, LEFT, buff=0.30)
    n = len(viajes)
    tot = tag_hud("%s ms  =  %d %s" % (fmt(ms, 0), n,
                                       "viaje" if n == 1 else "viajes"),
                  font_size=20, color=C_CALCULO)
    tot.next_to(cajas, RIGHT, buff=0.34)
    return VGroup(cajas, et, tot)


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
