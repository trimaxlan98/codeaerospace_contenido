from manim import *
import numpy as np


class SistemasDeReferenciaYActitud(Scene):
    def construct(self):
        titulo = Text("Sistemas de referencia y actitud", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Marco inercial: fijo respecto a las estrellas
        origen_i = LEFT * 3.8 + DOWN * 0.6
        inercial = VGroup(
            Arrow(origen_i, origen_i + RIGHT * 1.6, color=GREY_B, buff=0),
            Arrow(origen_i, origen_i + UP * 1.6, color=GREY_B, buff=0),
        )
        xi = MathTex("X_i", font_size=30, color=GREY_B).next_to(inercial[0], RIGHT, buff=0.1)
        yi = MathTex("Y_i", font_size=30, color=GREY_B).next_to(inercial[1], UP, buff=0.1)
        inercial_txt = Text("Marco inercial\n(fijo a las estrellas)", font_size=20,
                            color=GREY_B, line_spacing=0.9)
        inercial_txt.next_to(origen_i, DOWN, buff=0.8)
        estrellas = VGroup(*[
            Star(n=4, density=1, outer_radius=0.07, color=WHITE, fill_opacity=1)
            .move_to(origen_i + np.array([x, y, 0]))
            for x, y in [(-1.3, 2.1), (0.4, 2.5), (1.6, 2.2), (-0.7, 1.7)]
        ])
        self.play(GrowArrow(inercial[0]), GrowArrow(inercial[1]),
                  FadeIn(xi), FadeIn(yi), FadeIn(inercial_txt), FadeIn(estrellas),
                  run_time=2)

        # Marco del cuerpo: viaja con el satelite
        origen_b = RIGHT * 2.8 + DOWN * 0.6
        cuerpo = VGroup(
            Rectangle(width=1.1, height=0.7, color=BLUE_D, fill_opacity=0.3,
                      fill_color=BLUE_D),
            Arrow(ORIGIN, RIGHT * 1.4, color=YELLOW, buff=0),
            Arrow(ORIGIN, UP * 1.4, color=BLUE_B, buff=0),
        ).move_to(origen_b)
        cuerpo[1].put_start_and_end_on(origen_b, origen_b + RIGHT * 1.4)
        cuerpo[2].put_start_and_end_on(origen_b, origen_b + UP * 1.4)
        xb = MathTex("X_b", font_size=30, color=YELLOW).next_to(cuerpo[1], RIGHT, buff=0.1)
        yb = MathTex("Y_b", font_size=30, color=BLUE_B).next_to(cuerpo[2], UP, buff=0.1)
        cuerpo_txt = Text("Marco del cuerpo\n(pegado al satélite)", font_size=20,
                          color=BLUE_B, line_spacing=0.9)
        cuerpo_txt.next_to(origen_b, DOWN, buff=0.8)
        self.play(FadeIn(cuerpo), FadeIn(xb), FadeIn(yb), FadeIn(cuerpo_txt), run_time=1.5)

        # La actitud es la rotacion entre ambos marcos
        actitud = Text("Actitud = rotación que lleva un marco al otro",
                       font_size=23, color=GOLD).to_edge(DOWN)
        self.play(FadeIn(actitud), run_time=1)
        giro = VGroup(cuerpo, xb, yb)
        self.play(Rotate(giro, angle=PI / 5, about_point=origen_b), run_time=2)
        arco = Arc(radius=1.0, start_angle=0, angle=PI / 5, color=GOLD,
                   arc_center=origen_b)
        theta = MathTex(r"\theta", font_size=32, color=GOLD)
        theta.move_to(origen_b + 1.3 * np.array([np.cos(PI / 10), np.sin(PI / 10), 0]))
        self.play(Create(arco), Write(theta), run_time=1.2)

        # Roll, pitch, yaw
        rpy = VGroup(
            Text("Alabeo (roll)", font_size=20, color=YELLOW),
            Text("Cabeceo (pitch)", font_size=20, color=BLUE_B),
            Text("Guiñada (yaw)", font_size=20, color=GREY_B),
        ).arrange(RIGHT, buff=0.7).next_to(actitud, UP, buff=0.3)
        self.play(FadeIn(rpy, lag_ratio=0.3), run_time=1.5)
        self.play(Wiggle(cuerpo), run_time=1.5)

        # En 3D se usan cuaterniones
        cierre = Text("En 3D la actitud se guarda como cuaternión: sin ambigüedades ni bloqueos",
                      font_size=20, color=GREY_B).to_edge(DOWN)
        q = MathTex(r"q = (q_0,\, q_1,\, q_2,\, q_3)", font_size=34, color=GOLD)
        q.next_to(cierre, UP, buff=0.35)
        self.play(ReplacementTransform(actitud, cierre), FadeOut(rpy), Write(q),
                  run_time=1.8)
        self.wait(2)
