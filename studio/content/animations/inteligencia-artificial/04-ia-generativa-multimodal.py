from manim import *
import numpy as np


class IaGenerativaMultimodal(Scene):
    def construct(self):
        titulo = Text("IA generativa multimodal", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Modalidades de entrada
        modos = [
            ("texto", LEFT * 5.2 + UP * 1.6, BLUE_B),
            ("imagen", LEFT * 5.2 + UP * 0.2, GOLD),
            ("audio", LEFT * 5.2 + DOWN * 1.2, GREY_B),
        ]
        entradas = VGroup()
        for nombre, p, color in modos:
            caja = RoundedRectangle(width=1.6, height=0.7, corner_radius=0.12,
                                    color=color, fill_opacity=0.12, fill_color=color)
            caja.move_to(p)
            t = Text(nombre, font_size=19, color=color).move_to(caja)
            entradas.add(VGroup(caja, t))
        self.play(LaggedStart(*[FadeIn(e, shift=RIGHT * 0.3) for e in entradas],
                              lag_ratio=0.25), run_time=2)

        # Espacio latente compartido
        espacio = Circle(radius=1.25, color=YELLOW).move_to(LEFT * 1.2 + UP * 0.2)
        esp_txt = Text("espacio latente\ncompartido", font_size=18, color=YELLOW,
                       line_spacing=0.85).move_to(espacio)
        self.play(Create(espacio), FadeIn(esp_txt), run_time=1.5)
        flechas_in = VGroup(*[
            Arrow(e.get_right(), espacio.get_left() + UP * (0.5 - i * 0.5),
                  color=e[1].get_color(), buff=0.1, stroke_width=3)
            for i, e in enumerate(entradas)
        ])
        self.play(LaggedStart(*[GrowArrow(f) for f in flechas_in], lag_ratio=0.2),
                  run_time=1.5)
        idea = Text("Cercanos en el espacio aunque su forma difiera:\n'un cohete despegando' ≈ su foto ≈ su rugido",
                    font_size=18, color=GREY_B, line_spacing=0.9).to_edge(DOWN)
        puntos = VGroup(*[
            Dot(espacio.get_center() + 0.35 * np.array([np.cos(a), np.sin(a), 0]),
                color=c, radius=0.07)
            for a, c in [(0.5, BLUE_B), (2.5, GOLD), (4.5, GREY_B)]
        ])
        self.play(FadeIn(puntos), FadeIn(idea), run_time=1.5)

        # Generacion: difusion de ruido a imagen
        gen_txt = Text("Generar = recorrer el espacio al revés: de ruido a contenido",
                       font_size=20, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(idea, gen_txt), run_time=1.2)

        rng = np.random.default_rng(3)
        n = 6
        celdas = VGroup(*[
            Square(side_length=0.38, stroke_width=1, stroke_color=GREY_B)
            for _ in range(n * n)
        ]).arrange_in_grid(rows=n, cols=n, buff=0.02).move_to(RIGHT * 3.6 + UP * 0.2)
        grises = rng.uniform(0.1, 0.9, n * n)
        for c, g in zip(celdas, grises):
            c.set_fill(interpolate_color(BLACK, WHITE, float(g)), opacity=1)
        ruido_txt = Text("ruido", font_size=17, color=GREY_B)
        ruido_txt.next_to(celdas, UP, buff=0.2)
        self.play(FadeIn(celdas, lag_ratio=0.02), FadeIn(ruido_txt), run_time=1.5)

        # Denoising en pasos: emerge un circulo (el "sol")
        centro_img = np.array([2.5, 2.5])
        for paso, mezcla in [(1, 0.5), (2, 0.85), (3, 1.0)]:
            nuevos_colores = []
            for idx in range(n * n):
                fila, col = divmod(idx, n)
                dentro = (fila - centro_img[0]) ** 2 + (col - centro_img[1]) ** 2 <= 2.5
                objetivo = 0.95 if dentro else 0.15
                valor = (1 - mezcla) * grises[idx] + mezcla * objetivo
                nuevos_colores.append(valor)
            self.play(*[
                c.animate.set_fill(interpolate_color(BLACK, GOLD if v > 0.5 else BLUE_D,
                                                     min(v + 0.2, 1.0)), opacity=1)
                for c, v in zip(celdas, nuevos_colores)
            ], run_time=1.1)
        imagen_txt = Text("imagen", font_size=17, color=GOLD).move_to(ruido_txt)
        self.play(ReplacementTransform(ruido_txt, imagen_txt), run_time=0.8)

        cierre = Text("Un solo modelo lee y produce texto, imagen y sonido: multimodal",
                      font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(gen_txt, cierre), run_time=1.2)
        self.wait(2)
