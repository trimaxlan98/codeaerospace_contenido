import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from fractales import imagen_julia, imagen_mandelbrot, miniatura_julia


class FractalesDeEscape(Scene):
    """Demo de fractales.py: Mandelbrot, un Julia y miniaturas baratas.

    Todo el computo es numpy vectorizado y se muestra como ImageMobject:
    apto para el VPS incluso en calidad alta.
    """

    def construct(self):
        titulo = Text("Fractales de escape", font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        mandel = imagen_mandelbrot(res=(960, 540), max_iter=200,
                                   alto_escena=4.6).shift(DOWN * 0.4)
        self.play(FadeIn(mandel), run_time=1.5)
        self.wait(1)

        julia = imagen_julia(complex(-0.123, 0.745), res=(960, 540),
                             max_iter=200, alto_escena=4.6).shift(DOWN * 0.4)
        self.play(FadeOut(mandel), FadeIn(julia), run_time=1.5)
        self.wait(1)
        self.play(FadeOut(julia), run_time=0.8)

        minis = Group(*[
            miniatura_julia(c, lado=150, max_iter=100, alto_escena=1.8)
            for c in (complex(-0.4, 0.6), complex(0.285, 0.01),
                      complex(0, 1), complex(-0.8, 0.156))
        ]).arrange_in_grid(rows=1, cols=4, buff=0.35).shift(DOWN * 0.4)
        self.play(LaggedStart(*[FadeIn(m, scale=0.85) for m in minis],
                              lag_ratio=0.2), run_time=2)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)
