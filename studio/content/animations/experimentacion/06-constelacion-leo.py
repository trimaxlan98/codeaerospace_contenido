import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from constelacion import ConstelacionLEO, AnimarConstelacion, enlaces_isl


class ConstelacionLeo(Scene):
    def construct(self):
        titulo = Text("Constelación LEO", font_size=32, color=GOLD).to_edge(UP)
        subtitulo = Text("planos orbitales + enlaces inter-satelitales",
                         font_size=19, color=GREY_B)
        subtitulo.next_to(titulo, DOWN, buff=0.2)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), FadeIn(subtitulo),
                  run_time=1)

        cons = ConstelacionLEO(planos=4, sats_por_plano=9,
                               radio=2.7).shift(DOWN * 0.55)
        self.play(FadeIn(cons.tierra, scale=0.6), run_time=0.8)
        self.play(LaggedStart(
            *[Create(p["camino"]) for p in cons.planos_orbitales],
            lag_ratio=0.2), run_time=1.6)
        self.play(LaggedStart(
            *[FadeIn(p["sats"], scale=0.4) for p in cons.planos_orbitales],
            lag_ratio=0.2), run_time=1.2)

        enlaces = enlaces_isl(cons)
        self.play(FadeIn(enlaces), run_time=0.8)

        # Los enlaces siguen a los satelites gracias a sus updaters
        self.play(AnimarConstelacion(cons, vueltas=0.8), run_time=7)
        enlaces.clear_updaters()
        self.wait(0.6)
