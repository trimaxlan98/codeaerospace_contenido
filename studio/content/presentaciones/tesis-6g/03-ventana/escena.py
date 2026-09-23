import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arc, Circle, Create, DashedLine, Dot,
                   FadeIn, FadeOut, Line, Polygon, Rectangle, Scene, Square,
                   ValueTracker, VGroup, always_redraw, linear)

import ntn
import presentacion
import satelites as sat
import tesis6g as T6

LZ, PAL = T6.pieza()

H_KM = 600.0
EL_MIN = ntn.ELEVACION_MINIMA_DEG
PASE = ntn.pase_leo(H_KM, 53.0, lat_gs=19.43, lon_gs=-99.13)   # el mas alto del dia
PERIODO_MIN = sat.periodo_orbital(H_KM)["minutos"]
# Semiangulo central visible con elevacion >= EL_MIN (geometria de la esfera)
R_T = ntn.R_TIERRA_KM
LAMBDA = np.degrees(np.arccos(R_T * np.cos(np.radians(EL_MIN)) / (R_T + H_KM))) - EL_MIN

# ── vista cercana: la Tierra y la orbita A ESCALA ENTRE SI ───────────────────
R_S = 13.4                                  # radio de la Tierra en pantalla
R_O = R_S * (R_T + H_KM) / R_T              # la altura sale de la proporcion real
Y_SUP = -2.35                               # donde asoma la superficie
C_TIERRA = np.array([0.0, Y_SUP - R_S, 0.0])
ESTACION = np.array([0.0, Y_SUP, 0.0])
TH_BORDE = np.degrees(np.arcsin(7.4 / R_O))  # el satelite entra/sale del cuadro

# ── linea de tiempo: una vuelta entera ───────────────────────────────────────
TL_X0, TL_X1, TL_Y = -5.2, 5.2, 3.25


def en_orbita(th, centro=C_TIERRA, r=R_O):
    a = np.radians(th)
    return centro + r * np.array([np.sin(a), np.cos(a), 0.0])


def x_tiempo(th):
    """Posicion en la linea de tiempo del satelite en el angulo th (desde que
    entra por la izquierda hasta dar la vuelta completa)."""
    return TL_X0 + (TL_X1 - TL_X0) * ((th + TH_BORDE) % 360.0) / 360.0


class Ventana(Scene):
    """Un satelite LEO a 600 km solo es visible desde una estacion unos
    minutos por vuelta: la red no esta siempre ahi."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        tierra = Circle(radius=R_S, stroke_color=PAL.apoyo, stroke_width=3,
                        fill_color=PAL.tenue, fill_opacity=1.0).move_to(C_TIERRA)
        orbita = Circle(radius=R_O, stroke_color=PAL.apoyo, stroke_width=2,
                        stroke_opacity=0.7).move_to(C_TIERRA)
        est = Square(side_length=0.22, stroke_width=0, fill_color=PAL.tinta,
                     fill_opacity=1.0).move_to(ESTACION + UP * 0.11)
        # El cono de visibilidad: por encima de EL_MIN sobre el horizonte local
        pa, pb = en_orbita(-LAMBDA), en_orbita(LAMBDA)
        cono = Polygon(ESTACION, pa, *[en_orbita(t) for t in np.linspace(-LAMBDA, LAMBDA, 30)],
                       pb, stroke_width=0, fill_color=PAL.priv, fill_opacity=0.14)
        bordes = VGroup(DashedLine(ESTACION, pa, dash_length=0.12, stroke_color=PAL.priv,
                                   stroke_width=2),
                        DashedLine(ESTACION, pb, dash_length=0.12, stroke_color=PAL.priv,
                                   stroke_width=2))
        et_aos = T6.etiqueta("AOS", PAL, fs=28, color=PAL.priv).next_to(pa, UP + LEFT, buff=0.12)
        et_los = T6.etiqueta("LOS", PAL, fs=28, color=PAL.priv).next_to(pb, UP + RIGHT, buff=0.12)

        self.play(FadeIn(tierra), Create(orbita), FadeIn(est), run_time=1.2)
        self.play(FadeIn(cono), Create(bordes), run_time=0.8)

        # linea de tiempo de una vuelta completa
        riel = Line([TL_X0, TL_Y, 0], [TL_X1, TL_Y, 0], stroke_color=PAL.tenue,
                    stroke_width=10)
        dur_min = PASE["duracion_s"] / 60.0
        l_pase = (TL_X1 - TL_X0) * dur_min / PERIODO_MIN
        x_c = x_tiempo(0.0)
        tramo = Line([x_c - l_pase / 2, TL_Y, 0], [x_c + l_pase / 2, TL_Y, 0],
                     stroke_color=PAL.priv, stroke_width=10)
        self.play(FadeIn(riel), run_time=0.5)

        th = ValueTracker(-TH_BORDE)
        visible = lambda: abs(th.get_value()) <= LAMBDA
        satelite = always_redraw(lambda: VGroup(
            Dot(en_orbita(th.get_value()), radius=0.2, color=PAL.adapta, fill_opacity=0.25),
            Dot(en_orbita(th.get_value()), radius=0.1, color=PAL.adapta)))
        enlace = always_redraw(lambda: Line(
            ESTACION + UP * 0.22, en_orbita(th.get_value()), stroke_color=PAL.adapta,
            stroke_width=3, stroke_opacity=0.95 if visible() else 0.0))
        cabeza = always_redraw(lambda: Dot([x_tiempo(th.get_value()), TL_Y, 0],
                                           radius=0.09, color=PAL.tinta))
        self.add(enlace, satelite, cabeza)
        self.play(th.animate.set_value(-LAMBDA), run_time=1.5, rate_func=linear)
        self.play(FadeIn(et_aos), run_time=0.3)
        self.play(th.animate.set_value(LAMBDA), Create(tramo), run_time=3.0, rate_func=linear)
        self.play(FadeIn(et_los), run_time=0.3)
        self.play(th.animate.set_value(TH_BORDE), run_time=1.5, rate_func=linear)
        c_pase = T6.cifra(f"{dur_min:.1f} min", PAL, fs=32, color=PAL.priv)
        c_pase.next_to(tramo, DOWN, buff=0.2)
        self.play(FadeIn(c_pase), run_time=0.5)

        # ── 1. el pase ────────────────────────────────────────────────────
        presentacion.paso(self, "El pase")

        # La vista se aleja: la misma geometria, entera. El casquete visible
        # es el arco de +-LAMBDA sobre la estacion.
        r_ch = 2.05
        c_ch = np.array([0.0, -0.75, 0.0])
        r_och = r_ch * (R_T + H_KM) / R_T
        chica = VGroup(
            Circle(radius=r_ch, stroke_color=PAL.apoyo, stroke_width=3,
                   fill_color=PAL.tenue, fill_opacity=1.0).move_to(c_ch),
            Circle(radius=r_och, stroke_color=PAL.apoyo, stroke_width=2,
                   stroke_opacity=0.7).move_to(c_ch))
        arco_vis = Arc(radius=r_och, start_angle=np.radians(90 + LAMBDA),
                       angle=-np.radians(2 * LAMBDA), arc_center=c_ch,
                       stroke_color=PAL.priv, stroke_width=9)
        est_ch = Square(side_length=0.16, stroke_width=0, fill_color=PAL.tinta,
                        fill_opacity=1.0).move_to(c_ch + UP * (r_ch + 0.08))
        cerca = VGroup(tierra, orbita, est, cono, bordes, et_aos, et_los)
        self.remove(enlace, satelite)
        self.play(FadeOut(cerca, scale=0.2, shift=DOWN * 1.0),
                  FadeIn(chica), FadeIn(est_ch), Create(arco_vis), run_time=1.3)

        sat_ch = always_redraw(lambda: VGroup(
            Dot(en_orbita(th.get_value(), c_ch, r_och), radius=0.18, color=PAL.adapta,
                fill_opacity=0.25),
            Dot(en_orbita(th.get_value(), c_ch, r_och), radius=0.09, color=PAL.adapta)))
        self.add(sat_ch)
        self.play(th.animate.set_value(360.0 - TH_BORDE - 0.01), run_time=6.0, rate_func=linear)
        c_vuelta = T6.cifra(f"{PERIODO_MIN:.0f} min", PAL, fs=32, color=PAL.apoyo)
        c_vuelta.next_to(riel, DOWN, buff=0.2).align_to(riel, RIGHT)
        self.play(FadeIn(c_vuelta), run_time=0.5)
        self.wait(0.6)

        # ── 2. el resto de la vuelta, sin enlace ──────────────────────────
        presentacion.paso(self, "La vuelta")
