import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Brace, Create, DashedLine,
                   FadeIn, GrowFromCenter, Line, MathTex, RoundedRectangle, Scene,
                   Transform, VGroup)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
D = T6.datos_tesis()
# El par que reporta la tesis: margen alcanzable DEMOSTRADO (la peor semilla
# de G2b) y envolvente estimada (G1). Los dos son cotas INFERIORES: el
# oraculo voraz es cota inferior del optimo privilegiado (Prop. 4.8).
MA_DEC = min(g["mejora"] for g in D["g2b"])
MA = D["g1_ma"]


class TresClases(Scene):
    """Tres clases de politicas, una dentro de otra: las estaticas, las que
    se pueden desplegar (cada agente ve lo suyo) y las que lo ven todo. Sus
    mejores valores quedan ordenados, y de ahi salen los dos margenes."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        c = np.array([-3.2, -0.25, 0])
        cajas, nombres = VGroup(), VGroup()
        for (w, h, rol, nom, sim) in ((6.6, 5.9, "priv", "Privilegiadas", r"\Pi_{\mathrm{priv}}"),
                                      (5.0, 4.1, "adapta", "Desplegables", r"\Pi_{\mathrm{dec}}"),
                                      (3.2, 2.2, "estatica", "Estáticas", r"\Pi_{\mathrm{const}}")):
            col = getattr(PAL, rol)
            r = RoundedRectangle(corner_radius=0.3, width=w, height=h, stroke_color=col,
                                 stroke_width=4).move_to(c + DOWN * (5.9 - h) * 0.42)
            e = T6.etiqueta(nom, PAL, fs=28, color=col)
            s = MathTex(sim, color=col, font_size=38)
            g = VGroup(s, e).arrange(RIGHT, buff=0.2)
            g.next_to(r.get_corner(UP + LEFT), DOWN + RIGHT, buff=0.22)
            cajas.add(r)
            nombres.add(g)
        # de dentro hacia fuera: lo estatico es un caso particular de todo
        for i in (2, 1, 0):
            self.play(GrowFromCenter(cajas[i]), FadeIn(nombres[i]), run_time=0.8)

        # ── 1. anidadas ───────────────────────────────────────────────────
        presentacion.paso(self, "Anidadas")

        # eje de valor: la mejor politica de cada clase
        xe, yb, esc = 2.3, -2.6, 13.5          # 1 unidad de margen relativo = esc
        eje = Line([xe, yb - 0.2, 0], [xe, 2.9, 0], stroke_color=PAL.apoyo, stroke_width=2)
        niveles = [("estatica", 0.0, r"V^{\star}_{\mathrm{est}}"),
                   ("adapta", MA_DEC, r"V^{\star}_{\mathrm{dec}}"),
                   ("priv", MA, r"V^{\star}_{\mathrm{priv}}")]
        y_de = lambda m: yb + 0.3 + 15.0 * m
        marcas = VGroup()
        for rol, m, sim in niveles:
            col = getattr(PAL, rol)
            y = y_de(m)
            tic = Line([xe - 0.25, y, 0], [xe + 0.25, y, 0], stroke_color=col, stroke_width=6)
            t = MathTex(sim, color=col, font_size=40).next_to(tic, LEFT, buff=0.2)
            marcas.add(VGroup(tic, t))
        self.play(Create(eje), run_time=0.5)
        # cada clase "sube" su mejor valor desde su caja hasta el eje
        for i, (k, mk) in enumerate(zip((2, 1, 0), marcas)):
            self.play(FadeIn(mk, shift=RIGHT * 0.3),
                      cajas[k].animate.set_stroke(width=7), run_time=0.55)
            self.play(cajas[k].animate.set_stroke(width=4), run_time=0.2)

        # ── 2. ordenadas ──────────────────────────────────────────────────
        presentacion.paso(self, "Ordenadas")

        y_est, y_dec, y_pri = (y_de(m) for _, m, _ in niveles)
        ll_dec = Brace(Line([xe, y_est, 0], [xe, y_dec, 0]), direction=RIGHT, buff=1.35,
                       color=PAL.adapta)
        ll_ma = Brace(Line([xe, y_est, 0], [xe, y_pri, 0]), direction=RIGHT, buff=0.4,
                      color=PAL.priv)
        t_dec = MathTex(rf"\mathrm{{MA}}_{{\mathrm{{dec}}}}\ge {100 * MA_DEC:.1f}\%",
                        color=PAL.adapta, font_size=32).next_to(ll_dec, RIGHT, buff=0.18)
        t_ma = MathTex(rf"\mathrm{{MA}}\ge {100 * MA:.1f}\%", color=PAL.priv,
                       font_size=36).next_to(ll_ma, RIGHT, buff=0.2)
        t_ma.set_x(min(t_ma.get_x(), LZ.derecha - t_ma.width / 2))
        t_dec.set_x(min(t_dec.get_x(), LZ.derecha - t_dec.width / 2))
        self.play(GrowFromCenter(ll_ma), FadeIn(t_ma), run_time=0.8)
        self.play(GrowFromCenter(ll_dec), FadeIn(t_dec), run_time=0.8)
        self.wait(0.8)
        presentacion.paso(self, "Dos márgenes")
