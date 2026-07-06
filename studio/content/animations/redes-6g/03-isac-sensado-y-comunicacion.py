from manim import *
import numpy as np


class IsacSensadoYComunicacion(Scene):
    def construct(self):
        titulo = Text("ISAC: sensado y comunicación integrados",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        idea = Text("La misma onda que lleva tus datos funciona como radar",
                    font_size=21, color=GREY_B).next_to(titulo, DOWN, buff=0.25)
        self.play(FadeIn(idea), run_time=1.2)

        # Estacion base
        torre = VGroup(
            Line(DOWN * 2.8 + LEFT * 5, DOWN * 0.8 + LEFT * 5, color=GREY_B,
                 stroke_width=6),
            Rectangle(width=0.5, height=0.35, color=BLUE_B, fill_opacity=0.5,
                      fill_color=BLUE_B).move_to(DOWN * 0.7 + LEFT * 5),
        )
        torre_txt = Text("Estación base 6G", font_size=18, color=BLUE_B)
        torre_txt.next_to(torre, DOWN, buff=0.2)
        self.play(FadeIn(torre), FadeIn(torre_txt), run_time=1.2)

        # Usuario con telefono (comunicacion)
        usuario = Square(side_length=0.35, color=YELLOW, fill_opacity=0.6,
                         fill_color=YELLOW).move_to(RIGHT * 4.4 + DOWN * 2.3)
        usr_txt = Text("Usuario: datos", font_size=18, color=YELLOW)
        usr_txt.next_to(usuario, DOWN, buff=0.2)
        # Dron (objeto a sensar, no conectado)
        dron = VGroup(
            Rectangle(width=0.45, height=0.18, color=GREY_B, fill_opacity=0.7,
                      fill_color=GREY_B),
            Dot(LEFT * 0.28, color=GREY_B, radius=0.07),
            Dot(RIGHT * 0.28, color=GREY_B, radius=0.07),
        ).move_to(RIGHT * 1.6 + UP * 1.7)
        dron_txt = Text("Dron: sin conexión", font_size=18, color=GREY_B)
        dron_txt.next_to(dron, UP, buff=0.2)
        self.play(FadeIn(usuario), FadeIn(usr_txt), FadeIn(dron), FadeIn(dron_txt),
                  run_time=1.5)

        origen = torre[1].get_center()

        # Haz de comunicacion al usuario
        com = VGroup(*[
            Arc(radius=r, start_angle=-0.35, angle=0.28, color=YELLOW,
                arc_center=origen)
            for r in [1.2, 2.2, 3.2, 4.2]
        ])
        com_txt = Text("comunicación", font_size=17, color=YELLOW)
        com_txt.move_to(origen + RIGHT * 3.2 + DOWN * 1.4)
        self.play(LaggedStart(*[Create(c) for c in com], lag_ratio=0.2),
                  FadeIn(com_txt), run_time=2)

        # La misma senal rebota en el dron: eco
        ida = Line(origen, dron.get_center(), color=BLUE_B)
        eco = DashedLine(dron.get_center(), origen, color=GOLD)
        eco_txt = Text("eco (sensado)", font_size=17, color=GOLD)
        eco_txt.next_to(ida.get_center(), UP, buff=0.25)
        pulso = Dot(origen, color=BLUE_B, radius=0.07)
        self.play(Create(ida), FadeIn(pulso), run_time=0.8)
        self.play(pulso.animate.move_to(dron.get_center()), run_time=1.1,
                  rate_func=linear)
        self.play(pulso.animate.set_color(GOLD).move_to(origen), Create(eco),
                  FadeIn(eco_txt), run_time=1.1, rate_func=linear)
        self.play(FadeOut(pulso), run_time=0.4)

        # Del eco se extraen posicion y velocidad
        medidas = VGroup(
            Text("retardo → distancia: 212 m", font_size=19, color=GOLD),
            Text("Doppler → velocidad: 14 m/s", font_size=19, color=GOLD),
            Text("ángulo → dirección: 38°", font_size=19, color=GOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(LEFT * 3.4 + UP * 1.6)
        self.play(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.3) for m in medidas],
                              lag_ratio=0.3), run_time=2.5)
        marco = SurroundingRectangle(dron, color=GOLD, buff=0.15)
        self.play(Create(marco), run_time=0.8)
        self.play(VGroup(dron, marco).animate.shift(RIGHT * 1.6), run_time=2,
                  rate_func=linear)

        cierre = Text("Una sola infraestructura: red de datos y sensor urbano a la vez",
                      font_size=21, color=BLUE_B).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
