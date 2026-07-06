from manim import *
import numpy as np


class ElSistemaSolarComoEscenario(Scene):
    def construct(self):
        titulo = Text("El sistema solar como escenario de misiones",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Sol y planetas interiores sobre una recta de distancias (no a escala real)
        sol = Circle(radius=0.45, color=YELLOW, fill_opacity=1, fill_color=YELLOW)
        sol.move_to(LEFT * 5.8 + DOWN * 0.5)
        sol_txt = Text("Sol", font_size=20, color=YELLOW).next_to(sol, DOWN, buff=0.2)
        self.play(GrowFromCenter(sol), FadeIn(sol_txt), run_time=1)

        cuerpos = [
            ("Mercurio", 0.9, GREY_B, 0.10),
            ("Venus", 1.9, GOLD, 0.16),
            ("Tierra", 3.0, BLUE_D, 0.18),
            ("Marte", 4.2, RED_D, 0.13),
            ("Júpiter", 5.9, GREY_B, 0.32),
        ]
        planetas = VGroup()
        nombres = VGroup()
        for nombre, dx, color, r in cuerpos:
            p = Circle(radius=r, color=color, fill_opacity=1, fill_color=color)
            p.move_to(sol.get_center() + RIGHT * (0.8 + dx))
            n = Text(nombre, font_size=18, color=GREY_B).next_to(p, DOWN, buff=0.2)
            planetas.add(p)
            nombres.add(n)
        self.play(LaggedStart(*[GrowFromCenter(p) for p in planetas], lag_ratio=0.25),
                  LaggedStart(*[FadeIn(n) for n in nombres], lag_ratio=0.25),
                  run_time=3)

        # Destinos tipicos y tiempos de viaje
        tierra = planetas[2]
        destinos = [
            ("Luna: ~3 días", planetas[2].get_center() + UP * 0.9 + RIGHT * 0.3, BLUE_B),
            ("Marte: 6-9 meses", planetas[3].get_center(), YELLOW),
            ("Júpiter: ~5 años", planetas[4].get_center(), GOLD),
        ]
        luna = Dot(destinos[0][1], color=GREY_B, radius=0.06)
        self.play(FadeIn(luna), run_time=0.5)

        sonda = Dot(color=YELLOW, radius=0.08).move_to(tierra.get_center())
        self.play(FadeIn(sonda), run_time=0.5)
        info = Text("Cada destino impone su energía y su tiempo de viaje",
                    font_size=22, color=GREY_B).to_edge(DOWN)
        self.play(FadeIn(info), run_time=1)

        for etiqueta, punto, color in destinos:
            arco = ArcBetweenPoints(tierra.get_center(), punto, angle=-PI / 3,
                                    color=color)
            tag = Text(etiqueta, font_size=20, color=color)
            tag.next_to(punto, UP, buff=0.3)
            self.play(Create(arco), run_time=1)
            self.play(MoveAlongPath(sonda, arco), FadeIn(tag),
                      run_time=2, rate_func=smooth)
            self.play(sonda.animate.move_to(tierra.get_center()), run_time=0.8)

        cierre = Text("Una misión se diseña alrededor de la mecánica celeste, no contra ella",
                      font_size=22, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(info, cierre), run_time=1.2)
        self.wait(2)
