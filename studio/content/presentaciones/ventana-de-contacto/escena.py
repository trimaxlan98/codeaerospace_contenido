import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (Arc, Circle, Create, Dot, FadeIn, FadeOut, GrowFromCenter,
                   Line, Scene, Transform, UP, DOWN, LEFT, RIGHT, VGroup,
                   Write, MathTex, always_redraw, ValueTracker, PI, DEGREES)

import presentacion

PZA = presentacion.lienzo()


class VentanaDeContacto(Scene):
    """Por que una estacion terrena solo habla con un satelite LEO unos
    minutos: tres pasos, uno por clic."""

    def setup(self):
        presentacion.aplicar(self, PZA)

    def construct(self):
        r_tierra = 1.9
        r_orbita = 2.55

        tierra = Circle(radius=r_tierra, stroke_width=3,
                        stroke_color=PZA.acento, fill_opacity=0.06,
                        fill_color=PZA.acento).shift(DOWN * 0.9)
        orbita = Circle(radius=r_orbita, stroke_width=2,
                        stroke_color=PZA.apoyo).move_to(tierra)
        estacion = Dot(tierra.get_center() + UP * r_tierra, radius=0.075,
                       color=PZA.tinta)
        et_estacion = presentacion.rotulo("Estación", PZA, font_size=24)
        # Arriba y a la izquierda: pegado al punto, el rotulo caia encima de
        # la linea del horizonte, que pasa exactamente por ahi.
        et_estacion.move_to(estacion.get_center() + UP * 0.42 + LEFT * 1.15)

        t = presentacion.titulo("Ventana de contacto", PZA)
        t.move_to(UP * (PZA.tope - 0.45))

        self.play(FadeIn(t, shift=DOWN * 0.2), run_time=0.8)
        self.play(Create(tierra), Create(orbita), run_time=1.2)
        self.play(GrowFromCenter(estacion), FadeIn(et_estacion), run_time=0.6)

        # ── paso 1: el escenario ya está puesto ──────────────────────────
        presentacion.paso(self, "El escenario")

        # El satélite recorre la órbita; el enlace solo existe sobre el
        # horizonte local de la estación.
        ang = ValueTracker(200 * DEGREES)
        centro = tierra.get_center()

        def pos_sat():
            a = ang.get_value()
            return centro + r_orbita * np.array([np.cos(a), np.sin(a), 0.0])

        sat = always_redraw(lambda: Dot(pos_sat(), radius=0.07,
                                        color=PZA.acento))
        enlace = always_redraw(lambda: Line(
            estacion.get_center(), pos_sat(), stroke_width=3,
            stroke_color=PZA.acento,
            stroke_opacity=0.9 if pos_sat()[1] > estacion.get_center()[1] else 0.0))

        horizonte = Line(estacion.get_center() + LEFT * 3.1,
                         estacion.get_center() + RIGHT * 3.1,
                         stroke_width=2, stroke_color=PZA.apoyo)
        et_horizonte = presentacion.rotulo("Horizonte local", PZA, font_size=24)
        et_horizonte.next_to(horizonte, RIGHT, buff=0.15).shift(DOWN * 0.18)

        self.play(Create(horizonte), FadeIn(et_horizonte), run_time=0.7)
        self.add(sat, enlace)
        self.play(ang.animate.set_value(-20 * DEGREES), run_time=3.0)

        # ── paso 2: se vio el paso completo ──────────────────────────────
        presentacion.paso(self, "El paso")

        # La cifra: el arco visible sobre el horizonte, en minutos.
        arco = Arc(radius=r_orbita, start_angle=41 * DEGREES,
                   angle=98 * DEGREES, arc_center=centro,
                   stroke_width=6, stroke_color=PZA.acento)
        cifra = presentacion.dato("≈ 9 min por paso", PZA, font_size=30)
        cifra.move_to(UP * (PZA.tope - 1.15))

        self.play(Create(arco), run_time=1.2)
        self.play(Write(cifra), run_time=0.8)
        self.wait(0.6)

        # ── paso 3: la conclusión ────────────────────────────────────────
        presentacion.paso(self, "La cifra")
