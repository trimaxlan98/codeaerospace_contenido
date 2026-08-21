# =====================================================================
# CO.DE Academy - "Comunicaciones digitales · 6.3 El enlace cognitivo".
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
# mano en el clip: la curva dibujada y la cifra rotulada salen del MISMO
# array. El Q-learning (~1 s) vive AQUI, a nivel de modulo: se ejecuta
# UNA vez por render y jamas dentro de un updater.
EPISODIOS = 400
SEMILLA = 6
PASOS_EP = 40                    # decisiones por episodio (defecto de la lib)
BD = bandido_acm(EPISODIOS, semilla=SEMILLA)   # Q-learning tabular, UNA vez

# -- clip 2: la curva de aprendizaje ------------------------------------
REC = BD["recompensa_episodio"]                # bits-simbolo por episodio
EP = np.arange(len(REC), dtype=float)
VENTANA_MM = 20                                # media movil DECLARADA en el pie
MM = np.convolve(REC, np.ones(VENTANA_MM) / VENTANA_MM, mode="valid")
EP_MM = np.arange(len(MM), dtype=float) + (VENTANA_MM - 1) / 2.0
Q5 = len(REC) // 5                             # un quinto = 80 episodios
REC_INI = float(REC[:Q5].mean())               # 67.5 : el agente torpe
REC_FIN = float(REC[-Q5:].mean())              # 93.6 : el agente hecho
SUBIDA_PCT = 100.0 * (REC_FIN / REC_INI - 1.0)      # +38.6 %
REC_Y0, REC_Y1 = 20.0, 145.0                   # rango vertical del eje

# epsilon-greedy: los parametros por defecto de `bandido_acm` (epsilon0,
# el piso 0.05 y el 0.7 del decaimiento). Se rotulan como porcentaje.
EPS0, EPS_PISO, FRAC_DECAY = 0.9, 0.05, 0.7
EPS_INI_PCT = 100.0 * EPS0                     # 90 % al azar al empezar
EPS_FIN_PCT = 100.0 * EPS0 * EPS_PISO          # 4.5 % al final
EP_CONGELA = FRAC_DECAY * EPISODIOS            # episodio 280: epsilon al piso

# -- clip 3: el agente contra las reglas fijas ---------------------------
ACUM_A = BD["acumulada_agente"]
ACUM_C = BD["acumulada_conservador"]
ACUM_O = BD["acumulada_optimista"]
N_DEC = len(ACUM_A)                            # 16000 decisiones
PASOS = np.arange(1, N_DEC + 1, dtype=float)
_SALTO = 8                                     # resolucion del trazo (el
_IDX = np.unique(np.append(np.arange(0, N_DEC, _SALTO), N_DEC - 1))
PASOS_DIB = PASOS[_IDX]                        #  ultimo punto SIEMPRE dentro:
ACUM_A_DIB = ACUM_A[_IDX]                      #  el extremo dibujado ES la
ACUM_C_DIB = ACUM_C[_IDX]                      #  cifra rotulada)
ACUM_O_DIB = ACUM_O[_IDX]
FIN_A = float(ACUM_A[-1])                      # 33541
FIN_C = float(ACUM_C[-1])                      # 14422
FIN_O = float(ACUM_O[-1])                      # 30446
FACTOR_CONS = FIN_A / FIN_C                    # x2.3 sobre el conservador
GANA_OPT_PCT = 100.0 * (FIN_A / FIN_O - 1.0)   # +10.2 % sobre el optimista
ACUM_Y1 = 36000.0                              # techo visual del eje

# -- la mesa de juego: estados, acciones y recompensa ---------------------
POLITICA = BD["politica"]                      # [2 1 0] : la tabla sensata
ESTADOS = ("cielo claro", "nubes", "lluvia")
# el color dice el papel: azul el canal sano, gris la nube que lo enturbia,
# rojo el canal roto. (Un degradado azul->rojo daba un magenta que se
# confundia con el violeta del modcod mas denso.)
C_ESTADO = [C_SENAL, C_TENUE, C_RUIDO]
MODCOD_NOMBRES = [m[0] for m in MODCODS]
MODCOD_UMBRALES = [m[1] for m in MODCODS]      # 1.0 / 7.9 / 11.0 dB
MODCOD_TASAS = [m[2] for m in MODCODS]         # 1.00 / 2.25 / 3.33 bits/simb
MODCOD_COLORES = [C_BIT, C_COD, C_TECHO]       # como en la leccion 5.2

# El entorno de `bandido_acm`: SNR de cielo despejado y atenuacion MEDIA de
# cada estado (las constantes ATT del entorno, que la libreria no exporta).
SNR_CLARO = 13.0
ATT_ESTADO = np.array([0.0, 4.0, 12.0])
SNR_ESTADO = SNR_CLARO - ATT_ESTADO            # 13.0 / 9.0 / 1.0 dB
# recompensa = los bits que LLEGAN: la tasa del modcod si cierra, 0 si no.
RECOMPENSA = np.array(
    [[MODCOD_TASAS[a] if SNR_ESTADO[s] >= MODCOD_UMBRALES[a] else 0.0
      for a in range(len(MODCODS))] for s in range(len(ESTADOS))])
MEJOR_ACCION = [int(np.argmax(RECOMPENSA[s])) for s in range(len(ESTADOS))]

# -- clip 4: la mision completa ------------------------------------------
MODULOS = ("M1 - muestreo", "M2 - constelacion", "M3 - el vacio",
           "M4 - el codigo", "M5 - ACM", "M6 - el agente")
BITS_MISION = [1, 0, 1, 1, 0, 1]               # la palabra que cruza
MODCOD_MISION = MODCOD_NOMBRES[int(POLITICA[0])]   # lo que eligio el agente
TASA_MISION = MODCOD_TASAS[int(POLITICA[0])]       # 3.33 bits/simbolo
P_QPSK, _B_QPSK = constelacion_qpsk()          # el icono del modulo 2
# camino LEGAL del trellis K=3 para el icono del modulo 4: se siguen las
# transiciones reales de la libreria (RAMAS_CONV) con los bits de la mision.
_TRANS_CONV = {(s, b): s2 for s, b, s2, _sal in RAMAS_CONV}
CAMINO_TRELLIS = [0]
for _b in BITS_MISION[:4]:
    CAMINO_TRELLIS.append(_TRANS_CONV[(CAMINO_TRELLIS[-1], int(_b))])


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
