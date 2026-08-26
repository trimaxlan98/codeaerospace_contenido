# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 3.3 BGP: la política entre países".
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
                        arp_resolver, barra_bits, bgp_mejor_ruta,
                        cabecera, cabecera_ipv4, checksum_ip, cidr,
                        cola, cola_mm1, conmutacion, crc32_trama,
                        csma_cd, encapsular, enlace, entero_a_ip,
                        eui64, ficha, fragmentar, grafo_de,
                        ip_a_entero, ipv6_comprimir, ipv6_expandir,
                        little, mascara_bits, mux_estadistico, nodo,
                        paquete, pila, prefijo_mas_largo, reloj,
                        secuestro_bgp, switch_aprende, tabla,
                        topologia, trama_ethernet, troceado,
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
# Todo valor que se rotule sale de aqui o de la libreria, nunca escrito a
# mano en el clip: lo que se dibuja y lo que se escribe no pueden
# discrepar. Medido en el contenedor antes de escribir un solo clip.

# El mapa de la leccion: OCHO sistemas autonomos.
#   AS100 y AS200 son tier-1 y PARES entre si; AS100 y AS300 tambien son
#   pares. Lo demas son enlaces cliente->proveedor (jerarquia):
#   AS500 y AS300 cuelgan de AS100, AS400 de AS200, AS600 de AS500 y de
#   AS300, AS700 de AS300 y de AS400, y AS900 (el atacante) de AS500.
# El costo va a 1 porque `grafo_de` (y con el `secuestro_bgp`) lo exige;
# el dibujo va con costos=False, asi que ese 1 nunca sale en pantalla.
POS_AS = {"AS100": (-1.5, 1.80), "AS200": (1.6, 1.80),
          "AS300": (0.9, -1.30), "AS400": (4.0, 0.55),
          "AS500": (-4.0, 0.55), "AS600": (-1.9, -1.30),
          "AS700": (3.4, -1.45), "AS900": (-4.3, -1.60)}
ARISTAS_AS = {("AS100", "AS200"): 1, ("AS100", "AS300"): 1,
              ("AS100", "AS500"): 1, ("AS200", "AS400"): 1,
              ("AS300", "AS700"): 1, ("AS400", "AS700"): 1,
              ("AS500", "AS600"): 1, ("AS600", "AS300"): 1,
              ("AS500", "AS900"): 1}
TIPOS_AS = {"AS700": "servidor", "AS900": "host"}
# Hacia donde va el nombre de cada AS: puesto a mano porque `Topologia`
# los cuelga siempre DEBAJO y ahi los cruzan las aristas que bajan.
ETIQ_AS = {"AS100": UP, "AS200": UP, "AS300": DOWN, "AS400": RIGHT,
           "AS500": LEFT, "AS600": DOWN, "AS700": RIGHT, "AS900": DOWN}
PARES = (("AS100", "AS200"), ("AS100", "AS300"))
JERARQUIA = tuple(a for a in ARISTAS_AS if a not in PARES)

# Cuantos AS hay de verdad: NO lo calcula la libreria, es una medicion
# publica (CIDR Report / RIRs, 2025) y se declara como tal en pantalla.
AS_EN_INTERNET = "~75 000"

# El cable que existe y no se usa: AS600 cuelga de AS500 y de AS300, y no
# va a pagar a sus dos proveedores por llevar trafico que no es suyo.
VALLE = ("AS500", "AS600", "AS300")
RODEO = ("AS500", "AS100", "AS300")

# --- Clip 2: el anuncio recorre un anillo y vuelve al origen -----------
# Sub-mapa (los cinco AS del anillo), redibujado a la izquierda para que
# quepa la tabla: mismas aristas que en el mapa grande.
POS_ANILLO = {"AS700": (-4.85, -1.30), "AS300": (-5.25, 0.60),
              "AS100": (-3.65, 1.85), "AS200": (-1.85, 1.10),
              "AS400": (-2.15, -0.85)}
ARISTAS_ANILLO = {("AS700", "AS300"): 1, ("AS300", "AS100"): 1,
                  ("AS100", "AS200"): 1, ("AS200", "AS400"): 1,
                  ("AS400", "AS700"): 1}
ANILLO = ("AS700", "AS300", "AS100", "AS200", "AS400", "AS700")
ETIQ_ANILLO = {"AS700": DOWN, "AS300": LEFT, "AS100": UP, "AS200": RIGHT,
               "AS400": DOWN}


def _num(as_):
    """'AS300' -> '300'. El AS-path de BGP se escribe con numeros pelados."""
    return str(as_)[2:]


# Lo que VE cada AS al recibir el anuncio: el camino que ya trae, del
# vecino que se lo pasa hasta el origen. Crece un numero por salto.
FILAS_ANUNCIO = tuple(
    (ANILLO[i],
     " ".join(_num(a) for a in
              list(reversed(ANILLO[1:i])) + [ANILLO[0]]))
    for i in range(1, len(ANILLO)))
# -> (('AS300','700'), ('AS100','300 700'), ('AS200','100 300 700'),
#     ('AS400','200 100 300 700'), ('AS700','400 200 100 300 700'))
FILA_BUCLE = len(FILAS_ANUNCIO) - 1        # la que se descarta
AS_PATH_FINAL = FILAS_ANUNCIO[-1][1]

# --- Clip 3: tres rutas al MISMO prefijo, vistas desde AS100 -----------
PREFIJO = "203.0.113.0/24"
LP_CLIENTE = 200      # ruta por un cliente: la que le da dinero a AS100
LP_PAR = 100          # ruta por un par: ni cobra ni paga
RUTAS_BGP = ({"vecino": "AS200", "as_path": ["AS200", "AS400", "AS700"],
              "local_pref": LP_PAR},
             {"vecino": "AS300", "as_path": ["AS300", "AS700"],
              "local_pref": LP_PAR},
             {"vecino": "AS500",
              "as_path": ["AS500", "AS600", "AS300", "AS700"],
              "local_pref": LP_CLIENTE})
RUTAS_EMPATE = tuple(dict(r, local_pref=LP_PAR) for r in RUTAS_BGP)
# El que decide, con sus tres vecinos: mini-mapa a la izquierda de la tabla.
DECIDE = "AS100"
POS_DECISION = {"AS100": (-5.15, 0.35), "AS200": (-6.45, 1.55),
                "AS300": (-3.85, 1.55), "AS500": (-5.15, -1.10)}
ARISTAS_DECISION = {("AS200", "AS100"): 1, ("AS300", "AS100"): 1,
                    ("AS500", "AS100"): 1}
ETIQ_DECISION = {"AS100": RIGHT, "AS200": UP, "AS300": UP, "AS500": DOWN}
BGP_POLITICA = bgp_mejor_ruta([dict(r) for r in RUTAS_BGP])
BGP_DISTANCIA = bgp_mejor_ruta([dict(r) for r in RUTAS_EMPATE])
# MEDIDO: gana AS500 por "local-pref mas alta" con 4 saltos (el camino mas
# largo); igualando las local-pref gana AS300 por "AS-path mas corto" (2).
GANA_POLITICA = BGP_POLITICA["elegida"]["vecino"]
GANA_DISTANCIA = BGP_DISTANCIA["elegida"]["vecino"]
SALTOS_POLITICA = len(BGP_POLITICA["elegida"]["as_path"])
SALTOS_DISTANCIA = len(BGP_DISTANCIA["elegida"]["as_path"])
I_POLITICA = [r["vecino"] for r in RUTAS_BGP].index(GANA_POLITICA)
I_DISTANCIA = [r["vecino"] for r in RUTAS_BGP].index(GANA_DISTANCIA)


def _filas_rutas(rutas):
    """Las tres rutas como filas de tabla (gemelas: misma estructura)."""
    return [(r["vecino"], " ".join(_num(a) for a in r["as_path"]),
             str(len(r["as_path"])), str(r["local_pref"])) for r in rutas]


FILAS_RUTAS = _filas_rutas(RUTAS_BGP)
FILAS_RUTAS_EMPATE = _filas_rutas(RUTAS_EMPATE)

# --- Clip 4: el secuestro ---------------------------------------------
PREF_ESPECIFICO = "203.0.113.0/25"
CIDR_LEG = cidr(PREFIJO)
CIDR_ATA = cidr(PREF_ESPECIFICO)
LEGITIMO, ATACANTE = "AS700", "AS900"
IP_VICTIMA = "203.0.113.10"
LPM = prefijo_mas_largo([(PREFIJO, LEGITIMO), (PREF_ESPECIFICO, ATACANTE)],
                        IP_VICTIMA)
SEC_MISMO = secuestro_bgp(ARISTAS_AS, LEGITIMO, ATACANTE, PREFIJO,
                          mas_especifico=False)
SEC_ESPEC = secuestro_bgp(ARISTAS_AS, LEGITIMO, ATACANTE, PREF_ESPECIFICO,
                          mas_especifico=True)
AS_CAE = SEC_MISMO["envenenados"][0]         # el unico que cae sin mentir mas
SALTOS_ATA = len(SEC_MISMO["camino_atacante"][AS_CAE]) - 1
SALTOS_LEG = len(SEC_MISMO["camino_legitimo"][AS_CAE]) - 1
# MEDIDO: con el MISMO prefijo el atacante se lleva 1 de 6 (16.67 %), solo
# el AS que le queda mas cerca por AS-path (AS500, su propio proveedor);
# con un prefijo MAS ESPECIFICO se lleva 6 de 6 (100 %), porque el prefijo
# mas largo gana siempre (la regla del modulo 2).


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


def etiquetas_a(topo, direcciones, buff=0.14):
    """Recoloca los rotulos de nodo de una topologia, uno a uno.

    `Topologia` los pone SIEMPRE debajo del nodo, y en un grafo denso eso
    los deja justo encima de las aristas que salen hacia abajo. Aqui cada
    nodo dice hacia donde quiere su nombre (UP/DOWN/LEFT/RIGHT).
    """
    for k, d in dict(direcciones).items():
        n = topo.nodo(k)
        if n.etiqueta is not None:
            n.etiqueta.next_to(n.forma, d, buff=buff)
    return topo


def tramo(topo, a, b, desde=0.0, hasta=1.0):
    """Trayectoria ORIENTADA de `a` a `b` sobre un enlace de la topologia.

    `Topologia.enlace(a, b)` devuelve la MISMA linea para (a, b) y (b, a),
    dibujada en el sentido en que se declaro la arista: un MoveAlongPath
    sobre ella va al reves la mitad de las veces. Ademas conviene poder
    parar antes del nodo (`hasta` < 1), porque una ficha que termina en el
    nodo se le monta encima. Los extremos ya vienen con el `buff` del
    enlace, asi que el segmento no cruza los circulos.
    """
    e = topo.enlace(a, b)
    p0, p1 = e.linea.get_start(), e.linea.get_end()
    pa = topo.punto(a)
    if np.linalg.norm(p0 - pa) > np.linalg.norm(p1 - pa):
        p0, p1 = p1, p0
    v = VMobject()
    v.set_points_as_corners([p0 + (p1 - p0) * float(desde),
                             p0 + (p1 - p0) * float(hasta)])
    return v


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
