import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from particulas import Desintegrar, materializar


class DesintegracionEnParticulas(Scene):
    def construct(self):
        titulo = Text("Desintegración en partículas", font_size=32,
                      color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Un texto se disuelve en polvo…
        palabra = Text("SEÑAL", font_size=64, color=BLUE_B)
        self.play(Write(palabra), run_time=1.2)
        self.wait(0.4)
        self.play(Desintegrar(palabra, n=260, dispersion=1.8), run_time=1.8)
        self.remove(palabra)

        # …y el polvo converge en otra cosa: la señal se recompone.
        estrella = Star(n=5, outer_radius=1.1, color=YELLOW,
                        fill_opacity=0.9).shift(DOWN * 0.2)
        self.play(materializar(estrella, n=260, dispersion=2.2), run_time=1.8)
        self.play(Rotate(estrella, angle=TAU / 5), run_time=1)

        # Ida y vuelta encadenada con otra figura
        formula = MathTex(r"E = h\nu", font_size=60, color=TEAL_B)
        formula.shift(DOWN * 0.2)
        self.play(Desintegrar(estrella, n=220, dispersion=1.5, semilla=11),
                  run_time=1.4)
        self.remove(estrella)
        self.play(materializar(formula, n=220, dispersion=1.9, semilla=11),
                  run_time=1.6)
        self.wait(1)
