import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Circle, Create, DashedLine,
                   DashedVMobject, Dot, FadeIn, FadeOut, Line, Rectangle, Scene,
                   Square, Transform, ValueTracker, VGroup, always_redraw,
                   linear, there_and_back)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
E = T6.entorno_v2()

SAT1 = np.array([-4.3, 2.2, 0.0])
SAT2 = np.array([0.6, 2.5, 0.0])
GW = np.array([-1.6, -1.6, 0.0])
NUCLEO = np.array([4.6, -1.6, 0.0])
Y_SUELO = -2.05


def medidor(p, frac, color, discontinuo=False):
    """Un medidor vertical de capacidad (0..1) anclado en el punto p."""
    marco = Rectangle(width=0.32, height=1.2, stroke_color=PAL.apoyo, stroke_width=2)
    marco.move_to(p)
    h = max(1.2 * frac, 0.02)
    lleno = Rectangle(width=0.32, height=h, stroke_width=0, fill_color=color, fill_opacity=1.0)
    lleno.move_to(marco.get_bottom() + UP * h / 2)
    if discontinuo:
        marco = DashedVMobject(marco, num_dashes=16)
    return VGroup(marco, lleno)


class RedIntegrada(Scene):
    """NTNEnv-v2, el entorno de la tesis: dos satelites y un gateway con
    ruta terrestre alterna. Tres mecanismos hacen que adaptarse pague: el
    eclipse (visibilidad baja), la congestion del gateway y un canal
    degradado que NO se observa y hay que inferir."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        suelo = Line([-6.6, Y_SUELO, 0], [6.6, Y_SUELO, 0], stroke_color=PAL.apoyo, stroke_width=2)
        s1 = VGroup(Dot(SAT1, radius=0.2, color=PAL.adapta, fill_opacity=0.25),
                    Dot(SAT1, radius=0.11, color=PAL.adapta))
        s2 = VGroup(Dot(SAT2, radius=0.2, color=PAL.adapta, fill_opacity=0.25),
                    Dot(SAT2, radius=0.11, color=PAL.adapta))
        gw = Square(side_length=0.42, stroke_width=0, fill_color=PAL.tinta,
                    fill_opacity=1.0).move_to(GW)
        nuc = Circle(radius=0.3, stroke_color=PAL.tinta, stroke_width=4).move_to(NUCLEO)
        e1 = T6.etiqueta("Satélite 1", PAL, fs=28, color=PAL.tinta).next_to(s1, UP, buff=0.15)
        e2 = T6.etiqueta("Satélite 2", PAL, fs=28, color=PAL.tinta).next_to(s2, UP, buff=0.15)
        eg = T6.etiqueta("Gateway", PAL, fs=28, color=PAL.tinta).next_to(gw, DOWN, buff=0.35)
        en = T6.etiqueta("Red terrestre", PAL, fs=28, color=PAL.tinta).next_to(nuc, DOWN, buff=0.35)
        l1 = Line(SAT1, GW, stroke_color=PAL.priv, stroke_width=5)
        l2 = Line(SAT2, GW, stroke_color=PAL.priv, stroke_width=5)
        ruta = Line(GW, NUCLEO, stroke_color=PAL.ok, stroke_width=6)
        et_r = T6.etiqueta("Ruta alterna", PAL, fs=26, color=PAL.ok).next_to(ruta, UP, buff=0.15)
        self.play(Create(suelo), FadeIn(gw), FadeIn(nuc), FadeIn(eg), FadeIn(en), run_time=0.8)
        self.play(FadeIn(s1), FadeIn(s2), FadeIn(e1), FadeIn(e2), run_time=0.6)
        self.play(Create(l1), Create(l2), Create(ruta), FadeIn(et_r), run_time=1.0)
        # medidores de capacidad de cada camino
        m1 = medidor(l1.point_from_proportion(0.5) + LEFT * 0.7, 1.0, PAL.priv)
        m2 = medidor(l2.point_from_proportion(0.5) + RIGHT * 0.7, 1.0, PAL.priv)
        mr = medidor(ruta.point_from_proportion(0.72) + UP * 1.2, 1.0, PAL.ok)
        self.play(FadeIn(m1), FadeIn(m2), FadeIn(mr), run_time=0.6)

        # ── 1. la red ─────────────────────────────────────────────────────
        presentacion.paso(self, "La red")

        # Mecanismo 1: el satelite 1 cae bajo el umbral de visibilidad.
        l1e = DashedLine(SAT1, GW, dash_length=0.14, stroke_color=PAL.no, stroke_width=3)
        m1e = medidor(m1[0].get_center(), E["eclipse_factor"], PAL.no)
        c1 = T6.cifra(T6.pct(E["eclipse_factor"], 0), PAL, fs=30, color=PAL.no)
        c1.next_to(m1e, LEFT, buff=0.18)
        ecl = T6.etiqueta("Eclipse", PAL, fs=28, color=PAL.no).next_to(e1, RIGHT, buff=0.3)
        self.play(FadeOut(l1), FadeIn(l1e), Transform(m1, m1e), s1.animate.set_opacity(0.35),
                  run_time=1.0)
        self.play(FadeIn(c1), FadeIn(ecl), run_time=0.5)

        # ── 2. eclipse ────────────────────────────────────────────────────
        presentacion.paso(self, "Eclipse")

        # Mecanismo 2: la ruta alterna no es refugio: el gateway se congestiona.
        mr_pico = medidor(mr[0].get_center(), E["gw_capacidad_pico"], PAL.no)
        cr = T6.cifra(T6.pct(E["gw_capacidad_pico"], 0), PAL, fs=30, color=PAL.no)
        cr.next_to(mr_pico, RIGHT, buff=0.18)
        mr_libre = mr.copy()
        for _ in range(2):
            self.play(Transform(mr, mr_pico), ruta.animate.set_stroke(PAL.no, width=3),
                      run_time=0.7)
            self.play(Transform(mr, mr_libre.copy()), ruta.animate.set_stroke(PAL.ok, width=6),
                      run_time=0.7)
        self.play(Transform(mr, mr_pico), ruta.animate.set_stroke(PAL.no, width=3), run_time=0.7)
        self.play(FadeIn(cr), run_time=0.4)

        # ── 3. congestion ─────────────────────────────────────────────────
        presentacion.paso(self, "Congestión")

        # Mecanismo 3: un canal del satelite 2 se degrada y NADIE lo ve. Se
        # dibuja apagado y a trazos: esta en el estado, no en la observacion.
        m2o = medidor(m2[0].get_center(), E["canal_factor"], PAL.apoyo, discontinuo=True)
        c2 = T6.cifra(T6.pct(E["canal_factor"], 0), PAL, fs=30, color=PAL.apoyo)
        c2.next_to(m2o, RIGHT, buff=0.18)
        oculto = T6.etiqueta("No observable", PAL, fs=28, color=PAL.apoyo)
        oculto.next_to(e2, RIGHT, buff=0.3)
        l2o = DashedLine(SAT2, GW, dash_length=0.14, stroke_color=PAL.apoyo, stroke_width=4)
        self.play(FadeOut(m2), FadeIn(m2o), FadeOut(l2), FadeIn(l2o), run_time=1.0)
        self.play(FadeIn(c2), FadeIn(oculto), run_time=0.5)
        self.wait(0.8)
        presentacion.paso(self, "Canal oculto")
