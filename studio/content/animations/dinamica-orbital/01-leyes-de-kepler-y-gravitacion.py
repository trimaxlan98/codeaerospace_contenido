from manim import *
import numpy as np


class LeyesDeKeplerYGravitacion(Scene):
    def construct(self):
        titulo = Text("Leyes de Kepler y gravitación", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # 1a ley: orbitas elipticas con el Sol en un foco
        a, b = 2.6, 1.9
        c = np.sqrt(a**2 - b**2)
        centro = LEFT * 2.6 + DOWN * 0.6
        orbita = Ellipse(width=2 * a, height=2 * b, color=GREY_B).move_to(centro)
        foco = centro + RIGHT * c
        sol = Dot(foco, color=YELLOW, radius=0.16)
        sol_txt = Text("Sol en un foco", font_size=20, color=YELLOW)
        sol_txt.next_to(sol, DOWN, buff=0.25)
        ley1 = Text("1ª ley: la órbita es una elipse", font_size=22, color=BLUE_B)
        ley1.move_to(RIGHT * 3.7 + UP * 1.9)
        self.play(Create(orbita), FadeIn(sol), FadeIn(sol_txt), FadeIn(ley1), run_time=2)

        # 2a ley: areas iguales en tiempos iguales
        planeta = Dot(orbita.point_from_proportion(0), color=BLUE_D, radius=0.1)
        self.play(FadeIn(planeta), run_time=0.5)

        def sector(p0, p1, color):
            return Polygon(
                foco, orbita.point_from_proportion(p0),
                orbita.point_from_proportion((p0 + p1) / 2),
                orbita.point_from_proportion(p1),
                color=color, fill_opacity=0.35, fill_color=color, stroke_width=1,
            )

        # cerca del perihelio (rapido) y cerca del afelio (lento)
        s1 = sector(0.97, 0.10, GOLD)
        s2 = sector(0.45, 0.55, BLUE_B)
        ley2 = Text("2ª ley: áreas iguales\nen tiempos iguales",
                    font_size=22, color=GOLD, line_spacing=0.9)
        ley2.move_to(RIGHT * 3.7 + UP * 0.8)
        self.play(MoveAlongPath(planeta, orbita), run_time=5, rate_func=linear)
        self.play(FadeIn(s1), FadeIn(s2), FadeIn(ley2), run_time=1.5)
        rapido = Text("rápido", font_size=18, color=GOLD).next_to(s1, RIGHT, buff=0.15)
        lento = Text("lento", font_size=18, color=BLUE_B).next_to(s2, LEFT, buff=0.15)
        self.play(FadeIn(rapido), FadeIn(lento), run_time=1)

        # 3a ley
        ley3 = MathTex(r"T^2 \propto a^3", font_size=40, color=YELLOW)
        ley3.move_to(RIGHT * 3.7 + DOWN * 0.4)
        ley3_txt = Text("3ª ley: período y tamaño\nestán atados", font_size=20,
                        color=GREY_B, line_spacing=0.9).next_to(ley3, DOWN, buff=0.3)
        self.play(Write(ley3), FadeIn(ley3_txt), run_time=2)

        # Newton explica las tres con una sola formula
        newton = MathTex(r"F = \frac{G\,M\,m}{r^2}", font_size=40, color=BLUE_B)
        newton.to_edge(DOWN).shift(UP * 0.2 + LEFT * 2.6)
        newton_txt = Text("Newton: una sola ley explica las tres",
                          font_size=22, color=BLUE_B)
        newton_txt.next_to(newton, RIGHT, buff=0.6)
        flecha = Arrow(sol.get_center(), planeta.get_center(), color=YELLOW, buff=0.15)
        self.play(GrowArrow(flecha), run_time=1)
        self.play(Write(newton), FadeIn(newton_txt), run_time=2)
        self.wait(2)
