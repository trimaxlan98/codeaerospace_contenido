from manim import *
import numpy as np


class ElementosOrbitalesClasicos(Scene):
    def construct(self):
        titulo = Text("Elementos orbitales clásicos", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Plano de referencia (ecuador) y orbita inclinada, en vista esquematica
        centro = DOWN * 0.6 + LEFT * 2.4
        ecuador = Ellipse(width=6.0, height=1.4, color=GREY_B, stroke_opacity=0.7)
        ecuador.move_to(centro)
        ecuador_txt = Text("Plano de referencia (ecuador)", font_size=18, color=GREY_B)
        ecuador_txt.next_to(ecuador, DOWN, buff=0.2).shift(LEFT * 1.2)
        tierra = Dot(centro, color=BLUE_D, radius=0.14)
        self.play(Create(ecuador), FadeIn(tierra), FadeIn(ecuador_txt), run_time=1.5)

        orbita = Ellipse(width=5.4, height=2.6, color=BLUE_B)
        orbita.move_to(centro).rotate(PI / 7, about_point=centro)
        self.play(Create(orbita), run_time=1.5)

        # Panel con los 6 elementos, iluminados uno a uno
        elems = VGroup(
            MathTex(r"a", r"\;\text{: tamano (semieje mayor)}", font_size=30),
            MathTex(r"e", r"\;\text{: forma (excentricidad)}", font_size=30),
            MathTex(r"i", r"\;\text{: inclinacion del plano}", font_size=30),
            MathTex(r"\Omega", r"\;\text{: giro del plano (nodo)}", font_size=30),
            MathTex(r"\omega", r"\;\text{: giro de la elipse}", font_size=30),
            MathTex(r"\nu", r"\;\text{: posicion en la orbita}", font_size=30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        elems.move_to(RIGHT * 4.1 + DOWN * 0.4)
        for e in elems:
            e[0].set_color(YELLOW)
            e[1].set_color(GREY_B)
        self.play(FadeIn(elems, lag_ratio=0.1), run_time=1.5)

        # a: tamano
        eje = DashedLine(orbita.get_left(), orbita.get_right(), color=YELLOW)
        self.play(Indicate(elems[0], color=YELLOW), Create(eje), run_time=1.5)
        # e: forma — comparamos con una version mas excentrica
        self.play(Indicate(elems[1], color=YELLOW),
                  orbita.animate.stretch(0.65, dim=1), run_time=1.5)
        self.play(orbita.animate.stretch(1 / 0.65, dim=1), run_time=1)
        # i: inclinacion
        self.play(Indicate(elems[2], color=YELLOW),
                  Rotate(orbita, angle=PI / 10, about_point=centro), run_time=1.5)
        # Omega: orientacion del nodo
        self.play(Indicate(elems[3], color=YELLOW),
                  Rotate(orbita, angle=-PI / 5, about_point=centro), run_time=1.5)
        self.play(Rotate(orbita, angle=PI / 10, about_point=centro), run_time=0.8)
        # omega: rotacion de la elipse dentro de su plano
        self.play(Indicate(elems[4], color=YELLOW),
                  Rotate(orbita, angle=PI / 8, about_point=centro), run_time=1.5)
        # nu: donde esta el satelite ahora
        sat = Dot(orbita.point_from_proportion(0), color=GOLD, radius=0.09)
        self.play(FadeIn(sat), Indicate(elems[5], color=YELLOW), run_time=1)
        self.play(MoveAlongPath(sat, orbita), run_time=3, rate_func=linear)

        cierre = Text("Seis números bastan para describir cualquier órbita kepleriana",
                      font_size=22, color=GOLD).to_edge(DOWN)
        self.play(FadeIn(cierre), FadeOut(eje), run_time=1.2)
        self.wait(2)
