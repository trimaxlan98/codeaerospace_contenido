import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import (DOWN, LEFT, RIGHT, UP, Create, DashedLine, Dot, FadeIn,
                   GrowFromCenter, Line, Scene, VGroup, linear)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
H = {h["id"]: h for h in T6.HITOS}
A0, A1 = 2026.0, 2030.5
X0, X1, Y = -6.2, 6.2, -0.4


def x_de(anio):
    return X0 + (X1 - X0) * (anio - A0) / (A1 - A0)


class Horizonte(Scene):
    """El doctorado (feb-2026 a feb-2030) contra el reloj del estandar: la
    primera release 6G se congela, potencialmente, a inicios de 2029. La
    defensa cae justo del otro lado de esa frontera."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        riel = Line([X0, Y, 0], [X1, Y, 0], stroke_color=PAL.tenue, stroke_width=12)
        anios = VGroup()
        for a in range(2026, 2031):
            t = Line([x_de(a), Y - 0.22, 0], [x_de(a), Y + 0.22, 0], stroke_color=PAL.apoyo,
                     stroke_width=2)
            e = T6.etiqueta(str(a), PAL, fs=28).move_to([x_de(a), Y + 0.6, 0])
            anios.add(VGroup(t, e))
        doc = Line([x_de(T6.INICIO_DOCTORADO), Y, 0], [x_de(T6.FIN_DOCTORADO), Y, 0],
                   stroke_color=PAL.apoyo, stroke_width=12, stroke_opacity=0.6)
        self.play(Create(riel), FadeIn(anios), run_time=0.9)
        self.play(Create(doc), run_time=0.8)
        hecho = Line([x_de(T6.INICIO_DOCTORADO), Y, 0], [x_de(H["hoy"]["anio"]), Y, 0],
                     stroke_color=PAL.adapta, stroke_width=12)
        self.play(Create(hecho), run_time=1.0, rate_func=linear)

        def hito(clave, color, alto=1.1, lado=0):
            """Hito colgado BAJO el riel (los anios van arriba). `lado` saca
            la etiqueta a la izquierda (-1) o derecha (+1) del palo, para
            que dos hitos cercanos no se pisen."""
            x = x_de(H[clave]["anio"])
            d = Dot([x, Y, 0], radius=0.14, color=color)
            y2 = Y - alto
            palo = Line([x, Y - 0.18, 0], [x, y2, 0], stroke_color=color, stroke_width=2.5)
            e = T6.etiqueta(H[clave]["texto"], PAL, fs=30, color=color, peso="BOLD")
            if lado < 0:
                e.next_to([x, y2, 0], LEFT, buff=0.12)
            elif lado > 0:
                e.next_to([x, y2, 0], RIGHT, buff=0.12)
            else:
                e.next_to([x, y2, 0], DOWN, buff=0.12)
            return VGroup(palo, d, e)

        hoy = hito("hoy", PAL.adapta, alto=0.9, lado=-1)
        wit = hito("witcom", PAL.tinta, alto=1.7, lado=1)
        self.play(GrowFromCenter(hoy), run_time=0.5)
        self.play(GrowFromCenter(wit), run_time=0.5)

        # ── 1. hoy: semestre 2 de 8 ───────────────────────────────────────
        presentacion.paso(self, "Hoy")

        fr = hito("freeze", PAL.priv, alto=1.1)
        franja = DashedLine([x_de(H["freeze"]["anio"]), Y + 2.4, 0],
                            [x_de(H["freeze"]["anio"]), Y + 0.95, 0], dash_length=0.12,
                            stroke_color=PAL.priv, stroke_width=2)
        self.play(GrowFromCenter(fr), Create(franja), run_time=0.8)

        # ── 2. el estandar se congela ─────────────────────────────────────
        presentacion.paso(self, "Freeze 6G")

        de = hito("defensa", PAL.ok, alto=1.1)
        self.play(GrowFromCenter(de), run_time=0.6)
        self.wait(0.8)
        presentacion.paso(self, "Defensa")
