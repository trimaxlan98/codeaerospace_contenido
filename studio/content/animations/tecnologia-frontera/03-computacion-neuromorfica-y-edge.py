from manim import *
import numpy as np


class ComputacionNeuromorficaYEdge(Scene):
    def construct(self):
        titulo = Text("Computación neuromórfica y edge", font_size=33, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # CPU clasica: reloj constante, todo se procesa siempre
        cpu_txt = Text("Chip clásico: reloj fijo,\nconsume aunque no pase nada",
                       font_size=19, color=GREY_B, line_spacing=0.9)
        cpu_txt.move_to(LEFT * 4.1 + UP * 2.0)
        reloj = Square(side_length=1.0, color=GREY_B).move_to(LEFT * 4.1 + UP * 0.5)
        onda_reloj = FunctionGraph(
            lambda x: 0.25 * (1 if np.sin(14 * x) > 0 else -1),
            x_range=[-5.6, -2.6], color=GREY_B).shift(DOWN * 0.7)
        self.play(FadeIn(cpu_txt), Create(reloj), run_time=1.2)
        self.play(Create(onda_reloj), run_time=1.5)

        # Chip neuromorfico: neuronas que disparan solo con eventos
        neuro_txt = Text("Chip neuromórfico: dispara\nsolo cuando hay un evento",
                         font_size=19, color=YELLOW, line_spacing=0.9)
        neuro_txt.move_to(RIGHT * 0.6 + UP * 2.0)
        rng = np.random.default_rng(11)
        neuronas = VGroup(*[
            Dot(RIGHT * (0.0 + rng.uniform(-0.9, 1.6)) + UP * rng.uniform(-0.4, 1.1),
                color=YELLOW, radius=0.08)
            for _ in range(7)
        ])
        sinapsis = VGroup(*[
            Line(neuronas[i].get_center(), neuronas[j].get_center(), color=GREY_B,
                 stroke_width=1.5, stroke_opacity=0.5)
            for i, j in [(0, 2), (1, 2), (2, 4), (3, 4), (4, 5), (4, 6), (1, 3)]
        ])
        self.play(FadeIn(neuro_txt), Create(sinapsis), FadeIn(neuronas), run_time=1.8)
        # picos dispersos (spikes)
        for idx in [0, 2, 4, 6, 1, 3]:
            self.play(Flash(neuronas[idx], color=YELLOW, flash_radius=0.25),
                      run_time=0.4)
        gasto = Text("mil veces menos energía en tareas de percepción",
                     font_size=18, color=YELLOW)
        gasto.move_to(RIGHT * 0.7 + DOWN * 0.9)
        self.play(FadeIn(gasto), run_time=1)

        # Edge: procesar donde nacen los datos
        edge_txt = Text("Edge: el cómputo se acerca al dato", font_size=21, color=BLUE_B)
        edge_txt.move_to(DOWN * 1.8 + LEFT * 3.2)
        nube = VGroup(
            Circle(radius=0.42, color=GREY_B).shift(LEFT * 0.3),
            Circle(radius=0.5, color=GREY_B).shift(RIGHT * 0.15 + UP * 0.12),
            Circle(radius=0.36, color=GREY_B).shift(RIGHT * 0.55),
        ).move_to(RIGHT * 4.9 + DOWN * 1.6)
        nube_txt = Text("nube", font_size=17, color=GREY_B).move_to(nube)
        sensor = Square(side_length=0.4, color=BLUE_B, fill_opacity=0.3,
                        fill_color=BLUE_B).move_to(LEFT * 5.3 + DOWN * 2.7)
        sensor_txt = Text("sensor + chip", font_size=16, color=BLUE_B)
        sensor_txt.next_to(sensor, DOWN, buff=0.12)
        self.play(FadeIn(edge_txt), FadeIn(nube), FadeIn(nube_txt), FadeIn(sensor),
                  FadeIn(sensor_txt), run_time=1.8)

        lejos = DashedLine(sensor.get_right(), nube.get_left(), color=GREY_B)
        lejos_txt = Text("ida a la nube: 80 ms + ancho de banda", font_size=15,
                         color=GREY_B).next_to(lejos, UP, buff=0.1)
        local = Arc(radius=0.5, start_angle=PI / 2, angle=-TAU * 0.8, color=YELLOW,
                    arc_center=sensor.get_center())
        local_txt = Text("decidir en el borde: <1 ms", font_size=15, color=YELLOW)
        local_txt.next_to(sensor, RIGHT, buff=0.3).shift(DOWN * 0.15)
        self.play(Create(lejos), FadeIn(lejos_txt), run_time=1.3)
        self.play(Create(local), FadeIn(local_txt), run_time=1.3)

        cierre = Text("Juntos: sensores que perciben y deciden solos, gastando milivatios",
                      font_size=19, color=GOLD).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
