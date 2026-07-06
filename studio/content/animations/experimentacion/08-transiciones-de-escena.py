import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from transiciones import (transicion_deslizar, transicion_persiana,
                          transicion_zoom)


def diapositiva(titulo, cuerpo, color):
    t = Text(titulo, font_size=34, color=color)
    c = Text(cuerpo, font_size=22, color=GREY_B)
    return VGroup(t, c).arrange(DOWN, buff=0.5)


class TransicionesDeEscena(Scene):
    def construct(self):
        d1 = diapositiva("1 · Deslizar", "el contenido sale empujado", GOLD)
        d2 = diapositiva("2 · Zoom", "atraviesa la cámara", TEAL_B)
        d3 = diapositiva("3 · Persiana", "franjas que permutan la escena",
                         BLUE_B)
        cierre = diapositiva("Fin", "tres transiciones reutilizables", GREY_B)

        self.play(FadeIn(d1, shift=DOWN * 0.3), run_time=1)
        self.wait(1)
        self.play(transicion_deslizar(d1, d2, direccion=LEFT), run_time=1.4)
        self.wait(1)
        self.play(transicion_zoom(d2, d3), run_time=1.5)
        self.wait(1)
        self.play(transicion_persiana(d3, cierre, franjas=9))
        self.wait(1.2)
