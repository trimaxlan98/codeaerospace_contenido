import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Create, Dot, FadeIn, FadeOut, Line,
                   MathTex, Polygon, Rectangle, ReplacementTransform, Scene,
                   ValueTracker, VGroup, VMobject, always_redraw, linear)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
C = T6.curvas_margen()

# Marco del dibujo (unidades de manim; el mundo mide 14.2 x 8).
X0, X1 = -6.3, 1.6
Y0, Y1 = -2.9, 2.6
VMIN, VMAX = 0.30, 1.25


def xy(t, v):
    return np.array([X0 + (X1 - X0) * t,
                     Y0 + (Y1 - Y0) * (v - VMIN) / (VMAX - VMIN), 0.0])


def curva(serie, color, ancho):
    pts = [xy(t, v) for t, v in zip(C["t"], serie)]
    m = VMobject(stroke_color=color, stroke_width=ancho)
    m.set_points_as_corners(pts)
    return m


def en(serie, tau):
    """Punto de una serie en la fraccion tau del recorrido."""
    tau = float(np.clip(tau, 0.0, 1.0))
    return xy(tau, float(np.interp(tau, C["t"], serie)))


class Margen(Scene):
    """El Margen Adaptativo como una distancia: lo que paga la mejor opcion
    FIJA contra lo que paga quien ve todo y elige paso a paso."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        suelo = Line(xy(0, VMIN), xy(1, VMIN), stroke_color=PAL.apoyo,
                     stroke_width=2, stroke_opacity=0.6)
        opciones = VGroup(*[curva(C["R"][i], PAL.apoyo, 3) for i in range(3)])
        self.play(Create(suelo), run_time=0.6)
        self.play(*[Create(o) for o in opciones], run_time=2.2, rate_func=linear)

        # ── 1. las opciones cambian con el tiempo ─────────────────────────
        presentacion.paso(self, "Tres opciones")

        estatica = curva(C["estatica"], PAL.estatica, 6)
        et_est = T6.etiqueta("Mejor estática", PAL, fs=30, color=PAL.estatica)
        et_est.next_to(xy(1, C["estatica"][-1]), RIGHT, buff=0.25)
        tau = ValueTracker(0.0)
        bola = always_redraw(lambda: Dot(en(C["estatica"], tau.get_value()),
                                         radius=0.09, color=PAL.estatica))
        self.play(opciones.animate.set_stroke(opacity=0.45), run_time=0.5)
        self.add(bola)
        self.play(Create(estatica), tau.animate.set_value(1.0),
                  run_time=3.0, rate_func=linear)
        self.play(FadeIn(et_est, shift=LEFT * 0.15), run_time=0.5)

        # ── 2. la opcion fija, elegida por su promedio ────────────────────
        presentacion.paso(self, "La mejor estática")

        env = curva(C["envolvente"], PAL.priv, 6)
        et_env = T6.etiqueta("Oráculo", PAL, fs=30, color=PAL.priv)
        et_env.next_to(xy(1, C["envolvente"][-1]), RIGHT, buff=0.25)
        # Que la etiqueta del oraculo no pise a la de la estatica si los dos
        # finales caen cerca: se separan en vertical, nunca se enciman.
        if abs(et_env.get_center()[1] - et_est.get_center()[1]) < 0.55:
            et_env.shift(UP * (0.55 - (et_env.get_center()[1] - et_est.get_center()[1])))
        tau2 = ValueTracker(0.0)
        bola2 = always_redraw(lambda: Dot(en(C["envolvente"], tau2.get_value()),
                                          radius=0.09, color=PAL.priv))
        self.add(bola2)
        self.play(Create(env), tau2.animate.set_value(1.0),
                  run_time=3.4, rate_func=linear)
        self.play(FadeIn(et_env, shift=LEFT * 0.15), run_time=0.5)

        # ── 3. quien ve todo elige en cada instante ───────────────────────
        presentacion.paso(self, "El oráculo")

        arriba = [xy(t, v) for t, v in zip(C["t"], C["envolvente"])]
        abajo = [xy(t, v) for t, v in zip(C["t"], C["estatica"])][::-1]
        hueco = Polygon(*arriba, *abajo, stroke_width=0, fill_color=PAL.priv,
                        fill_opacity=0.30)
        hueco.set_z_index(-1)
        self.play(FadeIn(hueco), FadeOut(bola), FadeOut(bola2), run_time=1.0)

        # Las dos barras son los PROMEDIOS de las dos curvas, en la misma
        # escala vertical que el dibujo: la diferencia de alturas es el margen.
        xb, ancho = 5.6, 0.9
        alto = lambda v: (Y1 - Y0) * (v - VMIN) / (VMAX - VMIN)
        base = Rectangle(width=ancho, height=alto(C["V_est"]), stroke_width=0,
                         fill_color=PAL.estatica, fill_opacity=1.0)
        base.move_to([xb, Y0 + alto(C["V_est"]) / 2, 0])
        tope_h = alto(C["V_priv"]) - alto(C["V_est"])
        tope = Rectangle(width=ancho, height=tope_h, stroke_width=0,
                         fill_color=PAL.priv, fill_opacity=1.0)
        tope.move_to([xb, Y0 + alto(C["V_est"]) + tope_h / 2, 0])
        suelo_b = Line([xb - 0.7, Y0, 0], [xb + 0.7, Y0, 0],
                       stroke_color=PAL.apoyo, stroke_width=2, stroke_opacity=0.6)
        self.play(FadeIn(suelo_b), FadeIn(base, shift=UP * 0.2), run_time=0.8)
        self.play(ReplacementTransform(hueco.copy(), tope), run_time=1.6)
        et_ma = T6.etiqueta("Margen", PAL, fs=30, color=PAL.priv)
        et_ma.next_to(tope, UP, buff=0.18)
        self.play(FadeIn(et_ma, shift=DOWN * 0.1), run_time=0.5)

        # ── 4. la definicion ──────────────────────────────────────────────
        presentacion.paso(self, "El margen")

        f = MathTex(r"\mathrm{MA}=\frac{V^{\star}_{\mathrm{priv}}-V^{\star}_{\mathrm{est}}}"
                    r"{V^{\star}_{\mathrm{est}}}", color=PAL.tinta, font_size=46)
        f.move_to([xb - 0.35, Y1 + 0.55, 0])
        f.set_x(min(f.get_x(), LZ.derecha - f.width / 2))
        self.play(FadeIn(f, shift=DOWN * 0.15), run_time=0.9)
        self.wait(0.8)
        presentacion.paso(self, "La definición")
