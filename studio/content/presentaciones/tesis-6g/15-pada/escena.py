import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DEGREES, DOWN, LEFT, RIGHT, UP, Arc, ArcBetweenPoints,
                   Circle, Create, DashedVMobject, Dot, FadeIn, FadeOut,
                   GrowFromCenter, Line, MoveAlongPath, Rectangle, Scene,
                   Square, Transform, ValueTracker, VGroup, always_redraw,
                   linear)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
D = T6.datos_tesis()

CENTRO = np.array([-2.3, -0.1, 0.0])
RADIO = 2.15
R_NODO = 0.34
# Sentido horario: Percepcion arriba, Analisis a la derecha, Decision abajo,
# Accion a la izquierda — y vuelta a percibir.
MODULOS = [("Percepción", 90), ("Análisis", 0), ("Decisión", -90), ("Acción", 180)]


def en_circulo(centro, radio, grados):
    a = np.radians(grados)
    return centro + radio * np.array([np.cos(a), np.sin(a), 0.0])


def lazo(centro, radio, r_nodo, color, ancho=4, discontinuo=False):
    nodos, flechas = VGroup(), VGroup()
    for _, g in MODULOS:
        n = Circle(radius=r_nodo, stroke_color=color, stroke_width=ancho,
                   fill_color=PAL.fondo, fill_opacity=1.0)
        nodos.add(n.move_to(en_circulo(centro, radio, g)))
    hueco = np.degrees(r_nodo / radio) + 6
    for _, g in MODULOS:
        a = Arc(radius=radio, start_angle=np.radians(g - hueco),
                angle=-np.radians(90 - 2 * hueco), arc_center=centro,
                stroke_color=color, stroke_width=ancho)
        a.add_tip(tip_length=0.22, tip_width=0.22)
        a.get_tip().set_color(color)
        flechas.add(DashedVMobject(a, num_dashes=14) if discontinuo else a)
    return nodos, flechas


def red(centro, escala, color):
    """Tres satelites y una estacion enlazados: el sistema que se gobierna."""
    pts = [centro + escala * np.array(p) for p in
           ((-0.55, 0.35, 0), (0.0, 0.62, 0), (0.55, 0.35, 0), (0.0, -0.45, 0))]
    enl = VGroup(*[Line(pts[i], pts[j], stroke_color=color, stroke_width=2,
                        stroke_opacity=0.7) for i, j in ((0, 1), (1, 2), (0, 3), (1, 3), (2, 3))])
    sats = VGroup(*[Dot(p, radius=0.07 * escala / 0.9, color=color) for p in pts[:3]])
    est = Square(side_length=0.2 * escala / 0.9, stroke_width=0, fill_color=color,
                 fill_opacity=1.0).move_to(pts[3])
    return VGroup(enl, sats, est)


class Pada(Scene):
    """PADA: percibir, analizar, decidir, actuar. La parte lenta que piensa
    va FUERA del lazo rapido que actua, y ninguna politica nueva toca la red
    sin pasar antes por su gemelo digital."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        nodos, flechas = lazo(CENTRO, RADIO, R_NODO, PAL.tinta)
        etiquetas = VGroup()
        for (nombre, g), n in zip(MODULOS, nodos):
            e = T6.etiqueta(nombre, PAL, fs=30, color=PAL.tinta)
            d = en_circulo(np.zeros(3), 1.0, g)
            e.next_to(n, d, buff=0.2)
            etiquetas.add(e)
        sistema = red(CENTRO + DOWN * 0.25, 0.7, PAL.apoyo)
        self.play(FadeIn(sistema), run_time=0.6)
        self.play(*[GrowFromCenter(n) for n in nodos], FadeIn(etiquetas), run_time=0.9)
        self.play(*[Create(f) for f in flechas], run_time=1.2)

        # Un pulso recorre el ciclo: el lazo no termina, vuelve a percibir.
        ang = ValueTracker(90.0)
        pulso = always_redraw(lambda: Dot(en_circulo(CENTRO, RADIO, ang.get_value()),
                                          radius=0.12, color=PAL.adapta))
        self.add(pulso)
        self.play(ang.animate.set_value(90 - 720), run_time=4.0, rate_func=linear)

        # ── 1. el ciclo ───────────────────────────────────────────────────
        presentacion.paso(self, "El ciclo")

        # Dos ritmos. El lazo rapido va de percibir a actuar por dentro; el
        # lento (analizar y decidir la politica) sigue por fuera.
        p_perc = nodos[0].get_center()
        p_acc = nodos[3].get_center()
        # arco concentrico por dentro, de Accion (180) a Percepcion (90)
        cuerda = Arc(radius=RADIO - 0.45, start_angle=np.radians(172),
                     angle=-np.radians(74), arc_center=CENTRO,
                     stroke_color=PAL.tinta, stroke_width=4)
        cuerda.add_tip(tip_length=0.2, tip_width=0.2)
        cuerda.get_tip().set_color(PAL.tinta)
        rap = T6.etiqueta("10 ms–1 s", PAL, fs=28, color=PAL.tinta)
        rap.move_to(en_circulo(CENTRO, RADIO - 1.3, 128))
        lento = T6.etiqueta("> 1 s", PAL, fs=28, color=PAL.adapta)
        lento.move_to(en_circulo(CENTRO, RADIO + 0.62, -45))
        self.play(Create(cuerda), FadeIn(rap), FadeIn(lento), run_time=0.9)
        t_rap = ValueTracker(0.0)
        chispa = always_redraw(lambda: Dot(cuerda.point_from_proportion(t_rap.get_value() % 1.0),
                                           radius=0.1, color=PAL.tinta))
        self.add(chispa)
        # seis vueltas del rapido por cada media del lento
        self.play(t_rap.animate.set_value(6.0), ang.animate.set_value(90 - 720 - 180),
                  run_time=4.5, rate_func=linear)

        # ── 2. dos ritmos ─────────────────────────────────────────────────
        presentacion.paso(self, "Dos ritmos")

        c_gem = np.array([4.55, 0.55, 0.0])
        g_nodos, g_flechas = lazo(c_gem, 1.05, 0.2, PAL.apoyo, ancho=3, discontinuo=True)
        g_red = red(c_gem, 0.45, PAL.apoyo)
        et_g = T6.etiqueta("Gemelo digital", PAL, fs=28, color=PAL.apoyo)
        et_g.next_to(VGroup(g_nodos, g_flechas), UP, buff=0.3)
        self.play(FadeIn(g_nodos), Create(g_flechas), FadeIn(g_red), FadeIn(et_g),
                  run_time=1.2)

        # Una politica nueva (el cuadrito) entra primero al gemelo...
        pol = Square(side_length=0.34, stroke_width=0, fill_color=PAL.adapta,
                     fill_opacity=1.0).move_to(c_gem + np.array([0, 2.3, 0]))
        self.play(FadeIn(pol, shift=DOWN * 0.3), run_time=0.5)
        self.play(pol.animate.move_to(c_gem), run_time=0.8)
        # ...y solo sale si el entorno de prueba premia adaptarse (MA).
        compuerta = Rectangle(width=1.7, height=0.16, stroke_width=0,
                              fill_color=PAL.apoyo, fill_opacity=1.0)
        compuerta.move_to(c_gem + np.array([0, -1.75, 0]))
        et_c = T6.etiqueta(f"MA ≥ {round(100 * D['umbral'])}%", PAL, fs=26, color=PAL.apoyo)
        et_c.next_to(compuerta, DOWN, buff=0.18)
        self.play(FadeIn(compuerta), FadeIn(et_c), run_time=0.5)
        self.play(pol.animate.move_to(compuerta.get_center() + UP * 0.35), run_time=0.7)
        self.play(compuerta.animate.set_fill(PAL.ok), et_c.animate.set_color(PAL.ok),
                  run_time=0.4)
        # la politica aprobada llega al modulo de Decision de la red real
        destino = nodos[2].get_center()
        via = ArcBetweenPoints(pol.get_center(), destino, angle=-35 * DEGREES)
        self.play(MoveAlongPath(pol, via), run_time=1.4)
        self.play(nodos[2].animate.set_stroke(PAL.adapta), pol.animate.scale(0.6),
                  ang.animate.set_value(90 - 720 - 360), t_rap.animate.set_value(10.0),
                  run_time=2.2, rate_func=linear)
        self.wait(0.5)
        presentacion.paso(self, "Gemelo digital")
