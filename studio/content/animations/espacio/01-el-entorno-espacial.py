from manim import *


class ElEntornoEspacial(Scene):
    def construct(self):
        titulo = Text("El entorno espacial", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Tierra con capas atmosfericas a escala exagerada
        centro = DOWN * 1.6 + LEFT * 3
        tierra = Circle(radius=1.1, color=BLUE_D, fill_opacity=1, fill_color=BLUE_D)
        tierra.move_to(centro)
        self.play(GrowFromCenter(tierra), run_time=1.2)

        capas = [
            ("Troposfera  0-12 km", BLUE_B),
            ("Estratosfera  12-50 km", BLUE_B),
            ("Mesosfera  50-85 km", GREY_B),
            ("Termosfera  85-600 km", GREY_B),
        ]
        radios = [1.35, 1.6, 1.9, 2.15]
        etiquetas = VGroup()
        for i, ((nombre, color), r) in enumerate(zip(capas, radios)):
            anillo = Arc(radius=r, start_angle=-PI / 3, angle=2 * PI / 3,
                         color=color, arc_center=centro)
            texto = Text(nombre, font_size=20, color=color)
            texto.move_to(RIGHT * 3.2 + UP * (1.1 - i * 0.55))
            etiquetas.add(texto)
            self.play(Create(anillo), FadeIn(texto), run_time=1)

        # Linea de Karman: frontera convencional del espacio
        karman = DashedVMobject(
            Arc(radius=2.45, start_angle=-PI / 3, angle=2 * PI / 3,
                color=YELLOW, arc_center=centro),
            num_dashes=30,
        )
        karman_txt = Text("Línea de Kármán · 100 km", font_size=22, color=YELLOW)
        karman_txt.move_to(RIGHT * 3.2 + DOWN * 1.2)
        self.play(Create(karman), FadeIn(karman_txt), run_time=1.5)
        self.play(Indicate(karman_txt, color=YELLOW), run_time=1)

        # Cinturones de Van Allen
        van_allen = VGroup(
            Ellipse(width=5.6, height=3.4, color=GOLD).move_to(centro),
            Ellipse(width=6.8, height=4.4, color=GOLD).move_to(centro),
        )
        va_txt = Text("Cinturones de Van Allen", font_size=22, color=GOLD)
        va_txt.move_to(RIGHT * 3.2 + DOWN * 1.9)
        self.play(Create(van_allen), FadeIn(va_txt), run_time=2)

        # Particulas de radiacion atrapadas
        particulas = VGroup(*[
            Dot(van_allen[0].point_from_proportion(p), color=YELLOW, radius=0.05)
            for p in [0.05, 0.2, 0.45, 0.6, 0.85]
        ])
        self.play(FadeIn(particulas, lag_ratio=0.3), run_time=1.5)
        self.play(*[
            MoveAlongPath(d, van_allen[0])
            for d in particulas
        ], run_time=4, rate_func=linear)

        cierre = Text(
            "Vacío, radiación y ciclos térmicos: el entorno que toda nave debe sobrevivir",
            font_size=22, color=GREY_B,
        ).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.5)
        self.wait(2)
