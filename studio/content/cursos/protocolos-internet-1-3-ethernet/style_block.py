# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 1.3 El vecindario: Ethernet, MAC y ARP".
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
                        CAMPOS_IPV4, CAPAS_TCPIP, agregar_rutas,
                        arp_resolver, barra_bits, cabecera,
                        cabecera_ipv4, checksum_ip, cidr, cola,
                        cola_mm1, conmutacion, crc32_trama, csma_cd,
                        encapsular, enlace, entero_a_ip, eui64,
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
# NUNCA escrito a mano en el clip: lo que se dibuja y lo que se escribe no
# pueden discrepar. Medido en el contenedor antes de escribir los clips.

# --- Clip 1: la trama Ethernet y su FCS -------------------------------
MAC_A = "aa:bb:cc:00:11:22"      # el vecino que recibe
MAC_B = "aa:bb:cc:00:33:44"      # el que envia
MAC_C = "aa:bb:cc:00:55:66"      # los otros dos del cable
MAC_D = "aa:bb:cc:00:77:88"
CARGA_TRAMA = "HOLA MUNDO"
TRAMA = trama_ethernet(MAC_A, MAC_B, CARGA_TRAMA)
TRAMA_BYTES = len(TRAMA["bytes"])          # 60 B (carga rellenada a 46)
TRAMA_RELLENO = TRAMA["relleno"]           # 36 B de relleno
FCS_OK = "0x%08x" % TRAMA["fcs"]           # 0xdb518637
TIPO_OK = "0x%04x" % TRAMA["tipo"]         # 0x0800 = IPv4

# El bit 97 cae en el byte 12: el byte alto del campo Tipo. Al voltearlo,
# 0x08 pasa a 0x48 y el CRC-32 recalculado ya no coincide con el FCS que
# viajaba: la trama se descarta.
BIT_ROTO = 97
BYTE_ROTO = BIT_ROTO // 8                  # 12
BYTES_ROTOS = voltear_bit(TRAMA["bytes"], BIT_ROTO)
FCS_ROTO = "0x%08x" % crc32_trama(BYTES_ROTOS)   # 0xb7d3857e
TIPO_ROTO = "0x%02x%02x" % (BYTES_ROTOS[12], BYTES_ROTOS[13])   # 0x4800

# La trama como pieza `paquete`: pesos medidos para que ninguna MAC se
# encime (la pieza reescala el texto que no cabe en su campo).
ANCHO_TRAMA = 11.0
CAMPOS_TRAMA = [("Destino", 2.1, MAC_A), ("Origen", 2.1, MAC_B),
                ("Tipo", 1.0, TIPO_OK), ("Carga", 2.2, CARGA_TRAMA),
                ("FCS", 1.5, FCS_OK)]


def trama_pieza(valores=None):
    """La trama de la leccion, con el FCS (cifra calculada) en cian.

    `valores` = dict {campo: valor} para la GEMELA. La estructura es
    identica campo a campo, y los valores que cambian conservan su
    longitud: se puede hacer Transform entre dos de estas.
    """
    campos = CAMPOS_TRAMA
    if valores:
        campos = [(n, w, str(valores.get(n, v))) for n, w, v in campos]
    p = paquete(campos, ancho=ANCHO_TRAMA, alto=0.80, fs=16,
                color=C_PAQUETE, color_carga=C_PAQUETE)
    p.iluminar("FCS", C_CIFRA)
    return p


# --- Clip 2: CSMA/CD, tres estaciones sobre el mismo cable ------------
# Semillas probadas: 5 -> 7 ranuras / 2 colisiones (esperas 1,1,0 y 3,1:
# se ven ranuras de silencio, que es lo que hay que contar); 7 -> 14
# ranuras, no cabe en pantalla; 11 -> 5 ranuras pero casi todas las
# esperas salen 0 y el backoff no se ve. Se fija la 5.
CSMA_SEMILLA = 5
CSMA = csma_cd(3, semilla=CSMA_SEMILLA)
CSMA_N = CSMA["n_estaciones"]              # 3
CSMA_RANURAS = CSMA["ranuras"]             # 7 ranuras dibujadas
CSMA_COLISIONES = CSMA["colisiones"]       # 2 colisiones contadas
CSMA_POR_RANURA = {h["ranura"]: h for h in CSMA["historia"]}
ESTACIONES = ["E0", "E1", "E2"]

# Geometria del clip 2: el cable arriba, las estaciones colgando de el y
# la regla de ranuras abajo (7 cajas, una por ranura de la historia).
CABLE_Y = 1.62
CABLE_X = (-5.2, 5.2)
X_ESTACION = (-3.2, 0.0, 3.2)
EST_Y = 0.46          # centro de las estaciones
ESPERA_Y = -0.52      # donde se rotula la espera sorteada de cada una
RANURA_Y = -1.35      # centro de la regla de ranuras
CONTEO_Y = -2.45      # el conteo final de colisiones


def csma_evento(r):
    """Que pasa en la ranura r: dict de la historia o None (silencio)."""
    return CSMA_POR_RANURA.get(int(r))


# --- Clip 3: el switch que aprende ------------------------------------
# En el cable los nombres son MACs. Se rotula la COLA de cada una (los
# tres primeros bytes son el mismo fabricante en las cuatro): asi la
# tabla MAC cabe al lado de la red sin encimarse.
COLA_MAC = {k: v[-5:] for k, v in
            (("A", MAC_A), ("B", MAC_B), ("C", MAC_C), ("D", MAC_D))}
PUERTOS_SW = {COLA_MAC["A"]: 1, COLA_MAC["B"]: 2, COLA_MAC["C"]: 3}
EV_SWITCH = [(COLA_MAC["A"], COLA_MAC["B"]),   # inunda: no conoce a B
             (COLA_MAC["B"], COLA_MAC["A"]),   # unicast: ya aprendio A
             (COLA_MAC["A"], COLA_MAC["B"]),   # unicast: ya aprendio B
             (COLA_MAC["C"], COLA_MAC["A"])]   # unicast: A sigue en tabla
SW = switch_aprende(EV_SWITCH, PUERTOS_SW)
SW_PASOS = SW["pasos"]
SW_INUNDADAS = SW["inundadas"]             # 1 de 4
SW_UNICAST = SW["unicast"]                 # 3 de 4
SW_TOTAL = SW["total"]                     # 4
SW_FILAS = 3                               # filas fijas de la tabla MAC

POS_SW = {"SW": (-3.55, 0.35),
          COLA_MAC["A"]: (-6.05, 1.80), COLA_MAC["B"]: (-6.05, -1.10),
          COLA_MAC["C"]: (-0.95, 1.80), COLA_MAC["D"]: (-0.95, -1.10)}
ARISTAS_SW = {("SW", COLA_MAC["A"]): "p1", ("SW", COLA_MAC["B"]): "p2",
              ("SW", COLA_MAC["C"]): "p3", ("SW", COLA_MAC["D"]): "p4"}
TIPOS_SW = {"SW": "switch", COLA_MAC["A"]: "host", COLA_MAC["B"]: "host",
            COLA_MAC["C"]: "host", COLA_MAC["D"]: "host"}
HOSTS_SW = [COLA_MAC[k] for k in ("A", "B", "C", "D")]
TABLA_SW_POS = (3.85, 0.55)     # centro de la tabla MAC
ACCION_Y = -2.35                # donde se rotula inunda / unicast


def filas_mac(tabla_mac):
    """La tabla MAC como 3 filas SIEMPRE (las vacias con guiones): la
    gemela `.con_filas` exige estructura identica para el Transform."""
    filas = [[m, "p%d" % p] for m, p in sorted(tabla_mac.items(),
                                               key=lambda kv: kv[1])]
    while len(filas) < SW_FILAS:
        filas.append(["-", "-"])
    return filas[:SW_FILAS]


# --- Clip 4: ARP, quien tiene esta IP ---------------------------------
IP_YO = "192.168.1.10"
IP_DEST = "192.168.1.20"
VECINOS = {IP_DEST: MAC_B, "192.168.1.30": MAC_C, "192.168.1.40": MAC_D}
ARP1 = arp_resolver(IP_DEST, VECINOS)              # pregunta: 1
ARP2 = arp_resolver(IP_DEST, VECINOS, ARP1["cache"])   # ya en cache: 0
ARP_MAC = ARP1["mac"]                              # aa:bb:cc:00:33:44
ARP_BROADCAST = ARP1["pasos"][0]["a"]              # ff:ff:ff:ff:ff:ff
ARP_PREGUNTAS = ARP1["preguntas"] + ARP2["preguntas"]   # 1 en 2 envios
ARP_IPS = [IP_YO, IP_DEST, "192.168.1.30", "192.168.1.40"]
ARP_MACS = [MAC_A, MAC_B, MAC_C, MAC_D]
# Geometria del clip 4: los cuatro vecinos colgando del mismo cable, la
# pregunta/respuesta bajo el cable y la cache ARP mas abajo.
ARP_X = (-4.65, -1.55, 1.55, 4.65)
ARP_CABLE_X = (-5.9, 5.9)
ARP_CABLE_Y = 0.05
ARP_HOST_Y = 1.05
ARP_IP_Y = 1.88
ARP_TAG_Y = -0.72       # la pregunta y luego la respuesta
ARP_TABLA_Y = -1.72     # la cache ARP
ARP_CUENTA_Y = -2.58    # preguntas contadas


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
