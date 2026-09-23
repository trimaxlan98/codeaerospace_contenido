import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Create, DashedLine, Dot, FadeIn,
                   FadeOut, Line, Scene, Transform, VGroup, linear)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
D = T6.datos_tesis()

# 27 politicas estaticas (3 agentes x 3 acciones) con su valor VERDADERO.
# Juguete con la forma del problema, no los valores de NTNEnv-v2.
_rng = np.random.default_rng(3)
VERDAD = np.sort(100 + _rng.normal(0, 4.0, 27))
SIGMA = 10.0
V_MIN, V_MAX = 76.0, 124.0
X0, X1 = -6.2, 0.6
Y_FILA = 1.2


def x_de(v):
    return X0 + (X1 - X0) * (v - V_MIN) / (V_MAX - V_MIN)


def nube(valores, color):
    """Las 27 medias muestrales como puntos sobre una recta, con algo de
    separacion vertical para que no se tapen (la altura no significa nada)."""
    rango = np.argsort(np.argsort(valores))
    offs = ((rango % 3) - 1) * 0.32
    return VGroup(*[Dot([x_de(v), Y_FILA + o, 0], radius=0.07, color=color)
                    for v, o in zip(valores, offs)])


class Ganador(Scene):
    """La maldicion del ganador: elegir la mejor de 27 estaticas por su
    promedio en POCOS episodios sobreestima su valor, infla el denominador
    y deja el margen adaptativo por debajo del verdadero. Con mas episodios
    el sesgo desaparece; la curva de la tesis converge a 0.318."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        recta = Line([X0 - 0.2, Y_FILA - 0.95, 0], [X1 + 0.2, Y_FILA - 0.95, 0],
                     stroke_color=PAL.apoyo, stroke_width=2)
        mejor = float(VERDAD.max())
        raya = DashedLine([x_de(mejor), Y_FILA - 1.1, 0], [x_de(mejor), Y_FILA + 0.95, 0],
                          dash_length=0.1, stroke_color=PAL.estatica, stroke_width=3)
        et_raya = T6.etiqueta("Mejor real", PAL, fs=26, color=PAL.estatica)
        et_raya.next_to(raya, UP, buff=0.12)
        verdad = nube(VERDAD, PAL.estatica)
        self.play(Create(recta), FadeIn(verdad), run_time=0.8)
        self.play(Create(raya), FadeIn(et_raya), run_time=0.6)

        def ronda(episodios, semilla):
            m = T6.muestras_ganador(VERDAD, SIGMA, episodios, semilla)
            puntos = nube(m, PAL.apoyo)
            k = int(np.argmax(m))
            puntos[k].set_color(PAL.adapta).scale(1.6)
            return m, puntos, k

        # Semillas REPRESENTATIVAS: su sesgo es el sesgo medio de 20 000 repeticiones
        # (T6.maldicion_ganador), no una tirada que exagere.
        m1, p1, k1 = ronda(1, 63)
        self.play(Transform(verdad, p1), run_time=1.0)
        flecha = Line([x_de(mejor), Y_FILA - 1.35, 0], [x_de(m1[k1]), Y_FILA - 1.35, 0],
                      stroke_color=PAL.adapta, stroke_width=5).add_tip(tip_length=0.2)
        et1 = T6.etiqueta("1 episodio", PAL, fs=28, color=PAL.tinta)
        et1.move_to([X0 + 0.9, Y_FILA + 1.45, 0])
        self.play(Create(flecha), FadeIn(et1), run_time=0.7)

        # ── 1. con un episodio, el maximo miente ──────────────────────────
        presentacion.paso(self, "Un episodio")

        m30, p30, k30 = ronda(30, 102)
        flecha30 = Line([x_de(mejor), Y_FILA - 1.35, 0], [x_de(m30[k30]) + 1e-3, Y_FILA - 1.35, 0],
                        stroke_color=PAL.adapta, stroke_width=5).add_tip(tip_length=0.2)
        et30 = T6.etiqueta("30 episodios", PAL, fs=28, color=PAL.tinta).move_to(et1)
        # con 30 episodios el sesgo es de centesimas: la flecha desaparece
        self.play(Transform(verdad, p30), FadeOut(flecha), Transform(et1, et30), run_time=1.3)
        self.wait(0.4)

        # ── 2. con treinta, casi no ───────────────────────────────────────
        presentacion.paso(self, "Treinta episodios")

        # La curva MEDIDA en la tesis: MA estimado contra episodios.
        filas = sorted(D["sensibilidad"])
        gx0, gx1, gy0, gy1 = 1.9, 6.4, -2.9, 0.9
        ma_lo, ma_hi = 0.15, 0.35
        lx = lambda e: gx0 + (gx1 - gx0) * np.log10(e) / np.log10(30)
        ly = lambda v: gy0 + (gy1 - gy0) * (v - ma_lo) / (ma_hi - ma_lo)
        base = Line([gx0 - 0.1, gy0, 0], [gx1 + 0.1, gy0, 0], stroke_color=PAL.apoyo, stroke_width=2)
        umbral = DashedLine([gx0 - 0.1, ly(D["umbral"]), 0], [gx1 + 0.1, ly(D["umbral"]), 0],
                            dash_length=0.12, stroke_color=PAL.tinta, stroke_width=2.5)
        et_u = T6.cifra(T6.pct(D["umbral"], 0), PAL, fs=26, color=PAL.tinta)
        et_u.next_to(umbral, LEFT, buff=0.12)
        pts = [[lx(e), ly(v), 0] for e, v in filas]
        traza = Line(pts[0], pts[1], stroke_color=PAL.priv, stroke_width=4)
        for a, b in zip(pts[1:], pts[2:]):
            traza.append_points(Line(a, b).points)
        puntos = VGroup(*[Dot(p, radius=0.09, color=PAL.priv) for p in pts])
        eps = VGroup(*[T6.etiqueta(str(e), PAL, fs=24).move_to([lx(e), gy0 - 0.32, 0])
                       for e, _ in filas])
        fin = T6.cifra(f"{filas[-1][1]:.3f}", PAL, fs=30, color=PAL.priv)
        fin.next_to(puntos[-1], UP, buff=0.18)
        ini = T6.cifra(f"{filas[0][1]:.3f}", PAL, fs=30, color=PAL.priv)
        ini.next_to(puntos[0], DOWN, buff=0.18).shift(RIGHT * 0.35)
        self.play(Create(base), Create(umbral), FadeIn(et_u), FadeIn(eps), run_time=0.8)
        self.play(Create(traza), FadeIn(puntos), run_time=1.6, rate_func=linear)
        self.play(FadeIn(ini), FadeIn(fin), run_time=0.5)
        self.wait(0.8)
        presentacion.paso(self, "La curva de la tesis")
