# =====================================================================
# CO.DE Academy - "Procesamiento de señales · 10.2 Tiempo-frecuencia".
# Bloque de estilo del proyecto: se antepone al script de
# CADA clip; los clips NO repiten imports, solo definen su ClipN(Scene).
#
# Este archivo es el MOLDE de la familia "Procesamiento de señales" (30
# lecciones). Entre dos lecciones solo cambia la cabecera y el bloque
# "--- Numeros de la leccion ---".
#
# REGLA NUEVA DE ESTA FAMILIA: FORMATO MUDO. No hay pie narrativo. La
# palabra la pone la voz; la pantalla pone la cosa y su cifra. Por eso
# `pie_curso` NO EXISTE aqui y los rotulos pasan por `_vigilar()`, que
# ABORTA el render si alguien escribe una frase.
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

    Manim 0.20.1 deja el glifo del espacio anclado donde nacio el texto:
    al mover el mobject el bounding box se infla y rompe next_to / Brace /
    SurroundingRectangle. Filtrarlos tras construir lo deja estable.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submobjects = [s for s in self.submobjects if s.has_points()]


_bloques.Text = Text
_code_brand.Text = Text

import algebra_lineal as _al  # noqa: E402  (tras definir la sombra)
from algebra_lineal import (C_EJE, C_REJILLA, fmt, grafica,  # noqa: E402
                            plano, vector)

_al.Text = Text

import comunicaciones as _com  # noqa: E402
from comunicaciones import (Onda, EspectroArea, alias_de,  # noqa: E402
                            cuantizar, espectro_area, muestrear, onda,
                            psd_db, snr_cuantizacion)

_com.Text = Text

import dsp as _dsp  # noqa: E402
from dsp import (Espectrograma, LineaRetardos, Mariposa,  # noqa: E402
                 PlanoZ, a_db, analitica, chirp_y_golpe, convergencia,
                 curva_aprendizaje, dispersion, entrenar_filtro,
                 envolvente, error_coeficientes, escenario_cancelacion,
                 espectrograma, fase_inst, frecuencia_inst,
                 haar_niveles, heisenberg, kalman_escalar, lms,
                 medida_ruidosa, mejora_db, mu_maximo, parecido,
                 periodograma, pll, red_no_lineal, resolucion_welch,
                 rmse, ruido_blanco, stft, tono_con_deriva, welch,
                 Q15_ESCALA, banco_haar, banco_qmf, banda_muerta,
                 caida_cic, cic, ciclo_limite, coste_directo, coste_fft,
                 cruce_fft, diezmar, envuelve, error_farrow, error_q15,
                 error_reconstruccion, farrow, filtrar_punto_fijo,
                 interpolar_ceros, latencia_bloque, macs_diezmado,
                 margen, overlap_add, polifase, q15, remuestrear,
                 respuesta_cic, satura, snr_q15,
                 RespuestaFrec, alternancias, bilineal, es_simetrico,
                 fir_equirriple, fir_ventana, gibbs_db, goertzel,
                 ideal_truncado, iir_butter, iir_cheby1, iir_elip,
                 linea_retardos, macs_fir, macs_goertzel,
                 orden_necesario, peine, polos_butter_analogico,
                 polos_cuantizados, rizado_db, secciones, warp,
                 warp_inverso,
                 bin_de, bit_reverso, dft, dft_matriz, dos_tonos, enbw,
                 es_estable, es_fase_minima, f_de_bin, fft_por_etapas,
                 fuga_db, giro, h_en, lateral_db, lobulo_principal,
                 mariposa_dibujo, mariposas, notch, ops_dft, ops_fft,
                 ortogonales, plano_z, por_distancias, reflejar_ceros,
                 resonador, respuesta_dibujo, respuesta_frec,
                 retardo_grupo, scalloping_db, zpk,
                 C_APREND, C_BANDA, C_CALCULO, C_DATO,
                 C_IDEAL, C_MUESTRA, C_RUIDO, C_SALIDA, C_SENAL,
                 Barras, Deslizador, Escalera, EspectroDoble, Secuencia,
                 ancho_pico, autocorr_circular, banda_ocupada, barras,
                 butter_db, chirp, compresion, con_antialias,
                 convolucion, correlacion, deslizador, dither, droop_db,
                 enterrar, error_rms, escalera, escalones, espectro,
                 espectro_analogico, espectro_doble, espurio_db,
                 filtrar, ganancia_proceso_db, guarda, impulso,
                 macs_convolucion, muestras_de, noise_shaping,
                 pasos_convolucion, pn_larga, reconstruir_sinc,
                 recta_bits, replicas, respuesta_impulso, secuencia,
                 snr_jitter, solape_db, sqnr_en_banda, sqnr_medida,
                 suma_abs, ventana_de, vibracion, zoh)

_dsp.Text = Text

_RotulosBase = Rotulos


class Rotulos(_RotulosBase):
    """Relevo SECUENCIAL por zona: el rotulo anterior sale ANTES de que
    entre el nuevo (el original los cruza y se ven superpuestos)."""

    def mostrar(self, mobjeto, zona="abajo", run_time=0.42, salida=0.22,
                **kwargs):
        if self._zonas.get(zona) is not None:
            self.limpiar(zona, run_time=salida)
        return super().mostrar(mobjeto, zona=zona, run_time=run_time,
                               **kwargs)


config.background_color = CODE_BG

# --- Paleta del curso (el color dice el PAPEL) ------------------------
# azul el mundo continuo; ambar la secuencia y los coeficientes; cian
# TODA cifra calculada aqui; rojo ruido/error/alias; verde la salida;
# violeta el ideal; fucsia lo aprendido; naranja el espectro; gris el
# dato publico y el mobiliario.
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_ACENTO = CODE_ACCENT
C_ACENTO_2 = CODE_ACCENT_2

MARGEN_PIE = 0.62            # separacion del carril de cifra al borde

# --- EL GUARDIAN DEL FORMATO MUDO -------------------------------------
MAX_TITULO = 6               # palabras
MAX_CIFRA = 5                # palabras, contando el numero
MAX_TAG = 4                  # palabras de una etiqueta de mobiliario

# Tamanos minimos de un rotulo en Rajdhani, los dos MEDIDOS en el
# contenedor:
#  - a 16-17 px la fuente redondea los avances y PARTE palabras
#    ("retardada" sale "ret ardada");
#  - por debajo de 22 px se come el espacio ENTRE palabras: a 18 px
#    "por separado" sale "porseparado" (comprobado en el frame qh de la
#    leccion 2.1), a 20 queda apretado, a 22 se lee limpio.
# Space Mono (tag_hud, cifra_pie) no tiene ninguno de los dos problemas a
# ningun tamano de los que usa el curso.
FS_MIN_DISPLAY = 18
FS_MIN_MULTI = 22            # si el rotulo tiene mas de una palabra


def _palabras(texto):
    """Cuenta solo los tokens con algo alfanumerico: '=', '->' y '·' no
    son palabras."""
    return [p for p in str(texto).split()
            if any(c.isalnum() for c in p)]


def _vigilar(texto, maximo, quien):
    """ABORTA el render si un rotulo se convierte en subtitulo.

    Esta familia no lleva pie narrativo (ver cabecera). El limite se
    comprueba aqui y no en la revision visual porque a ojo una frase de
    ocho palabras en Rajdhani 25 parece perfectamente razonable.
    """
    n = len(_palabras(texto))
    if n > maximo:
        raise ValueError(
            f"FORMATO MUDO: {quien} admite {maximo} palabras y le llegaron "
            f"{n}: {texto!r}. La frase va en la NARRACION, no en pantalla.")
    return texto


# --- Numeros de la leccion --------------------------------------------
N_TF = 2048
X_TF = chirp_y_golpe(N_TF)
F_TF, DB_TF = espectro(X_TF, 1.0)          # el espectro ENTERO: el golpe
                                            # se diluye en el
NPER = (64, 256)
STFT = {n: stft(X_TF, n, 0.75) for n in NPER}
T_S = {n: STFT[n][0] for n in NPER}
F_S = {n: STFT[n][1] for n in NPER}
S_DB = {n: STFT[n][2] for n in NPER}
HEIS = {n: heisenberg(n, 1.0) for n in NPER}
DT = {n: HEIS[n][0] for n in NPER}          # 64 y 256 muestras
DF = {n: HEIS[n][1] for n in NPER}          # 0.0156 y 0.0039
PRODUCTO = {n: HEIS[n][2] for n in NPER}    # 1.00 en los dos: SIEMPRE
POS_GOLPE = N_TF * 3 // 5                   # donde esta el golpe
T_GOLPE = POS_GOLPE / 1.0

DETALLES, APROX = haar_niveles(X_TF, 3)
LARGOS_DET = [len(d) for d in DETALLES]     # [1024, 512, 256]
ENERGIA_DET = [float(np.sum(d ** 2)) for d in DETALLES]  # 179.6/181.3/92.6


# --- Rotulos ----------------------------------------------------------
def _con_fondo(mobjeto, buff=0.14, opacidad=0.82):
    """Rectangulo del color del fondo detras de un rotulo: se lee limpio
    aunque haya piezas debajo."""
    fondo = BackgroundRectangle(mobjeto, color=CODE_BG,
                                fill_opacity=opacidad, buff=buff)
    return VGroup(fondo, mobjeto)


def titulo_curso(texto, font_size=34, color=None):
    """Titulo de clip (Rajdhani) anclado arriba. Zona 'arriba'."""
    _vigilar(texto, MAX_TITULO, "titulo_curso")
    t = titulo_marca(texto, font_size=font_size,
                     color=C_TITULO if color is None else color)
    if t.width > 7.6:
        t.scale_to_fit_width(7.6)
    t.to_edge(UP, buff=0.52)
    return _con_fondo(t)


def cifra_pie(texto, font_size=26, color=None):
    """EL CARRIL DE LA CIFRA (zona 'abajo'): una medicion con su etiqueta
    corta, en Space Mono. Es lo unico que ocupa el pie en esta familia.
    Solo ASCII: Space Mono no trae acentos, griegas ni superindices."""
    _vigilar(texto, MAX_CIFRA, "cifra_pie")
    t = Text(str(texto), font=FUENTE_HUD, font_size=font_size,
             color=C_CALCULO if color is None else color)
    if t.width > config.frame_width - 2.6:
        t.scale_to_fit_width(config.frame_width - 2.6)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(t)


def formula_pie(tex, font_size=36, color=None):
    """MathTex corto en la MISMA zona que la cifra (nunca se suman).
    Aqui viven las griegas, los superindices y el ≈."""
    m = MathTex(tex, font_size=font_size,
                color=C_CALCULO if color is None else color)
    if m.width > config.frame_width - 3.0:
        m.scale_to_fit_width(config.frame_width - 3.0)
    m.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(m)


def dato_pie(texto, font_size=24):
    """Un dato que NO se calculo aqui (literatura, hoja de datos): va en
    GRIS, para que el cian siga significando 'medido en pantalla'."""
    _vigilar(texto, MAX_CIFRA, "dato_pie")
    t = Text(f"{texto}   · dato", font=FUENTE_HUD, font_size=font_size,
             color=C_DATO)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(t)


def hud_modulo(texto):
    """Etiqueta de telemetria del modulo, esquina superior izquierda."""
    t = etiqueta_hud(texto)
    t.to_corner(UL, buff=0.5)
    return t


def tag_junto(mobjeto, texto, direccion=DOWN, buff=0.16, font_size=18,
              color=None):
    """Etiqueta de mobiliario pegada a un mobject (no narrativa).

    El tamano se sube a FS_MIN_DISPLAY si hace falta (ver arriba por que).
    Para etiquetas de DOS palabras, mejor `tag_hud`: Space Mono respeta el
    espacio y Rajdhani no lo hace hasta los 24 px.
    """
    _vigilar(texto, MAX_TAG, "tag_junto")
    minimo = (FS_MIN_MULTI if len(_palabras(texto)) > 1
              else FS_MIN_DISPLAY)
    t = Text(str(texto), font_size=max(font_size, minimo),
             color=C_TENUE if color is None else color)
    t.set_opacity(0.9)
    t.next_to(mobjeto, direccion, buff=buff)
    return t


def tag_hud(texto, font_size=19, color=None):
    """Cifra tecnica flotante en Space Mono (SOLO ASCII)."""
    _vigilar(texto, MAX_CIFRA, "tag_hud")
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size,
                color=C_CALCULO if color is None else color)


def panel_cifras(*lineas, buff=0.22, esquina=UR, desplazar=None):
    """Columna de cifras medidas arriba a la derecha, con fondo. Cada
    linea es (texto, color) o solo texto."""
    g = VGroup()
    for ln in lineas:
        texto, color = ln if isinstance(ln, tuple) else (ln, None)
        g.add(tag_hud(texto, font_size=19, color=color))
    g.arrange(DOWN, buff=buff, aligned_edge=RIGHT)
    g.to_corner(esquina, buff=0.55).shift(DOWN * 0.45)
    if desplazar is not None:
        g.shift(desplazar)
    return _con_fondo(g, buff=0.18, opacidad=0.78)


def llave(mobjeto, texto=None, direccion=UP, font_size=22, color=None,
          buff=0.12):
    """Brace opcionalmente etiquetado (etiquetas de 1-3 palabras)."""
    col = C_CALCULO if color is None else color
    b = Brace(mobjeto, direction=direccion, color=col)
    if texto is None:
        return VGroup(b)
    _vigilar(texto, MAX_TAG, "llave")
    minimo = (FS_MIN_MULTI if len(_palabras(texto)) > 1
              else FS_MIN_DISPLAY)
    t = Text(str(texto), font_size=max(font_size, minimo), color=col)
    t.next_to(b, direccion, buff=buff)
    return VGroup(b, t)


def cierre_leccion(escena, rot, linea_blanca, linea_cian, *apagar,
                   espera=4.4):
    """El cierre a pantalla limpia de la leccion (clip 4): apaga lo que
    se le pase, limpia los rotulos y muestra dos lineas."""
    if apagar:
        escena.play(*[FadeOut(m) for m in apagar], run_time=0.8)
    rot.limpiar(run_time=0.4)
    l1 = Text(linea_blanca, font_size=40, color=C_TITULO)
    l2 = Text(linea_cian, font_size=40, color=C_CALCULO)
    l1.move_to(UP * 0.42)
    l2.move_to(DOWN * 0.42)
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
