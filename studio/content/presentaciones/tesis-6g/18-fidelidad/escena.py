import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Circle, Create, DashedLine,
                   DashedVMobject, Dot, FadeIn, Line, Scene, VGroup, linear)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
D = T6.datos_tesis()

X0, X1, Y0, Y1 = -5.6, 5.4, -2.7, 2.9
MA_MAX = 0.45


def y_de(ma):
    return Y0 + (Y1 - Y0) * ma / MA_MAX


class Fidelidad(Scene):
    """Lo que viene: llevar el marco a un simulador con orbitas reales,
    enlaces entre satelites y latencias medidas, y preguntar si el margen
    SOBREVIVE al realismo. Si no sobrevive, tambien es un resultado."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        eje_x = Line([X0, Y0, 0], [X1, Y0, 0], stroke_color=PAL.apoyo, stroke_width=2)
        eje_x.add_tip(tip_length=0.22, tip_width=0.22)
        et_x = T6.etiqueta("Realismo", PAL, fs=30).next_to(eje_x, DOWN, buff=0.2).align_to(eje_x, RIGHT)
        eje_y = Line([X0, Y0, 0], [X0, Y1, 0], stroke_color=PAL.apoyo, stroke_width=2)
        et_y = T6.etiqueta("Margen", PAL, fs=30).next_to(eje_y, UP, buff=0.15).align_to(eje_y, LEFT)
        yu = y_de(D["umbral"])
        umbral = DashedLine([X0, yu, 0], [X1 - 0.2, yu, 0], dash_length=0.14,
                            stroke_color=PAL.tinta, stroke_width=3)
        c_u = T6.cifra(T6.pct(D["umbral"], 0), PAL, fs=28, color=PAL.tinta)
        c_u.next_to([X0, yu, 0], LEFT, buff=0.15)
        self.play(Create(eje_x), Create(eje_y), FadeIn(et_x), FadeIn(et_y), run_time=0.9)
        self.play(Create(umbral), FadeIn(c_u), run_time=0.6)

        xs = [X0 + 1.3, X0 + 2.9]              # v1 y v2: mismo realismo de juguete
        v1 = Dot([xs[0], y_de(D["g0_ma"]), 0], radius=0.14, color=PAL.no)
        v2 = Dot([xs[1], y_de(D["g1_ma"]), 0], radius=0.14, color=PAL.ok)
        e1 = T6.etiqueta("v1", PAL, fs=28, color=PAL.no).next_to(v1, UP, buff=0.15)
        e2 = T6.etiqueta("v2 · hoy", PAL, fs=28, color=PAL.ok).next_to(v2, UP, buff=0.15)
        self.play(FadeIn(v1), FadeIn(e1), run_time=0.5)
        self.play(FadeIn(v2), FadeIn(e2), run_time=0.5)

        # ── 1. hoy: un entorno pequeno que si pasa ────────────────────────
        presentacion.paso(self, "Hoy")

        # v3: emulador con orbitas reales. Su margen NO se conoce: se dibuja
        # un circulo vacio a trazos y un abanico de posibles, cruzando la raya.
        x3 = X1 - 1.6
        destinos = [0.38, 0.30, 0.22, 0.12, 0.05]
        abanico = VGroup(*[DashedLine(v2.get_center(), [x3, y_de(m), 0], dash_length=0.12,
                                      stroke_color=PAL.apoyo, stroke_width=2.5)
                           for m in destinos])
        ghost = DashedVMobject(Circle(radius=0.34, stroke_color=PAL.tinta, stroke_width=3),
                               num_dashes=14).move_to([x3, y_de(0.215), 0])
        q = T6.cifra("?", PAL, fs=46, color=PAL.tinta).move_to(ghost)
        e3 = T6.etiqueta("Órbitas reales", PAL, fs=28, color=PAL.tinta)
        e3.next_to(VGroup(*[a for a in abanico]), UP, buff=0.2).set_x(x3 - 0.9)
        self.play(Create(abanico), run_time=1.6, rate_func=linear)
        self.play(FadeIn(ghost), FadeIn(q), FadeIn(e3), run_time=0.7)
        # arriba de la raya: el metodo sigue; abajo: el resultado es saber
        # que realismo mata el margen. Los dos lados se iluminan.
        arriba = Line([x3 + 0.6, yu + 0.15, 0], [x3 + 0.6, y_de(0.40), 0], stroke_color=PAL.ok,
                      stroke_width=6)
        abajo = Line([x3 + 0.6, yu - 0.15, 0], [x3 + 0.6, y_de(0.02), 0], stroke_color=PAL.no,
                     stroke_width=6)
        self.play(Create(arriba), Create(abajo), run_time=0.8)
        self.wait(0.8)
        presentacion.paso(self, "¿Sobrevive?")
