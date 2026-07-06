import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from brillo import con_brillo, punto_brillante


class BrilloYHalos(Scene):
    def construct(self):
        titulo = con_brillo(Text("Brillo y halos", font_size=36, color=GOLD),
                            ancho_max=10, opacidad=0.3)
        titulo.to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Un "cielo": estrellas con halo de distintos tamaños y colores
        posiciones = [(-4.5, 0.6), (-2.8, -1.2), (-1.0, 0.9), (0.8, -0.6),
                      (2.4, 1.1), (4.3, -1.0)]
        colores = [WHITE, BLUE_B, YELLOW, WHITE, RED_B, TEAL_B]
        estrellas = VGroup(*[
            punto_brillante([x, y, 0], color=c, radio=0.05 + 0.02 * (i % 3))
            for i, ((x, y), c) in enumerate(zip(posiciones, colores))
        ])
        self.play(LaggedStart(*[FadeIn(e, scale=0.3) for e in estrellas],
                              lag_ratio=0.15), run_time=2)

        # El satelite: nucleo + halo que "respira"
        sat = punto_brillante([0, -2.6, 0], color=YELLOW, radio=0.1,
                              alcance=4.0)
        etiqueta = Text("satélite activo", font_size=20, color=YELLOW)
        etiqueta.next_to(sat, DOWN, buff=0.35)
        self.play(FadeIn(sat, scale=0.5), FadeIn(etiqueta), run_time=1)
        self.play(sat.animate.scale(1.35), rate_func=there_and_back,
                  run_time=1.4)
        self.play(sat.animate.scale(1.35), rate_func=there_and_back,
                  run_time=1.4)

        # Una orbita con el mismo halo aplicado a un trazo
        orbita = con_brillo(Arc(radius=2.4, start_angle=PI * 0.15,
                                angle=PI * 0.7, color=BLUE_B),
                            ancho_max=9, opacidad=0.35)
        self.play(Create(orbita), run_time=1.6)
        self.wait(1)
