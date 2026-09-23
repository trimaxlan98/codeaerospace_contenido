import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Create, DashedVMobject, FadeIn,
                   FadeOut, GrowArrow, MathTex, RoundedRectangle, Scene, VGroup)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()


def caja(w, h, color, grosor=4):
    return RoundedRectangle(corner_radius=0.18, width=w, height=h, stroke_color=color,
                            stroke_width=grosor)


class Ctde(Scene):
    """CTDE, el paradigma de QMIX: se ENTRENA con un mezclador que ve el
    estado global y se EJECUTA sin el, cada agente con su observacion. El
    mezclador es monotono: si un agente mejora, el equipo no empeora."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        xs = [-3.4, 0.0, 3.4]
        y_ag, y_mz, y_st = -1.6, 1.1, 2.9
        agentes = VGroup()
        for i, x in enumerate(xs):
            b = caja(1.9, 1.0, PAL.adapta).move_to([x, y_ag, 0])
            q = MathTex(rf"Q_{i + 1}", color=PAL.adapta, font_size=44).move_to(b)
            agentes.add(VGroup(b, q))
        obs = VGroup(*[MathTex(rf"o_{i + 1}", color=PAL.tinta, font_size=40)
                       .move_to([x, y_ag - 1.35, 0]) for i, x in enumerate(xs)])
        f_obs = VGroup(*[Arrow(o.get_top(), a.get_bottom(), buff=0.1, stroke_width=4,
                               color=PAL.tinta, max_tip_length_to_length_ratio=0.3)
                         for o, a in zip(obs, agentes)])
        mezc = caja(5.2, 1.0, PAL.priv).move_to([0, y_mz, 0])
        q_tot = MathTex(r"Q_{\mathrm{tot}}", color=PAL.priv, font_size=44).move_to(mezc)
        et_m = T6.etiqueta("Mezclador", PAL, fs=28, color=PAL.priv).next_to(mezc, RIGHT, buff=0.3)
        estado = MathTex("s", color=PAL.priv, font_size=48).move_to([0, y_st, 0])
        et_s = T6.etiqueta("Estado global", PAL, fs=28, color=PAL.priv).next_to(estado, RIGHT, buff=0.3)
        f_mz = VGroup(*[Arrow(a.get_top(), mezc.get_bottom() + RIGHT * (x * 0.55), buff=0.1,
                              stroke_width=4, color=PAL.adapta,
                              max_tip_length_to_length_ratio=0.25)
                        for a, x in zip(agentes, xs)])
        f_st = Arrow(estado.get_bottom(), mezc.get_top(), buff=0.12, stroke_width=4,
                     color=PAL.priv, max_tip_length_to_length_ratio=0.3)
        entrenar = T6.etiqueta("Entrenar", PAL, fs=32, color=PAL.tinta, peso="BOLD")
        entrenar.move_to([-5.3, y_st, 0])

        self.play(FadeIn(entrenar), *[FadeIn(a) for a in agentes], run_time=0.7)
        self.play(FadeIn(obs), *[GrowArrow(f) for f in f_obs], run_time=0.7)
        self.play(FadeIn(mezc), FadeIn(q_tot), FadeIn(et_m), *[GrowArrow(f) for f in f_mz],
                  run_time=0.9)
        self.play(FadeIn(estado), FadeIn(et_s), GrowArrow(f_st), run_time=0.7)
        mono = MathTex(r"\frac{\partial Q_{\mathrm{tot}}}{\partial Q_i}\ge 0", color=PAL.priv,
                       font_size=40).next_to(mezc, LEFT, buff=0.35)
        self.play(FadeIn(mono), run_time=0.6)

        # ── 1. entrenar viendo todo ───────────────────────────────────────
        presentacion.paso(self, "Entrenar")

        ejecutar = T6.etiqueta("Ejecutar", PAL, fs=32, color=PAL.tinta, peso="BOLD").move_to(entrenar)
        fantasma = DashedVMobject(mezc.copy().set_stroke(PAL.apoyo, width=2), num_dashes=40)
        self.play(FadeOut(VGroup(q_tot, et_m, f_mz, estado, et_s, f_st, mono)),
                  FadeOut(mezc), FadeIn(fantasma), FadeOut(entrenar), FadeIn(ejecutar),
                  run_time=1.0)
        # cada agente decide solo, con lo que ve: acciones hacia la red
        acc = VGroup(*[Arrow(a.get_top(), a.get_top() + UP * 1.0, buff=0.08, stroke_width=5,
                             color=PAL.adapta, max_tip_length_to_length_ratio=0.35)
                       for a in agentes])
        a_txt = VGroup(*[MathTex(rf"a_{i + 1}", color=PAL.adapta, font_size=40)
                         .next_to(f, UP, buff=0.08) for i, f in enumerate(acc)])
        self.play(*[GrowArrow(f) for f in acc], FadeIn(a_txt), run_time=0.8)
        self.wait(0.8)
        presentacion.paso(self, "Ejecutar")
