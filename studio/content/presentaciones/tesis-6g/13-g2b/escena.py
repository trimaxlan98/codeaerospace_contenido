import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import (DOWN, LEFT, RIGHT, UP, DashedVMobject, FadeIn, GrowFromEdge,
                   Line, Rectangle, Scene, VGroup)

import presentacion
import tesis6g as T6

LZ, PAL = T6.pieza()
D = T6.datos_tesis()
G = D["g2b"]

Y_BASE = -2.7
ALTO_MAX = 5.2                       # alto de la barra del mayor oraculo
V_MAX = max(g["oraculo"] for g in G)
ANCHO = 0.78
HUECO = 0.26


def barra(x, valor, color, contorno=False):
    h = ALTO_MAX * valor / V_MAX     # las barras NACEN EN CERO: sin trampa de eje
    if contorno:
        r = Rectangle(width=ANCHO, height=h, stroke_color=color, stroke_width=4,
                      fill_opacity=0.0)
        r = DashedVMobject(r, num_dashes=40)
    else:
        r = Rectangle(width=ANCHO, height=h, stroke_width=0, fill_color=color,
                      fill_opacity=1.0)
    r.move_to([x, Y_BASE + h / 2, 0])
    return r


def leyenda(texto, color, contorno=False):
    if contorno:
        m = DashedVMobject(Rectangle(width=0.34, height=0.34, stroke_color=color,
                                     stroke_width=3), num_dashes=8)
    else:
        m = Rectangle(width=0.34, height=0.34, stroke_width=0, fill_color=color,
                      fill_opacity=1.0)
    e = T6.etiqueta(texto, PAL, fs=28, color=color)
    return VGroup(m, e.next_to(m, RIGHT, buff=0.16))


class G2b(Scene):
    """La compuerta G2b por semilla: la mejor politica estatica, QMIX y el
    oraculo (que es cota INFERIOR del optimo: se dibuja a trazos)."""

    def setup(self):
        T6.aplicar_pieza(self, LZ)

    def construct(self):
        centros = [-3.6, 0.0, 3.6]
        paso_x = ANCHO + HUECO
        suelo = Line([-6.2, Y_BASE, 0], [6.2, Y_BASE, 0], stroke_color=PAL.apoyo,
                     stroke_width=2)
        semillas = VGroup()
        for c, g in zip(centros, G):
            e = T6.etiqueta(f"Semilla {g['semilla']}", PAL, fs=28, color=PAL.apoyo)
            e.move_to([c, Y_BASE - 0.42, 0])
            semillas.add(e)
        self.play(FadeIn(suelo), FadeIn(semillas), run_time=0.8)

        est = [barra(c - paso_x, g["estatica"], PAL.estatica) for c, g in zip(centros, G)]
        self.play(*[GrowFromEdge(b, DOWN) for b in est], run_time=1.2)
        # Leyenda en una fila arriba: cada serie entra con su paso.
        ley = [leyenda("Estática", PAL.estatica), leyenda("QMIX", PAL.adapta),
               leyenda("Oráculo", PAL.priv, contorno=True)]
        fila = VGroup(*ley).arrange(RIGHT, buff=0.9).move_to([0, 3.35, 0])
        self.play(FadeIn(ley[0]), run_time=0.4)

        # ── 1. la mejor de las 27 politicas fijas ─────────────────────────
        presentacion.paso(self, "La mejor estática")

        qm = [barra(c, g["qmix"], PAL.adapta) for c, g in zip(centros, G)]
        self.play(*[GrowFromEdge(b, DOWN) for b in qm], run_time=1.4)
        mejoras = VGroup()
        for b, g in zip(qm, G):
            m = T6.cifra(f"+{T6.pct(g['mejora'])}", PAL, fs=27, color=PAL.adapta)
            m.next_to(b, UP, buff=0.18)
            mejoras.add(m)
        self.play(FadeIn(mejoras, shift=DOWN * 0.1), FadeIn(ley[1]), run_time=0.7)
        self.wait(0.6)

        # ── 2. lo aprendido le gana en las tres ───────────────────────────
        presentacion.paso(self, "QMIX")

        orc = [barra(c + paso_x, g["oraculo"], PAL.priv, contorno=True)
               for c, g in zip(centros, G)]
        self.play(*[FadeIn(b, shift=UP * 0.2) for b in orc], run_time=1.0)
        self.play(FadeIn(ley[2]), run_time=0.4)
        self.wait(0.8)
        presentacion.paso(self, "Oráculo")
