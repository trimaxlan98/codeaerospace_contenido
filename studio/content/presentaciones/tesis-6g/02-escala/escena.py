import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, Dot, FadeIn, FadeOut,
                   LaggedStart, Scene, Square, Transform, VGroup)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
E = T6.ESCALA
POR_PUNTO = 100                                   # cada punto: 100 satelites
N = int(round(E["activos"] / POR_PUNTO))
N_SL = int(round(E["starlink"] / POR_PUNTO))
COLS = 21


class Escala(Scene):
    """Mas de dieciseis mil satelites activos, dos de cada tres de una sola
    constelacion. Nadie los supervisa uno a uno: la automatizacion es
    aritmetica."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        # la escala humana: un operador y las decenas que puede vigilar
        op = Square(side_length=0.36, stroke_width=0, fill_color=PAL.tinta,
                    fill_opacity=1.0).move_to([-4.6, -0.2, 0])
        rng = np.random.default_rng(42)
        ang = rng.uniform(0, 2 * np.pi, 24)
        rad = rng.uniform(0.7, 1.4, 24)
        pocos = VGroup(*[Dot(op.get_center() + r * np.array([np.cos(a), np.sin(a), 0]),
                             radius=0.07, color=PAL.estatica) for a, r in zip(ang, rad)])
        cerco = Circle(radius=1.6, stroke_color=PAL.apoyo, stroke_width=2).move_to(op)
        et_op = T6.etiqueta("Un operador", PAL, fs=28).next_to(cerco, DOWN, buff=0.25)
        self.play(FadeIn(op), Create(cerco), FadeIn(et_op), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pocos], lag_ratio=0.05),
                  run_time=1.2)

        # ── 1. decenas, a mano ────────────────────────────────────────────
        presentacion.paso(self, "Un operador")

        filas = int(np.ceil(N / COLS))
        paso = 0.34
        x0 = -0.9
        y0 = (filas - 1) * paso / 2 - 0.2
        malla = VGroup(*[Dot([x0 + (i % COLS) * paso, y0 - (i // COLS) * paso, 0],
                             radius=0.1, color=PAL.estatica) for i in range(N)])
        leyenda = VGroup(Dot(radius=0.1, color=PAL.estatica),
                         T6.etiqueta(f"= {POR_PUNTO} satélites", PAL, fs=26))
        leyenda[1].next_to(leyenda[0], RIGHT, buff=0.15)
        leyenda.next_to(malla, UP, buff=0.35).align_to(malla, LEFT)
        total = T6.cifra(f"{E['activos']:,}".replace(",", " "), PAL, fs=40, color=PAL.tinta)
        total.next_to(malla, UP, buff=0.3).align_to(malla, RIGHT)
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in malla], lag_ratio=0.01),
                  FadeIn(leyenda), run_time=2.6)
        self.play(FadeIn(total), run_time=0.5)

        # ── 2. dieciseis mil ──────────────────────────────────────────────
        presentacion.paso(self, "Dieciséis mil")

        sl = VGroup(*[malla[i].copy().set_color(PAL.adapta) for i in range(N_SL)])
        self.play(LaggedStart(*[Transform(malla[i], sl[i]) for i in range(N_SL)],
                              lag_ratio=0.008), run_time=2.0)
        c_sl = T6.cifra(T6.pct(E["starlink"] / E["activos"], 0), PAL, fs=40, color=PAL.adapta)
        e_sl = T6.etiqueta("una constelación", PAL, fs=26, color=PAL.adapta)
        grp = VGroup(c_sl, e_sl).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        grp.next_to(malla, DOWN, buff=0.3).align_to(malla, LEFT)
        self.play(FadeIn(grp), run_time=0.6)
        self.wait(0.8)
        presentacion.paso(self, "Dos tercios")
