"""Librería compartida de piezas ilustrativas Co.De Aerospace.

Reglas (convención de piezas limpias para presentación):
  * SIN títulos, subtítulos ni narración. Solo etiquetas imprescindibles
    de diagrama: máximo 3 palabras por etiqueta (las cifras cuentan como 1).
  * Fondo navy (oscuro) o blanco (claro): CODE_TEMA=oscuro|claro.
  * Colores con rol fijo: SATÉLITE ámbar, ANTENA cian, CIELO violeta,
    lo que FALLA rojo, lo LOGRADO verde.
  * Sin marca de agua ni HUD: la pieza se funde con el slide.

Uso:
    from code_lib import *
    class MiPieza(Pieza):
        def construct(self):
            ...
"""
import os
import numpy as np
from manim import *

FUENTE = "Carlito"
TEMA = os.environ.get("CODE_TEMA", "oscuro").lower()
OSCURO = TEMA != "claro"

if OSCURO:
    FONDO, TINTA, TENUE = "#0B1F3A", "#F1F5F9", "#8AA0B8"
    C_EJE, C_TIERRA, C_TIERRA_2 = "#31506f", "#2563EB", "#1E3A8A"
    C_SAT, C_ANT, C_CIELO = "#F59E0B", "#22D3EE", "#A78BFA"
    C_MAL, C_OK = "#F43F5E", "#34D399"
    C_PANEL = "#12325A"
else:
    FONDO, TINTA, TENUE = "#FFFFFF", "#0F172A", "#64748B"
    C_EJE, C_TIERRA, C_TIERRA_2 = "#B6C2D0", "#2563EB", "#93B4F5"
    C_SAT, C_ANT, C_CIELO = "#D97706", "#0891B2", "#7C3AED"
    C_MAL, C_OK = "#E11D48", "#059669"
    C_PANEL = "#E2E8F0"

config.background_color = FONDO


class _Glifo(Text):
    """Dígito/signo en la tipografía de marca (Text) para DecimalNumber."""

    def __init__(self, texto, **kw):
        kw.setdefault("font", FUENTE)
        super().__init__(texto, **kw)


_DecimalNumberLatex = DecimalNumber


class DecimalNumber(_DecimalNumberLatex):  # noqa: F811
    """DecimalNumber de Manim, pero en Carlito (sin pasar por LaTeX)."""

    def __init__(self, number=0, num_decimal_places=2, mob_class=_Glifo, **kw):
        super().__init__(number, num_decimal_places, mob_class=mob_class, **kw)


def _vigilar(texto, maximo=3):
    palabras = str(texto).replace("\n", " ").split()
    if len(palabras) > maximo:
        raise ValueError(f"Etiqueta demasiado larga ({len(palabras)} palabras): {texto!r}")


def et(texto, tam=22, color=None, **kw):
    """Etiqueta de diagrama (<= 3 palabras)."""
    _vigilar(texto)
    return Text(str(texto), font=FUENTE, font_size=tam, color=color or TINTA, **kw)


def et_junto(texto, mob, direccion=DOWN, tam=20, color=None, buff=0.15):
    return et(texto, tam, color or TENUE).next_to(mob, direccion, buff=buff)


def cifra(valor, unidad="", tam=30, color=None, decimales=0):
    """Número vivo (DecimalNumber + unidad) para cifras que cambian."""
    n = DecimalNumber(valor, num_decimal_places=decimales, font_size=tam,
                      color=color or C_ANT)
    n.set_stroke(width=0)
    grupo = VGroup(n)
    if unidad:
        grupo.add(Text(unidad, font=FUENTE, font_size=tam * 0.7, color=TENUE))
        grupo.arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
    return grupo


def punto_orbita(radio, ang, centro=ORIGIN, excentricidad=0.0):
    """Punto en órbita elíptica con foco en `centro` (semieje mayor = radio)."""
    e = excentricidad
    r = radio * (1 - e**2) / (1 + e * np.cos(ang))
    return centro + np.array([r * np.cos(ang), r * np.sin(ang), 0])


# ---------- íconos ---------------------------------------------------------
def tierra(radio=1.5, meridianos=True):
    g = VGroup(Circle(radius=radio, color=C_TIERRA, fill_color=C_TIERRA_2,
                      fill_opacity=1, stroke_width=2))
    if meridianos:
        for k in (0.35, 0.7):
            g.add(Ellipse(width=2 * radio * k, height=2 * radio, color=C_EJE,
                          stroke_width=1, stroke_opacity=0.8))
        for k in (-0.5, 0, 0.5):
            y = radio * k
            w = 2 * np.sqrt(radio**2 - y**2)
            g.add(Line([-w / 2, y, 0], [w / 2, y, 0], color=C_EJE,
                       stroke_width=1, stroke_opacity=0.8))
    return g


def satelite(tam=0.3, color=None, paneles=True):
    """Ícono de satélite: cuerpo + dos paneles solares."""
    c = color or C_SAT
    cuerpo = Square(tam, color=c, fill_color=c, fill_opacity=0.9, stroke_width=1.5)
    g = VGroup(cuerpo)
    if paneles:
        for s in (-1, 1):
            p = Rectangle(width=tam * 1.3, height=tam * 0.7, color=c,
                          fill_color=C_CIELO, fill_opacity=0.55, stroke_width=1.5)
            p.next_to(cuerpo, RIGHT * s, buff=tam * 0.12)
            g.add(p)
    return g


def antena_parabolica(tam=0.6, color=None, ang=90 * DEGREES):
    """Plato parabólico + alimentador. `ang` = dirección a la que apunta."""
    c = color or C_ANT
    plato = Arc(radius=tam, start_angle=-55 * DEGREES, angle=110 * DEGREES,
                color=c, stroke_width=4)
    plato.rotate(-0 * DEGREES).move_to(ORIGIN)
    foco = Line(plato.get_center() + RIGHT * tam * 0.15, ORIGIN + RIGHT * tam * 0.15,
                stroke_width=0)
    feed = Dot(RIGHT * tam * 0.55, radius=0.05, color=c)
    mastil = Line(ORIGIN, RIGHT * tam * 0.55, color=c, stroke_width=1.5)
    g = VGroup(plato, mastil, feed)
    g.rotate(ang)
    return g


def estacion(tam=0.5, color=None):
    """Estación terrena: base + plato apuntando arriba."""
    c = color or C_ANT
    base = Polygon([-tam * .5, 0, 0], [tam * .5, 0, 0], [0, tam * .55, 0],
                   color=c, fill_color=c, fill_opacity=0.35, stroke_width=2)
    plato = antena_parabolica(tam * 0.55, c, ang=100 * DEGREES).move_to(base.get_top() + UP * tam * 0.15)
    return VGroup(base, plato)


def nodo(texto="", radio=0.28, color=None, relleno=0.25, tam=18):
    c = color or C_ANT
    g = VGroup(Circle(radius=radio, color=c, fill_color=c, fill_opacity=relleno,
                      stroke_width=2))
    if texto:
        g.add(et(texto, tam, c))
    return g


def caja(texto, ancho=2.0, alto=0.8, color=None, tam=22, relleno=0.18):
    c = color or C_ANT
    r = RoundedRectangle(corner_radius=0.12, width=ancho, height=alto, color=c,
                         fill_color=c, fill_opacity=relleno, stroke_width=2.5)
    return VGroup(r, et(texto, tam, TINTA))


def flecha(a, b, color=None, ancho=3, punta=0.18, **kw):
    return Arrow(a, b, buff=0, color=color or TENUE, stroke_width=ancho,
                 max_tip_length_to_length_ratio=0.25, tip_length=punta, **kw)


def haz(a, b, color=None, ancho=2, op=0.85):
    return DashedLine(a, b, color=color or C_ANT, stroke_width=ancho,
                      dash_length=0.12, stroke_opacity=op)


def pulso(a, b, color=None, radio=0.07):
    """Dot que viaja de a a b: usar con MoveAlongPath/ .animate."""
    return Dot(a, radius=radio, color=color or C_SAT)


def estrellas(n=70, semilla=1, ancho=14, alto=8, op=0.6):
    rng = np.random.default_rng(semilla)
    g = VGroup()
    for _ in range(n):
        p = [rng.uniform(-ancho / 2, ancho / 2), rng.uniform(-alto / 2, alto / 2), 0]
        g.add(Dot(p, radius=rng.uniform(0.008, 0.028), color=TINTA,
                  fill_opacity=rng.uniform(0.2, op) if OSCURO else 0))
    return g



def _instante_foto():
    """CODE_FOTO_T=<segundos>: guarda un PNG de ese instante y detiene la escena.
    CODE_FOTO_SALIDA=<ruta.png>. Pensado para `manim render -s -t` (fotogramas/stickers)."""
    t = os.environ.get("CODE_FOTO_T")
    return float(t) if t else None


class _FotoMixin:
    def _guardar_foto(self):
        from manim.utils.exceptions import EndSceneEarlyException
        self.renderer.update_frame(self, ignore_skipping=True)
        self.renderer.camera.get_image().save(os.environ["CODE_FOTO_SALIDA"])
        raise EndSceneEarlyException()

    def _get_animation_time_progression(self, animations, duration):
        if _instante_foto() is None:
            return super()._get_animation_time_progression(animations, duration)

        class _Pasos(list):  # pasos finos también en modo salto (-s)
            def close(self):
                pass
        return _Pasos(list(np.arange(0, duration, 1 / 30)) + [duration])

    def update_to_time(self, t):
        super().update_to_time(t)
        objetivo = _instante_foto()
        # en modo salto, renderer.time ya incluye la duración de esta animación
        if objetivo is not None and (self.renderer.time - self.duration + t) >= objetivo:
            self._guardar_foto()

    def wait(self, *a, **kw):
        super().wait(*a, **kw)
        objetivo = _instante_foto()
        if objetivo is not None and self.renderer.time >= objetivo:
            self._guardar_foto()


class Pieza(_FotoMixin, Scene):
    """Escena 2D base: fondo del tema, sin marca. `respiro()` entre pasos."""

    def setup(self):
        self.camera.background_color = FONDO

    def respiro(self, t=0.6):
        self.wait(t)

    def cierre(self, t=0.6):
        if os.environ.get("CODE_FOTO"):
            return  # modo fotograma: conserva el estado final
        """Deja ver el estado final un momento y funde a fondo limpio."""
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=t)
        self.wait(0.3)


class Pieza3D(_FotoMixin, ThreeDScene):
    """Escena 3D base (misma paleta)."""

    def setup(self):
        self.camera.background_color = FONDO

    def respiro(self, t=0.6):
        self.wait(t)

    def cierre(self, t=0.6):
        if os.environ.get("CODE_FOTO"):
            return  # modo fotograma: conserva el estado final
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=t)
        self.wait(0.3)


def esfera_tierra(radio=1.5, res=(28, 56)):
    """Tierra 3D: esfera + malla de paralelos/meridianos."""
    s = Sphere(radius=radio, resolution=res).set_color(C_TIERRA_2).set_opacity(0.9)
    malla = VGroup()
    for lat in np.linspace(-60, 60, 5) * DEGREES:
        malla.add(ParametricFunction(
            lambda t, la=lat: radio * np.array([np.cos(la) * np.cos(t), np.cos(la) * np.sin(t), np.sin(la)]),
            t_range=[0, TAU], color=C_TIERRA, stroke_width=1, stroke_opacity=0.6))
    for lon in np.linspace(0, PI, 6, endpoint=False):
        malla.add(ParametricFunction(
            lambda t, lo=lon: radio * np.array([np.cos(t) * np.cos(lo), np.cos(t) * np.sin(lo), np.sin(t)]),
            t_range=[0, TAU], color=C_TIERRA, stroke_width=1, stroke_opacity=0.6))
    return VGroup(s, malla)


def orbita3d(radio, incl=0.0, raan=0.0, color=None, ancho=2, op=0.8):
    """Círculo orbital 3D (inclinación y RAAN en radianes)."""
    def f(t):
        p = np.array([radio * np.cos(t), radio * np.sin(t), 0.0])
        ci, si, cr, sr = np.cos(incl), np.sin(incl), np.cos(raan), np.sin(raan)
        p = np.array([p[0], p[1] * ci, p[1] * si])
        return np.array([p[0] * cr - p[1] * sr, p[0] * sr + p[1] * cr, p[2]])
    return ParametricFunction(f, t_range=[0, TAU], color=color or C_SAT,
                              stroke_width=ancho, stroke_opacity=op)


def punto_orbita3d(radio, ang, incl=0.0, raan=0.0):
    p = np.array([radio * np.cos(ang), radio * np.sin(ang) * np.cos(incl),
                  radio * np.sin(ang) * np.sin(incl)])
    cr, sr = np.cos(raan), np.sin(raan)
    return np.array([p[0] * cr - p[1] * sr, p[0] * sr + p[1] * cr, p[2]])
