import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Create, DashedVMobject, Dot, FadeIn,
                   FadeOut, Line, MathTex, Rectangle, Scene, ValueTracker,
                   VGroup, VMobject, always_redraw, linear)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
C = T6.curvas_margen(plano=True)       # la ruta estable domina en TODO instante

X0, X1 = -6.3, 1.6
Y0, Y1 = -2.9, 2.6
VMIN, VMAX = 0.30, 1.25

# Una politica adaptativa cualquiera: cambia a la opcion A cuando A "parece"
# buena (satelite a la vista). En este entorno eso solo puede costar.
VIS = C["R"][0] > np.median(C["R"][0])
ADAPT = np.where(VIS, C["R"][0], C["R"][2])


def xy(t, v):
    return np.array([X0 + (X1 - X0) * t, Y0 + (Y1 - Y0) * (v - VMIN) / (VMAX - VMIN), 0.0])


def curva(serie, color, ancho):
    m = VMobject(stroke_color=color, stroke_width=ancho)
    m.set_points_as_corners([xy(t, v) for t, v in zip(C["t"], serie)])
    return m


class Piso(Scene):
    """El piso de falsabilidad (Teorema 4.7.1): si el entorno no premia
    adaptarse (MA = 0), ninguna politica adaptativa puede ganarle a la
    estatica. Comparar algoritmos ahi no informa nada."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        suelo = Line(xy(0, VMIN), xy(1, VMIN), stroke_color=PAL.apoyo, stroke_width=2,
                     stroke_opacity=0.6)
        opciones = VGroup(*[curva(C["R"][i], PAL.apoyo, 3) for i in range(3)])
        self.play(Create(suelo), run_time=0.5)
        self.play(*[Create(o) for o in opciones], run_time=2.0, rate_func=linear)

        est = curva(C["estatica"], PAL.estatica, 6)
        et_est = T6.etiqueta("Mejor estática", PAL, fs=30, color=PAL.estatica)
        et_est.next_to(xy(1, C["estatica"][-1]), RIGHT, buff=0.25).shift(DOWN * 0.3)
        self.play(opciones.animate.set_stroke(opacity=0.45), Create(est), run_time=1.4)
        self.play(FadeIn(et_est), run_time=0.4)

        # ── 1. una opcion gana siempre ────────────────────────────────────
        presentacion.paso(self, "Una opción domina")

        # el oraculo ve todo... y elige lo mismo en cada instante: su curva
        # cae ENCIMA de la estatica (a trazos, para que se vean las dos)
        env = DashedVMobject(curva(C["envolvente"], PAL.priv, 6), num_dashes=60)
        et_env = T6.etiqueta("Oráculo", PAL, fs=30, color=PAL.priv)
        et_env.next_to(et_est, UP, buff=0.18).align_to(et_est, LEFT)
        self.play(Create(env), run_time=2.0, rate_func=linear)
        self.play(FadeIn(et_env), run_time=0.4)
        ma = MathTex(rf"\mathrm{{MA}}={C['MA']:.0f}", color=PAL.priv, font_size=50)
        ma.move_to([5.5, 2.4, 0])
        self.play(FadeIn(ma), run_time=0.5)

        # ── 2. el oraculo coincide con la estatica ────────────────────────
        presentacion.paso(self, "Margen cero")

        ad = curva(ADAPT, PAL.adapta, 5)
        et_ad = T6.etiqueta("Adaptativa", PAL, fs=30, color=PAL.adapta)
        et_ad.next_to(et_est, DOWN, buff=0.18).align_to(et_est, LEFT)
        self.play(Create(ad), run_time=2.4, rate_func=linear)
        self.play(FadeIn(et_ad), run_time=0.4)
        # barras: los promedios. La adaptativa queda por debajo, siempre.
        y0 = Y0
        alto = lambda v: (Y1 - Y0) * (v - VMIN) / (VMAX - VMIN)
        xs = [5.0, 6.05]
        b_est = Rectangle(width=0.8, height=alto(C["V_est"]), stroke_width=0,
                          fill_color=PAL.estatica, fill_opacity=1.0)
        b_est.move_to([xs[0], y0 + alto(C["V_est"]) / 2, 0])
        v_ad = float(ADAPT.mean())
        b_ad = Rectangle(width=0.8, height=alto(v_ad), stroke_width=0,
                         fill_color=PAL.adapta, fill_opacity=1.0)
        b_ad.move_to([xs[1], y0 + alto(v_ad) / 2, 0])
        piso = Line([4.45, y0, 0], [6.6, y0, 0], stroke_color=PAL.apoyo, stroke_width=2)
        self.play(FadeIn(piso), FadeIn(b_est, shift=UP * 0.2), FadeIn(b_ad, shift=UP * 0.2),
                  run_time=0.9)
        self.wait(0.8)
        presentacion.paso(self, "Ninguna gana")
