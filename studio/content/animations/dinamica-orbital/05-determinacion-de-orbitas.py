from manim import *
import numpy as np


class DeterminacionDeOrbitas(Scene):
    def construct(self):
        titulo = Text("Determinación y propagación de órbitas",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        centro = DOWN * 0.8 + LEFT * 2.6
        tierra = Dot(centro, color=BLUE_D, radius=0.14)
        real = Ellipse(width=5.2, height=3.2, color=BLUE_B, stroke_opacity=0.0)
        real.move_to(centro).rotate(PI / 12, about_point=centro)
        self.play(FadeIn(tierra), run_time=0.8)

        # Observaciones ruidosas desde radar/telescopio
        obs_txt = Text("1) Observar: medidas con ruido (radar, óptica, GPS)",
                       font_size=22, color=YELLOW).to_edge(DOWN)
        rng = np.random.default_rng(7)
        proporciones = np.linspace(0.05, 0.75, 9)
        puntos = VGroup()
        for p in proporciones:
            base = real.point_from_proportion(float(p))
            ruido = rng.normal(0, 0.09, 2)
            puntos.add(Dot(base + np.array([ruido[0], ruido[1], 0]),
                           color=YELLOW, radius=0.06))
        self.play(FadeIn(obs_txt), LaggedStart(*[FadeIn(d, scale=2) for d in puntos],
                                               lag_ratio=0.15), run_time=3)

        # Ajuste: la elipse que mejor explica las medidas
        ajuste_txt = Text("2) Ajustar: la órbita que mejor explica los datos",
                          font_size=22, color=BLUE_B).to_edge(DOWN)
        ajuste = real.copy().set_stroke(color=BLUE_B, opacity=1)
        self.play(ReplacementTransform(obs_txt, ajuste_txt), run_time=1)
        self.play(Create(ajuste), run_time=2.5)
        residuos = VGroup(*[
            Line(d.get_center(),
                 real.point_from_proportion(float(p)), color=GREY_B, stroke_width=2)
            for d, p in zip(puntos, proporciones)
        ])
        self.play(Create(residuos), run_time=1.2)
        self.play(FadeOut(residuos), run_time=0.8)

        # Propagacion: predecir hacia adelante, con incertidumbre creciente
        prop_txt = Text("3) Propagar: predecir la posición futura",
                        font_size=22, color=GOLD).to_edge(DOWN)
        sat = Dot(real.point_from_proportion(0.75), color=GOLD, radius=0.09)
        self.play(ReplacementTransform(ajuste_txt, prop_txt), FadeIn(sat), run_time=1)

        t = ValueTracker(0.75)
        incert = always_redraw(lambda: Ellipse(
            width=0.25 + (t.get_value() - 0.75) * 2.4,
            height=0.15 + (t.get_value() - 0.75) * 1.2,
            color=GOLD, stroke_opacity=0.8, fill_opacity=0.2, fill_color=GOLD,
        ).move_to(real.point_from_proportion(t.get_value() % 1.0)))
        sat.add_updater(lambda m: m.move_to(real.point_from_proportion(t.get_value() % 1.0)))
        self.add(incert)
        self.play(t.animate.set_value(1.55), run_time=4, rate_func=linear)
        sat.clear_updaters()

        nota = Text("La incertidumbre crece con el tiempo: hay que volver a medir",
                    font_size=22, color=GREY_B).to_edge(DOWN)
        self.play(ReplacementTransform(prop_txt, nota), run_time=1.2)
        cierre = Text("Así se vigilan satélites y basura: medir, ajustar, predecir, repetir",
                      font_size=21, color=BLUE_B).next_to(nota, UP, buff=0.25)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
