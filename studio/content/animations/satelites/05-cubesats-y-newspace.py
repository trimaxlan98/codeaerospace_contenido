from manim import *


class CubesatsYNewspace(Scene):
    def construct(self):
        titulo = Text("CubeSats y NewSpace", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # La unidad: 1U = cubo de 10 cm
        u1 = Square(side_length=0.8, color=BLUE_B, fill_opacity=0.25, fill_color=BLUE_B)
        u1.move_to(LEFT * 4.5 + UP * 0.8)
        u1_txt = Text("1U = 10×10×10 cm · ~1.3 kg", font_size=20, color=BLUE_B)
        u1_txt.next_to(u1, DOWN, buff=0.3)
        self.play(Create(u1), FadeIn(u1_txt), run_time=1.5)

        # Formatos estandar: 3U y 6U
        u3 = VGroup(*[
            Square(side_length=0.8, color=BLUE_B, fill_opacity=0.25, fill_color=BLUE_B)
            for _ in range(3)
        ]).arrange(UP, buff=0).move_to(LEFT * 1.5 + UP * 0.8)
        u3_txt = Text("3U", font_size=20, color=BLUE_B).next_to(u3, DOWN, buff=0.3)
        u6 = VGroup(*[
            Square(side_length=0.8, color=GOLD, fill_opacity=0.25, fill_color=GOLD)
            for _ in range(6)
        ]).arrange_in_grid(rows=3, cols=2, buff=0).move_to(RIGHT * 1.5 + UP * 0.8)
        u6_txt = Text("6U", font_size=20, color=GOLD).next_to(u6, DOWN, buff=0.3)
        self.play(ReplacementTransform(u1.copy(), u3), FadeIn(u3_txt), run_time=1.5)
        self.play(ReplacementTransform(u3.copy(), u6), FadeIn(u6_txt), run_time=1.5)

        # Comparacion con un satelite clasico
        clasico = Rectangle(width=1.9, height=2.4, color=GREY_B,
                            fill_opacity=0.15, fill_color=GREY_B)
        clasico.move_to(RIGHT * 4.7 + UP * 0.8)
        clasico_txt = Text("Satélite clásico\n(toneladas, ~10 años)", font_size=18,
                           color=GREY_B, line_spacing=0.8)
        clasico_txt.next_to(clasico, DOWN, buff=0.3)
        self.play(Create(clasico), FadeIn(clasico_txt), run_time=1.5)

        # Comparacion de costo y tiempo de desarrollo
        self.play(VGroup(u1, u1_txt).animate.set_opacity(0.4), run_time=0.6)
        comparar = VGroup(
            Text("Costo:    millones  →  decenas de miles USD", font_size=21, color=YELLOW),
            Text("Desarrollo:    10 años  →  18 meses", font_size=21, color=YELLOW),
            Text("Riesgo: repartido en muchas unidades baratas", font_size=21, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_edge(DOWN).shift(UP * 0.9)
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3) for c in comparar],
                              lag_ratio=0.4), run_time=3)
        self.wait(1)

        # Despliegue en enjambre desde un adaptador
        self.play(FadeOut(comparar), run_time=0.8)
        cohete = Rectangle(width=0.5, height=1.4, color=GREY_B, fill_opacity=0.3)
        cohete.move_to(DOWN * 2.4 + LEFT * 5)
        enjambre = VGroup(*[
            Square(side_length=0.16, color=BLUE_B, fill_opacity=0.8, fill_color=BLUE_B)
            .move_to(cohete.get_center())
            for _ in range(8)
        ])
        self.play(FadeIn(cohete), run_time=0.6)
        destinos = [DOWN * 2.4 + LEFT * 5 + RIGHT * (1 + i * 0.9) + UP * (0.2 * (i % 3))
                    for i in range(8)]
        self.play(LaggedStart(*[
            s.animate.move_to(d) for s, d in zip(enjambre, destinos)
        ], lag_ratio=0.15), run_time=3)

        cierre = Text("NewSpace: estandarizar y abaratar abre el espacio a todos",
                      font_size=22, color=GOLD).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
