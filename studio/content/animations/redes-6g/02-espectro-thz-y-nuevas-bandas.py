from manim import *
import numpy as np


class EspectroSubThzYNuevasBandas(Scene):
    def construct(self):
        titulo = Text("Espectro: sub-THz y nuevas bandas", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Eje de frecuencias en escala log
        eje = NumberLine(x_range=[0, 4, 1], length=11.5, color=GREY_B,
                         include_numbers=False).move_to(UP * 1.2)
        marcas = VGroup(*[
            Text(t, font_size=18, color=GREY_B).next_to(eje.number_to_point(x), DOWN, buff=0.2)
            for x, t in [(0, "1 GHz"), (1, "10 GHz"), (2, "100 GHz"),
                         (3, "1 THz"), (4, "10 THz")]
        ])
        self.play(Create(eje), FadeIn(marcas), run_time=1.5)

        # Bandas
        bandas = [
            ("sub-6 GHz\n(4G/5G)", 0.0, 0.8, BLUE_D),
            ("mmWave 5G\n24-52 GHz", 1.35, 0.4, BLUE_B),
            ("sub-THz 6G\n90-300 GHz", 2.0, 0.55, YELLOW),
            ("THz\nexploración", 3.0, 0.7, GOLD),
        ]
        cajas = VGroup()
        for nombre, x0, ancho, color in bandas:
            r = Rectangle(width=ancho / 4 * 11.5, height=0.5, color=color,
                          fill_opacity=0.4, fill_color=color)
            r.move_to(eje.number_to_point(x0 + ancho / 2) + UP * 0.45)
            t = Text(nombre, font_size=15, color=color, line_spacing=0.85)
            t.next_to(r, UP, buff=0.12)
            cajas.add(VGroup(r, t))
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cajas],
                              lag_ratio=0.3), run_time=3)

        # El trade-off fundamental
        trade = VGroup(
            Text("↑ frecuencia  →  ↑ ancho de banda (más datos)", font_size=21,
                 color=YELLOW),
            Text("↑ frecuencia  →  ↓ alcance y penetración", font_size=21,
                 color=RED_D),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(LEFT * 2.9 + DOWN * 1.1)
        self.play(FadeIn(trade[0], shift=RIGHT * 0.3), run_time=1.2)
        self.play(FadeIn(trade[1], shift=RIGHT * 0.3), run_time=1.2)

        # Absorcion molecular: ventanas de transmision
        ejes = Axes(x_range=[0, 4, 1], y_range=[0, 2.4, 1], x_length=4.6, y_length=1.9,
                    axis_config={"color": GREY_B, "include_ticks": False})
        ejes.move_to(RIGHT * 3.9 + DOWN * 1.5)
        curva = ejes.plot(
            lambda x: 0.3 + 1.8 * np.exp(-18 * (x - 1.6) ** 2)
            + 1.5 * np.exp(-24 * (x - 2.7) ** 2) + 0.9 * np.exp(-30 * (x - 3.5) ** 2),
            color=RED_D, x_range=[0.1, 3.9, 0.02])
        abso_txt = Text("Absorción del aire (O₂, H₂O):\nse transmite en las 'ventanas'",
                        font_size=16, color=GREY_B, line_spacing=0.85)
        abso_txt.next_to(ejes, UP, buff=0.15)
        self.play(Create(ejes), FadeIn(abso_txt), run_time=1.2)
        self.play(Create(curva), run_time=2)
        ventana = Arrow(ejes.c2p(2.15, 2.1), ejes.c2p(2.15, 0.6), color=YELLOW,
                        buff=0)
        vent_txt = Text("ventana", font_size=15, color=YELLOW)
        vent_txt.next_to(ventana.get_start(), UP, buff=0.08)
        self.play(GrowArrow(ventana), FadeIn(vent_txt), run_time=1.2)

        cierre = Text("Sub-THz: celdas de metros con fibra invisible en el aire — y haces muy directivos",
                      font_size=19, color=BLUE_B).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
