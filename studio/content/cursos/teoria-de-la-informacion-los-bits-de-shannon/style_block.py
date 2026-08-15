# =====================================================================
# CO.DE Academy - "Teoria de la informacion: los bits de Shannon"
# Bloque de estilo del proyecto. Se antepone al script de CADA clip; los
# clips NO repiten imports: solo definen su clase ClipN(Scene).
# =====================================================================
import math
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand as _code_brand
from code_brand import (CODE_ACCENT, CODE_ACCENT_2, CODE_BG, CODE_INK,
                        CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD, Rotulos,
                        esquinas_hud, etiqueta_hud, marca_agua,
                        registrar_fuentes, titulo_marca)

# --- Tipografia de marca ---------------------------------------------
registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

_TextBase = Text


class Text(_TextBase):
    """Sombra de Text que descarta los glifos vacios (espacios).

    Manim 0.20.1 deja el glifo del espacio anclado donde nacio el texto:
    al mover el mobject, el bounding box se infla y rompe next_to / Brace.
    Filtrarlos tras construir lo deja estable.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submobjects = [s for s in self.submobjects if s.has_points()]


_code_brand.Text = Text

import informacion as _informacion  # noqa: E402  (tras definir la sombra)
from informacion import (ALFABETO, ALTO_IMG, ANCHO_IMG,  # noqa: E402
                         B_TRANSPONDEDOR_HZ, CN_DB_1, CN_DB_2,
                         DATOS_HAMMING, ESPACIO, FRASE_REDUNDANTE, HITOS,
                         MENSAJE_HUFFMAN, MODCODS_DVBS2, N_BITS_CANAL,
                         N_BLOQUES, N_PREGUNTAS, NIVELES_JPG, P_BSC,
                         P_CODIGOS, P_MONEDA_TRUCADA, POS_ERROR_HAMMING,
                         REDUNDANCIA_SHANNON_1951, SEMILLA_CANAL,
                         SEMILLA_CODIGOS, SIMBOLOS, TASA_HAMMING,
                         TASA_REP3, TEXTO_ES, arbol_huffman,
                         arbol_preguntas, ber_bpsk, bits_codificados,
                         bits_fijos, bits_imagen, bits_para, bits_rle,
                         caja_numero, capacidad_bsc, capacidad_shannon,
                         cn0_desde_cn, codificar, cuantizar,
                         curva_capacidad_bsc, curva_entropia_binaria,
                         curva_shannon_hartley, curva_sorpresa,
                         db_a_lineal, ebn0_minimo_db, eficiencia_espectral,
                         entropia, entropia_binaria, entropia_texto,
                         esquema_bsc, flujo, frecuencias,
                         hamming_codificar, hamming_corregir,
                         hamming_decodificar, hamming_sindrome,
                         histograma_simbolos, huffman, icono_bits,
                         icono_fuente, imagen_bits, imagen_esfera,
                         imagen_gris, informacion_mutua_bsc, lineal_a_db,
                         linea_tiempo, longitud_media, normalizar,
                         paridades, pasos_huffman, plano_shannon,
                         preguntas_para, redundancia, repeticion_codificar,
                         repeticion_decodificar, rle, simular_bsc,
                         simular_codigos, sin_vocales, snr_para_eficiencia,
                         sorpresa, tira_bits, tira_codigo, venn_hamming,
                         voltear)

_informacion.Text = Text

_RotulosBase = Rotulos


class Rotulos(_RotulosBase):
    """Relevo SECUENCIAL por zona: el rotulo anterior sale ANTES de que
    entre el nuevo (el original los cruza ~0.5 s)."""

    def mostrar(self, mobjeto, zona="abajo", run_time=0.45, salida=0.25,
                **kwargs):
        if self._zonas.get(zona) is not None:
            self.limpiar(zona, run_time=salida)
        return super().mostrar(mobjeto, zona=zona, run_time=run_time,
                               **kwargs)

config.background_color = CODE_BG

# --- Paleta del curso -------------------------------------------------
# Regla: el BIT (la informacion, la sorpresa, lo que se mide) es ambar;
# la FUENTE (simbolos, probabilidades, el mensaje) cian; los CODIGOS
# (compresion, correccion, lo que funciona) verde; el RUIDO (bits
# volteados, perdida, error) rojo; la ENTROPIA, la capacidad y el techo
# de Shannon violeta.
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_ACENTO = CODE_ACCENT
C_ACENTO_2 = CODE_ACCENT_2
C_BIT = "#f59e0b"            # ambar: el bit, la informacion, la sorpresa
C_FUENTE = "#22d3ee"         # cian: la fuente, los simbolos, el mensaje
C_CODIGO = "#34d399"         # verde: codigos, compresion, correccion
C_RUIDO = "#f43f5e"          # rojo: ruido, bits volteados, perdida, error
C_LIMITE = "#a78bfa"         # violeta: entropia, capacidad, techo de Shannon
C_EJE = "#31414f"            # gris azulado de mobiliario

MARGEN_PIE = 0.68

# --- Numeros del curso ------------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria (calculado o
# medido sobre los datos), nunca escrito a mano en el clip.
BITS_MONEDA = sorpresa(0.5)                              # 1.0
BITS_DADO = bits_para(6)                                 # 2.585
BITS_BARAJA = bits_para(52)                              # 5.700
BITS_CARA_TRUCADA = sorpresa(P_MONEDA_TRUCADA)           # 0.152
BITS_CRUZ_TRUCADA = sorpresa(1 - P_MONEDA_TRUCADA)       # 3.322
N_OBJETOS_20 = 2 ** N_PREGUNTAS                          # 1 048 576
H_MONEDA_TRUCADA = entropia_binaria(P_MONEDA_TRUCADA)    # 0.469
H_UNIFORME_27 = bits_para(len(SIMBOLOS))                 # 4.755
FREC_ES = frecuencias(TEXTO_ES)                          # medidas (27 claves)
H_ES = entropia_texto(TEXTO_ES)                          # ~4.1 (medida)
SIMBOLO_TOP = max(FREC_ES, key=FREC_ES.get)              # " " (espacio)
LETRA_TOP = max((s for s in FREC_ES if s != ESPACIO), key=FREC_ES.get)
REDUNDANCIA_ES = redundancia(H_ES, len(SIMBOLOS))        # ~0.13 (medida)
FREC_HUFFMAN = frecuencias(MENSAJE_HUFFMAN)              # A5 B2 R2 C1 D1 (fracciones)
FREC_HUFFMAN = {s: f for s, f in FREC_HUFFMAN.items() if f > 0}
CODIGO_HUFFMAN = huffman(FREC_HUFFMAN)                   # A=0, R=10, B=110, ...
H_HUFFMAN = entropia(FREC_HUFFMAN)                       # 2.040
L_HUFFMAN = longitud_media(CODIGO_HUFFMAN, FREC_HUFFMAN)  # 2.091
BITS_HUFFMAN = bits_codificados(MENSAJE_HUFFMAN, CODIGO_HUFFMAN)  # 23
BITS_FIJOS_HUFFMAN = len(MENSAJE_HUFFMAN) * bits_fijos(len(FREC_HUFFMAN))  # 33
CODIGO_ES = huffman(FREC_ES)
L_ES = longitud_media(CODIGO_ES, FREC_ES)                # ~4.15 (medida)
BITS_FIJOS_27 = bits_fijos(len(SIMBOLOS))                # 5
N_SIMBOLOS_TEXTO = len(normalizar(TEXTO_ES))
BITS_TEXTO_ASCII = 8 * N_SIMBOLOS_TEXTO
BITS_TEXTO_FIJOS = BITS_FIJOS_27 * N_SIMBOLOS_TEXTO
BITS_TEXTO_HUFFMAN = bits_codificados(TEXTO_ES, CODIGO_ES)
FRASE_SIN_VOCALES = sin_vocales(FRASE_REDUNDANTE)        # "L NFRMCN S MD"
ICONO = icono_bits(ANCHO_IMG, ALTO_IMG)                  # planeta con anillo 0/1
BITS_ICONO = int(ICONO.size)                             # 384
BITS_ICONO_RLE = bits_rle(ICONO.flatten())               # medido (< 192)
ESFERA = imagen_esfera(ANCHO_IMG, ALTO_IMG)              # 0..255
ESFERA_JPG = cuantizar(ESFERA, NIVELES_JPG)              # 4 niveles
BITS_ESFERA_8 = bits_imagen(ESFERA, 8)                   # 3072
BITS_ESFERA_2 = bits_imagen(ESFERA_JPG, 2)               # 768
_rng_canal = np.random.default_rng(SEMILLA_CANAL)
BITS_ENVIADOS = _rng_canal.integers(0, 2, N_BITS_CANAL)  # 64 bits (semilla)
BITS_RECIBIDOS, N_VOLTEADOS = simular_bsc(BITS_ENVIADOS, P_BSC, SEMILLA_CANAL)  # 5 volteados
C_BSC_01 = capacidad_bsc(P_BSC)                          # 0.531
C_BSC_001 = capacidad_bsc(0.01)                          # 0.919
C_BSC_05 = capacidad_bsc(0.5)                            # 0.0
C_ENLACE_1 = capacidad_shannon(B_TRANSPONDEDOR_HZ, db_a_lineal(CN_DB_1))  # 124.5e6
C_ENLACE_2 = capacidad_shannon(B_TRANSPONDEDOR_HZ, db_a_lineal(CN_DB_2))  # 239.7e6
ETA_10 = eficiencia_espectral(CN_DB_1)                   # 3.46
ETA_13 = eficiencia_espectral(CN_DB_1 + 3)               # 4.39
EBN0_MIN = ebn0_minimo_db()                              # -1.59
CN0_ENLACE_1 = cn0_desde_cn(CN_DB_1, B_TRANSPONDEDOR_HZ)  # 85.6 dBHz
PALABRA_HAMMING = hamming_codificar(DATOS_HAMMING)       # 7 bits
PALABRA_CON_ERROR = voltear(PALABRA_HAMMING, POS_ERROR_HAMMING)
SINDROME = hamming_sindrome(PALABRA_CON_ERROR)           # 5
PALABRA_CORREGIDA, POS_CORREGIDA = hamming_corregir(PALABRA_CON_ERROR)
BER = simular_codigos(P_CODIGOS, N_BLOQUES, SEMILLA_CODIGOS)  # {"sin","rep3","hamming"}
GAPS_DVBS2 = [(nombre, eta, db, db - snr_para_eficiencia(eta))
              for nombre, eta, db in MODCODS_DVBS2]      # distancia al techo (dB)


# --- Rotulos ----------------------------------------------------------
def titulo_curso(texto, font_size=34, color=None):
    t = titulo_marca(texto, font_size=font_size,
                     color=C_TITULO if color is None else color)
    if t.width > config.frame_width - 2.0:
        t.scale_to_fit_width(config.frame_width - 2.0)
    t.to_edge(UP, buff=0.52)
    return t


def pie_curso(texto, font_size=25, color=None):
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    if t.width > config.frame_width - 2.6:
        t.scale_to_fit_width(config.frame_width - 2.6)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return t


def formula_pie(tex, font_size=34, color=None):
    m = MathTex(tex, font_size=font_size,
                color=C_ACENTO if color is None else color)
    if m.width > config.frame_width - 3.0:
        m.scale_to_fit_width(config.frame_width - 3.0)
    m.to_edge(DOWN, buff=MARGEN_PIE)
    return m


def hud_modulo(texto):
    t = etiqueta_hud(texto)
    t.to_corner(UL, buff=0.5)
    return t


def tag_junto(mobjeto, texto, direccion=DOWN, buff=0.16, font_size=18,
              color=None):
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    t.set_opacity(0.85)
    t.next_to(mobjeto, direccion, buff=buff)
    return t


def tag_hud(texto, font_size=15, color=None):
    """Cifra medida (Space Mono, ASCII puro) SIN posicion: el clip la
    coloca."""
    t = Text(texto, font=FUENTE_HUD, font_size=font_size,
             color=C_FUENTE if color is None else color)
    return t


def miles(n):
    """1048576 -> '1 048 576' (espacio fino como separador)."""
    return f"{int(round(n)):,}".replace(",", " ")


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
