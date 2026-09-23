import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import (DashedVMobject, DOWN, LEFT, RIGHT, UP, Create, DashedLine, FadeIn, FadeOut,
                   GrowFromEdge, Line, Rectangle, Scene, Transform, VGroup)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
D = T6.datos_tesis()
SEM = [g["semilla"] for g in D["g2b"]]
ORC = {g["semilla"]: g["oraculo"] for g in D["g2b"]}
MOCK = D["piloto_mock"]
TOPE_R5 = 1.05                       # R5: invalida toda corrida > 1.05 x oraculo

Y_BASE = -2.8
ALTO_MAX = 5.1                       # alto del piloto mas alto
V_MAX = max(MOCK.values())
ANCHO = 0.95


def alto(v):
    return ALTO_MAX * v / V_MAX


def barra(x, v, color):
    r = Rectangle(width=ANCHO, height=alto(v), stroke_width=0, fill_color=color,
                  fill_opacity=1.0)
    return r.move_to([x, Y_BASE + alto(v) / 2, 0])


def leyenda(texto, color, linea=False, peso="NORMAL"):
    if linea:
        m = DashedLine(LEFT * 0.26, RIGHT * 0.26, dash_length=0.1, stroke_color=color,
                       stroke_width=3)
    else:
        m = Rectangle(width=0.34, height=0.34, stroke_width=0, fill_color=color,
                      fill_opacity=1.0)
    e = T6.etiqueta(texto, PAL, fs=28, color=color, peso=peso)
    return VGroup(m, e.next_to(m, RIGHT, buff=0.16))


class GuardiaR5(Scene):
    """El dia que el protocolo tumbo un resultado espectacular: el piloto
    salia casi 3 veces por encima del oraculo, lo que ninguna politica
    legitima puede hacer. La regla R5 lo invalida sola."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        xs = [-3.4, 0.0, 3.4]
        suelo = Line([-6.0, Y_BASE, 0], [6.0, Y_BASE, 0], stroke_color=PAL.apoyo,
                     stroke_width=2)
        et_s = VGroup(*[T6.etiqueta(f"Semilla {s}", PAL, fs=28).move_to([x, Y_BASE - 0.42, 0])
                        for x, s in zip(xs, SEM)])
        orc = [barra(x - 0.55, ORC[s], PAL.priv) for x, s in zip(xs, SEM)]
        self.play(FadeIn(suelo), FadeIn(et_s), run_time=0.7)
        self.play(*[GrowFromEdge(b, DOWN) for b in orc], run_time=1.1)
        topes = VGroup(*[DashedLine([x - 1.25, Y_BASE + alto(TOPE_R5 * ORC[s]), 0],
                                    [x + 1.25, Y_BASE + alto(TOPE_R5 * ORC[s]), 0],
                                    dash_length=0.12, stroke_color=PAL.tinta, stroke_width=3)
                         for x, s in zip(xs, SEM)])
        ley = [leyenda("Oráculo", PAL.priv), leyenda("Tope R5", PAL.tinta, linea=True),
               leyenda("Piloto", PAL.adapta)]
        VGroup(*ley).arrange(RIGHT, buff=0.9).move_to([0, 3.4, 0])
        self.play(Create(topes), FadeIn(ley[0]), FadeIn(ley[1]), run_time=0.9)

        # ── 1. el techo que nada legitimo puede pasar ─────────────────────
        presentacion.paso(self, "El techo")

        pil = [barra(x + 0.55, MOCK[s], PAL.adapta) for x, s in zip(xs, SEM)]
        self.play(*[GrowFromEdge(b, DOWN) for b in pil], run_time=1.6)
        veces = VGroup()
        for b, s in zip(pil, SEM):
            c = T6.cifra(f"{MOCK[s] / ORC[s]:.1f}×", PAL, fs=34, color=PAL.adapta)
            c.next_to(b, UP, buff=0.16)
            veces.add(c)
        self.play(FadeIn(veces, shift=DOWN * 0.1), FadeIn(ley[2]), run_time=0.6)
        self.wait(0.6)

        # ── 2. el piloto: un resultado demasiado bueno ────────────────────
        presentacion.paso(self, "El piloto")

        rojas = [barra(x + 0.55, MOCK[s], PAL.no) for x, s in zip(xs, SEM)]
        cruces = VGroup()
        for b in pil:
            a = Line(b.get_corner(DOWN + LEFT), b.get_corner(UP + RIGHT),
                     stroke_color=PAL.fondo, stroke_width=7)
            z = Line(b.get_corner(UP + LEFT), b.get_corner(DOWN + RIGHT),
                     stroke_color=PAL.fondo, stroke_width=7)
            cruces.add(a, z)
        veces_r = VGroup(*[v.copy().set_color(PAL.no) for v in veces])
        self.play(*[Transform(a, b) for a, b in zip(pil, rojas)],
                  Transform(veces, veces_r), run_time=0.6)
        self.play(Create(cruces), run_time=0.8)
        inv = leyenda("Invalidado", PAL.no, peso="BOLD")
        inv.move_to(ley[2], aligned_edge=LEFT)
        self.play(FadeOut(ley[2]), FadeIn(inv), run_time=0.5)
        self.wait(0.8)
        presentacion.paso(self, "Invalidado")
