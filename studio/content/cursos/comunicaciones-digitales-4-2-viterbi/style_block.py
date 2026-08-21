# =====================================================================
# CO.DE Academy - "Comunicaciones digitales · 4.2 Viterbi: el camino más probable".
# Bloque de estilo del proyecto. Se antepone al
# script de CADA clip; los clips NO repiten imports: solo definen su
# ClipN(Scene).
#
# Copia del molde de la familia (leccion 1.1): cambia SOLO la cabecera
# y la tabla de numeros de la leccion.
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
from senal import PulsoDeSenal, destello
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
from algebra_lineal import (C_EJE, C_REJILLA, fmt, flecha_libre,  # noqa: E402
                            grafica, plano, vector)

_al.Text = Text

import comunicaciones as _com  # noqa: E402
from comunicaciones import (C_BANDA, C_BIT, C_CIFRA, C_COD, C_IA,  # noqa: E402
                            C_RUIDO, C_SENAL, C_TECHO, MODCODS,
                            acm_conmutar, alias_de, amplificar,
                            ancho_banda, apertura_ojo,
                            autoencoder_constelacion, awgn, bandido_acm,
                            banda_espacio, ber_montecarlo,
                            ber_teorica_qam, bits_de_muestra,
                            buscar_preambulo, campo_vecino, cdma_extraer,
                            cdma_mezclar, conformar, constelacion_apsk16,
                            constelacion_bpsk, constelacion_psk8,
                            constelacion_qam16, constelacion_qam64,
                            constelacion_qpsk, conv_codificar,
                            correlacion_circular, cuantizar, curva_ber,
                            d_min, demodular, diagrama_ojo, doppler_de,
                            energia_media, enlace_tierra,
                            entrenar_frontera, espectro_area, fspl_db,
                            frontera_de, frontera_decision, grafo_ldpc,
                            isi_en, ldpc_decodificar, ldpc_pequeno,
                            lluvia_serie, mapa_haces, muestrear, onda,
                            pase_cielo, pase_leo, perceptron_mini,
                            plano_iq, ppm_fotones, predecir_red, psd_db,
                            pulso_lento, pulso_rc, pulso_rect,
                            q_de, ranuras_ppm, registro_conv,
                            rejilla_acceso, RAMAS_CONV, saleh,
                            secuencia_pn, senal_con_preambulo,
                            ser_montecarlo, snr_cuantizacion, tren_bits,
                            trellis, viterbi, walsh)

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
# Regla: EL COLOR DICE EL PAPEL. Ambar el bit y el dato; cian TODA cifra
# calculada; azul la forma de onda y el canal fisico; rojo el ruido y los
# errores; verde los codigos y lo corregido; violeta el techo de Shannon;
# fucsia lo aprendido; naranja el espectro y las ranuras; gris mobiliario.
C_TITULO = CODE_INK          # #e8edf3 titulos
C_TENUE = CODE_MUTED         # #94a0b0 pies y elementos secundarios
C_ACENTO = CODE_ACCENT       # #f59e0b ambar
C_ACENTO_2 = CODE_ACCENT_2   # #ea580c naranja de cierre
C_CALCULO = C_CIFRA          # cian: cifras y resultados numericos

MARGEN_PIE = 0.68            # separacion del pie al borde inferior

# --- Numeros de la leccion --------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria, nunca escrito a
# mano en el clip: el trellis dibujado y la metrica escrita no pueden
# discrepar. El mensaje es REAL: se codifica, se ensucia y se decodifica
# con la libreria, y las tres cosas salen del MISMO array.
CONV_K = 3                       # memoria del codigo (leccion 4.1)
CONV_G = "(7,5)"                 # generadores en octal
CONV_TASA = "1/2"                # dos bits de salida por bit de entrada
PASOS = 8                        # bits del mensaje = pasos del trellis
N_ESTADOS = 4                    # 2^(K-1)
MENSAJE = [1, 0, 1, 1, 0, 1, 1, 0]           # los 8 bits que salen de la sonda
_COD, ESTADOS = conv_codificar(MENSAJE)      # 16 bits codificados, 9 estados
CODIFICADO = [int(b) for b in _COD]
N_CAMINOS = 2 ** PASOS           # 256 caminos posibles en la rejilla
IDX_ERROR = (3, 11)              # los dos bits que el canal voltea
RECIBIDO = list(CODIFICADO)
for _i in IDX_ERROR:
    RECIBIDO[_i] ^= 1
N_ERR_CANAL = sum(int(a != b) for a, b in zip(CODIFICADO, RECIBIDO))   # 2
PARES_RX = [(RECIBIDO[2 * t], RECIBIDO[2 * t + 1]) for t in range(PASOS)]

INF_MET = 10 ** 9                # marca de estado inalcanzable

# El camino ganador y los bits salen de la libreria...
VIT = viterbi(RECIBIDO)
BITS_DEC = [int(b) for b in VIT["bits"]]
CAMINO = [int(s) for s in VIT["camino"]]
ESTADO_FINAL = CAMINO[-1]

# ...pero las METRICAS se recalculan aqui. BUG de la libreria (reportado,
# no tocado): en `viterbi` el costo de rama se escribe
#     costo = (o1 != r[t][0]) + (o2 != r[t][1])
# y como r es un array de numpy, cada comparacion es un np.bool_: la suma
# de dos np.bool_ es un OR logico, no una suma. El resultado satura en 1 y
# una rama que difiere en LOS DOS bits cuesta 1 en vez de 2. Como esta
# leccion ROTULA en pantalla la distancia Hamming de las ramas (una rama
# que predice 00 contra un par recibido 11 tiene que costar 2), la tabla
# rehace la pasada hacia adelante con enteros de python. La libreria
# decodifica el mismo camino en este caso y se comprueba con un assert.
def _metricas_hamming():
    """Pasada de Viterbi con distancia Hamming de BITS (enteros puros).
    -> metricas[t][s] acumuladas (INF_MET = estado inalcanzable)."""
    met = [[INF_MET] * N_ESTADOS for _ in range(PASOS + 1)]
    met[0][0] = 0
    for t in range(PASOS):
        for s in range(N_ESTADOS):
            if met[t][s] >= INF_MET:
                continue
            for _s, b, s2, (o1, o2) in RAMAS_CONV:
                if _s != s:
                    continue
                c = int(o1 != PARES_RX[t][0]) + int(o2 != PARES_RX[t][1])
                if met[t][s] + c < met[t + 1][s2]:
                    met[t + 1][s2] = met[t][s] + c
    return met


METRICAS = _metricas_hamming()   # metricas[t][s], INF_MET = inalcanzable
METRICA_FINAL = min(METRICAS[PASOS])         # 2 = los dos bits volteados
CORREGIDO = [int(b) for b in conv_codificar(BITS_DEC)[0]]
N_ERR_VITERBI = sum(int(a != b) for a, b in zip(CODIFICADO, CORREGIDO))  # 0
N_DIF_BITS = sum(int(a != b) for a, b in zip(MENSAJE, BITS_DEC))         # 0
VOYAGER_K = 7                    # el codigo que volo a los planetas exteriores
VOYAGER_ESTADOS = 2 ** (VOYAGER_K - 1)       # 64 estados en vez de 4

# El camino ambar del clip 1 (mensaje verdadero) y el verde del clip 4
# (superviviente de Viterbi) tienen que ser el MISMO: se comprueba aqui.
assert CAMINO == list(ESTADOS)
assert BITS_DEC == MENSAJE and N_DIF_BITS == 0 and N_ERR_VITERBI == 0
# el estado mas barato de la ultima columna es el final del camino ganador
assert METRICAS[PASOS][ESTADO_FINAL] == METRICA_FINAL == N_ERR_CANAL

_SALIDA = {(s, b): sal for s, b, _s2, sal in RAMAS_CONV}
_DESTINO = {(s, b): s2 for s, b, s2, _sal in RAMAS_CONV}
_ORDEN_RAMA = {(s, b): k for k, (s, b, _s2, _sal) in enumerate(RAMAS_CONV)}


def vivo(t, s):
    """True si el estado s es alcanzable en la etapa t (metrica finita)."""
    return METRICAS[t][s] < INF_MET


def salida_rama(s, b):
    """Los dos bits que PREDICE la rama (estado s, bit b)."""
    return _SALIDA[(s, b)]


def destino_rama(s, b):
    """El estado al que lleva la rama (s, b): s2 = (b<<1) | (s>>1)."""
    return _DESTINO[(s, b)]


def costo_rama(t, s, b):
    """Distancia Hamming entre lo que predice la rama y el par recibido."""
    o1, o2 = _SALIDA[(s, b)]
    return int((o1 != PARES_RX[t][0]) + (o2 != PARES_RX[t][1]))


def idx_rama(t, s, b):
    """Indice de la rama (t, s, b) dentro de trellis.todas_ramas()."""
    return t * len(RAMAS_CONV) + _ORDEN_RAMA[(s, b)]


def poda(t):
    """Que sobrevive en el tramo t -> t+1. -> {s2: (gana, pierde, total)}
    con gana/pierde = (s, b) y total = la metrica acumulada del ganador.
    El desempate (metrica igual) es el de `viterbi`: gana el estado de
    indice menor, que es el que la libreria visita primero."""
    salida = {}
    for s2 in range(N_ESTADOS):
        cands = sorted((METRICAS[t][s] + costo_rama(t, s, b), s, b)
                       for s, b, ss, _sal in RAMAS_CONV
                       if ss == s2 and vivo(t, s))
        if not cands:
            continue
        salida[s2] = {"gana": (cands[0][1], cands[0][2]),
                      "pierde": [(c[1], c[2]) for c in cands[1:]],
                      "total": int(cands[0][0])}
    return salida


# la poda reconstruida y la tabla de metricas coinciden SIEMPRE
for _t in range(PASOS):
    for _s2, _d in poda(_t).items():
        assert _d["total"] == METRICAS[_t + 1][_s2]


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


def panel_derecha(*mobjetos, buff=0.35):
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
