from manim import *
import numpy as np


class SuperficiesInteligentesReconfigurables(Scene):
    def construct(self):
        titulo = Text("Superficies inteligentes reconfigurables (RIS)",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Escena urbana: antena, edificio que bloquea, usuario en sombra
        antena = VGroup(
            Line(DOWN * 2.9 + LEFT * 5.6, DOWN * 1.1 + LEFT * 5.6, color=GREY_B,
                 stroke_width=5),
            Dot(DOWN * 1.0 + LEFT * 5.6, color=BLUE_B, radius=0.12),
        )
        ant_txt = Text("Antena", font_size=18, color=BLUE_B)
        ant_txt.next_to(antena, DOWN, buff=0.15)
        edificio = Rectangle(width=1.3, height=2.6, color=GREY_B, fill_opacity=0.5,
                             fill_color=GREY_B).move_to(LEFT * 1.6 + DOWN * 1.7)
        usuario = Square(side_length=0.32, color=YELLOW, fill_opacity=0.7,
                         fill_color=YELLOW).move_to(RIGHT * 2.6 + DOWN * 2.5)
        usr_txt = Text("Usuario sin señal", font_size=18, color=YELLOW)
        usr_txt.next_to(usuario, RIGHT, buff=0.25)
        self.play(FadeIn(antena), FadeIn(ant_txt), FadeIn(edificio),
                  FadeIn(usuario), FadeIn(usr_txt), run_time=2)

        # El haz directo se bloquea
        directo = Arrow(antena[1].get_center(), usuario.get_center(), color=RED_D,
                        buff=0.15)
        bloqueo = Cross(scale_factor=0.3).move_to(
            edificio.get_center() + UP * 0.4)
        problema = Text("En sub-THz, un obstáculo mata el enlace",
                        font_size=20, color=RED_D).to_edge(DOWN)
        self.play(GrowArrow(directo), FadeIn(problema), run_time=1.2)
        self.play(Create(bloqueo), directo.animate.set_stroke(opacity=0.25),
                  run_time=1)

        # RIS en la pared de otro edificio
        ris = VGroup(*[
            Square(side_length=0.22, color=GOLD, fill_opacity=0.35, fill_color=GOLD)
            for _ in range(8)
        ]).arrange_in_grid(rows=2, cols=4, buff=0.06)
        ris.rotate(-PI / 14).move_to(UP * 1.7 + RIGHT * 0.4)
        ris_txt = Text("RIS: cientos de celdas pasivas\nque desfasan la onda al reflejar",
                       font_size=18, color=GOLD, line_spacing=0.9)
        ris_txt.next_to(ris, RIGHT, buff=0.4)
        self.play(FadeIn(ris, lag_ratio=0.1), FadeIn(ris_txt), run_time=2)

        # Camino reflejado y controlado
        sube = Arrow(antena[1].get_center(), ris.get_center(), color=BLUE_B, buff=0.2)
        baja = Arrow(ris.get_center(), usuario.get_center(), color=BLUE_B, buff=0.2)
        solucion = Text("La superficie 'dobla' el haz hacia el usuario: espejo programable",
                        font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(problema, solucion), GrowArrow(sube),
                  run_time=1.2)
        fases = VGroup(*[
            c.copy().set_fill(YELLOW, opacity=0.7) for c in ris
        ])
        self.play(LaggedStart(*[FadeIn(f, rate_func=there_and_back) for f in fases],
                              lag_ratio=0.1), run_time=1.2)
        self.remove(fases)
        self.play(GrowArrow(baja), run_time=1)
        self.play(Flash(usuario, color=YELLOW, flash_radius=0.5), run_time=0.8)
        ok = Text("Usuario conectado", font_size=18, color=YELLOW).move_to(usr_txt)
        self.play(ReplacementTransform(usr_txt, ok), run_time=0.8)

        # Reconfigurable: si el usuario se mueve, el haz lo sigue
        self.play(usuario.animate.shift(RIGHT * 1.8), ok.animate.shift(RIGHT * 1.8),
                  Transform(baja, Arrow(ris.get_center(),
                                        usuario.get_center() + RIGHT * 1.8,
                                        color=BLUE_B, buff=0.2)),
                  run_time=2)

        cierre = Text("Sin radios ni cables: casi sin consumo, la pared se vuelve parte de la red",
                      font_size=19, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(solucion, cierre), run_time=1.2)
        self.wait(2)
