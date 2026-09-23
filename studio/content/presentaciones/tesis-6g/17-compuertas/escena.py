import re
import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Create, DashedLine, DashedVMobject,
                   Dot, FadeIn, Line, Rectangle, Rotate, Scene, VGroup, linear)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
D = T6.datos_tesis()
COMP = {c["id"]: c for c in D["compuertas"]}
ORDEN = ["G0", "G1", "G2a", "G2b", "G3", "G4"]


def valor_corto(cid):
    """La cifra de cada compuerta, en el color de lo que significa."""
    if cid == "G0":
        return T6.pct(D["g0_ma"]), PAL.no          # el entorno v1 NO premiaba adaptarse
    if cid == "G1":
        return T6.pct(D["g1_ma"]), PAL.ok
    if cid == "G2a":
        a, b = re.findall(r"\d+(?:\.\d+)?", COMP["G2a"]["valor"])[:2]
        return f"+{a}–{b} %", PAL.ok
    if cid == "G2b":
        m = [g["mejora"] for g in D["g2b"]]
        return f"+{100 * min(m):.1f}–{100 * max(m):.1f} %", PAL.ok
    return None, None


class Compuertas(Scene):
    """Las compuertas del protocolo, como esclusas: el proyecto solo avanza
    cuando la anterior se abre. G3 y G4 siguen cerradas (a trazos): estan
    desbloqueadas pero NO se han corrido."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        xs = np.linspace(-5.4, 5.4, len(ORDEN))
        y = -0.3
        canal = Line([-6.6, y, 0], [6.6, y, 0], stroke_color=PAL.tenue, stroke_width=14)
        self.play(Create(canal), run_time=0.7)

        puertas, postes, nombres, cifras = {}, VGroup(), VGroup(), {}
        for cid, x in zip(ORDEN, xs):
            hecha = COMP[cid]["estado"] == "passed"
            col = PAL.tinta if hecha else PAL.apoyo
            p = VGroup(Line([x - 0.55, y - 0.75, 0], [x - 0.55, y + 0.75, 0], stroke_color=col,
                            stroke_width=4),
                       Line([x + 0.55, y - 0.75, 0], [x + 0.55, y + 0.75, 0], stroke_color=col,
                            stroke_width=4))
            puerta = Rectangle(width=1.1, height=0.18, stroke_width=0, fill_color=col,
                               fill_opacity=1.0).move_to([x, y, 0])
            if not hecha:
                puerta = DashedVMobject(Rectangle(width=1.1, height=0.18, stroke_color=col,
                                                  stroke_width=3).move_to([x, y, 0]), num_dashes=10)
            n = T6.etiqueta(cid, PAL, fs=32, color=col, peso="BOLD").move_to([x, y + 1.2, 0])
            postes.add(p)
            nombres.add(n)
            puertas[cid] = puerta
            txt, c = valor_corto(cid)
            if txt:
                cifras[cid] = T6.cifra(txt, PAL, fs=26, color=c).move_to([x, y - 1.2, 0])
        self.play(FadeIn(postes), FadeIn(nombres), *[FadeIn(p) for p in puertas.values()],
                  run_time=0.9)

        barco = Dot([-6.5, y, 0], radius=0.16, color=PAL.adapta)
        self.add(barco)

        def cruzar(cid, x):
            self.play(barco.animate.move_to([x - 0.9, y, 0]), run_time=0.45, rate_func=linear)
            pu = puertas[cid]
            # girar y recolorear en DOS play: en el mismo se pisan (trampas.md)
            self.play(Rotate(pu, angle=np.pi / 2, about_point=[x - 0.55, y, 0]), run_time=0.4)
            self.play(pu.animate.set_fill(PAL.ok), run_time=0.15)
            self.play(FadeIn(cifras[cid], shift=UP * 0.1),
                      barco.animate.move_to([x + 0.9, y, 0]), run_time=0.45, rate_func=linear)

        for cid, x in zip(ORDEN[:2], xs[:2]):
            cruzar(cid, x)

        # ── 1. el instrumento: G0 lo reprueba, G1 lo aprueba ─────────────
        presentacion.paso(self, "Instrumento")

        for cid, x in zip(ORDEN[2:4], xs[2:4]):
            cruzar(cid, x)
        # llega a G3 y se queda: desbloqueada, sin correr
        self.play(barco.animate.move_to([xs[4] - 0.9, y, 0]), run_time=0.5, rate_func=linear)
        self.play(puertas["G3"].animate.set_stroke(PAL.adapta), run_time=0.4)
        self.play(puertas["G3"].animate.set_stroke(PAL.apoyo), run_time=0.4)
        self.wait(0.6)
        presentacion.paso(self, "Pendiente G3")
