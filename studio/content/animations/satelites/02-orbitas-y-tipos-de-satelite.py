from manim import *
import numpy as np


class OrbitasYTiposDeSatelite(Scene):
    def construct(self):
        titulo = Text("Órbitas y familias de satélites", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        centro = DOWN * 0.5 + LEFT * 2.5
        tierra = Circle(radius=0.55, color=BLUE_D, fill_opacity=1, fill_color=BLUE_D)
        tierra.move_to(centro)
        self.play(GrowFromCenter(tierra), run_time=1)

        # Tres regimenes clasicos (radios no a escala)
        datos = [
            ("LEO · 400-2000 km · ~90 min", 1.1, BLUE_B),
            ("MEO · ~20 000 km · ~12 h (GPS)", 1.9, GREY_B),
            ("GEO · 35 786 km · 24 h", 2.9, GOLD),
        ]
        orbitas = VGroup()
        leyenda = VGroup()
        for i, (nombre, r, color) in enumerate(datos):
            o = Circle(radius=r, color=color).move_to(centro)
            t = Text(nombre, font_size=19, color=color)
            t.move_to(RIGHT * 3.9 + UP * (1.6 - i * 0.5))
            orbitas.add(o)
            leyenda.add(t)
            self.play(Create(o), FadeIn(t), run_time=1.2)

        # Cada altitud implica un periodo distinto: 3 satelites en movimiento
        sats = VGroup(*[
            Dot(o.point_from_proportion(0), color=c, radius=0.08)
            for o, (_, _, c) in zip(orbitas, datos)
        ])
        self.play(FadeIn(sats), run_time=0.8)
        # velocidades relativas ~ ley de Kepler: mas alto, mas lento
        self.play(
            MoveAlongPath(sats[0], orbitas[0]),
            Rotate(sats[1], angle=TAU * 0.35, about_point=centro),
            Rotate(sats[2], angle=TAU * 0.12, about_point=centro),
            run_time=6, rate_func=linear,
        )

        nota = Text("Más altitud = período más largo (Kepler)",
                    font_size=22, color=GREY_B)
        nota.move_to(RIGHT * 3.9 + DOWN * 0.1)
        self.play(FadeIn(nota), run_time=1)

        # Orbita polar heliosincrona: barre toda la superficie
        polar = Ellipse(width=1.0, height=5.9, color=YELLOW).move_to(centro)
        polar_txt = Text("Polar / heliosíncrona:\nobservación de la Tierra",
                         font_size=19, color=YELLOW, line_spacing=0.8)
        polar_txt.move_to(RIGHT * 3.9 + DOWN * 1.2)
        sat_polar = Dot(polar.point_from_proportion(0.25), color=YELLOW, radius=0.08)
        self.play(Create(polar), FadeIn(polar_txt), run_time=1.5)
        self.play(FadeIn(sat_polar), run_time=0.4)
        self.play(MoveAlongPath(sat_polar, polar), run_time=3, rate_func=linear)

        cierre = Text("La órbita se elige según la misión: cobertura, latencia o persistencia",
                      font_size=22, color=BLUE_B).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
