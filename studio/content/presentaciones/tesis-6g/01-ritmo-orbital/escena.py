import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arc, Circle, Create, Dot, FadeIn,
                   FadeOut, GrowFromEdge, Line, Rectangle, Scene, Transform,
                   ValueTracker, VGroup, always_redraw, linear)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
A = T6.ASTREA

C_ORB = np.array([-3.4, 0.0, 0.0])
R_TIERRA = 1.35
R_ORB = 2.45
VUELTA_S = 4.0            # segundos de video por vuelta (90 min de orbita)


def en_orbita(grados):
    a = np.radians(grados)
    return C_ORB + R_ORB * np.array([np.cos(a), np.sin(a), 0.0])


class RitmoOrbital(Scene):
    """ASTREA: un modelo de lenguaje aconseja al controlador termico de una
    carga en la ISS. Aconsejando cada 15 minutos el sistema empeora;
    aconsejando al ritmo de la orbita (90 min) mejora. No fallo la
    inteligencia: fallo el ritmo."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        tierra = Circle(radius=R_TIERRA, stroke_color=PAL.apoyo, stroke_width=3,
                        fill_color=PAL.tenue, fill_opacity=1.0).move_to(C_ORB)
        orbita = Circle(radius=R_ORB, stroke_color=PAL.apoyo, stroke_width=2,
                        stroke_opacity=0.7).move_to(C_ORB)
        ang = ValueTracker(90.0)
        giro = ValueTracker(0.0)

        def satelite():
            p = en_orbita(ang.get_value())
            # el lazo rapido del controlador: un arco que gira sin parar
            lazo = Arc(radius=0.34, start_angle=np.radians(giro.get_value()),
                       angle=np.radians(260), arc_center=p, stroke_color=PAL.tinta,
                       stroke_width=3)
            return VGroup(lazo, Dot(p, radius=0.11, color=PAL.adapta))

        sat = always_redraw(satelite)
        self.play(FadeIn(tierra), Create(orbita), run_time=1.0)
        self.add(sat)
        self.play(ang.animate.set_value(90 - 360), giro.animate.set_value(-360 * 7),
                  run_time=VUELTA_S, rate_func=linear)

        # ── 1. la orbita y el lazo rapido que controla ────────────────────
        presentacion.paso(self, "El lazo")

        # Barras: violaciones termicas relativas a la linea base (= 1).
        y0, h_base = -2.6, 2.6
        xs = {"base": 2.2, "rapida": 3.9, "orbital": 5.6}

        def barra(x, rel, color):
            h = h_base * rel
            r = Rectangle(width=1.0, height=h, stroke_width=0, fill_color=color,
                          fill_opacity=1.0)
            return r.move_to([x, y0 + h / 2, 0])

        suelo = Line([1.4, y0, 0], [6.4, y0, 0], stroke_color=PAL.apoyo, stroke_width=2)
        b_base = barra(xs["base"], 1.0, PAL.estatica)
        e_base = T6.etiqueta("Base", PAL, fs=28).next_to(b_base, DOWN, buff=0.4)
        e_base.set_y(y0 - 0.4)
        titulo_b = T6.etiqueta("Violaciones térmicas", PAL, fs=30, color=PAL.tinta)
        titulo_b.move_to([xs["rapida"], y0 + h_base * 1.42 + 0.55, 0])
        self.play(FadeIn(suelo), GrowFromEdge(b_base, DOWN), FadeIn(e_base),
                  FadeIn(titulo_b), run_time=0.9)

        def pulsos(n, fase=90.0):
            """Marcas en la orbita donde llega un consejo: n por vuelta."""
            return VGroup(*[Dot(en_orbita(fase - k * 360 / n), radius=0.07,
                                color=PAL.priv) for k in range(n)])

        n_rap = round(A["ventana_orbital_min"] / A["ventana_rapida_min"])
        marcas = pulsos(n_rap)
        self.play(FadeIn(marcas), run_time=0.5)
        # cada consejo es una onda que sale del satelite
        ondas = []
        for k in range(n_rap):
            a0 = 90 - 360 - k * 360 / n_rap
            self.play(ang.animate.set_value(a0 - 360 / n_rap),
                      giro.animate.set_value(giro.get_value() - 360 * 7 / n_rap),
                      run_time=VUELTA_S / n_rap, rate_func=linear)
            o = Circle(radius=0.2, stroke_color=PAL.priv, stroke_width=3).move_to(
                en_orbita(ang.get_value()))
            self.add(o)
            ondas.append(o)
            self.play(o.animate.scale(3.2).set_stroke(opacity=0), run_time=0.18)
            self.remove(o)
        b_rap = barra(xs["rapida"], 1.0 + A["violaciones_rapida"], PAL.no)
        e_rap = T6.etiqueta(f"{A['ventana_rapida_min']} min", PAL, fs=28, color=PAL.no)
        e_rap.move_to([xs["rapida"], y0 - 0.4, 0])
        c_rap = T6.cifra(f"+{T6.pct(A['violaciones_rapida'])}", PAL, fs=30, color=PAL.no)
        self.play(GrowFromEdge(b_rap, DOWN), FadeIn(e_rap), run_time=0.9)
        c_rap.next_to(b_rap, UP, buff=0.16)
        self.play(FadeIn(c_rap), run_time=0.4)

        # ── 2. consejo cada 15 minutos: seis por vuelta ───────────────────
        presentacion.paso(self, "Cada 15 min")

        una = pulsos(1)
        self.play(Transform(marcas, una), run_time=0.6)
        a0 = ang.get_value()
        self.play(ang.animate.set_value(a0 - 360), giro.animate.set_value(giro.get_value() - 360 * 7),
                  run_time=VUELTA_S, rate_func=linear)
        o = Circle(radius=0.2, stroke_color=PAL.priv, stroke_width=3).move_to(
            en_orbita(ang.get_value()))
        self.add(o)
        self.play(o.animate.scale(3.6).set_stroke(opacity=0), run_time=0.3)
        self.remove(o)
        b_orb = barra(xs["orbital"], 1.0 + A["violaciones_orbital"], PAL.ok)
        e_orb = T6.etiqueta(f"{A['ventana_orbital_min']} min", PAL, fs=28, color=PAL.ok)
        e_orb.move_to([xs["orbital"], y0 - 0.4, 0])
        c_orb = T6.cifra(f"−{T6.pct(-A['violaciones_orbital'])}", PAL, fs=30, color=PAL.ok)
        self.play(GrowFromEdge(b_orb, DOWN), FadeIn(e_orb), run_time=0.9)
        c_orb.next_to(b_orb, UP, buff=0.16)
        self.play(FadeIn(c_orb), run_time=0.4)
        self.wait(0.6)

        # ── 3. consejo al ritmo de la orbita ──────────────────────────────
        presentacion.paso(self, "Cada vuelta")
