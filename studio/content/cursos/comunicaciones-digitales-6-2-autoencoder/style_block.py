# =====================================================================
# CO.DE Academy - "Comunicaciones digitales · 6.2 La constelación inventada".
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
# mano en el clip: la constelacion dibujada y la cifra escrita salen del
# MISMO array. Los calculos caros (autoencoder, Monte Carlo) viven aqui,
# a nivel de modulo, una sola vez — jamas dentro de un updater.
M_AE = 8                       # simbolos de la constelacion aprendida
BITS_SIMBOLO = 3               # log2(8): tres bits por simbolo
PASOS_AE = 250                 # pasos de gradiente del entrenamiento
SEMILLA_AE = 3
SIGMA_AE = 0.20                # el ruido que la red supone al entrenar

# El entrenamiento MEDIDO: historial [(paso, puntos)] cada 10 pasos y la
# distancia minima por paso.
AE = autoencoder_constelacion(M_AE, PASOS_AE, sigma=SIGMA_AE,
                              semilla=SEMILLA_AE)
HIST_AE = dict(AE["historial"])           # paso -> puntos complejos
DMIN_AE = AE["d_min"]                     # [(paso, d)]
PASOS_DMIN = np.array([p for p, _ in DMIN_AE], dtype=float)
SERIE_DMIN = np.array([d for _, d in DMIN_AE], dtype=float)
IDX_PASO = {int(p): i for i, (p, _) in enumerate(DMIN_AE)}
EPOCAS = (0, 10, 30, 60, 120, 250)        # las que se animan en el clip 2

Z_INI = HIST_AE[EPOCAS[0]]                # el amasijo inicial
Z_FIN = HIST_AE[PASOS_AE]                 # la constelacion aprendida
D_INI = d_min(Z_INI)                      # 0.151
D_FIN = d_min(Z_FIN)                      # 0.926
E_AE = energia_media(Z_FIN)               # 1.000 (la atadura del entreno)
E_INI = energia_media(Z_INI)              # 1.000 tambien al empezar

# La referencia clasica: 8-PSK Gray, misma energia media.
P_PSK8, B_PSK8 = constelacion_psk8()
D_PSK8 = d_min(P_PSK8)                    # 0.765
E_PSK8 = energia_media(P_PSK8)            # 1.000

# Error de SIMBOLO CONTADO en el mismo canal (mismo n, misma semilla).
EBN0_SER = 10.0
N_SER = 100000
SEMILLA_SER = 4
EBN0_BARRIDO = (4.0, 6.0, 8.0, 10.0)      # los cuatro puntos de la curva
SER_AE_BARR = [(db, ser_montecarlo(Z_FIN, db, BITS_SIMBOLO, n=N_SER,
                                   semilla=SEMILLA_SER))
               for db in EBN0_BARRIDO]
SER_PSK8_BARR = [(db, ser_montecarlo(P_PSK8, db, BITS_SIMBOLO, n=N_SER,
                                     semilla=SEMILLA_SER))
                 for db in EBN0_BARRIDO]
PARES_AE = [(db, r[0]) for db, r in SER_AE_BARR]
PARES_PSK8 = [(db, r[0]) for db, r in SER_PSK8_BARR]
SER_AE, ERR_AE, _ = dict(SER_AE_BARR)[EBN0_SER]        # 0.00027 / 27
SER_PSK8, ERR_PSK8, _ = dict(SER_PSK8_BARR)[EBN0_SER]  # 0.00299 / 299
RAZON_SER = SER_PSK8 / SER_AE             # 11.1 veces menos errores


def par_mas_cercano(puntos):
    """Los DOS indices que realizan la distancia minima del set (el
    segmento que `d_min` mide). -> (i, j)"""
    p = np.asarray(puntos)
    d = np.abs(p[:, None] - p[None, :])
    np.fill_diagonal(d, np.inf)
    i, j = np.unravel_index(int(np.argmin(d)), d.shape)
    return int(i), int(j)


PAR_AE = par_mas_cercano(Z_FIN)
PAR_PSK8 = par_mas_cercano(P_PSK8)


def poli_ber(cb, pares, color, grosor=2.4):
    """Poligonal que une puntos medidos (db, ser) sobre una `curva_ber`."""
    c = VMobject(color=color, stroke_width=grosor)
    c.set_points_as_corners([cb.en(db, s) for db, s in pares])
    return c


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
