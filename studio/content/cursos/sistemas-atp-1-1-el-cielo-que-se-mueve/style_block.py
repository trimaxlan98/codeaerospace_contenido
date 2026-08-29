# =====================================================================
# CO.DE Academy - "Sistemas ATP · 1.1 El cielo que se mueve". Bloque de
# estilo del proyecto: se antepone al script de CADA clip; los clips NO
# repiten imports, solo definen su ClipN(Scene).
#
# Este archivo es el MOLDE de la familia "Sistemas ATP" (9 lecciones).
# Entre dos lecciones solo cambia la cabecera y el bloque
# "--- Numeros de la leccion ---".
#
# FORMATO MUDO. No hay pie narrativo. La palabra la pone la voz; la
# pantalla pone la cosa y su cifra. Por eso `pie_curso` NO EXISTE aqui y
# los rotulos pasan por `_vigilar()`, que ABORTA el render si alguien
# escribe una frase.
# =====================================================================
import math
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand as _code_brand
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

    Manim 0.20.1 deja el glifo del espacio anclado donde nacio el texto:
    al mover el mobject el bounding box se infla y rompe next_to / Brace /
    SurroundingRectangle. Filtrarlos tras construir lo deja estable.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submobjects = [s for s in self.submobjects if s.has_points()]


_code_brand.Text = Text

import algebra_lineal as _al  # noqa: E402  (tras definir la sombra)
from algebra_lineal import C_EJE as C_EJE_AL  # noqa: E402
from algebra_lineal import fmt, grafica, plano, vector  # noqa: E402

_al.Text = Text

# El sustrato de dibujo del curso 9: la boveda celeste ya estaba hecha.
import apuntado as _ap  # noqa: E402
from apuntado import (antena, aguja_velocidad, cono_keyhole,  # noqa: E402
                      curva_s_doppler, curvas_seguimiento,
                      mascara_elevacion, tarjeta_tle, traza_pase,
                      vista_polar)

_ap.Text = Text

import atp as _atp  # noqa: E402
from atp import (C_CALCULO, C_CIELO, C_DATO, C_EJE, C_OK,  # noqa: E402
                 C_PELIGRO, C_SAT, OBJETIVO_DEG,
                 altitud_de_movimiento_medio, ancho_haz, angulo_central,
                 arco_central_pase, barras_comparar, cadena,
                 campana_montecarlo, comparar_bandas, constante_mecanica,
                 controlabilidad, curva_doppler, doppler_hz,
                 duracion_pase, eb_n0, elevacion_de_angulo_central,
                 elmax_aleatorio, enu_a_azel, error_admisible,
                 error_arrastre, error_por_reloj, fspl_db, ganancia_plato,
                 g_sobre_t, haz, histograma, histograma_datos,
                 incertidumbre_percentil, kd_para_zeta, kp_para_arrastre,
                 lqr, lqr_doble_integrador, margen_fase_con_retardo,
                 margenes, matrices_eje, montura, par_motor,
                 par_necesario, par_viento, percentiles,
                 perdida_apuntamiento, perfil_pase, periodo_orbital,
                 plano_qr, presupuesto_barras, presupuesto_cn0,
                 presupuesto_cuadratura, radio_keyhole, rango_oblicuo,
                 resolucion_encoder, simular_adquisicion, simular_pase,
                 sobreimpulso, tabla_doppler, tasa_acimut, tasa_doppler,
                 t_establecimiento, traza_backlash, traza_error,
                 velocidad_angular_cenit, velocidad_circular,
                 velocidad_radial_max, zeta_wn)

_atp.Text = Text

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
# cian TODA cifra calculada aqui, y la ANTENA (sujeto del curso); ambar
# el satelite, la referencia que hay que seguir y el p95; violeta el
# cielo, los marcos y lo predicho; rojo el keyhole, la saturacion y el
# error fuera de presupuesto; verde el enganche y el enlace que cierra;
# gris el dato publico y el mobiliario.
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
#    "por separado" sale "porseparado" (comprobado en el frame qh de una
#    leccion ya publicada), a 20 queda apretado, a 22 se lee limpio.
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
# Todo valor que se rotule sale de aqui o de atp.py, nunca escrito a
# mano en el clip: lo dibujado y lo escrito no pueden discrepar.
H_LEO = 550.0                          # km, la estacion del curso
H_BAJA = 400.0                         # km, la orbita mas rapida
H_GEO = 35786.0                        # km (dato publico)
MASCARA = 5.0                          # grados

V_LEO = velocidad_circular(H_LEO)                  # 7.589 km/s
W_LEO = velocidad_angular_cenit(H_LEO)             # 0.7906 grados/s
V_BAJA = velocidad_circular(H_BAJA)                # 7.669 km/s
W_BAJA = velocidad_angular_cenit(H_BAJA)           # 1.099 grados/s
T_LEO_MIN = periodo_orbital(H_LEO) / 60.0          # 95.50 min
T_GEO_H = periodo_orbital(H_GEO) / 3600.0          # 23.93 h (dia sidereo)

DUR_PASE_MIN = duracion_pase(H_LEO, 90.0, MASCARA) / 60.0    # 9.82 min
ARCO_PASE = arco_central_pase(H_LEO, 90.0, MASCARA)          # 37.0 grados
PERFIL = perfil_pase(H_LEO, 72.0, MASCARA, az_culminacion_deg=140.0,
                     n=360)

LUNA_DEG = 0.52                        # diametro aparente (dato publico)
LUNAS_POR_SEG = W_LEO / LUNA_DEG       # 1.52 lunas por segundo

TH3_S = ancho_haz(3.0, 2.2e9)          # 3.18 grados
TH3_KA = ancho_haz(3.0, 30.0e9)        # 0.233 grados
ESC_HAZ = TH3_S / 34.0                 # MISMA escala angular en los dos


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
    espacio y Rajdhani no lo hace hasta los 22 px.
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
    se le pase, limpia los rotulos y muestra dos lineas.

    OJO: solo apaga lo que se le PASA. Si el clip dibujo `.ejes` o
    `.curva` de una pieza suelta, hay que pasarlos tambien o sobreviven
    cruzando el cierre.
    """
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
