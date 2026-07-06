from manim import *
import numpy as np


class BasuraEspacial(Scene):
    def construct(self):
        titulo = Text("Basura espacial y sostenibilidad orbital",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        tierra = Circle(radius=0.9, color=BLUE_D, fill_opacity=1, fill_color=BLUE_D)
        tierra.shift(DOWN * 0.6)
        self.play(GrowFromCenter(tierra), run_time=1)

        # Poblacion inicial de objetos en LEO (posiciones deterministas)
        rng = np.random.default_rng(42)
        orbitas = VGroup(*[
            Circle(radius=r, color=GREY_B, stroke_opacity=0.4).move_to(tierra)
            for r in [1.5, 1.9, 2.3]
        ])
        self.play(Create(orbitas), run_time=1.5)

        objetos = VGroup()
        for r in [1.5, 1.9, 2.3]:
            for ang in rng.uniform(0, TAU, 6):
                p = tierra.get_center() + r * np.array([np.cos(ang), np.sin(ang), 0])
                objetos.add(Dot(p, color=GREY_B, radius=0.045))
        contador_txt = Text("Objetos rastreados:", font_size=22, color=GREY_B)
        contador = Integer(18, font_size=30, color=YELLOW)
        panel = VGroup(contador_txt, contador).arrange(RIGHT, buff=0.25)
        panel.to_corner(UR).shift(DOWN * 0.8)
        self.play(FadeIn(objetos, lag_ratio=0.05), FadeIn(panel), run_time=2)

        # Colision: dos objetos generan una nube de fragmentos
        a, b = objetos[3], objetos[10]
        choque = tierra.get_center() + 1.9 * np.array([np.cos(0.8), np.sin(0.8), 0])
        self.play(a.animate.move_to(choque), b.animate.move_to(choque), run_time=1.5)
        self.play(Flash(Dot(choque), color=YELLOW, flash_radius=0.6), run_time=0.8)

        fragmentos = VGroup()
        for ang in np.linspace(0, TAU, 12, endpoint=False):
            destino = choque + 0.9 * np.array([np.cos(ang), np.sin(ang), 0])
            fragmentos.add(Dot(choque, color=YELLOW, radius=0.03))
        anims = [f.animate.move_to(
            choque + 0.9 * np.array([np.cos(ang), np.sin(ang), 0]))
            for f, ang in zip(fragmentos, np.linspace(0, TAU, 12, endpoint=False))]
        self.add(fragmentos)
        self.play(*anims, contador.animate.set_value(30), run_time=1.8)

        kessler = Text("Síndrome de Kessler: cada choque siembra el siguiente",
                       font_size=22, color=YELLOW).to_edge(DOWN)
        self.play(FadeIn(kessler), run_time=1.2)
        self.wait(1)

        # Mitigacion: desorbitar al final de la vida util
        sat = Dot(tierra.get_center() + RIGHT * 2.3, color=BLUE_B, radius=0.08)
        self.play(FadeIn(sat), run_time=0.5)
        espiral = ParametricFunction(
            lambda t: tierra.get_center() + (2.3 - 1.15 * t) * np.array([
                np.cos(TAU * t), np.sin(TAU * t), 0]),
            t_range=[0, 1], color=BLUE_B,
        )
        mitiga = Text("Mitigación: desorbitar en menos de 25 años tras la misión",
                      font_size=22, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(kessler, mitiga), run_time=1)
        self.play(Create(espiral), MoveAlongPath(sat, espiral),
                  run_time=4, rate_func=linear)
        self.play(FadeOut(sat, scale=0.2), run_time=0.8)

        cierre = Text("La órbita baja es un recurso compartido y finito",
                      font_size=24, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(mitiga, cierre), run_time=1.2)
        self.wait(2)
