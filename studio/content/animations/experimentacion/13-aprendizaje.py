import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from aprendizaje import (COLOR_MODELO, COLOR_PERDIDA, curva_perdida,
                         datos_xor, entrenar_mlp, frontera_imagen,
                         puntos_datos)


class DemoAprendizaje(Scene):
    """Demo de aprendizaje.py: XOR, entrenamiento y frontera de decision.

    Todo el calculo es numpy determinista y la frontera se dibuja como un
    unico ImageMobject encajado en los ejes: apto para el VPS.
    """

    def construct(self):
        titulo = Text("XOR: la red dobla el espacio", font_size=30,
                      color=COLOR_MODELO).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=0.8)

        # Plano de datos a la izquierda y mini-eje de perdida a la derecha
        plano = Axes(x_range=[-2.2, 2.2, 2.2], y_range=[-2.2, 2.2, 2.2],
                     x_length=4.6, y_length=4.6, tips=False,
                     axis_config={"stroke_width": 2.5, "color": "#31414f",
                                  "include_ticks": False})
        plano.shift(LEFT * 3.2 + DOWN * 0.4)
        mini = Axes(x_range=[0, 1, 1], y_range=[0, 1, 1],
                    x_length=3.4, y_length=2.2, tips=False,
                    axis_config={"stroke_width": 2.5, "color": "#31414f",
                                 "include_ticks": False})
        mini.shift(RIGHT * 3.4 + DOWN * 1.0)
        self.play(Create(plano), run_time=0.8)

        X, y = datos_xor()
        puntos = puntos_datos(plano, X, y)
        self.play(LaggedStart(*[FadeIn(p, scale=0.6) for p in puntos],
                              lag_ratio=0.02), run_time=1.6)

        # Entrenamiento determinista: converge de verdad (perdida final ~1e-3)
        ent = entrenar_mlp(X, y, ocultas=4, epocas=1200, lr=0.9, semilla=3,
                           instantaneas=12)

        # Instantanea inicial: la frontera aun no separa nada
        inicial = frontera_imagen(plano, ent.modelos[0])
        self.play(FadeIn(inicial), run_time=1.0)
        self.wait(0.8)

        # Instantanea final: la region se curva y encierra los racimos
        final = frontera_imagen(plano, ent.modelos[-1])
        self.play(FadeOut(inicial), FadeIn(final), run_time=1.5)
        self.wait(0.6)

        # La perdida cae durante esas mismas epocas
        etiqueta = Text("pérdida", font_size=20, color=COLOR_PERDIDA)
        etiqueta.next_to(mini, UP, buff=0.18)
        self.play(Create(mini), FadeIn(etiqueta), run_time=0.8)
        self.play(Create(curva_perdida(mini, ent.perdidas)), run_time=2.2)

        info = Text(f"pérdida final: {ent.perdida_final:.4f}", font_size=20,
                    color=COLOR_MODELO)
        info.next_to(mini, DOWN, buff=0.3)
        self.play(FadeIn(info), run_time=0.6)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
