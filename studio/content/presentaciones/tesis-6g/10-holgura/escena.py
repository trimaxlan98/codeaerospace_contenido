import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Dot, FadeIn, FadeOut, Line, MathTex,
                   Rectangle, Scene, Square, Transform, VGroup)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()

# Tres filas, una por clase de politica. Todas ven el MISMO mundo (la casilla
# que paga, que cambia en cada paso); solo el oraculo la ve.
FILAS = [("Oráculo", "priv"), ("Estática", "estatica"), ("Descentralizada", "adapta")]
Y_FILAS = [1.55, 0.0, -1.55]
X_IZQ = -3.2               # donde empieza la fila de casillas
LADO = 0.62
PASO_X = 0.74
X_BARRAS = 4.6


def casillas(m, y):
    return VGroup(*[Square(side_length=LADO, stroke_color=PAL.apoyo, stroke_width=2.5)
                    .move_to([X_IZQ + i * PASO_X, y, 0]) for i in range(m)])


class Holgura(Scene):
    """La construccion de la tesis que muestra que el margen puede ser
    enorme sin que NINGUNA politica desplegable gane nada: m casillas, una
    paga, y quien no la ve no puede hacer mejor que quedarse quieto.
    MA = m - 1 y MA_dec = 0, exactos."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        rng = np.random.default_rng(42)
        etiquetas = VGroup()
        for (nombre, rol), y in zip(FILAS, Y_FILAS):
            e = T6.etiqueta(nombre, PAL, fs=28, color=getattr(PAL, rol))
            e.move_to([X_IZQ - 0.55 - 0.8, y, 0])
            e.align_to([X_IZQ - 0.55, 0, 0], RIGHT)
            etiquetas.add(e)

        def tablero(m):
            return VGroup(*[casillas(m, y) for y in Y_FILAS])

        m = 3
        tab = tablero(m)
        self.play(FadeIn(etiquetas), FadeIn(tab), run_time=0.9)

        fichas = VGroup(*[Dot(radius=0.17, color=getattr(PAL, rol)) for _, rol in FILAS])
        for f, y in zip(fichas, Y_FILAS):
            f.move_to([X_IZQ, y, 0])
        self.play(FadeIn(fichas), run_time=0.4)

        # barras de acierto acumulado, a la derecha
        y0, h_max = -2.4, 4.4
        suelo = Line([X_BARRAS - 1.25, y0, 0], [X_BARRAS + 1.25, y0, 0],
                     stroke_color=PAL.apoyo, stroke_width=2)
        xs_b = [X_BARRAS - 0.8, X_BARRAS, X_BARRAS + 0.8]

        def barras(fr):
            g = VGroup()
            for x, v, (_, rol) in zip(xs_b, fr, FILAS):
                h = max(h_max * v, 0.02)
                g.add(Rectangle(width=0.55, height=h, stroke_width=0,
                                fill_color=getattr(PAL, rol), fill_opacity=1.0)
                      .move_to([x, y0 + h / 2, 0]))
            return g
        bs = barras([0, 0, 0])
        self.play(FadeIn(suelo), FadeIn(bs), run_time=0.4)

        def jugar(m, tab, pasos, dt):
            """El mundo sortea la casilla que paga; el oraculo va a ella, la
            estatica y la descentralizada (que no ven nada) se quedan en la 0."""
            aciertos = np.zeros(3)
            for k in range(pasos):
                s = int(rng.integers(0, m))
                luz = VGroup(*[Square(side_length=LADO, stroke_width=0, fill_color=PAL.tenue,
                                      fill_opacity=1.0).move_to(fila[s]) for fila in tab])
                luz.set_z_index(-1)
                destinos = [s, 0, 0]
                self.add(luz)
                self.play(*[f.animate.move_to(tab[j][d]) for j, (f, d) in
                            enumerate(zip(fichas, destinos))], run_time=dt)
                aciertos += [1, s == 0, s == 0]
                self.play(Transform(bs, barras(aciertos / (k + 1))), run_time=dt * 0.6)
                self.remove(luz)
            return aciertos / pasos

        jugar(m, tab, 10, 0.26)
        # los valores EXACTOS de la construccion, no los del muestreo
        j = T6.juego_coordinacion(m)
        self.play(Transform(bs, barras([j["V_priv"], j["V_est"], j["V_dec"]])), run_time=0.6)
        ma = MathTex(rf"\mathrm{{MA}}={j['MA']:.0f}", color=PAL.priv, font_size=44)
        mad = MathTex(rf"\mathrm{{MA}}_{{\mathrm{{dec}}}}={j['MA_dec']:.0f}", color=PAL.adapta,
                      font_size=44)
        VGroup(ma, mad).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([X_BARRAS, 3.05, 0])
        self.play(FadeIn(ma), FadeIn(mad), run_time=0.6)

        # ── 1. tres casillas ──────────────────────────────────────────────
        presentacion.paso(self, "Tres casillas")

        m2 = 8
        tab2 = tablero(m2)
        self.play(FadeOut(tab), FadeIn(tab2), *[f.animate.move_to([X_IZQ, y, 0])
                                                for f, y in zip(fichas, Y_FILAS)], run_time=1.0)
        jugar(m2, tab2, 12, 0.22)
        j2 = T6.juego_coordinacion(m2)
        ma2 = MathTex(rf"\mathrm{{MA}}={j2['MA']:.0f}", color=PAL.priv, font_size=44).move_to(ma, aligned_edge=LEFT)
        mad2 = MathTex(rf"\mathrm{{MA}}_{{\mathrm{{dec}}}}={j2['MA_dec']:.0f}", color=PAL.adapta,
                       font_size=44).move_to(mad, aligned_edge=LEFT)
        self.play(Transform(bs, barras([j2["V_priv"], j2["V_est"], j2["V_dec"]])),
                  Transform(ma, ma2), Transform(mad, mad2), run_time=0.8)
        self.wait(0.8)
        presentacion.paso(self, "Ocho casillas")
