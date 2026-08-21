# =====================================================================
# CO.DE Academy - "Comunicaciones digitales · 1.2 El pulso y su eco: ISI y Nyquist".
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
# mano en el clip: el pulso dibujado y la cifra escrita no pueden
# discrepar. Cada pulso se muestrea a SPS puntos por simbolo y vive sobre
# el MISMO eje t (en simbolos), de -SPAN/2 a +SPAN/2: por eso las tres
# formas son gemelas de estructura identica y se pueden Transform.
SPS = 16                      # muestras por simbolo (resolucion del trazo)
SPAN = 6                      # simbolos de soporte de cada pulso
BETA = 0.35                   # roll-off del coseno alzado (el de DVB-S2)
TAU_CANAL = 0.9               # constante del canal de un polo, en simbolos

T_PULSO, H_RECT = pulso_rect(span=SPAN, sps=SPS)          # el ideal
_T_L, H_LENTO = pulso_lento(TAU_CANAL, span=SPAN, sps=SPS)   # el torpe
_T_R, H_RC = pulso_rc(BETA, span=SPAN, sps=SPS)              # el de Nyquist
RANGO_PULSO = (-0.42, 1.30)   # caja comun de los tres pulsos

# Lo que vale cada pulso en SU instante de decision y en el de los vecinos
# (isi_en MIDE la cola sobre el array que se dibuja).
LENTO_K = [isi_en(H_LENTO, SPS, k) for k in range(4)]   # 0.67 0.57 0.19 0.06
RC_K = [isi_en(H_RC, SPS, k) for k in range(4)]         # 1.00 0.00 0.00 0.00
K_CEROS = (-3, -2, -1, 1, 2, 3)     # donde el coseno alzado cruza cero
RC_CEROS = [isi_en(H_RC, SPS, k) for k in K_CEROS]      # todos 0.00

# Los tres simbolos de la leccion (+1, +1, -1) con un hueco a cada lado
# para que se vean los pulsos enteros: deciden en t = 1, 2 y 3.
SIMBOLOS = [0, 1, 1, -1, 0]
BITS_SIMBOLOS = [1, 1, 0]           # los mismos, escritos como bits
K_DECISION = (1, 2, 3)
AMPLITUDES = (1, 1, -1)

T_TREN, Y_LENTO = conformar(SIMBOLOS, H_LENTO, SPS)
_T2, Y_RC = conformar(SIMBOLOS, H_RC, SPS)
DEC_LENTO = [float(Y_LENTO[k * SPS]) for k in K_DECISION]   # .67 1.24 .09
DEC_RC = [float(Y_RC[k * SPS]) for k in K_DECISION]         # 1.00 1.00 -1.00
RANGO_TREN = (-1.55, 1.55)          # caja comun de los dos trenes

# El eco de cada simbolo por separado (mismo eje que el tren): la suma de
# los tres ES Y_LENTO, y lo que cada uno aporta en t = 3 son las cifras
# que se rotulan en el clip 2.
ECOS_LENTO = []
for _k, _a in zip(K_DECISION, AMPLITUDES):
    _s = [0] * len(SIMBOLOS)
    _s[_k] = _a
    ECOS_LENTO.append(conformar(_s, H_LENTO, SPS)[1])
APORTES_EN_3 = [float(_y[3 * SPS]) for _y in ECOS_LENTO]    # .19 .57 -.67

# El diagrama de ojo: 31 simbolos aleatorios de semilla fija conformados
# con el coseno alzado. Con SPS=16 y 31 simbolos la pieza dibuja 28
# trazas y la apertura MEDIDA cubre exactamente los instantes dibujados.
SEMILLA_BITS = 20260821
SEMILLA_RUIDO = 4242
N_SIMBOLOS_OJO = 31
N_TRAZAS = 28
RANGO_OJO = 2.8                     # deja sitio a las trazas con ruido
BITS_OJO = (np.random.default_rng(SEMILLA_BITS)
            .integers(0, 2, N_SIMBOLOS_OJO) * 2 - 1)
T_OJO, Y_OJO = conformar(BITS_OJO, H_RC, SPS)
APERTURA_LIMPIA = apertura_ojo(Y_OJO, SPS)                  # 2.00

SIGMA_1, SIGMA_2 = 0.18, 0.42       # dos niveles del mismo ruido gaussiano
RUIDO_1 = np.random.default_rng(SEMILLA_RUIDO).normal(0, SIGMA_1, len(Y_OJO))
RUIDO_2 = np.random.default_rng(SEMILLA_RUIDO).normal(0, SIGMA_2, len(Y_OJO))
Y_OJO_1 = Y_OJO + RUIDO_1
Y_OJO_2 = Y_OJO + RUIDO_2
APERTURA_1 = apertura_ojo(Y_OJO_1, SPS)                     # 1.42
APERTURA_2 = apertura_ojo(Y_OJO_2, SPS)                     # 0.65


def _snr_db(senal, ruido):
    """SNR MEDIDA entre los dos arrays que se dibujan, en dB."""
    return 10.0 * math.log10(float(np.mean(np.asarray(senal) ** 2)
                                   / np.mean(np.asarray(ruido) ** 2)))


SNR_1 = _snr_db(Y_OJO, RUIDO_1)     # ~14.9 dB
SNR_2 = _snr_db(Y_OJO, RUIDO_2)     # ~7.6 dB


def bordes_ojo(y, sps=SPS):
    """Los dos bordes que MIDE `apertura_ojo`: la traza positiva mas baja
    y la negativa mas alta en el instante de decision. Sirven para dibujar
    la barra de apertura exactamente donde esta la cifra rotulada."""
    v = np.asarray(y, dtype=float)[2 * sps::sps]
    return float(v[v > 0].min()), float(v[v < 0].max())


BORDES_LIMPIO = bordes_ojo(Y_OJO)   # (1.00, -1.00)
BORDES_1 = bordes_ojo(Y_OJO_1)
BORDES_2 = bordes_ojo(Y_OJO_2)


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
