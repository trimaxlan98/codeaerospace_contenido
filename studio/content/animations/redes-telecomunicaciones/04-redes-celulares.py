from manim import *
import numpy as np


class RedesCelularesDe1GA5G(Scene):
    def construct(self):
        titulo = Text("Redes celulares: de 1G a 5G", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # La idea celular: reutilizar frecuencias en celdas
        celdas = VGroup()
        colores = [BLUE_D, GOLD, GREY_B, GOLD, GREY_B, BLUE_D, BLUE_D]
        centros = [ORIGIN, UP * 1.05 + LEFT * 0.9, UP * 1.05 + RIGHT * 0.9,
                   DOWN * 1.05 + LEFT * 0.9, DOWN * 1.05 + RIGHT * 0.9,
                   LEFT * 1.8, RIGHT * 1.8]
        for c, col in zip(centros, colores):
            hexa = RegularPolygon(n=6, start_angle=PI / 6, color=col)
            hexa.scale(0.62).move_to(c + LEFT * 3.4 + DOWN * 0.5)
            celdas.add(hexa)
        antenas = VGroup(*[
            Dot(h.get_center(), color=YELLOW, radius=0.05) for h in celdas
        ])
        idea = Text("Celdas: la misma frecuencia se reutiliza lejos",
                    font_size=21, color=GREY_B).to_edge(DOWN)
        self.play(LaggedStart(*[Create(h) for h in celdas], lag_ratio=0.15),
                  FadeIn(idea), run_time=2.5)
        self.play(FadeIn(antenas), run_time=0.8)

        # Un movil se mueve entre celdas: handover
        movil = Square(side_length=0.18, color=WHITE, fill_opacity=1)
        movil.move_to(celdas[5].get_center() + DOWN * 0.2)
        enlace = Line(movil.get_center(), antenas[5].get_center(), color=YELLOW)
        self.play(FadeIn(movil), Create(enlace), run_time=0.8)
        self.play(movil.animate.move_to(celdas[0].get_center() + DOWN * 0.3),
                  Transform(enlace, Line(celdas[0].get_center() + DOWN * 0.3,
                                         antenas[0].get_center(), color=YELLOW)),
                  run_time=2)

        # Evolucion generacional: barras de velocidad (escala log)
        gen = [("1G", "voz analógica", 0.3, GREY_B),
               ("2G", "voz digital + SMS", 0.7, GREY_B),
               ("3G", "datos móviles", 1.3, BLUE_D),
               ("4G", "banda ancha móvil", 2.2, BLUE_B),
               ("5G", "baja latencia + IoT", 3.1, GOLD)]
        barras = VGroup()
        for i, (g, desc, h, col) in enumerate(gen):
            barra = Rectangle(width=0.55, height=h, color=col, fill_opacity=0.8,
                              fill_color=col)
            barra.move_to(RIGHT * (1.6 + i * 1.05) + DOWN * 2.2, aligned_edge=DOWN)
            g_txt = Text(g, font_size=20, color=col).next_to(barra, DOWN, buff=0.15)
            barras.add(VGroup(barra, g_txt))
        esc = Text("Velocidad (escala log)", font_size=18, color=GREY_B)
        esc.move_to(RIGHT * 3.7 + UP * 1.6)
        self.play(FadeIn(esc), run_time=0.8)
        for barra in barras:
            self.play(GrowFromEdge(barra[0], DOWN), FadeIn(barra[1]), run_time=0.7)

        descripciones = VGroup(*[
            Text(f"{g}: {d}", font_size=18, color=col)
            for g, d, _, col in gen
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(RIGHT * 3.6 + UP * 0.4)
        self.play(ReplacementTransform(esc, descripciones), run_time=1.5)

        cierre = Text("Cada generación: más espectro, celdas más pequeñas, más inteligencia",
                      font_size=20, color=YELLOW).to_edge(DOWN)
        self.play(ReplacementTransform(idea, cierre), run_time=1.2)
        self.wait(2)
