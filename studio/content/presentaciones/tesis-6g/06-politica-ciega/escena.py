import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, DashedVMobject, FadeIn,
                   FadeOut, Line, Scene, VGroup, VMobject, linear)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()

# Dos bancos de pruebas: uno sin estocasticidad (cada episodio repite el
# anterior) y uno con azar. Juguete con la forma del hallazgo de Ellis et al.
# (NeurIPS 2023, SMACv2): en SMAC una politica de lazo abierto, que solo mira
# el reloj, alcanzaba tasas de victoria no triviales.
T, SIN = T6.trayectorias(n=6, azar=0.0, semilla=42)
_, CON = T6.trayectorias(n=6, azar=0.85, semilla=42)
PLAN = SIN[0]                      # lo que memoriza quien solo mira el reloj


def panel(x0, trayectorias, color):
    ancho, alto = 5.6, 3.2
    def xy(t, v):
        return [x0 + ancho * t, -0.4 + alto * v / 2.2, 0]
    g = VGroup()
    for tr in trayectorias:
        m = VMobject(stroke_color=color, stroke_width=3, stroke_opacity=0.8)
        m.set_points_smoothly([xy(t, v) for t, v in zip(T, tr)])
        g.add(m)
    return g, xy


class PoliticaCiega(Scene):
    """Si el mundo repite siempre lo mismo, una politica que no mira nada
    -solo el reloj- basta. Para saber si hace falta adaptarse hay que medir
    el entorno ANTES de comparar algoritmos."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        xa, xb = -6.3, 0.7
        sin, xy_a = panel(xa, SIN, PAL.estatica)
        con, xy_b = panel(xb, CON, PAL.estatica)
        et_a = T6.etiqueta("Sin azar", PAL, fs=30, color=PAL.tinta).move_to([xa + 2.8, 2.7, 0])
        et_b = T6.etiqueta("Con azar", PAL, fs=30, color=PAL.tinta).move_to([xb + 2.8, 2.7, 0])
        sep = Line([0.2, -2.9, 0], [0.2, 2.9, 0], stroke_color=PAL.tenue, stroke_width=2)

        self.play(FadeIn(et_a), Create(sep), run_time=0.5)
        # seis episodios que caen exactamente uno encima de otro
        for m in sin:
            self.play(Create(m), run_time=0.45, rate_func=linear)

        # ── 1. el mismo episodio, seis veces ──────────────────────────────
        presentacion.paso(self, "Sin azar")

        def plan(xy):
            m = VMobject(stroke_color=PAL.adapta, stroke_width=6)
            m.set_points_smoothly([xy(t, v) for t, v in zip(T, PLAN)])
            return DashedVMobject(m, num_dashes=40)
        reloj = VGroup(Circle(radius=0.26, stroke_color=PAL.adapta, stroke_width=3),
                       Line([0, 0, 0], [0, 0.18, 0], stroke_color=PAL.adapta, stroke_width=3),
                       Line([0, 0, 0], [0.13, 0, 0], stroke_color=PAL.adapta, stroke_width=3))
        et_p = T6.etiqueta("Lazo abierto", PAL, fs=28, color=PAL.adapta)
        leyenda = VGroup(reloj, et_p).arrange(RIGHT, buff=0.2).move_to([-0.2, -3.25, 0])
        pa = plan(xy_a)
        self.play(Create(pa), FadeIn(leyenda), run_time=1.6, rate_func=linear)
        self.wait(0.4)

        # ── 2. quien solo mira el reloj, acierta ──────────────────────────
        presentacion.paso(self, "Lazo abierto")

        self.play(FadeIn(et_b), run_time=0.4)
        self.play(*[Create(m) for m in con], run_time=2.0, rate_func=linear)
        pb = plan(xy_b)
        self.play(Create(pb), run_time=1.6, rate_func=linear)
        self.wait(0.8)
        presentacion.paso(self, "Con azar")
