# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 2.3 IPv6: el espacio que no se acaba".
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
                        CAMPOS_IPV4, CAMPOS_IPV6, CAPAS_TCPIP,
                        agregar_rutas, arp_resolver, barra_bits, cabecera,
                        cabecera_ipv4, checksum_ip, cidr, cola,
                        cola_mm1, conmutacion, crc32_trama, csma_cd,
                        encapsular, enlace, entero_a_ip,
                        espacio_direcciones, eui64,
                        fragmentar, ip_a_entero, ipv6_comprimir,
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
# Todo valor que se rotule sale de aqui o de la libreria `protocolos.py`,
# NUNCA escrito a mano en el clip. Medido en el contenedor:
#   espacio_direcciones(32)  = {'total': 4294967296, 'por_persona': 0.5302}
#   espacio_direcciones(128) = {'exp10': 38.5318, 'por_m2_tierra': 6.6722e23}
#   ipv6_comprimir('2001:0db8:...:8329')      -> '2001:db8::ff00:42:8329'
#   eui64('aa:bb:cc:11:22:33')  -> interfaz 'a8bb:ccff:fe11:2233',
#       direccion '2001:db8:1:1:a8bb:ccff:fe11:2233', 0xaa -> 0xa8
#   sum(bits) CAMPOS_IPV4 = 160 (20 B); sum(bits) CAMPOS_IPV6 = 320 (40 B)


def _cientifica(x, dec=2):
    """(mantisa_str, exponente) para notacion cientifica en MathTex.

    Helper de formato sobre un numero que YA viene de la libreria (nunca
    se inventa el valor, solo se le da forma de mantisa x 10^exp)."""
    x = float(x)
    exp = int(math.floor(math.log10(x))) if x > 0 else 0
    mant = x / (10.0 ** exp)
    return fmt(mant, dec), exp


# Clip 1 - el espacio de 32 bits se agoto.
E32 = espacio_direcciones(32)
TOTAL_32_TXT = f"{E32['total']:,}".replace(",", " ")     # "4 294 967 296"
POR_PERSONA_32 = fmt(E32["por_persona"], 2)               # "0.53"
POBLACION_TXT = "8 100 000 000"                           # 8.1e9, del propio
                                                          # espacio_direcciones
# Cronologia REAL del agotamiento del pool libre de IPv4 por registro
# regional (fechas publicas de IANA/los 5 RIR; no las calcula la libreria,
# no hay numero que inventar: son fechas de un hecho historico).
AGOTAMIENTO_IPV4 = [
    ("IANA", 2011), ("APNIC", 2011), ("RIPE NCC", 2012),
    ("LACNIC", 2014), ("ARIN", 2015), ("AFRINIC", 2020),
]

# Clip 2 - 128 bits: la escala honesta.
E128 = espacio_direcciones(128)
E128_MANT, E128_EXP = _cientifica(E128["total"])          # "3.40", 38
M2_MANT, M2_EXP = _cientifica(E128["por_m2_tierra"])      # "6.67", 23
DIR6_EJEMPLO = "2001:0db8:0000:0000:0000:ff00:0042:8329"
DIR6_GRUPOS = ipv6_expandir(DIR6_EJEMPLO)                 # 8 grupos de 4 hex
DIR6_COMPRIMIDA = ipv6_comprimir(DIR6_EJEMPLO)            # '2001:db8::ff00:42:8329'


def _hex_a_binario(grupos):
    """Los N*16 bits de una lista de grupos hexadecimales -> '0101...'."""
    return "".join(format(int(g, 16), "016b") for g in grupos)


# Clip 3 - SLAAC / EUI-64.
MAC_EJEMPLO = "aa:bb:cc:11:22:33"
PREFIJO_SLAAC = "2001:db8:1:1"                            # /64 (4 grupos)
EUI = eui64(MAC_EJEMPLO, PREFIJO_SLAAC)
DIR6_SLAAC_BIN = _hex_a_binario(ipv6_expandir(EUI["direccion"]))
MAC_BYTES = MAC_EJEMPLO.split(":")                        # ['aa','bb',...]

# Clip 4 - convivir: la cabecera fija de 40 B junto a la de 20 B.
CAB4 = cabecera_ipv4(origen="192.0.2.10", destino="192.0.2.20", ttl=64,
                     protocolo=6)
BITS_IPV4 = sum(b for _, b in CAMPOS_IPV4)                # 160 -> 20 B
BITS_IPV6 = sum(b for _, b in CAMPOS_IPV6)                # 320 -> 40 B
BYTES_IPV4, BYTES_IPV6 = BITS_IPV4 // 8, BITS_IPV6 // 8
# Mapeo EXACTO entre los 12 campos de CAMPOS_IPV4 y los 8 de CAMPOS_IPV6
# (verificado: fuera + renombrados + iguales = 12; iguales + renombrados +
# nuevo = 8).
CAMPOS_FUERA = ["IHL", "Identificacion", "Banderas", "Desplazamiento",
               "Checksum"]
CAMPOS_RENOMBRADOS = [("DSCP/ECN", "Clase de trafico"),
                      ("Longitud total", "Longitud de carga"),
                      ("TTL", "Limite de saltos"),
                      ("Protocolo", "Siguiente cabecera")]
CAMPOS_IGUALES = ["Version", "Direccion origen", "Direccion destino"]
CAMPO_NUEVO_IPV6 = "Etiqueta de flujo"
# Adopcion real de IPv6 en trafico mundial: cifra publica aproximada
# (mediciones de Google sobre su propio trafico), NO calculada por
# `protocolos.py` -> se declara como tal en el pie, nunca como "medido".
ADOPCION_IPV6_PCT = 45.0


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
