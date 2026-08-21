# =====================================================================
# CO.DE Academy - "Comunicaciones digitales · 4.3 LDPC: el murmullo que corrige".
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
# mano en el clip: el grafo dibujado y la cifra escrita no pueden
# discrepar. Los calculos caros (Monte Carlo) viven AQUI, a nivel de
# modulo, una sola vez.

# --- el codigo pequeno: H (9 x 12) del sistema triple de Steiner ------
H_LDPC = ldpc_pequeno()                       # 9 checks x 12 bits
N_CHECKS, N_BITS = H_LDPC.shape               # 9, 12
PESO_COL = int(H_LDPC.sum(axis=0)[0])         # 3 checks por bit
PESO_FIL = int(H_LDPC.sum(axis=1)[0])         # 4 bits por check
CHECK_DEMO = 0                                # el check que se ilustra
BITS_CHECK = [int(i) for i in np.nonzero(H_LDPC[CHECK_DEMO])[0]]  # 0,3,6,9
FILAS_H_TXT = [" ".join(str(int(v)) for v in fila) for fila in H_LDPC]

# --- el par de errores garantizado por la validacion de la libreria ---
BITS_ERROR = (0, 2)                           # sindrome 6 -> 3 -> 0
X_LIMPIO = np.zeros(N_BITS, dtype=int)
S_LIMPIO = (H_LDPC @ X_LIMPIO) % 2            # todo par: peso 0
X_ERROR = X_LIMPIO.copy()
X_ERROR[list(BITS_ERROR)] = 1
PASOS_LDPC = ldpc_decodificar(X_ERROR, H_LDPC)   # [(x, s, bit_volteado)]
PESOS_S = [int(s.sum()) for _, s, _ in PASOS_LDPC]        # [6, 3, 0]
VOLTEOS = [v for _, _, v in PASOS_LDPC][1:]               # [0, 2]
S_ERROR = PASOS_LDPC[0][1]                    # el sindrome que acusa
CUENTAS_0 = (H_LDPC.T @ S_ERROR)              # acusaciones por bit
CUENTA_MAX = int(CUENTAS_0.max())             # 3 = todos sus checks
ACUSADOS = [int(i) for i in np.nonzero(CUENTAS_0 == CUENTA_MAX)[0]]

# --- geometria del grafo (misma en los 3 primeros clips) --------------
ANCHO_GRAFO, ALTO_GRAFO = 6.0, 2.3
POS_GRAFO = LEFT * 1.35 + DOWN * 0.15

# --- clip 4: la cascada sin codigo y la pared de Shannon --------------
PUNTOS_Q, BITS_Q = constelacion_qpsk()
SEMILLA_MC, N_MC = 7, 200000
EBN0_MC = [2.0, 4.0, 6.0, 8.0]
_MC = [ber_montecarlo(PUNTOS_Q, BITS_Q, db, N_MC, SEMILLA_MC)
       for db in EBN0_MC]
BER_MC = [m[0] for m in _MC]                  # BER contadas
PARES_MC = list(zip(EBN0_MC, BER_MC))
ERR_4DB, NBITS_4DB = _MC[1][1], _MC[1][2]     # errores y bits a 4 dB
BER_4DB, BER_8DB = BER_MC[1], BER_MC[3]
BER_OBJETIVO = 1e-5                           # un error por cada 100 000


def _ebn0_para_ber(objetivo, lo=-2.0, hi=14.0):
    """El Eb/N0 (dB) al que la QPSK SIN codigo alcanza `objetivo`,
    resuelto por biseccion sobre la BER teorica de la libreria."""
    for _ in range(60):
        med = 0.5 * (lo + hi)
        if float(np.atleast_1d(ber_teorica_qam(4, med))[0]) > objetivo:
            lo = med
        else:
            hi = med
    return 0.5 * (lo + hi)


EBN0_SIN_CODIGO = _ebn0_para_ber(BER_OBJETIVO)   # ~9.6 dB
EBN0_SHANNON = 0.0        # techo de Shannon para tasa 1/2 (curso 21)
BRECHA_DB = EBN0_SIN_CODIGO - EBN0_SHANNON       # el premio del codigo
N_DVBS2 = 64800           # bits del bloque LDPC de DVB-S2
BER_X0, BER_X1 = -2.0, 12.0
POS_BER = LEFT * 2.15 + DOWN * 0.15


def fmt_ber(b):
    """Una BER en notacion cientifica ASCII (fmt no llega a 10^-5)."""
    return f"{float(b):.1e}"


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
