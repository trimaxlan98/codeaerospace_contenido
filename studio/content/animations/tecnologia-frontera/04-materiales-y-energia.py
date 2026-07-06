from manim import *
import numpy as np


class MaterialesAvanzadosYEnergia(Scene):
    def construct(self):
        titulo = Text("Materiales avanzados y energía", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Grafeno: red hexagonal de un atomo de espesor
        graf_txt = Text("Grafeno: carbono en 2D", font_size=20, color=BLUE_B)
        graf_txt.move_to(LEFT * 4.3 + UP * 2.0)
        hexs = VGroup()
        for fila in range(3):
            for col in range(3):
                h = RegularPolygon(n=6, start_angle=PI / 6, color=BLUE_B)
                h.scale(0.42)
                dx = col * 1.1 + (0.55 if fila % 2 else 0)
                h.move_to(LEFT * 5.4 + RIGHT * dx + UP * (1.1 - fila * 0.95))
                hexs.add(h)
        propied = Text("200× más fuerte que el acero,\nconductor casi perfecto",
                       font_size=16, color=GREY_B, line_spacing=0.9)
        propied.next_to(hexs, DOWN, buff=0.25)
        self.play(FadeIn(graf_txt), LaggedStart(*[Create(h) for h in hexs],
                                                lag_ratio=0.08), run_time=2.5)
        self.play(FadeIn(propied), run_time=1)

        # Perovskitas: eficiencia solar subiendo
        ejes = Axes(x_range=[2009, 2025, 4], y_range=[0, 30, 10],
                    x_length=4.4, y_length=2.6,
                    axis_config={"color": GREY_B, "include_ticks": False})
        ejes.move_to(RIGHT * 3.4 + UP * 0.9)
        solar_txt = Text("Celdas solares de perovskita: eficiencia (%)",
                         font_size=17, color=GOLD).next_to(ejes, UP, buff=0.15)
        curva = ejes.plot(
            lambda x: 3.8 + 23 * (1 - np.exp(-(x - 2009) / 5.5)),
            color=GOLD, x_range=[2009, 2025, 0.1])
        silicio = DashedVMobject(ejes.plot(lambda x: 26.5, color=GREY_B,
                                           x_range=[2009, 2025, 0.5]), num_dashes=25)
        sil_txt = Text("silicio (récord ~27%)", font_size=14, color=GREY_B)
        sil_txt.next_to(ejes.c2p(2013, 26.5), UP, buff=0.1)
        self.play(Create(ejes), FadeIn(solar_txt), run_time=1.2)
        self.play(Create(silicio), FadeIn(sil_txt), run_time=1)
        self.play(Create(curva), run_time=2.5)
        nota = Text("de 3.8% a >26% en 15 años: baratas y flexibles",
                    font_size=16, color=GOLD).next_to(ejes, DOWN, buff=0.15)
        self.play(FadeIn(nota), run_time=1)

        # Baterias: densidad de energia
        bat_txt = Text("Baterías: más energía por kg", font_size=20, color=YELLOW)
        bat_txt.move_to(LEFT * 3.9 + DOWN * 1.35)
        barras = VGroup()
        datos = [("plomo", 0.4, GREY_B), ("Li-ion", 1.4, BLUE_B),
                 ("estado sólido", 2.2, YELLOW)]
        for i, (nombre, h, color) in enumerate(datos):
            b = Rectangle(width=0.62, height=h, color=color, fill_opacity=0.75,
                          fill_color=color)
            b.move_to(LEFT * (5.1 - i * 1.35) + DOWN * 3.1, aligned_edge=DOWN)
            t = Text(nombre, font_size=14, color=color).next_to(b, UP, buff=0.08)
            barras.add(VGroup(b, t))
        self.play(FadeIn(bat_txt), run_time=0.8)
        for b in barras:
            self.play(GrowFromEdge(b[0], DOWN), FadeIn(b[1]), run_time=0.7)

        # Por que importa
        impacto = VGroup(
            Text("Materiales → energía → todo lo demás:", font_size=19, color=GREY_B),
            Text("satélites más ligeros, autos eléctricos, chips fríos",
                 font_size=19, color=BLUE_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        impacto.move_to(RIGHT * 3.2 + DOWN * 2.3)
        self.play(FadeIn(impacto), run_time=1.5)
        self.wait(2)
