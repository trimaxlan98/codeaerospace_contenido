import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, DashedLine, FadeIn,
                   FadeOut, GrowFromEdge, Line, MathTex, Rectangle,
                   RoundedRectangle, Scene, Transform, ValueTracker, VGroup,
                   VMobject, always_redraw, linear)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()

# La analogia del seminario (no son datos): dos medicos, un termometro que
# marca 37 grados SIEMPRE. Los porcentajes de acierto son los del guion.
ACIERTO_A, ACIERTO_B = 0.70, 0.72
LECTURA = 37

X0, X1 = -6.4, -1.4        # la temperatura verdadera del paciente
Y_MIN, Y_MAX = -2.3, 2.3
T_MIN, T_MAX = 35.0, 40.5  # escala de temperatura del dibujo


def y_de(temp):
    return Y_MIN + (Y_MAX - Y_MIN) * (temp - T_MIN) / (T_MAX - T_MIN)


def verdadera(x, fase):
    """Temperatura del paciente: cambia de verdad (fiebre, baja, sube)."""
    u = (x - X0) / (X1 - X0)
    return 37.6 + 1.3 * np.sin(2 * np.pi * (1.3 * u + fase)) + 0.5 * np.sin(
        2 * np.pi * (3.1 * u - 0.7 * fase))


class Termometro(Scene):
    """Con un termometro que marca siempre lo mismo, la diferencia entre dos
    medicos no significa nada: no hay nada que medir."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        # dos barras que compiten
        yb = -2.3
        def barra(x, v, color):
            h = 5.0 * v
            r = Rectangle(width=1.05, height=h, stroke_width=0, fill_color=color,
                          fill_opacity=1.0)
            return r.move_to([x, yb + h / 2, 0])
        xa, xb = 3.3, 5.1
        ba, bb = barra(xa, ACIERTO_A, PAL.estatica), barra(xb, ACIERTO_B, PAL.adapta)
        suelo = Line([2.4, yb, 0], [6.0, yb, 0], stroke_color=PAL.apoyo, stroke_width=2)
        la = T6.etiqueta("A", PAL, fs=32, color=PAL.estatica).move_to([xa, yb - 0.4, 0])
        lb = T6.etiqueta("B", PAL, fs=32, color=PAL.adapta).move_to([xb, yb - 0.4, 0])
        ca = T6.cifra(T6.pct(ACIERTO_A, 0), PAL, fs=34, color=PAL.estatica)
        cb = T6.cifra(T6.pct(ACIERTO_B, 0), PAL, fs=34, color=PAL.adapta)
        self.play(FadeIn(suelo), FadeIn(la), FadeIn(lb), run_time=0.5)
        self.play(GrowFromEdge(ba, DOWN), GrowFromEdge(bb, DOWN), run_time=1.3)
        ca.next_to(ba, UP, buff=0.16)
        cb.next_to(bb, UP, buff=0.16)
        self.play(FadeIn(ca), FadeIn(cb), run_time=0.5)

        # ── 1. B parece mejor que A ───────────────────────────────────────
        presentacion.paso(self, "Dos médicos")

        # El termometro: su columna NO se mueve.
        xt = 0.35
        tubo = RoundedRectangle(corner_radius=0.26, width=0.52, height=Y_MAX - Y_MIN + 0.3,
                                stroke_color=PAL.apoyo, stroke_width=3)
        tubo.move_to([xt, (Y_MAX + Y_MIN) / 2 + 0.15, 0])
        bulbo = Circle(radius=0.42, stroke_width=0, fill_color=PAL.no,
                       fill_opacity=1.0).move_to([xt, Y_MIN - 0.3, 0])
        hcol = y_de(LECTURA) - Y_MIN + 0.1
        col = Rectangle(width=0.3, height=hcol, stroke_width=0, fill_color=PAL.no,
                        fill_opacity=1.0).move_to([xt, Y_MIN - 0.1 + hcol / 2, 0])
        c_t = T6.cifra(f"{LECTURA}°", PAL, fs=36, color=PAL.no)
        c_t.next_to(col.get_top(), RIGHT, buff=0.4)
        self.play(FadeIn(tubo), FadeIn(bulbo), GrowFromEdge(col, DOWN), run_time=0.9)
        self.play(FadeIn(c_t), run_time=0.4)

        # la temperatura verdadera cambia; la lectura es una raya plana
        fase = ValueTracker(0.0)
        xs = np.linspace(X0, X1, 160)

        def curva():
            m = VMobject(stroke_color=PAL.tinta, stroke_width=4)
            m.set_points_smoothly([[x, y_de(verdadera(x, fase.get_value())), 0] for x in xs])
            return m
        viva = always_redraw(curva)
        lectura = DashedLine([X0, y_de(LECTURA), 0], [xt - 0.35, y_de(LECTURA), 0],
                             dash_length=0.14, stroke_color=PAL.no, stroke_width=3)
        self.play(Create(viva), run_time=1.0)
        self.play(Create(lectura), run_time=0.6)
        self.play(fase.animate.set_value(1.6), run_time=4.0, rate_func=linear)

        # ── 2. el paciente cambia; el termometro no ───────────────────────
        presentacion.paso(self, "El termómetro")

        # Con ese instrumento, A y B son indistinguibles: la diferencia se
        # disuelve en el mismo gris.
        ba2, bb2 = barra(xa, ACIERTO_A, PAL.tenue), barra(xb, ACIERTO_B, PAL.tenue)
        igual = MathTex("=", color=PAL.tinta, font_size=110).move_to([(xa + xb) / 2, yb + 1.6, 0])
        self.play(Transform(ba, ba2), Transform(bb, bb2),
                  ca.animate.set_color(PAL.apoyo), cb.animate.set_color(PAL.apoyo),
                  la.animate.set_color(PAL.apoyo), lb.animate.set_color(PAL.apoyo),
                  fase.animate.set_value(2.4), run_time=1.6, rate_func=linear)
        self.play(FadeIn(igual, scale=0.7), fase.animate.set_value(2.9),
                  run_time=1.0, rate_func=linear)
        self.wait(0.6)
        presentacion.paso(self, "Nada que medir")
