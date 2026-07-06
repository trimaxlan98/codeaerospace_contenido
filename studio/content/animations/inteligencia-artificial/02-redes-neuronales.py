from manim import *
import numpy as np


class RedesNeuronalesDesdeCero(Scene):
    def construct(self):
        titulo = Text("Redes neuronales desde cero", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Una neurona: suma ponderada + activacion
        entradas = VGroup(*[
            Dot(LEFT * 5.6 + UP * (1.2 - i * 1.0), color=BLUE_B, radius=0.1)
            for i in range(3)
        ])
        ent_txt = VGroup(*[
            MathTex(f"x_{i+1}", font_size=30, color=BLUE_B).next_to(d, LEFT, buff=0.2)
            for i, d in enumerate(entradas)
        ])
        neurona = Circle(radius=0.45, color=GOLD).move_to(LEFT * 3.0 + UP * 0.2)
        sigma = MathTex(r"\Sigma \to f", font_size=30, color=GOLD).move_to(neurona)
        pesos = VGroup(*[
            Line(d.get_center(), neurona.get_left() + RIGHT * 0.05, color=GREY_B)
            for d in entradas
        ])
        w_txt = VGroup(*[
            MathTex(f"w_{i+1}", font_size=26, color=YELLOW)
            .move_to(p.get_center() + UP * 0.22)
            for i, p in enumerate(pesos)
        ])
        salida = Arrow(neurona.get_right(), neurona.get_right() + RIGHT * 1.1,
                       color=GOLD, buff=0.05)
        self.play(FadeIn(entradas), FadeIn(ent_txt), run_time=1)
        self.play(Create(pesos), FadeIn(w_txt), Create(neurona), Write(sigma),
                  GrowArrow(salida), run_time=2)
        formula = MathTex(r"y = f\!\left(\sum_i w_i x_i + b\right)",
                          font_size=36, color=GREY_B)
        formula.move_to(LEFT * 3.4 + DOWN * 1.9)
        self.play(Write(formula), run_time=1.8)

        # Apilar neuronas: una red por capas
        capas = [3, 4, 4, 2]
        red = VGroup()
        posiciones = []
        for j, n in enumerate(capas):
            columna = []
            for i in range(n):
                p = RIGHT * (1.6 + j * 1.3) + UP * (0.9 * (n - 1) / 2 - 0.9 * i + 0.4)
                columna.append(p)
                red.add(Circle(radius=0.14, color=BLUE_B if j == 0 else
                               (GOLD if j == len(capas) - 1 else GREY_B),
                               fill_opacity=0.3))
                red[-1].move_to(p)
            posiciones.append(columna)
        conexiones = VGroup()
        for j in range(len(capas) - 1):
            for a in posiciones[j]:
                for b in posiciones[j + 1]:
                    conexiones.add(Line(a, b, color=GREY_B, stroke_width=1.2,
                                        stroke_opacity=0.5))
        red_txt = Text("capas ocultas", font_size=17, color=GREY_B)
        red_txt.move_to(RIGHT * 3.5 + UP * 2.2)
        self.play(Create(conexiones), FadeIn(red), FadeIn(red_txt), run_time=2.5)

        # Pase hacia adelante
        pulso = VGroup(*[Dot(p, color=YELLOW, radius=0.07) for p in posiciones[0]])
        self.play(FadeIn(pulso), run_time=0.4)
        for j in range(1, len(capas)):
            nuevos = VGroup(*[Dot(p, color=YELLOW, radius=0.07)
                              for p in posiciones[j]])
            self.play(ReplacementTransform(pulso, nuevos), run_time=0.7)
            pulso = nuevos
        self.play(FadeOut(pulso), run_time=0.4)

        # Entrenamiento: descenso por gradiente
        ejes = Axes(x_range=[-2, 2, 1], y_range=[0, 3, 1], x_length=3.4, y_length=2.0,
                    axis_config={"color": GREY_B, "include_ticks": False})
        ejes.move_to(RIGHT * 3.6 + DOWN * 2.0)
        curva = ejes.plot(lambda x: 0.7 * x ** 2 + 0.3, color=BLUE_B)
        bola = Dot(ejes.c2p(-1.7, 0.7 * 1.7 ** 2 + 0.3), color=YELLOW, radius=0.09)
        error_txt = Text("error del modelo", font_size=15, color=GREY_B)
        error_txt.next_to(ejes, UP, buff=0.1)
        self.play(Create(ejes), Create(curva), FadeIn(bola), FadeIn(error_txt),
                  run_time=1.5)
        for x in [-1.0, -0.5, -0.15, 0.0]:
            self.play(bola.animate.move_to(ejes.c2p(x, 0.7 * x ** 2 + 0.3)),
                      run_time=0.6)

        cierre = Text("Aprender = ajustar millones de pesos para que el error baje",
                      font_size=21, color=GOLD).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
