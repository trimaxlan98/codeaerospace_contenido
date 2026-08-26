# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 8.2 DTN: la red que tolera la desconexión".
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
# mano en el clip: lo que se dibuja y lo que se escribe no pueden
# discrepar.

# El plan de contactos de la leccion: tres tramos entre el rover y el
# centro de control, cada uno con SU ventana, y ninguna se solapa con la
# siguiente. De ahi sale TODO lo demas.
PLAN = [(0, 2, "rover", "orbitador"),
        (6, 7.5, "orbitador", "DSN"),
        (7.6, 12, "DSN", "control")]
CAMINO = ["rover", "orbitador", "DSN", "control"]

VENT = ventanas_contacto(PLAN)          # 3 ventanas, 7.9 h de 12 = 65.8 %
SIN_CAMINO = tcp_sin_camino(PLAN)       # False: nunca existe la ruta
DTN = dtn_custodia(CAMINO, PLAN)        # 8 MB entregados en 7.65 h

H_INI = 0.0
H_FIN = VENT["horas_totales"]           # 12.0 h de plan dibujado
HORAS_SIN_ENLACE = VENT["horas_totales"] - VENT["horas_con_enlace"]   # 4.1
HUECO_LARGO = VENT["huecos"][0]         # (2.0, 6.0) -> 4.0 h
HUECO_CORTO = VENT["huecos"][1]         # (7.5, 7.6) -> 0.1 h = 6 min
HUECO_LARGO_H = HUECO_LARGO[1] - HUECO_LARGO[0]
HUECO_CORTO_MIN = 60.0 * (HUECO_CORTO[1] - HUECO_CORTO[0])

PASOS = DTN["pasos"]                    # tres saltos, con su espera y su t
ESPERAS = [p["espera_h"] for p in PASOS]            # 0.00 / 5.95 / 1.55 h
T_SALTO = [p["t_h"] for p in PASOS]                 # 0.05 / 6.05 / 7.65 h
PCT_RETENIDO = 100.0 * DTN["retenido_h"] / DTN["total_h"]   # 98.0 %
EN_ENLACE_H = DTN["total_h"] - DTN["retenido_h"]    # 0.15 h de los 7.65
TAM_MB = DTN["tam_mb"]                              # 8 MB

# El apreton que ni siquiera empieza (clip 1). Los mensajes son los de
# la libreria; lo que no existe es el segundo tramo cuando el SYN pide paso.
HS = handshake_tcp()
SYN = HS["eventos"][0]

# La distancia que obliga a todo esto: Marte a 1.5 UA (modulo 8). El
# apreton de TCP gasta un RTT completo antes del primer byte.
MARTE = retardo_marte(1.5)                          # 12.48 min luz de ida
MIN_ANTES_DEL_PRIMER_BYTE = (MARTE["rtt_min"] *
                             HS["antes_del_primer_byte_ms"] / HS["rtt_ms"])

# Para comparar: el enlace geoestacionario del clip 8.1, donde TCP AUN
# funciona. Es la ultima frontera en la que hay camino completo.
GEO = rtt_orbital(H_GEO)                            # 238.7 ms de RTT


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


# --- El plan de contactos dibujado ------------------------------------
# La libreria no trae eje de tiempo CONTINUO (`ranuras` es discreta y las
# ventanas de esta leccion caen en 7.5 y 7.6 h), asi que los carriles se
# dibujan aqui. Las cifras siguen saliendo de `ventanas_contacto`.
ANCHO_PLAN = 8.4          # unidades de manim para las 12 h del eje
ALTO_CARRIL = 0.32
SEP_CARRIL = 0.82


def plan_contactos(fs=15, color_ventana=C_RED):
    """Un carril por tramo sobre UN eje de horas comun.

    Devuelve el VGroup con `.carriles`, `.barras`, `.etiquetas` y `.eje`
    (la linea del eje sirve para convertir horas en x DESPUES de mover el
    grupo: ver `x_hora`).
    """
    x0, x1 = -ANCHO_PLAN / 2.0, ANCHO_PLAN / 2.0
    carriles, barras, etiquetas = VGroup(), VGroup(), VGroup()
    n = len(VENT["ventanas"])
    for i, v in enumerate(VENT["ventanas"]):
        y = (n - 1 - i) * SEP_CARRIL           # el primer tramo, arriba
        base = Rectangle(width=x1 - x0, height=ALTO_CARRIL,
                         stroke_color=C_EJE, stroke_width=1.4,
                         fill_opacity=0.0)
        base.move_to(np.array([0.0, y, 0.0]))
        a = x0 + (x1 - x0) * (v["desde"] - H_INI) / (H_FIN - H_INI)
        b = x0 + (x1 - x0) * (v["hasta"] - H_INI) / (H_FIN - H_INI)
        barra = Rectangle(width=max(b - a, 0.07), height=ALTO_CARRIL,
                          stroke_color=color_ventana, stroke_width=2.0,
                          fill_color=color_ventana, fill_opacity=0.45)
        barra.move_to(np.array([(a + b) / 2.0, y, 0.0]))
        et = tag_hud("%s > %s" % (v["de"], v["a"]), font_size=fs,
                     color=C_EJE)
        et.next_to(base, LEFT, buff=0.26)
        carriles.add(base)
        barras.add(barra)
        etiquetas.add(et)
    y_eje = -SEP_CARRIL * 0.70
    eje = Line(np.array([x0, y_eje, 0.0]), np.array([x1, y_eje, 0.0]),
               color=C_EJE, stroke_width=1.6)
    marcas = VGroup()
    for h in range(0, 13, 2):
        x = x0 + (x1 - x0) * (h - H_INI) / (H_FIN - H_INI)
        tick = Line(np.array([x, y_eje, 0.0]),
                    np.array([x, y_eje - 0.11, 0.0]),
                    color=C_EJE, stroke_width=1.4)
        num = tag_hud("%d" % h, font_size=fs - 2, color=C_EJE)
        num.next_to(tick, DOWN, buff=0.08)
        marcas.add(tick, num)
    et_eje = tag_hud("horas", font_size=fs - 1, color=C_EJE)
    et_eje.next_to(eje, RIGHT, buff=0.20)
    g = VGroup(carriles, barras, etiquetas, eje, marcas, et_eje)
    g.carriles, g.barras, g.etiquetas = carriles, barras, etiquetas
    g.eje, g.mobiliario = eje, VGroup(eje, marcas, et_eje)
    return g


def x_hora(g, h):
    """La x de la hora `h` en un plan ya colocado en pantalla."""
    a, b = g.eje.get_start()[0], g.eje.get_end()[0]
    return a + (b - a) * (float(h) - H_INI) / (H_FIN - H_INI)


def y_carril(g, i):
    """La y del carril del tramo `i` (0 = el de arriba)."""
    return g.carriles[i].get_center()[1]


def en_plan(g, h, i, dy=0.0):
    """El punto (hora, carril) de un plan ya colocado."""
    return np.array([x_hora(g, h), y_carril(g, i) + dy, 0.0])


def reloj_h(h, etiqueta="t", color=None):
    """Contador de HORAS (la pieza `reloj` de la libreria rotula ms).

    Ancho FIJO (`%05.2f`): las gemelas conservan el numero de glifos y el
    Transform entre dos relojes no rompe los digitos.
    """
    return tag_hud("%s = %05.2f h" % (etiqueta, float(h)), font_size=23,
                   color=C_CALCULO if color is None else color)


def cruz(punto, tam=0.20, color=C_PERDIDA, grosor=5.0):
    """Una X sobre un punto: el tramo que no existe (la libreria no trae
    marca de corte)."""
    g = VGroup(
        Line(np.array([-tam, -tam, 0.0]), np.array([tam, tam, 0.0]),
             color=color, stroke_width=grosor),
        Line(np.array([-tam, tam, 0.0]), np.array([tam, -tam, 0.0]),
             color=color, stroke_width=grosor))
    g.move_to(punto)
    return g


def cifras_apiladas(lineas, fs=20, buff=0.20, pos=None):
    """Columna de `tag_hud` alineada a la izquierda. `lineas` = [(texto,
    color), ...]."""
    g = VGroup(*[tag_hud(t, font_size=fs, color=c) for t, c in lineas])
    g.arrange(DOWN, buff=buff, aligned_edge=LEFT)
    if pos is not None:
        g.move_to(pos)
    return g


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
