from manim import *
import numpy as np


class ManiobrasOrbitales(Scene):
    def construct(self):
        titulo = Text("Maniobras orbitales: la transferencia de Hohmann",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        centro = DOWN * 0.5 + LEFT * 2.2
        tierra = Circle(radius=0.4, color=BLUE_D, fill_opacity=1, fill_color=BLUE_D)
        tierra.move_to(centro)
        r1, r2 = 1.2, 2.9
        baja = Circle(radius=r1, color=BLUE_B).move_to(centro)
        alta = Circle(radius=r2, color=GREY_B).move_to(centro)
        baja_txt = Text("Órbita inicial", font_size=19, color=BLUE_B)
        baja_txt.next_to(baja, DOWN, buff=0.1).shift(RIGHT * 1.1)
        alta_txt = Text("Órbita objetivo", font_size=19, color=GREY_B)
        alta_txt.next_to(alta, UP, buff=0.15)
        self.play(GrowFromCenter(tierra), Create(baja), Create(alta),
                  FadeIn(baja_txt), FadeIn(alta_txt), run_time=2)

        # Satelite en orbita baja
        sat = Dot(centro + RIGHT * r1, color=YELLOW, radius=0.09)
        self.play(FadeIn(sat), run_time=0.4)
        self.play(Rotate(sat, angle=TAU, about_point=centro), run_time=2.5,
                  rate_func=linear)

        # Elipse de transferencia tangente a ambas orbitas
        a_t = (r1 + r2) / 2
        b_t = np.sqrt(r1 * r2)
        transfer = Ellipse(width=2 * a_t, height=2 * b_t, color=GOLD)
        transfer.move_to(centro + LEFT * (a_t - r1))
        media = DashedVMobject(transfer, num_dashes=40)

        # Delta-v 1 en perigeo
        dv1 = Arrow(centro + RIGHT * r1, centro + RIGHT * r1 + UP * 0.9,
                    color=YELLOW, buff=0)
        dv1_txt = MathTex(r"\Delta v_1", font_size=32, color=YELLOW)
        dv1_txt.next_to(dv1, RIGHT, buff=0.15)
        paso1 = Text("1) Impulso tangente: entrar a la elipse de transferencia",
                     font_size=21, color=YELLOW).to_edge(DOWN)
        self.play(GrowArrow(dv1), Write(dv1_txt), FadeIn(paso1), run_time=1.5)
        self.play(Create(media), run_time=1.5)

        # Vuelo por la mitad de la elipse
        arco = ParametricFunction(
            lambda t: transfer.point_from_proportion(t % 1.0),
            t_range=[0, 0.5], color=GOLD, stroke_width=0,
        )
        self.play(MoveAlongPath(sat, arco), run_time=3, rate_func=smooth)

        # Delta-v 2 en apogeo para circularizar
        apo = centro + LEFT * r2
        dv2 = Arrow(apo, apo + DOWN * 0.9, color=GOLD, buff=0)
        dv2_txt = MathTex(r"\Delta v_2", font_size=32, color=GOLD)
        dv2_txt.next_to(dv2, LEFT, buff=0.15)
        paso2 = Text("2) Segundo impulso en el apogeo: circularizar",
                     font_size=21, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(paso1, paso2), GrowArrow(dv2), Write(dv2_txt),
                  run_time=1.5)
        self.play(Rotate(sat, angle=-PI * 0.9, about_point=centro), run_time=3,
                  rate_func=linear)

        nota = Text("Dos impulsos, mínima energía: así se sube de LEO a GEO",
                    font_size=22, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(paso2, nota), run_time=1.2)
        self.wait(2)
