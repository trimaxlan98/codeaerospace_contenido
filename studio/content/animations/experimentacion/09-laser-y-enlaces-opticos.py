import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from brillo import punto_brillante
from laser import disparo, rafaga


class LaserYEnlacesOpticos(Scene):
    def construct(self):
        titulo = Text("Enlaces ópticos y láser", font_size=32,
                      color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        estacion = punto_brillante([-5.2, -2.4, 0], color=TEAL_B, radio=0.13)
        sat_a = punto_brillante([-1.5, 2.0, 0], color=YELLOW, radio=0.1)
        sat_b = punto_brillante([3.2, 1.2, 0], color=YELLOW, radio=0.1)
        basura = punto_brillante([5.0, -1.8, 0], color=RED_B, radio=0.09)
        et = Text("estación óptica", font_size=17).next_to(estacion, DOWN,
                                                           buff=0.3)
        eb = Text("desecho", font_size=17, color=RED_B).next_to(basura, DOWN,
                                                                buff=0.3)
        self.play(*[FadeIn(m) for m in (estacion, sat_a, sat_b, basura,
                                        et, eb)], run_time=1.2)

        # Uplink optico tierra -> satelite A (disparo unico)
        self.play(disparo(estacion.get_center(), sat_a.get_center(),
                          color=GREEN, duracion=1.4))
        # Enlace laser inter-satelital con trafico continuo (rafaga)
        self.play(rafaga(sat_a.get_center(), sat_b.get_center(),
                         color=TEAL_B, pulsos=4, duracion=2.4))
        # Laser de seguimiento sobre un desecho (dos pulsos cortos)
        self.play(disparo(sat_b.get_center(), basura.get_center(),
                          color=RED, duracion=1.0, radio_impacto=0.35))
        self.play(disparo(sat_b.get_center(), basura.get_center(),
                          color=RED, duracion=0.8, radio_impacto=0.3))
        self.wait(0.8)
