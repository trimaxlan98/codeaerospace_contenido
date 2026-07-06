import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from brillo import punto_brillante
from senal import PulsoDeSenal, destello


class PulsosDeSenal(Scene):
    def construct(self):
        titulo = Text("Pulsos de señal", font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Estación terrena, satélite GEO y estación remota
        tierra = punto_brillante([-5, -2.2, 0], color=TEAL_B, radio=0.12)
        sat = punto_brillante([0, 2.2, 0], color=YELLOW, radio=0.1)
        remota = punto_brillante([5, -2.2, 0], color=RED_B, radio=0.12)
        et_t = Text("estación A", font_size=18).next_to(tierra, DOWN, buff=0.3)
        et_s = Text("satélite", font_size=18).next_to(sat, UP, buff=0.3)
        et_r = Text("estación B", font_size=18).next_to(remota, DOWN, buff=0.3)
        self.play(*[FadeIn(m) for m in (tierra, sat, remota, et_t, et_s, et_r)],
                  run_time=1.2)

        subida = ArcBetweenPoints(tierra.get_center(), sat.get_center(),
                                  angle=-0.35, color=GREY_C, stroke_width=2)
        bajada = ArcBetweenPoints(sat.get_center(), remota.get_center(),
                                  angle=-0.35, color=GREY_C, stroke_width=2)
        self.play(Create(subida), Create(bajada), run_time=1)

        paquete = punto_brillante(color=WHITE, radio=0.05, alcance=3.5)
        paquete.move_to(tierra.get_center())
        self.add(paquete)

        # Uplink: el paquete viaja con su destello por el enlace
        self.play(PulsoDeSenal(paquete, subida), destello(subida, YELLOW),
                  run_time=1.4)
        # Downlink hacia la estación remota
        self.play(PulsoDeSenal(paquete, bajada), destello(bajada, YELLOW),
                  run_time=1.4)
        # ACK: ida y vuelta en una sola animación por el mismo camino
        ack = Text("ACK (ida y vuelta)", font_size=18, color=GREY_B)
        ack.to_edge(DOWN)
        self.play(FadeIn(ack), run_time=0.5)
        self.play(PulsoDeSenal(paquete, bajada, ida_y_vuelta=True),
                  destello(bajada, TEAL_B), run_time=2)
        self.wait(0.8)
