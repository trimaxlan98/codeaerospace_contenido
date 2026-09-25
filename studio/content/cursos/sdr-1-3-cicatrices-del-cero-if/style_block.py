# =====================================================================
# CO.DE Academy - "SDR · 1.3 Las cicatrices del cero-IF".
# Bloque de estilo del proyecto: se antepone al script de CADA clip; los
# clips NO repiten imports, solo definen su ClipN(Scene).
#
# MOLDE de la familia "SDR" (curso 38, 24 lecciones). Entre dos lecciones
# solo cambian la cabecera y el bloque "--- Numeros de la leccion ---".
# FORMATO MUDO (sin pie narrativo, guardian `_vigilar()`) y SIN
# "Modulo 0N": hud_modulo() ABORTA el render.
#
# Colores por ROL: cian = medido aqui; gris = norma, hoja de datos o
# parametro elegido; ambar = la senal; fucsia = lo que pone el receptor.
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

import sdr as S

# --- Tipografia de marca ---------------------------------------------
registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

_TextBase = Text


class Text(_TextBase):
    """Sombra de Text que descarta los glifos vacios (espacios): el glifo
    del espacio queda anclado donde nacio el texto e infla el bounding box
    (bug de manim 0.20.1)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submobjects = [s for s in self.submobjects if s.has_points()]


_code_brand.Text = Text
S.Text = Text
_RotulosBase = Rotulos


class Rotulos(_RotulosBase):
    """Relevo SECUENCIAL por zona: el rotulo anterior sale ANTES de que
    entre el nuevo."""

    def mostrar(self, mobjeto, zona="abajo", run_time=0.42, salida=0.22,
                **kwargs):
        if self._zonas.get(zona) is not None:
            self.limpiar(zona, run_time=salida)
        return super().mostrar(mobjeto, zona=zona, run_time=run_time,
                               **kwargs)


config.background_color = CODE_BG

# --- Paleta del curso: el color dice el PAPEL -------------------------
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_CALCULO = S.C_CALCULO      # cian: cifra calculada aqui
C_SENAL = S.C_SENAL          # ambar: la senal que se quiere recibir
C_I = S.C_I                  # azul: componente I
C_Q = S.C_Q                  # violeta: componente Q
C_LO = S.C_LO                # fucsia: LO, NCO, reloj, lazo
C_RUIDO = S.C_RUIDO          # rojo: ruido, imagen, espurio
C_OK = S.C_OK                # verde: lo recuperado, lo decodificado
C_DATO = S.C_DATO            # gris: norma, hoja de datos, parametro

MARGEN_PIE = 0.62

# --- EL GUARDIAN DEL FORMATO MUDO -------------------------------------
MAX_TITULO = 6
MAX_CIFRA = 5
MAX_TAG = 4
FS_MIN_DISPLAY = 18
FS_MIN_MULTI = 22            # Rajdhani junta palabras por debajo de 22 px


def _palabras(texto):
    return [p for p in str(texto).split() if any(c.isalnum() for c in p)]


def _vigilar(texto, maximo, quien):
    n = len(_palabras(texto))
    if n > maximo:
        raise ValueError(
            f"FORMATO MUDO: {quien} admite {maximo} palabras y le llegaron "
            f"{n}: {texto!r}. La frase va en la NARRACION, no en pantalla.")
    return texto


def fmt(x, dec=1):
    """Numero con `dec` decimales, sin rstrip (se come ceros de enteros)."""
    return f"{float(x):.{dec}f}"


# --- Numeros de la leccion --------------------------------------------
FS = S.RTL["fs"]
F_TONO = 180e3                                     # tono de prueba (elegido)
EPS, PHI = 0.05, 3.0                               # desbalance (parametros)
XL, XN = S.senal_iq_prueba()                       # limpia / con ruido
P_REF = float(np.mean(np.abs(XN) ** 2))
XDC = S.con_dc(XN, -12.0)
DC_ANTES = S.dc_dbc(XDC, P_REF)                    # -12.0 dBc
XB = S.quitar_dc(XDC, 0.995)
DC_DESP = S.dc_dbc(XB, P_REF, desde=4000)          # -73.8 dBc
YD = S.desbalance_iq(XN, EPS, PHI)
IRR_ANTES = S.irr_db(EPS, PHI)                     # 28.9 dB (= irr_medida)
YC = S.corregir_iq(YD)
IRR_SUELO = S.irr_corregida_minima(EPS, PHI)[0]    # 80 -> "mas de 80 dB"
OFFSET = 250e3                                     # sintonia desplazada


# --- Rotulos ----------------------------------------------------------
def _con_fondo(mobjeto, buff=0.14, opacidad=0.82):
    fondo = BackgroundRectangle(mobjeto, color=CODE_BG, fill_opacity=opacidad,
                                buff=buff)
    return VGroup(fondo, mobjeto)


def titulo_curso(texto, font_size=34, color=None):
    _vigilar(texto, MAX_TITULO, "titulo_curso")
    t = titulo_marca(texto, font_size=font_size,
                     color=C_TITULO if color is None else color)
    if t.width > 7.6:
        t.scale_to_fit_width(7.6)
    t.to_edge(UP, buff=0.52)
    return _con_fondo(t)


def cifra_pie(texto, font_size=26, color=None):
    """El carril de la cifra (zona 'abajo'), Space Mono, SOLO ASCII."""
    _vigilar(texto, MAX_CIFRA, "cifra_pie")
    t = Text(str(texto), font=FUENTE_HUD, font_size=font_size,
             color=C_CALCULO if color is None else color)
    if t.width > config.frame_width - 2.6:
        t.scale_to_fit_width(config.frame_width - 2.6)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(t)


def formula_pie(tex, font_size=36, color=None):
    m = MathTex(tex, font_size=font_size,
                color=C_CALCULO if color is None else color)
    if m.width > config.frame_width - 3.0:
        m.scale_to_fit_width(config.frame_width - 3.0)
    m.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(m)


def dato_pie(texto, font_size=24):
    """Un dato que NO se calculo aqui (norma, hoja de datos): en GRIS."""
    _vigilar(texto, MAX_CIFRA, "dato_pie")
    t = Text(f"{texto}   · dato", font=FUENTE_HUD, font_size=font_size,
             color=C_DATO)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(t)


def hud_modulo(*_a, **_k):
    raise RuntimeError(
        "Curso 38: NO hay etiqueta 'Modulo 0N' en pantalla (pedido del "
        "dueno). Quita la llamada a hud_modulo().")


def tag_junto(mobjeto, texto, direccion=DOWN, buff=0.16, font_size=18,
              color=None):
    _vigilar(texto, MAX_TAG, "tag_junto")
    minimo = FS_MIN_MULTI if len(_palabras(texto)) > 1 else FS_MIN_DISPLAY
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


def tag_dato(texto, font_size=19):
    """Dato de norma / hoja de datos flotante, en GRIS (Space Mono)."""
    _vigilar(texto, MAX_CIFRA, "tag_dato")
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size,
                color=C_DATO)


def panel_cifras(*lineas, buff=0.22, esquina=UR, desplazar=None):
    g = VGroup()
    for ln in lineas:
        texto, color = ln if isinstance(ln, tuple) else (ln, None)
        g.add(tag_hud(texto, font_size=19, color=color))
    g.arrange(DOWN, buff=buff, aligned_edge=RIGHT)
    g.to_corner(esquina, buff=0.55).shift(DOWN * 0.45)
    if desplazar is not None:
        g.shift(desplazar)
    return _con_fondo(g, buff=0.18, opacidad=0.78)


def cierre_leccion(escena, rot, linea_blanca, linea_cian, *apagar,
                   espera=4.4):
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


# --- Dibujo compartido ------------------------------------------------
def mhz(f, dec=1):
    return f"{f / 1e6:.{dec}f}"


def contador_texto(valor, dec=1, color=None, font_size=40):
    return Text(f"{valor:.{dec}f}", font=FUENTE_HUD, font_size=font_size,
                color=C_CALCULO if color is None else color)


class Contador(VGroup):
    """Contador numerico de ancho fijo: numero + rotulo debajo. Reserva el
    ancho de `muestra` (invisible) y crece hacia la IZQUIERDA desde su
    borde derecho. `fijar(v)` (become, FUERA de play) o `anim(escena,
    hasta, run_time)` (ValueTracker + updater)."""

    def __init__(self, valor=0.0, rotulo="", dec=1, muestra="88.8",
                 font_size=44, color=None):
        super().__init__()
        self._fs, self._dec = font_size, dec
        self._color = C_CALCULO if color is None else color
        self.muestra = Text(muestra, font=FUENTE_HUD, font_size=font_size)
        self.muestra.set_opacity(0)
        self.num = contador_texto(valor, dec, self._color, font_size)
        self.num.move_to(self.muestra, aligned_edge=RIGHT)
        self.rot = Text(rotulo, font_size=22, color=C_TENUE)
        self.rot.next_to(self.muestra, DOWN, buff=0.16, aligned_edge=RIGHT)
        self.add(self.muestra, self.num, self.rot)

    def fijar(self, v):
        nuevo = contador_texto(v, self._dec, self._color, self._fs)
        nuevo.move_to(self.muestra, aligned_edge=RIGHT)
        self.num.become(nuevo)

    def anim(self, escena, hasta, run_time=2.0, desde=0.0, rate_func=linear,
             extra=()):
        vt = ValueTracker(desde)
        self.num.add_updater(lambda m: self.fijar(vt.get_value()))
        escena.play(vt.animate.set_value(hasta), *extra, run_time=run_time,
                    rate_func=rate_func)
        self.num.clear_updaters()
        self.fijar(hasta)


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
