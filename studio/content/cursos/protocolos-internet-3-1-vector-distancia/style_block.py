# =====================================================================
# CO.DE Academy - "Protocolos de Internet · 3.1 Vector distancia: aprender por rumores".
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
                        ttl_camino, verificar_checksum, voltear_bit,
                        bellman_ford, conteo_al_infinito, ficha,
                        grafo_de)

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
# discrepar. Las cifras de esta leccion salen de `bellman_ford` y de
# `conteo_al_infinito`, medidas en el contenedor antes de escribir nada.

INF = float("inf")
INFINITO_RIP = 16          # el tope de RIP: 16 saltos = "no llego"
NO_LLEGO = "no llego"      # el infinito JAMAS se rotula "inf"
VACIO = "-"

# --- La red de los clips 1-3: seis routers, ocho enlaces --------------
# Los costos estan elegidos (busqueda exhaustiva sobre la topologia) para
# que NINGUN nodo tenga dos rutas empatadas: un empate cambia la columna
# "siguiente" sin cambiar el costo y en pantalla parece un error.
DESTINO = "F"
POS_RED = {"A": (-6.05, 0.05), "B": (-4.35, 1.55), "C": (-4.35, -1.45),
           "D": (-2.05, 1.55), "E": (-2.05, -1.45), "F": (-0.35, 0.05)}
ARISTAS_RED = {("A", "B"): 2, ("A", "C"): 1, ("B", "C"): 4, ("B", "D"): 5,
               ("C", "E"): 6, ("D", "E"): 3, ("D", "F"): 7, ("E", "F"): 1}
TIPOS_RED = {"F": "servidor"}
VECINOS = grafo_de(ARISTAS_RED)

BF = bellman_ford(ARISTAS_RED, DESTINO)
BF_HIST = BF["historia"]            # 4 tablas: ronda 0 .. ronda 3
BF_RONDAS = BF["rondas"]            # 3
NODOS = BF["nodos"]                 # A B C D E F

# El router que se abre en el clip 1 y sus vecinos MEDIDOS.
YO = "C"
VECINOS_YO = sorted(VECINOS[YO].items())          # A 1, B 4, E 6


def camino_por_tabla(t, origen, destino=DESTINO):
    """Sigue la columna 'siguiente' desde `origen`: el camino que el rumor
    construyo, salto a salto."""
    cam = [origen]
    while cam[-1] != destino and len(cam) <= len(t):
        sig = t[cam[-1]][1]
        if sig is None:
            break
        cam.append(sig)
    return cam


CAMINO_OPT = camino_por_tabla(BF["tabla"], "A")   # A-C-E-F
COSTO_OPT = BF["tabla"]["A"][0]                   # 8
ENLACE_CLAVE = ("E", "F")                         # el barato que sostiene todo


def rondas_estable(historia):
    """La primera ronda en que la tabla ya no cambia.

    `conteo_al_infinito` devuelve `max_rondas` de historia aunque se haya
    estabilizado mucho antes: contar las rondas de verdad es mirar cuando
    dos tablas consecutivas son iguales.
    """
    for k in range(len(historia) - 1):
        if historia[k] == historia[k + 1]:
            return k
    return len(historia) - 1


# --- Clip 3: se cae el enlace E-F (F sigue siendo alcanzable) ---------
CAIDA = conteo_al_infinito(ARISTAS_RED, DESTINO, ENLACE_CLAVE,
                           max_rondas=12, infinito=INFINITO_RIP)
CAIDA_RONDAS = rondas_estable(CAIDA["historia"])          # 7
CAIDA_HIST = CAIDA["historia"][:CAIDA_RONDAS + 1]         # r0 .. r7
CAIDA_TABLA = CAIDA_HIST[-1]
COSTO_ANTES = BF["tabla"]["A"][0]                         # 8
COSTO_DESPUES = CAIDA_TABLA["A"][0]                       # 14
CAMINO_DESPUES = camino_por_tabla(CAIDA_TABLA, "A")       # A-B-D-F
# Cuanto SUBE una cifra por ronda mientras A y C se creen mutuamente:
# el enlace A-C cuesta 1, asi que el rumor de ida y vuelta suma 2.
PASO_RUMOR = 2 * ARISTAS_RED[("A", "C")]                  # 2

# --- Clip 4: la cadena, la unica topologia donde el conteo ocurre -----
# Se CAMBIA de red y el pie lo dice: el conteo al infinito solo pasa si el
# corte deja el destino INALCANZABLE, y en la red de arriba siempre queda
# otro camino.
DESTINO_CAD = "D"
POS_CADENA = {"A": (-5.95, 0.60), "B": (-4.10, 0.60),
              "C": (-2.25, 0.60), "D": (-0.40, 0.60)}
ARISTAS_CADENA = {("A", "B"): 1, ("B", "C"): 1, ("C", "D"): 1}
CORTE_CAD = ("C", "D")
NODOS_CAD = ["A", "B", "C", "D"]

BF_CAD = bellman_ford(ARISTAS_CADENA, DESTINO_CAD)
BF_CAD_TABLA = BF_CAD["tabla"]                  # A 3, B 2, C 1, D 0

CI = conteo_al_infinito(ARISTAS_CADENA, DESTINO_CAD, CORTE_CAD,
                        max_rondas=20, infinito=INFINITO_RIP)
CI_HIST = CI["historia"]                        # r0 .. r14
CI_RONDAS = CI["rondas"]                        # 14
CI_SERIES = CI["series"]                        # C: 16,3,5,5,7,7,...,16
CI_HUERFANO = CI["huerfano"]                    # C

CI_HD = conteo_al_infinito(ARISTAS_CADENA, DESTINO_CAD, CORTE_CAD,
                           max_rondas=20, horizonte_dividido=True,
                           infinito=INFINITO_RIP)
CI_HD_HIST = CI_HD["historia"]                  # r0 .. r2
CI_HD_RONDAS = CI_HD["rondas"]                  # 2

# La primera mentira: lo que B le sigue anunciando a C tras el corte.
RUMOR_B = int(BF_CAD_TABLA["B"][0])             # 2
RUMOR_C = int(CI_HIST[1]["C"][0])               # 3 = 2 + 1


# --- La tabla de rutas en pantalla ------------------------------------
CAB_RUTAS = ["router", "costo a %s", "siguiente"]
ANCHOS_RUTAS = [1.45, 1.85, 1.60]
POS_TABLA = np.array([3.55, 0.30, 0.0])         # clips 1-3 (6 filas)
POS_TABLA_CAD = np.array([3.55, -0.10, 0.0])    # clip 4 (4 filas)
POS_RONDA = np.array([3.55, -1.62, 0.0])        # el contador de rondas
POS_RONDA_CAD = np.array([3.55, -1.42, 0.0])


def filas_rutas(t, nodos, destino, tope=None):
    """La tabla {nodo: (costo, siguiente)} como filas de texto.

    `tope`: si se pasa, todo costo >= tope se rotula NO_LLEGO (asi se
    rotula el 16 de RIP cuando lo que significa es "no hay ruta"). En el
    clip 4 se pasa None a proposito: ahi la gracia es VER subir el numero.
    """
    filas = []
    for n in nodos:
        c, sig = t.get(n, (INF, None))
        if c == INF or (tope is not None and c >= tope):
            costo = NO_LLEGO
        else:
            costo = "%d" % int(round(c))
        if n == destino:
            sig_txt = "yo"
        elif sig is None:
            sig_txt = VACIO
        else:
            sig_txt = str(sig)
        filas.append([str(n), costo, sig_txt])
    return filas


def _pintar_rutas(tb, filas, destino):
    """El color dice el papel: cian la cifra calculada, azul el vecino por
    el que se sale, verde el destino, gris lo que aun no se sabe.

    `Tabla` pinta la fila entera de un color; el repintado por celda no
    toca la ESTRUCTURA, asi que dos gemelas repintadas igual siguen siendo
    gemelas y el Transform no rompe glifos.
    """
    for i, f in enumerate(filas):
        nombre, costo, sig = f
        es_destino = nombre == destino
        tb.celda(i, 0).set_color(C_OK if es_destino else C_RED)
        tb.celda(i, 1).set_color(C_EJE if costo in (NO_LLEGO, VACIO)
                                 else C_CIFRA)
        tb.celda(i, 2).set_color(C_OK if sig == "yo" else
                                 (C_EJE if sig == VACIO else C_RED))
    return tb


def tabla_rutas(t, nodos=None, destino=DESTINO, tope=INFINITO_RIP,
                resaltar=None, centro=None, alto=0.44, fs=18):
    """La tabla de rutas hacia `destino`, lista para Transform.

    `filas_max` reserva SIEMPRE las mismas filas y `resaltable` reserva el
    rectangulo de resaltado en todas: dos tablas construidas por aqui son
    gemelas de estructura identica aunque cambien las cifras o se mueva el
    resaltado (trampa heredada de la 1.3).
    """
    nodos = list(nodos or NODOS)
    filas = filas_rutas(t, nodos, destino, tope)
    cab = [CAB_RUTAS[0], CAB_RUTAS[1] % destino, CAB_RUTAS[2]]
    tb = tabla(cab, filas, anchos=ANCHOS_RUTAS, alto=alto, fs=fs,
               filas_max=len(nodos), resaltable=True, resaltar=resaltar)
    tb.move_to(POS_TABLA if centro is None else centro)
    return _pintar_rutas(tb, filas, destino)


def contador_ronda(k, centro=None, color=None):
    """"ronda NN" en ancho FIJO: dos contadores son gemelos y el Transform
    no deja digitos a medio morfar."""
    t = tag_hud("ronda %02d" % int(k), font_size=20,
                color=C_CIFRA if color is None else color)
    t.move_to(POS_RONDA if centro is None else centro)
    return t



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
