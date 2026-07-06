from manim import *
import numpy as np


class ModulacionYCodificacion(Scene):
    def construct(self):
        titulo = Text("Modulación y codificación", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Bits a transmitir
        bits = [1, 0, 1, 1]
        bits_txt = VGroup(*[
            Text(str(b), font_size=30, color=YELLOW) for b in bits
        ]).arrange(RIGHT, buff=0.9).move_to(UP * 2.1 + LEFT * 2.5)
        bits_lbl = Text("Datos:", font_size=22, color=GREY_B)
        bits_lbl.next_to(bits_txt, LEFT, buff=0.5)
        self.play(FadeIn(bits_lbl), FadeIn(bits_txt, lag_ratio=0.2), run_time=1.5)

        # Portadora y esquemas de modulacion
        ejes = Axes(x_range=[0, 4, 1], y_range=[-1.4, 1.4, 1],
                    x_length=7.5, y_length=2.2,
                    axis_config={"color": GREY_B, "include_ticks": False})
        ejes.move_to(LEFT * 2.2 + DOWN * 0.3)

        def moduladora(esquema):
            def f(x):
                bit = bits[min(int(x), 3)]
                if esquema == "ASK":
                    return (1.0 if bit else 0.25) * np.sin(TAU * 2 * x)
                if esquema == "FSK":
                    return np.sin(TAU * (3 if bit else 1.5) * x)
                fase = 0 if bit else PI
                return np.sin(TAU * 2 * x + fase)
            return f

        etiqueta = Text("ASK: la amplitud lleva el bit", font_size=22, color=BLUE_B)
        etiqueta.next_to(ejes, DOWN, buff=0.3)
        onda = ejes.plot(moduladora("ASK"), color=BLUE_B, x_range=[0, 4, 0.01])
        self.play(Create(ejes), run_time=1)
        self.play(Create(onda), FadeIn(etiqueta), run_time=2)

        for esquema, texto, color in [
            ("FSK", "FSK: la frecuencia lleva el bit", GOLD),
            ("PSK", "PSK: la fase lleva el bit", YELLOW),
        ]:
            nueva = ejes.plot(moduladora(esquema), color=color, x_range=[0, 4, 0.01])
            nuevo_txt = Text(texto, font_size=22, color=color).next_to(ejes, DOWN, buff=0.3)
            self.play(Transform(onda, nueva),
                      ReplacementTransform(etiqueta, nuevo_txt), run_time=2)
            etiqueta = nuevo_txt

        # Constelacion QPSK: 2 bits por simbolo
        plano = Axes(x_range=[-1.5, 1.5, 1], y_range=[-1.5, 1.5, 1],
                     x_length=2.6, y_length=2.6,
                     axis_config={"color": GREY_B, "include_ticks": False})
        plano.move_to(RIGHT * 4.6 + DOWN * 0.3)
        qpsk_txt = Text("QPSK: 2 bits por símbolo", font_size=19, color=GOLD)
        qpsk_txt.next_to(plano, DOWN, buff=0.2)
        puntos = VGroup(*[
            VGroup(Dot(plano.c2p(x, y), color=GOLD, radius=0.07),
                   Text(lbl, font_size=16, color=GREY_B)
                   .next_to(plano.c2p(x, y), UR * 0.4, buff=0.06))
            for x, y, lbl in [(0.9, 0.9, "00"), (-0.9, 0.9, "01"),
                              (-0.9, -0.9, "11"), (0.9, -0.9, "10")]
        ])
        self.play(Create(plano), FadeIn(qpsk_txt), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(p, scale=1.5) for p in puntos], lag_ratio=0.25),
                  run_time=2)

        # Codificacion de canal: redundancia contra errores
        cierre = Text("Codificación: se agregan bits de paridad para corregir errores en el canal",
                      font_size=20, color=GREY_B).to_edge(DOWN)
        extra = Text("1 0 1 1  +  p p", font_size=24, color=YELLOW)
        extra.next_to(cierre, UP, buff=0.25)
        self.play(FadeIn(cierre), FadeIn(extra), run_time=1.5)
        self.wait(2)
