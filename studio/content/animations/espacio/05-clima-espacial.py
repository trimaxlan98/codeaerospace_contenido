from manim import *
import numpy as np


class ClimaEspacial(Scene):
    def construct(self):
        titulo = Text("Clima espacial y sus efectos", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Sol activo a la izquierda
        sol = Circle(radius=0.8, color=YELLOW, fill_opacity=1, fill_color=YELLOW)
        sol.move_to(LEFT * 5 + DOWN * 0.5)
        corona = VGroup(*[
            Line(sol.get_center() + 0.9 * np.array([np.cos(a), np.sin(a), 0]),
                 sol.get_center() + 1.25 * np.array([np.cos(a), np.sin(a), 0]),
                 color=GOLD)
            for a in np.linspace(0, TAU, 12, endpoint=False)
        ])
        self.play(GrowFromCenter(sol), Create(corona), run_time=1.5)

        # Tierra con magnetosfera a la derecha
        tierra = Circle(radius=0.5, color=BLUE_D, fill_opacity=1, fill_color=BLUE_D)
        tierra.move_to(RIGHT * 4 + DOWN * 0.5)
        magnetosfera = VGroup(*[
            ArcBetweenPoints(
                tierra.get_center() + UP * 0.5 * s + LEFT * 0.1,
                tierra.get_center() + DOWN * 0.5 * s + LEFT * 0.1,
                angle=PI * 0.8, color=BLUE_B, stroke_opacity=0.7,
            )
            for s in [1.4, 2.0, 2.6]
        ])
        self.play(GrowFromCenter(tierra), Create(magnetosfera), run_time=2)
        mag_txt = Text("Magnetosfera: el escudo", font_size=20, color=BLUE_B)
        mag_txt.next_to(tierra, UP, buff=1.4)
        self.play(FadeIn(mag_txt), run_time=0.8)

        # Fulguracion y eyeccion de masa coronal
        flare = Text("Fulguración + CME", font_size=22, color=YELLOW)
        flare.next_to(sol, UP, buff=0.6)
        self.play(Flash(sol, color=YELLOW, flash_radius=1.4), FadeIn(flare), run_time=1.2)

        particulas = VGroup(*[
            Dot(sol.get_center() + np.array([0.9, dy, 0]), color=GOLD, radius=0.06)
            for dy in [-0.5, -0.25, 0, 0.25, 0.5]
        ])
        self.add(particulas)
        self.play(*[
            p.animate.shift(RIGHT * 6.6)
            for p in particulas
        ], run_time=3, rate_func=linear)

        # El escudo desvia la mayoria; parte entra por los polos
        desviadas = [particulas[0], particulas[1], particulas[3]]
        polares = [particulas[2], particulas[4]]
        self.play(
            *[p.animate.shift(UP * 1.8 + RIGHT * 1).set_opacity(0.2) for p in desviadas[:2]],
            *[p.animate.shift(DOWN * 1.8 + RIGHT * 1).set_opacity(0.2) for p in desviadas[2:]],
            *[p.animate.move_to(tierra.get_center() + UP * 0.55) for p in polares],
            run_time=2,
        )
        aurora = Arc(radius=0.62, start_angle=PI / 3, angle=PI / 3,
                     color=GREEN, stroke_width=8, arc_center=tierra.get_center())
        self.play(Create(aurora), FadeOut(VGroup(*polares)), run_time=1.2)
        aurora_txt = Text("Auroras", font_size=18, color=GREEN).next_to(aurora, UP, buff=0.15)
        self.play(FadeIn(aurora_txt), run_time=0.6)

        # Efectos sobre la tecnologia
        efectos = VGroup(
            Text("· Satélites: daño en electrónica y paneles", font_size=20, color=GREY_B),
            Text("· GPS y radio: errores y apagones de señal", font_size=20, color=GREY_B),
            Text("· Red eléctrica: corrientes inducidas", font_size=20, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(DOWN).shift(LEFT * 1.5)
        self.play(LaggedStart(*[FadeIn(e, shift=RIGHT * 0.3) for e in efectos],
                              lag_ratio=0.4), run_time=3)
        self.wait(2)
