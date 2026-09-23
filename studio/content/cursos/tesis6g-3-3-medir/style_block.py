# =====================================================================
# CO.DE Academy - "Tesis 6G · 3.3 Medir sin engañarse". Bloque de estilo
# del proyecto: se antepone al script de CADA clip; los clips NO repiten
# imports, solo definen su ClipN(Scene).
#
# MOLDE de la familia "Tesis 6G por dentro" (curso 36, 12 lecciones).
# Entre dos lecciones solo cambian la cabecera y el bloque
# "--- Numeros de la leccion ---". Hereda la mecanica del molde del curso
# 27 (procesamiento-senales-1-1): FORMATO MUDO, sin pie narrativo, con un
# guardian `_vigilar()` que ABORTA el render si un rotulo se vuelve frase.
#
# Las cifras de la TESIS (G1, G2b, R5...) se leen de los JSON copiados por
# studio/tools/traer_datos_tesis.py (repo privado, no se versionan): un
# clip que las use solo renderiza en la maquina de desarrollo.
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

import ntn
import satelites as sat
import tesis6g as T6

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
# Los mismos papeles que las piezas limpias de la tesis (tesis6g.Paleta),
# en la paleta de la marca. Cian = TODA cifra calculada aqui; gris = dato.
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_CALCULO = "#22d3ee"    # cian: cifra calculada aqui
C_DATO = "#94a0b0"       # gris: dato publicado o de la tesis, NO medido aqui
C_ESTATICA = "#c8ccd1"   # la gestion estatica (best_static)
C_ADAPTA = CODE_ACCENT   # ambar: lo adaptativo / aprendido / el satelite
C_PRIV = "#a78bfa"       # violeta: la informacion privilegiada, el oraculo
C_OK = "#34d399"         # verde: aprobado, enlace vivo
C_NO = "#f43f5e"         # rojo: invalidado, sin enlace
C_TIERRA = "#16233a"     # relleno de la Tierra
C_ENLACE = "#3b82f6"     # azul: el enlace radio

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
H_KM = 600.0
R_T = ntn.R_TIERRA_KM
EL_MIN = ntn.ELEVACION_MINIMA_DEG
LAMBDA = np.degrees(np.arccos(R_T * np.cos(np.radians(EL_MIN))
                              / (R_T + H_KM))) - EL_MIN
D = T6.datos_tesis()
E = T6.entorno_v2()
K2 = T6.oraculo_k2()
# Dos ramas desde el MISMO estado (TEOREMA_MARGEN_ADAPTATIVO §4, semilla 42):
# interferencia tras [0,0,0] (colision) y tras [0,1,2]. Son cifras de la
# tesis (dato); la huella que sigue la calcula la regla I <- 0.7 I.
RAMA_CHOQUE = np.array([1.0000, 0.8275, 0.4442])
RAMA_LIBRE = np.array([1.0000, 0.0775, 0.0942])
DELTA0 = float(np.max(np.abs(RAMA_CHOQUE - RAMA_LIBRE)))            # 0.75
HUELLA = DELTA0 * E["decaimiento"] ** np.arange(12)
_rng = np.random.default_rng(3)
VERDAD = np.sort(100 + _rng.normal(0, 4.0, 27))                     # 27 estaticas (juguete)
SIGMA = 10.0
M1 = T6.muestras_ganador(VERDAD, SIGMA, 1, 63)                      # semilla del sesgo medio
M30 = T6.muestras_ganador(VERDAD, SIGMA, 30, 102)
SENS = sorted(D["sensibilidad"])
ORC = {g["semilla"]: g["oraculo"] for g in D["g2b"]}
MOCK = D["piloto_mock"]
TOPE_R5 = 1.05


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
    """Un dato que NO se calculo aqui: en GRIS."""
    _vigilar(texto, MAX_CIFRA, "dato_pie")
    t = Text(f"{texto}   · dato", font=FUENTE_HUD, font_size=font_size,
             color=C_DATO)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(t)


def hud_modulo(texto):
    t = etiqueta_hud(texto)
    t.to_corner(UL, buff=0.5)
    return t


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


# --- Dibujo compartido de la leccion ---------------------------------
def vista_pase(y_sup=-2.2, r_s=13.4):
    """La Tierra y la orbita LEO-600 A ESCALA ENTRE SI, vistas de lado, con
    la estacion arriba y el cono de elevacion >= 10 grados. Devuelve el
    grupo y una funcion th -> punto de la orbita (th desde la vertical)."""
    r_o = r_s * (R_T + H_KM) / R_T
    c = np.array([0.0, y_sup - r_s, 0.0])
    est = np.array([0.0, y_sup, 0.0])
    en = lambda th: c + r_o * np.array([np.sin(np.radians(th)),
                                        np.cos(np.radians(th)), 0.0])
    tierra = Circle(radius=r_s, stroke_color=C_TENUE, stroke_width=2.5,
                    fill_color=C_TIERRA, fill_opacity=1.0).move_to(c)
    orbita = Circle(radius=r_o, stroke_color=C_TENUE, stroke_width=1.5,
                    stroke_opacity=0.6).move_to(c)
    cono = Polygon(est, *[en(t) for t in np.linspace(-LAMBDA, LAMBDA, 30)],
                   stroke_width=0, fill_color=C_ENLACE, fill_opacity=0.12)
    bordes = VGroup(DashedLine(est, en(-LAMBDA), dash_length=0.12,
                               stroke_color=C_ENLACE, stroke_width=2),
                    DashedLine(est, en(LAMBDA), dash_length=0.12,
                               stroke_color=C_ENLACE, stroke_width=2))
    estacion = Square(side_length=0.22, stroke_width=0, fill_color=CODE_INK,
                      fill_opacity=1.0).move_to(est + UP * 0.11)
    g = VGroup(tierra, orbita, cono, bordes, estacion)
    g.en, g.est, g.r_o, g.centro = en, est, r_o, c
    return g


class Cuadro:
    """Un cuadro de datos sin ejes de manim (que cruzan por el origen): mapea
    (x, y) de datos a pantalla dentro de la caja (x0, x1, y0, y1). El rango y
    se ELIGE, no se recorta despues (trampas.md)."""

    def __init__(self, caja, rango_x, rango_y):
        self.x0, self.x1, self.y0, self.y1 = caja
        self.rx, self.ry = rango_x, rango_y

    def p(self, x, y):
        fx = (x - self.rx[0]) / (self.rx[1] - self.rx[0])
        fy = (y - self.ry[0]) / (self.ry[1] - self.ry[0])
        return np.array([self.x0 + (self.x1 - self.x0) * fx,
                         self.y0 + (self.y1 - self.y0) * fy, 0.0])

    def serie(self, xs, ys, color, ancho=4, esquinas=True):
        m = VMobject(stroke_color=color, stroke_width=ancho)
        pts = [self.p(x, y) for x, y in zip(xs, ys)]
        (m.set_points_as_corners if esquinas else m.set_points_smoothly)(pts)
        return m

    def suelo(self, y=None, color=None):
        y = self.ry[0] if y is None else y
        return Line(self.p(self.rx[0], y), self.p(self.rx[1], y),
                    stroke_color=C_TENUE if color is None else color, stroke_width=2)

    def raya(self, y, color, dash=0.1, ancho=2):
        return DashedLine(self.p(self.rx[0], y), self.p(self.rx[1], y),
                          dash_length=dash, stroke_color=color, stroke_width=ancho)

    def franjas(self, xs, mascara, color, opacidad=0.18):
        """Rectangulos verticales donde `mascara` es cierta (tramos seguidos)."""
        g = VGroup()
        i, n = 0, len(xs)
        dx = (xs[1] - xs[0]) if n > 1 else 1
        while i < n:
            if mascara[i]:
                j = i
                while j + 1 < n and mascara[j + 1]:
                    j += 1
                a, b = self.p(xs[i] - dx / 2, self.ry[0]), self.p(xs[j] + dx / 2, self.ry[1])
                r = Rectangle(width=b[0] - a[0], height=b[1] - a[1], stroke_width=0,
                              fill_color=color, fill_opacity=opacidad)
                g.add(r.move_to((a + b) / 2))
                i = j + 1
            else:
                i += 1
        return g


def satelite_en(p, color=None):
    color = C_ADAPTA if color is None else color
    return VGroup(Dot(p, radius=0.2, color=color, fill_opacity=0.22),
                  Dot(p, radius=0.1, color=color))


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
