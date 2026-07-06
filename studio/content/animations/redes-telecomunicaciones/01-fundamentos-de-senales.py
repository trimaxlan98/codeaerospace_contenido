from manim import *
import numpy as np


class FundamentosDeSenales(Scene):
    def construct(self):
        titulo = Text("Fundamentos de señales y espectro", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Dominio del tiempo: una senal senoidal
        ejes_t = Axes(x_range=[0, 4, 1], y_range=[-1.6, 1.6, 1],
                      x_length=5.6, y_length=2.6,
                      axis_config={"color": GREY_B, "include_ticks": False})
        ejes_t.move_to(LEFT * 3.3 + DOWN * 0.4)
        t_txt = Text("Tiempo", font_size=19, color=GREY_B)
        t_txt.next_to(ejes_t, DOWN, buff=0.2)
        onda = ejes_t.plot(lambda x: np.sin(TAU * x), color=BLUE_B)
        self.play(Create(ejes_t), FadeIn(t_txt), run_time=1.2)
        self.play(Create(onda), run_time=2)

        # Amplitud y frecuencia
        amp = Text("Amplitud: cuánto sube", font_size=20, color=YELLOW)
        amp.move_to(LEFT * 3.3 + UP * 1.7)
        onda_amp = ejes_t.plot(lambda x: 1.4 * np.sin(TAU * x), color=YELLOW)
        self.play(FadeIn(amp), Transform(onda, onda_amp), run_time=1.5)
        freq = Text("Frecuencia: cuántas veces por segundo", font_size=20, color=GOLD)
        freq.move_to(LEFT * 3.3 + UP * 1.7)
        onda_freq = ejes_t.plot(lambda x: np.sin(TAU * 2.5 * x), color=GOLD)
        self.play(ReplacementTransform(amp, freq), Transform(onda, onda_freq), run_time=1.5)
        self.wait(0.5)

        # Dominio de la frecuencia: el espectro
        ejes_f = Axes(x_range=[0, 5, 1], y_range=[0, 1.6, 1],
                      x_length=5.0, y_length=2.6,
                      axis_config={"color": GREY_B, "include_ticks": False})
        ejes_f.move_to(RIGHT * 3.5 + DOWN * 0.4)
        f_txt = Text("Frecuencia (espectro)", font_size=19, color=GREY_B)
        f_txt.next_to(ejes_f, DOWN, buff=0.2)
        self.play(Create(ejes_f), FadeIn(f_txt), run_time=1.2)

        # Una senal compleja es suma de senoides: barras del espectro
        compleja = ejes_t.plot(
            lambda x: 0.8 * np.sin(TAU * x) + 0.45 * np.sin(TAU * 2 * x)
            + 0.25 * np.sin(TAU * 3.5 * x), color=BLUE_B)
        comp_txt = Text("Toda señal = suma de senoides (Fourier)",
                        font_size=20, color=BLUE_B).move_to(LEFT * 3.3 + UP * 1.7)
        self.play(ReplacementTransform(freq, comp_txt), Transform(onda, compleja),
                  run_time=2)

        barras = VGroup()
        for f, h, c in [(1, 0.8, BLUE_B), (2, 0.45, BLUE_B), (3.5, 0.25, BLUE_B)]:
            b = Line(ejes_f.c2p(f, 0), ejes_f.c2p(f, h * 1.5), color=c, stroke_width=8)
            barras.add(b)
        flecha = Arrow(ejes_t.get_right(), ejes_f.get_left(), color=GOLD, buff=0.2)
        fourier = Text("FFT", font_size=22, color=GOLD).next_to(flecha, UP, buff=0.1)
        self.play(GrowArrow(flecha), FadeIn(fourier), run_time=1)
        self.play(LaggedStart(*[Create(b) for b in barras], lag_ratio=0.3), run_time=2)

        # Ancho de banda
        bw = BraceBetweenPoints(ejes_f.c2p(1, 1.45), ejes_f.c2p(3.5, 1.45),
                                direction=UP, color=YELLOW)
        bw_txt = Text("Ancho de banda", font_size=19, color=YELLOW)
        bw_txt.next_to(bw, UP, buff=0.1)
        self.play(FadeIn(bw), FadeIn(bw_txt), run_time=1.2)

        cierre = Text("El espectro es el recurso: más ancho de banda, más datos",
                      font_size=22, color=GOLD).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
