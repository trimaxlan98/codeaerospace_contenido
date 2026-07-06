from manim import *
import numpy as np


class MediosDeTransmision(Scene):
    def construct(self):
        titulo = Text("Medios de transmisión", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Tres franjas: cobre, fibra, radio
        y_cobre, y_fibra, y_radio = 1.6, 0.0, -1.7

        # Cobre: par trenzado
        cobre_txt = Text("Cobre (par trenzado / coaxial)", font_size=21, color=GOLD)
        cobre_txt.move_to(LEFT * 4 + UP * (y_cobre + 0.7))
        trenza1 = FunctionGraph(lambda x: 0.18 * np.sin(3 * x), x_range=[-5.5, 0.5],
                                color=GOLD).shift(UP * y_cobre)
        trenza2 = FunctionGraph(lambda x: -0.18 * np.sin(3 * x), x_range=[-5.5, 0.5],
                                color=GOLD).shift(UP * y_cobre)
        self.play(FadeIn(cobre_txt), Create(trenza1), Create(trenza2), run_time=1.8)

        # Fibra: luz rebotando por reflexion total interna
        fibra_txt = Text("Fibra óptica", font_size=21, color=BLUE_B)
        fibra_txt.move_to(LEFT * 4 + UP * (y_fibra + 0.65))
        tubo = VGroup(
            Line(LEFT * 5.5 + UP * (y_fibra + 0.3), RIGHT * 0.5 + UP * (y_fibra + 0.3),
                 color=BLUE_D),
            Line(LEFT * 5.5 + UP * (y_fibra - 0.3), RIGHT * 0.5 + UP * (y_fibra - 0.3),
                 color=BLUE_D),
        )
        zigzag = VMobject(color=BLUE_B)
        pts = []
        for i in range(7):
            x = -5.5 + i
            y = y_fibra + (0.25 if i % 2 == 0 else -0.25)
            pts.append(np.array([x, y, 0]))
        zigzag.set_points_as_corners(pts)
        self.play(FadeIn(fibra_txt), Create(tubo), run_time=1.2)
        pulso = Dot(pts[0], color=YELLOW, radius=0.07)
        self.play(Create(zigzag), run_time=1.5)
        self.play(MoveAlongPath(pulso, zigzag), run_time=1.5, rate_func=linear)

        # Radio: ondas desde una antena
        radio_txt = Text("Radio (inalámbrico / satélite)", font_size=21, color=GREY_B)
        radio_txt.move_to(LEFT * 4 + UP * (y_radio + 0.75))
        antena = Line(LEFT * 5 + UP * (y_radio - 0.4), LEFT * 5 + UP * (y_radio + 0.4),
                      color=GREY_B)
        ondas = VGroup(*[
            Arc(radius=r, start_angle=-PI / 3, angle=2 * PI / 3, color=GREY_B,
                arc_center=LEFT * 5 + UP * (y_radio + 0.4))
            for r in [0.5, 1.0, 1.5]
        ])
        self.play(FadeIn(radio_txt), Create(antena), run_time=1)
        self.play(LaggedStart(*[Create(o) for o in ondas], lag_ratio=0.3), run_time=2)

        # Comparacion: capacidad y alcance
        tabla = VGroup(
            Text("Medio", font_size=20, color=GREY_B),
            Text("Capacidad", font_size=20, color=GREY_B),
            Text("Cobre", font_size=20, color=GOLD),
            Text("~10 Gb/s, corto alcance", font_size=20, color=GOLD),
            Text("Fibra", font_size=20, color=BLUE_B),
            Text("Tb/s, miles de km", font_size=20, color=BLUE_B),
            Text("Radio", font_size=20, color=GREY_B),
            Text("Gb/s, movilidad total", font_size=20, color=GREY_B),
        ).arrange_in_grid(rows=4, cols=2, buff=(0.6, 0.28), col_alignments="ll")
        tabla.move_to(RIGHT * 3.9 + DOWN * 0.1)
        self.play(FadeIn(tabla, lag_ratio=0.1), run_time=2.5)

        cierre = Text("La fibra es la columna vertebral; la radio, la última milla móvil",
                      font_size=21, color=YELLOW).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
