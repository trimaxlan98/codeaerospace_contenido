import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Brace, Circle, Create, DashedLine,
                   FadeIn, GrowFromEdge, Line, Rectangle, RoundedRectangle,
                   Scene, Transform, VGroup, linear)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
D = T6.datos_tesis()

# Escala vertical del termometro: de 0 a 40 % de margen.
MA_MAX = 0.40
Y_BASE, Y_TOPE = -2.2, 3.1
ANCHO_TUBO = 0.62


def y_de(ma):
    return Y_BASE + (Y_TOPE - Y_BASE) * ma / MA_MAX


def termometro(x):
    tubo = RoundedRectangle(corner_radius=ANCHO_TUBO / 2, width=ANCHO_TUBO,
                            height=Y_TOPE - Y_BASE + 0.35, stroke_color=PAL.apoyo,
                            stroke_width=3)
    tubo.move_to([x, (Y_TOPE + Y_BASE) / 2 + 0.17, 0])
    bulbo = Circle(radius=0.52, stroke_color=PAL.apoyo, stroke_width=3)
    bulbo.move_to([x, Y_BASE - 0.40, 0])
    return VGroup(tubo, bulbo)


def columna(x, ma, color):
    alto = max(y_de(ma) - Y_BASE, 1e-3)
    c = Rectangle(width=ANCHO_TUBO - 0.22, height=alto, stroke_width=0,
                  fill_color=color, fill_opacity=1.0)
    c.move_to([x, Y_BASE + alto / 2, 0])
    return c


def bulbo_lleno(x, color):
    b = Circle(radius=0.40, stroke_width=0, fill_color=color, fill_opacity=1.0)
    return b.move_to([x, Y_BASE - 0.40, 0])


class Recorrido(Scene):
    """El banco de pruebas de la tesis, medido con su propio termometro: la
    version 1 no premiaba adaptarse (1.7 %), la version 2 si (31.8 %)."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        x1, x2 = -2.3, 2.3
        t1, t2 = termometro(x1), termometro(x2)
        n1 = T6.etiqueta("Entorno v1", PAL, fs=30, color=PAL.tinta)
        n2 = T6.etiqueta("Entorno v2", PAL, fs=30, color=PAL.tinta)
        n1.next_to(t1, DOWN, buff=0.22)
        n2.next_to(t2, DOWN, buff=0.22)

        yu = y_de(D["umbral"])
        umbral = DashedLine([x1 - 1.9, yu, 0], [x2 + 1.9, yu, 0], dash_length=0.16,
                            stroke_color=PAL.tinta, stroke_width=3)
        et_u = T6.etiqueta("Umbral", PAL, fs=28, color=PAL.tinta)
        et_u.next_to(umbral, LEFT, buff=0.25)
        c_u = T6.cifra(T6.pct(D["umbral"], 0), PAL, fs=34, color=PAL.tinta)
        c_u.next_to(umbral, RIGHT, buff=0.25)

        self.play(Create(t1), Create(t2), FadeIn(n1), FadeIn(n2), run_time=1.2)
        self.play(Create(umbral), FadeIn(et_u), FadeIn(c_u), run_time=1.0)

        # ── 1. la raya se pinta ANTES de medir ────────────────────────────
        presentacion.paso(self, "El umbral")

        b1 = bulbo_lleno(x1, PAL.no)
        col1 = columna(x1, D["g0_ma"], PAL.no)
        self.play(FadeIn(b1), run_time=0.4)
        self.play(GrowFromEdge(col1, DOWN), run_time=1.0)
        c1 = T6.cifra(T6.pct(D["g0_ma"]), PAL, fs=40, color=PAL.no)
        c1.next_to(col1, RIGHT, buff=0.45).align_to(col1, DOWN).shift(UP * 0.1)
        self.play(FadeIn(c1, shift=LEFT * 0.1), run_time=0.6)
        self.wait(0.6)

        # ── 2. el primer banco: un termometro roto (el mio) ───────────────
        presentacion.paso(self, "Entorno v1")

        b2 = bulbo_lleno(x2, PAL.apoyo)
        col2 = columna(x2, D["g1_ma"], PAL.apoyo)
        col2_ok = columna(x2, D["g1_ma"], PAL.ok)
        b2_ok = bulbo_lleno(x2, PAL.ok)
        self.play(FadeIn(b2), run_time=0.4)
        # sube lineal (como un contador) y se vuelve verde al cruzar la raya
        frac = (D["umbral"] / D["g1_ma"])
        self.play(GrowFromEdge(col2, DOWN), run_time=2.4, rate_func=linear)
        self.play(Transform(col2, col2_ok), Transform(b2, b2_ok), run_time=0.5)
        c2 = T6.cifra(T6.pct(D["g1_ma"]), PAL, fs=40, color=PAL.ok)
        c2.next_to(col2, RIGHT, buff=0.45).align_to(col2, UP).shift(DOWN * 0.05)
        self.play(FadeIn(c2, shift=LEFT * 0.1), run_time=0.6)
        self.wait(0.6)

        # ── 3. el segundo banco pasa la compuerta ─────────────────────────
        presentacion.paso(self, "Entorno v2")

        # El par que reporta la tesis: el margen alcanzable demostrado (la
        # peor semilla de G2b) debajo de la envolvente medida.
        alcanzado = min(g["mejora"] for g in D["g2b"])
        col3 = columna(x2, alcanzado, PAL.adapta)
        col3.stretch(1.0, 0)
        llave = Brace(col3, direction=LEFT, buff=0.45, color=PAL.adapta)
        c3 = T6.cifra(T6.pct(alcanzado), PAL, fs=36, color=PAL.adapta)
        c3.next_to(llave, LEFT, buff=0.18)
        et3 = T6.etiqueta("Alcanzado", PAL, fs=26, color=PAL.adapta)
        et3.next_to(c3, UP, buff=0.12).align_to(c3, RIGHT)
        self.play(GrowFromEdge(col3, DOWN), run_time=1.2)
        self.play(FadeIn(llave), FadeIn(c3), FadeIn(et3), run_time=0.8)
        self.wait(0.8)
        presentacion.paso(self, "Alcanzado")
