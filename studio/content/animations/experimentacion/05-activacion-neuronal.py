import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from neuronal import RedNeuronal


class ActivacionNeuronal(Scene):
    def construct(self):
        titulo = Text("Activación de una red neuronal", font_size=32,
                      color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        red = RedNeuronal(capas=(4, 7, 7, 3)).shift(DOWN * 0.4)
        entrada = Text("entrada", font_size=18, color=GREY_B)
        entrada.next_to(red.capas_neuronas[0], DOWN, buff=0.45)
        salida = Text("salida", font_size=18, color=GREY_B)
        salida.next_to(red.capas_neuronas[-1], DOWN, buff=0.45)

        self.play(Create(red), run_time=2.4)
        self.play(FadeIn(entrada), FadeIn(salida), run_time=0.6)

        # Dos pasadas forward con colores distintos (dos inferencias)
        self.play(red.activacion(color=YELLOW))
        self.wait(0.3)
        self.play(red.activacion(color=TEAL_B))
        self.wait(0.8)
