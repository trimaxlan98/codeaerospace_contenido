# =====================================================================
# CO.DE Academy - "Comunicaciones digitales · 2.3 El ruido decide: la curva BER".
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
# mano en el clip: la nube DIBUJADA y el error CONTADO salen del mismo
# array, y los puntos Monte Carlo caen sobre la curva teorica porque son
# la misma cuenta. Los calculos caros (ber_montecarlo) viven aqui, a
# nivel de modulo, una sola vez — jamas dentro de un updater.

# La constelacion del modulo 2: QPSK (2 bits/simbolo) y 16-QAM (4).
PQ, BQ = constelacion_qpsk()          # 4 puntos Gray, Es = 1
P16, B16 = constelacion_qam16()       # 16 puntos Gray, Es = 1
K_QPSK, K_QAM16 = int(BQ.shape[1]), int(B16.shape[1])
D_MIN_QPSK = d_min(PQ)                # 1.41 con energia media 1

# --- Las dos nubes que se ven en pantalla (clips 1 y 2) ---------------
ALCANCE_IQ = 1.75                     # el marco del plano_iq
SEM_NUBE = 5                          # semilla FIJA de las dos nubes
N_NUBE = 500                          # tope de plano_iq.nube
EBN0_ALTO, EBN0_BAJO = 12.0, 4.0      # dB de las dos nubes
_IDX = np.tile(np.arange(len(PQ)), N_NUBE // len(PQ))


def _dentro(rx):
    """Los que caen DENTRO del marco: los unicos que plano_iq.nube pinta."""
    return ((np.abs(np.real(rx)) <= ALCANCE_IQ)
            & (np.abs(np.imag(rx)) <= ALCANCE_IQ))


_RX_A = awgn(PQ[_IDX], EBN0_ALTO, K_QPSK, semilla=SEM_NUBE)
_RX_B = awgn(PQ[_IDX], EBN0_BAJO, K_QPSK, semilla=SEM_NUBE)
# se cuenta EXACTAMENTE sobre lo que se dibuja (aqui no cae ninguno fuera)
VISIBLES = _dentro(_RX_A) & _dentro(_RX_B)
RX_ALTO, RX_BAJO, IDX_VIS = _RX_A[VISIBLES], _RX_B[VISIBLES], _IDX[VISIBLES]
N_VIS = int(len(IDX_VIS))                       # 500 simbolos en pantalla
DEC_ALTO = demodular(RX_ALTO, PQ)
DEC_BAJO = demodular(RX_BAJO, PQ)
MAL_ALTO = DEC_ALTO != IDX_VIS                  # ninguno a 12 dB
MAL_BAJO = DEC_BAJO != IDX_VIS                  # los que cruzan a 4 dB
N_MAL_ALTO = int(np.sum(MAL_ALTO))              # 0
N_MAL_BAJO = int(np.sum(MAL_BAJO))              # 14
SER_BAJO = N_MAL_BAJO / N_VIS                   # 2.8e-2 simbolos
BITS_MAL_BAJO = int(np.sum(BQ[IDX_VIS] != BQ[DEC_BAJO]))
N_BITS_VIS = N_VIS * K_QPSK                     # 1000 bits en pantalla
BER_NUBE = BITS_MAL_BAJO / N_BITS_VIS           # 1.4e-2 bits
# las cuatro regiones del demodulador ideal, al borde exacto del marco
CAMPO_QPSK, XS_QPSK = campo_vecino(PQ, -ALCANCE_IQ, ALCANCE_IQ, 88)

# --- La curva BER medida (clips 3 y 4) --------------------------------
SEM_MC = 3                            # semilla FIJA del Monte Carlo
N_MC = 200000                         # 2e5 simbolos por punto (tope)
DB_QPSK = (2.0, 4.0, 6.0, 8.0)
DB_QAM16 = (2.0, 4.0, 6.0, 8.0, 10.0, 12.0)
BER_QPSK = [(db, ber_montecarlo(PQ, BQ, db, N_MC, SEM_MC)[0])
            for db in DB_QPSK]
BER_QAM16 = [(db, ber_montecarlo(P16, B16, db, N_MC, SEM_MC)[0])
             for db in DB_QAM16]
BER_4 = dict(BER_QPSK)[4.0]           # 1.2e-2 medido
BER_8 = dict(BER_QPSK)[8.0]           # 1.9e-4 medido
RAZON_4_8 = BER_4 / BER_8             # ~65 veces menos errores


def _db_para_ber(m, objetivo):
    """El Eb/N0 (dB) al que la M-QAM teorica alcanza `objetivo` de BER."""
    lo, hi = 0.0, 24.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if float(np.atleast_1d(ber_teorica_qam(m, mid))[0]) > objetivo:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


BER_OBJ = 1e-4                        # la tasa a la que se comparan
DB_OBJ_QPSK = _db_para_ber(4, BER_OBJ)     # 8.4 dB
DB_OBJ_QAM16 = _db_para_ber(16, BER_OBJ)   # 12.2 dB
BRECHA_DB = DB_OBJ_QAM16 - DB_OBJ_QPSK     # 3.8 dB de precio


def sci(x, dec=1):
    """Notacion cientifica para MathTex: '1.2 \\cdot 10^{-2}'.
    NUNCA en Text/tag_hud — Rajdhani y Space Mono no traen superindices."""
    x = float(x)
    if x <= 0.0:
        return "0"
    e = int(math.floor(math.log10(x)))
    m = x / 10.0 ** e
    if round(m, dec) >= 10.0:
        m, e = m / 10.0, e + 1
    return r"%s \cdot 10^{%d}" % (fmt(m, dec), e)


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
