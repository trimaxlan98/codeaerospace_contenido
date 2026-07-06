import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from brillo import punto_brillante
from kepler import OrbitaKepler, MoverKepler


class OrbitaKeplerReal(Scene):
    def construct(self):
        titulo = Text("Órbita kepleriana real", font_size=32,
                      color=GOLD).to_edge(UP)
        subtitulo = Text("acelera en el perigeo, frena en el apogeo",
                         font_size=20, color=GREY_B)
        subtitulo.next_to(titulo, DOWN, buff=0.2)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), FadeIn(subtitulo),
                  run_time=1)

        orbita = OrbitaKepler(a=3.1, e=0.65, color=BLUE_B).shift(DOWN * 0.7)
        tierra = punto_brillante(color=BLUE, radio=0.16, alcance=2.4)
        tierra.move_to(orbita._foco_absoluto())

        perigeo = Text("perigeo", font_size=18, color=YELLOW)
        perigeo.next_to(orbita.posicion(0.0), RIGHT, buff=0.25)
        apogeo = Text("apogeo", font_size=18, color=TEAL_B)
        apogeo.next_to(orbita.posicion(0.5), LEFT, buff=0.25)

        self.play(Create(orbita.trayectoria), FadeIn(tierra), run_time=1.5)
        self.play(FadeIn(perigeo), FadeIn(apogeo), run_time=0.8)

        sat = punto_brillante(color=YELLOW, radio=0.07, alcance=3.0)
        sat.move_to(orbita.posicion(0.0))
        estela = TracedPath(sat.get_center, dissipating_time=1.1,
                            stroke_color=YELLOW, stroke_width=3)
        self.add(estela, sat)

        # Dos vueltas: la velocidad varia sola porque MoverKepler resuelve
        # la ecuacion de Kepler en cada frame (2a ley: areas iguales).
        self.play(MoverKepler(sat, orbita, vueltas=2), run_time=9)
        self.wait(0.6)
