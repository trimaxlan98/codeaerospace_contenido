from manim import *
import numpy as np


class FotonicaYComunicacionesOpticas(Scene):
    def construct(self):
        titulo = Text("Fotónica y comunicaciones ópticas avanzadas",
                      font_size=31, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # WDM: varios colores por la misma fibra
        fibra = VGroup(
            Line(LEFT * 1.2 + UP * 1.3, RIGHT * 5.9 + UP * 1.3, color=GREY_B),
            Line(LEFT * 1.2 + UP * 0.7, RIGHT * 5.9 + UP * 0.7, color=GREY_B),
        )
        fibra_txt = Text("una sola fibra", font_size=17, color=GREY_B)
        fibra_txt.next_to(fibra, DOWN, buff=0.15).shift(RIGHT * 2.2)
        colores = [RED_D, YELLOW, GREEN_D, BLUE_B]
        canales = VGroup()
        for i, color in enumerate(colores):
            onda = FunctionGraph(
                lambda x, k=i: 0.14 * np.sin(9 * x) + 1.75 - k * 0.5,
                x_range=[-6.3, -1.5], color=color)
            etiqueta = MathTex(fr"\lambda_{i+1}", font_size=26, color=color)
            etiqueta.next_to(onda, LEFT, buff=0.12)
            canales.add(VGroup(onda, etiqueta))
        wdm_txt = Text("WDM: cada longitud de onda es un canal independiente",
                       font_size=20, color=YELLOW).to_edge(DOWN)
        self.play(Create(fibra), FadeIn(fibra_txt), FadeIn(wdm_txt), run_time=1.5)
        self.play(LaggedStart(*[Create(c[0]) for c in canales], lag_ratio=0.2),
                  LaggedStart(*[FadeIn(c[1]) for c in canales], lag_ratio=0.2),
                  run_time=2.5)

        # Los cuatro entran a la fibra como pulsos
        pulsos = VGroup(*[
            Dot(LEFT * 1.4 + UP * 1.0, color=c, radius=0.07).shift(LEFT * 0.25 * i)
            for i, c in enumerate(colores)
        ])
        self.play(FadeIn(pulsos), run_time=0.5)
        self.play(*[p.animate.shift(RIGHT * 7.0) for p in pulsos], run_time=2.5,
                  rate_func=linear)
        capacidad = Text("80+ canales × 400 Gb/s = decenas de Tb/s por fibra",
                         font_size=19, color=GOLD)
        capacidad.move_to(RIGHT * 2.4 + UP * 2.15)
        self.play(FadeIn(capacidad), FadeOut(pulsos), run_time=1.2)

        # Fotonica integrada: el chip optico
        chip = Rectangle(width=3.4, height=1.7, color=BLUE_B, fill_opacity=0.08,
                         fill_color=BLUE_B).move_to(LEFT * 3.4 + DOWN * 1.9)
        chip_txt = Text("chip fotónico", font_size=18, color=BLUE_B)
        chip_txt.next_to(chip, UP, buff=0.15)
        guias = VGroup(
            ArcBetweenPoints(chip.get_left() + RIGHT * 0.2 + UP * 0.4,
                             chip.get_right() + LEFT * 0.2 + UP * 0.1,
                             angle=-PI / 5, color=YELLOW),
            ArcBetweenPoints(chip.get_left() + RIGHT * 0.2 + DOWN * 0.4,
                             chip.get_right() + LEFT * 0.2 + DOWN * 0.1,
                             angle=PI / 5, color=YELLOW),
            Circle(radius=0.28, color=GOLD).move_to(chip.get_center() + UP * 0.02),
        )
        guia_txt = Text("guías de onda y anillos moduladores en silicio",
                        font_size=16, color=GREY_B).next_to(chip, DOWN, buff=0.15)
        self.play(Create(chip), FadeIn(chip_txt), run_time=1.2)
        self.play(Create(guias), FadeIn(guia_txt), run_time=1.8)

        # Ventaja fotonica
        ventajas = VGroup(
            Text("· sin resistencia: menos calor", font_size=18, color=GREY_B),
            Text("· enlaces ópticos entre GPUs (IA)", font_size=18, color=YELLOW),
            Text("· láser al espacio: Gb/s a la Luna", font_size=18, color=BLUE_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(RIGHT * 3.4 + DOWN * 1.9)
        self.play(LaggedStart(*[FadeIn(v, shift=RIGHT * 0.3) for v in ventajas],
                              lag_ratio=0.3), run_time=2.5)

        cierre = Text("La luz ya no solo transporta datos entre ciudades: ahora también dentro del chip",
                      font_size=18, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(wdm_txt, cierre), run_time=1.2)
        self.wait(2)
