from manim import *
import numpy as np


class PerturbacionesOrbitales(Scene):
    def construct(self):
        titulo = Text("Perturbaciones orbitales", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        intro = Text("La órbita kepleriana perfecta no existe: el mundo real la deforma",
                     font_size=22, color=GREY_B).next_to(titulo, DOWN, buff=0.3)
        self.play(FadeIn(intro), run_time=1.2)

        centro = DOWN * 1 + LEFT * 3.2
        tierra = Circle(radius=0.45, color=BLUE_D, fill_opacity=1, fill_color=BLUE_D)
        tierra.move_to(centro)
        # Tierra achatada: el J2 nace de este abultamiento
        tierra.stretch(1.25, dim=0)
        orbita = Ellipse(width=4.2, height=2.4, color=BLUE_B).move_to(centro)
        self.play(FadeIn(tierra), Create(orbita), run_time=1.5)

        # J2: precesion — la elipse gira lentamente
        j2_txt = VGroup(
            Text("J2: achatamiento terrestre", font_size=22, color=YELLOW),
            Text("la órbita precesa (gira su plano)", font_size=19, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(RIGHT * 3.7 + UP * 1.4)
        self.play(FadeIn(j2_txt), run_time=1)
        traza = orbita.copy().set_stroke(opacity=0.25)
        self.add(traza)
        self.play(Rotate(orbita, angle=PI / 3, about_point=centro), run_time=3,
                  rate_func=linear)

        # Arrastre atmosferico: la orbita baja y se circulariza
        drag_txt = VGroup(
            Text("Arrastre atmosférico (LEO)", font_size=22, color=RED_D),
            Text("frena y encoge la órbita", font_size=19, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(RIGHT * 3.7 + UP * 0.2)
        self.play(FadeIn(drag_txt), run_time=1)
        self.play(orbita.animate.scale(0.72, about_point=centro), run_time=2.5)

        # Tercer cuerpo y presion solar
        luna = Dot(RIGHT * 6.3 + DOWN * 2.6, color=GREY_B, radius=0.12)
        luna_txt = Text("Luna/Sol: tercer cuerpo", font_size=20, color=GREY_B)
        luna_txt.next_to(luna, UP, buff=0.2).shift(LEFT * 0.9)
        tiron = Arrow(orbita.get_right(), luna.get_center(), color=GREY_B,
                      buff=0.2, stroke_width=3)
        self.play(FadeIn(luna), FadeIn(luna_txt), GrowArrow(tiron), run_time=1.5)
        self.play(orbita.animate.stretch(1.12, dim=0), run_time=1.2)

        srp_txt = VGroup(
            Text("Presión de radiación solar", font_size=22, color=GOLD),
            Text("los fotones también empujan", font_size=19, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(RIGHT * 3.7 + DOWN * 1.2)
        fotones = VGroup(*[
            Arrow(LEFT * 6.8 + UP * (0.4 - 0.4 * i) + DOWN * 1, LEFT * 5.8 + UP * (0.4 - 0.4 * i) + DOWN * 1,
                  color=GOLD, buff=0, stroke_width=3, max_tip_length_to_length_ratio=0.2)
            for i in range(3)
        ])
        self.play(FadeIn(srp_txt), LaggedStart(*[GrowArrow(f) for f in fotones],
                                               lag_ratio=0.2), run_time=1.8)

        cierre = Text("Mantener una órbita exige corregirla: por eso los satélites llevan propelente",
                      font_size=21, color=BLUE_B).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
