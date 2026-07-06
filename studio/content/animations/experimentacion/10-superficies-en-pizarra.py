import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np

from manim import *
from brillo import punto_brillante
from pizarra3d import (curva_3d, ejes_pizarra, esfera_pizarra,
                       malla_superficie, proyectar)


class SuperficiesEnPizarra(Scene):
    def construct(self):
        titulo = Text("Superficies 3D en 2D (pizarrón)", font_size=30,
                      color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Superficie de perdida (paraboloide) con descenso por gradiente
        def perdida(x, y):
            return 0.28 * (x * x + y * y)

        ejes = ejes_pizarra(longitud=2.2).shift(LEFT * 3.2 + DOWN * 1.6)
        cuenco = malla_superficie(perdida, x_range=(-1.9, 1.9),
                                  y_range=(-1.9, 1.9), lineas=8)
        cuenco.shift(LEFT * 3.2 + DOWN * 1.6)
        self.play(Create(ejes), run_time=1.2)
        self.play(Create(cuenco), run_time=2.6)

        # Trayectoria del descenso: espiral que cae al minimo
        def descenso(t):
            r = 1.8 * (1 - t)
            ang = 4.5 * t
            x, y = r * np.cos(ang), r * np.sin(ang)
            return (x, y, perdida(x, y) + 0.03)

        camino = curva_3d(descenso, 0, 1, color=RED_B, grosor=3)
        camino.shift(LEFT * 3.2 + DOWN * 1.6)
        bola = punto_brillante(color=RED_B, radio=0.07)
        bola.move_to(camino.get_start())
        etiqueta = Text("descenso por gradiente", font_size=18, color=RED_B)
        etiqueta.next_to(cuenco, DOWN, buff=0.3)
        self.add(bola)
        self.play(Create(camino), MoveAlongPath(bola, camino),
                  FadeIn(etiqueta), run_time=3.5, rate_func=smooth)

        # Solidos de pizarron al costado
        esfera = esfera_pizarra(radio=1.0).shift(RIGHT * 3.6 + UP * 0.9)
        self.play(Create(esfera), run_time=1.6)
        self.wait(1)
