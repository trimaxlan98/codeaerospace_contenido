"""Helpers compartidos de las piezas de tesis (seminario de divulgación y comité tutorial).

Importa todo de code_lib y añade lo que se repite en las piezas de la tesis doctoral
«Gobernanza autónoma de redes programables» (Alan Rosas Palacios, IPN):

  * chips de estatus que la tesis exige en pantalla (En desarrollo · Ilustrativo · de terceros),
  * gráficos pequeños (marca ✓/✗, barras, trazo de curva, cifra viva).

Uso:
    from tesis_lib import *
    class MiPieza(Pieza):
        def construct(self):
            self.add(chip_desarrollo())
"""
from code_lib import *
import numpy as np


def suave(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def trazo(xs, ys, color, ancho=3, op=1.0):
    """Polilínea a partir de arreglos numpy (más rápida y controlable que una gráfica de Manim)."""
    m = VMobject()
    m.set_points_as_corners(np.column_stack([xs, ys, np.zeros_like(xs)]))
    m.set_fill(opacity=0)
    m.set_stroke(color, width=ancho, opacity=op)
    return m


def cifra_viva(fn, unidad="", tam=26, color=None, dec=0, centro=ORIGIN, borde=ORIGIN):
    """Cifra que se actualiza sola con fn() (Carlito, sin LaTeX). Para animarla: ValueTracker + fn."""
    col = color or C_ANT
    g = VGroup(Text("0", font=FUENTE, font_size=tam, color=col))
    if unidad:
        g.add(Text(unidad, font=FUENTE, font_size=tam * 0.7, color=TENUE))

    def act(m):
        txt = f"{fn():.{dec}f}".replace("-", "−")
        m[0].become(Text(txt, font=FUENTE, font_size=tam, color=col))
        if len(m) > 1:
            m.arrange(RIGHT, buff=0.1, aligned_edge=DOWN)
        m.move_to(centro, aligned_edge=borde)
    g.add_updater(act)
    act(g)
    return g


# ---------- chips de estatus (≤ 3 palabras, esquina inferior derecha por defecto) ----------
def chip(texto, color=None, tam=18, esquina=DR, buff=0.35):
    """Etiqueta redondeada de estatus. Devuelve el VGroup ya colocado en la esquina."""
    c = color or C_SAT
    t = et(texto, tam, c)
    caja_ = RoundedRectangle(corner_radius=0.14, width=t.width + 0.5, height=t.height + 0.3, color=c,
                             fill_color=c, fill_opacity=0.12, stroke_width=2)
    t.move_to(caja_)
    return VGroup(caja_, t).to_corner(esquina, buff=buff)


def chip_desarrollo(esquina=DR):
    """Regla de la tesis: PADA, Margen Adaptativo, NTNEnv-v2 y los resultados de QMIX van marcados así."""
    return chip("En desarrollo", C_SAT, esquina=esquina)


def chip_ilustrativo(esquina=DR):
    return chip("Ilustrativo", TENUE, esquina=esquina)


def chip_tercero(texto, esquina=DL):
    """Resultado o cita de otros autores: «Ellis 2023», «Preprint»…"""
    return chip(texto, C_CIELO, esquina=esquina)


# ---------- marcas ----------
def marca_ok(pos=ORIGIN, tam=0.28, color=None):
    c = color or C_OK
    m = VMobject().set_points_as_corners([pos + np.array([-tam * .5, 0, 0]), pos + np.array([-tam * .12, -tam * .42, 0]),
                                           pos + np.array([tam * .55, tam * .5, 0])])
    return m.set_stroke(c, width=5).set_fill(opacity=0)


def marca_no(pos=ORIGIN, tam=0.28, color=None):
    c = color or C_MAL
    a = Line(pos + np.array([-tam * .5, tam * .5, 0]), pos + np.array([tam * .5, -tam * .5, 0]))
    b = Line(pos + np.array([-tam * .5, -tam * .5, 0]), pos + np.array([tam * .5, tam * .5, 0]))
    return VGroup(a, b).set_stroke(c, width=5)


def barra(x, y0, alto, ancho=0.6, color=None, op=0.85):
    """Barra vertical con base en y0 (alto puede ser negativo)."""
    c = color or C_ANT
    r = Rectangle(width=ancho, height=max(abs(alto), 1e-3), color=c, fill_color=c, fill_opacity=op, stroke_width=2)
    r.move_to([x, y0 + alto / 2, 0])
    return r
