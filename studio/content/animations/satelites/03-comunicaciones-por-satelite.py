from manim import *
import numpy as np


class ComunicacionesPorSatelite(Scene):
    def construct(self):
        titulo = Text("Comunicaciones por satélite", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Superficie terrestre y dos estaciones lejanas
        suelo = Arc(radius=8, start_angle=PI / 2 - 0.5, angle=1.0,
                    color=GREY_B, arc_center=DOWN * 10.4)
        est_a = Triangle(color=BLUE_B, fill_opacity=1, fill_color=BLUE_B).scale(0.25)
        est_a.move_to(LEFT * 4.6 + DOWN * 2.6)
        est_b = est_a.copy().set_color(BLUE_D).move_to(RIGHT * 4.6 + DOWN * 2.6)
        txt_a = Text("Estación A", font_size=19, color=BLUE_B).next_to(est_a, DOWN, buff=0.2)
        txt_b = Text("Estación B", font_size=19, color=BLUE_D).next_to(est_b, DOWN, buff=0.2)
        self.play(Create(suelo), FadeIn(est_a), FadeIn(est_b),
                  FadeIn(txt_a), FadeIn(txt_b), run_time=1.5)

        problema = Text("La curvatura terrestre bloquea el enlace directo",
                        font_size=22, color=GREY_B).to_edge(DOWN)
        directo = DashedLine(est_a.get_top(), est_b.get_top(), color=RED_D)
        cruz = Cross(scale_factor=0.3).move_to(directo.get_center())
        self.play(Create(directo), FadeIn(problema), run_time=1.2)
        self.play(Create(cruz), run_time=0.8)
        self.play(FadeOut(directo), FadeOut(cruz), run_time=0.8)

        # Satelite repetidor ("bent pipe")
        sat = VGroup(
            Square(side_length=0.4, color=GOLD, fill_opacity=0.4, fill_color=GOLD),
            Rectangle(width=0.5, height=0.22, color=BLUE_D, fill_opacity=0.8,
                      fill_color=BLUE_D).shift(LEFT * 0.5),
            Rectangle(width=0.5, height=0.22, color=BLUE_D, fill_opacity=0.8,
                      fill_color=BLUE_D).shift(RIGHT * 0.5),
        ).move_to(UP * 1.8)
        sat_txt = Text("Transpondedor: recibe, amplifica y reenvía",
                       font_size=20, color=GOLD).next_to(sat, UP, buff=0.3)
        self.play(FadeIn(sat, shift=DOWN * 0.4), FadeIn(sat_txt), run_time=1.5)

        # Enlace ascendente y descendente
        subida = Arrow(est_a.get_top(), sat.get_corner(DL), color=YELLOW, buff=0.15)
        bajada = Arrow(sat.get_corner(DR), est_b.get_top(), color=BLUE_B, buff=0.15)
        subida_txt = Text("Uplink · 14 GHz", font_size=18, color=YELLOW)
        subida_txt.next_to(subida.get_center(), LEFT, buff=0.25)
        bajada_txt = Text("Downlink · 12 GHz", font_size=18, color=BLUE_B)
        bajada_txt.next_to(bajada.get_center(), RIGHT, buff=0.25)
        self.play(GrowArrow(subida), FadeIn(subida_txt), run_time=1.2)
        self.play(GrowArrow(bajada), FadeIn(bajada_txt), run_time=1.2)

        # Paquete viajando y latencia GEO
        paquete = Dot(est_a.get_top(), color=WHITE, radius=0.07)
        self.play(FadeIn(paquete), run_time=0.4)
        self.play(paquete.animate.move_to(sat.get_center()), run_time=1.4, rate_func=linear)
        self.play(paquete.animate.move_to(est_b.get_top()), run_time=1.4, rate_func=linear)
        latencia = Text("GEO: ~250 ms ida y vuelta · LEO: ~30 ms",
                        font_size=22, color=YELLOW).to_edge(DOWN)
        self.play(ReplacementTransform(problema, latencia), run_time=1.2)

        # Huella de cobertura
        huella = Arc(radius=2.6, start_angle=-PI / 2 - 0.6, angle=1.2,
                     color=GOLD, arc_center=sat.get_center())
        cono = VGroup(
            DashedLine(sat.get_bottom(), sat.get_center() + 2.6 * np.array(
                [np.sin(-0.6), -np.cos(-0.6), 0]), color=GOLD, stroke_opacity=0.6),
            DashedLine(sat.get_bottom(), sat.get_center() + 2.6 * np.array(
                [np.sin(0.6), -np.cos(0.6), 0]), color=GOLD, stroke_opacity=0.6),
        )
        huella_txt = Text("Huella: la zona que ve el satélite", font_size=20, color=GOLD)
        huella_txt.move_to(DOWN * 0.4)
        self.play(Create(cono), Create(huella), FadeIn(huella_txt), run_time=2)
        self.wait(2)
