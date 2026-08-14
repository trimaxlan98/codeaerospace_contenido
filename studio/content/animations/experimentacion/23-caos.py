import math
import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from caos import (COLOR_FASE, COLOR_GEMELO, COLOR_ORDEN, COLOR_SISTEMA,
                  FEIGENBAUM_DELTA, R_BIFURCACIONES, abanico_pendulos,
                  cobweb, curva_lorenz, curva_separacion,
                  feigenbaum_cocientes, imagen_bifurcacion, mapa_retorno,
                  orbita_logistica, par_lorenz, ruido_uniforme,
                  trayectoria_lorenz)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoCaos(Scene):
    """Demo de caos.py: la telarana logistica por valores de r, el
    diagrama de bifurcacion con marcadores, el atractor de Lorenz
    dibujandose, el par gemelo con su curva de separacion y el Lyapunov
    medido, el abanico de pendulos reproducido por alpha y el mapa de
    retorno de caos contra ruido.

    Todo es determinista: mismo script, mismo render. Los numeros
    (lambda, delta, cocientes) salen de las piezas, medidos.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("Caos", font_size=28, color=COLOR_GEMELO)
        titulo.to_edge(UP, buff=0.22)
        self.add(titulo)

        # --- acto 1: logistico y bifurcacion ---
        tela = cobweb(2.9, lado=2.6).move_to(LEFT * 4.0 + UP * 0.9)
        self.play(FadeIn(tela), run_time=0.5)
        self.play(Transform(tela, tela.con_r(3.9)), run_time=0.8)

        diag = imagen_bifurcacion(res=(700, 400), alto_escena=2.6)
        diag.move_to(RIGHT * 3.2 + UP * 0.9)
        self.play(FadeIn(diag), run_time=0.6)
        marca = DashedLine(diag.punto_de(R_BIFURCACIONES[0], 0.05),
                           diag.punto_de(R_BIFURCACIONES[0], 0.95),
                           stroke_width=1.6, color=COLOR_GEMELO)
        coc = Text(f"d = {FEIGENBAUM_DELTA:.3f}", font=FUENTE_HUD,
                   font_size=14, color=COLOR_GEMELO)
        coc.next_to(diag, DOWN, buff=0.12)
        self.play(Create(marca), FadeIn(coc), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(tela), FadeOut(diag), FadeOut(marca),
                  FadeOut(coc), run_time=0.4)

        # --- acto 2: Lorenz y su Lyapunov ---
        pts_a, pts_b, d = par_lorenz(1e-6, n=6000)
        a = curva_lorenz(pts_a, alto=2.9, grosor=1.5)
        b = curva_lorenz(pts_b, alto=2.9, grosor=1.5, color=COLOR_GEMELO,
                         como=a)
        for t in (a, b):
            t.shift(UP * 1.1)
        self.play(Create(a), Create(b), run_time=2.6, rate_func=linear)
        sep = curva_separacion(d, ancho=5.0, alto=1.7)
        sep.move_to(DOWN * 1.9)
        lam = Text(f"lambda = {sep.lyapunov():.2f}", font=FUENTE_HUD,
                   font_size=15, color=COLOR_GEMELO)
        lam.next_to(sep, RIGHT, buff=0.3)
        self.play(FadeIn(sep.ejes), Create(sep.traza), run_time=1.2)
        self.play(Create(sep.recta_ajuste()), FadeIn(lam), run_time=0.7)
        self.wait(0.5)
        self.play(*[FadeOut(m) for m in (a, b, sep, lam)], run_time=0.4)

        # --- acto 3: pendulos y el detector de reglas ---
        abanico = abanico_pendulos(12, 0.01, n=2600, escala=0.85)
        abanico.move_to(LEFT * 3.6 + DOWN * 0.2)
        abanico.en(0.0)
        self.play(FadeIn(abanico), run_time=0.4)
        self.play(UpdateFromAlphaFunc(abanico, lambda m, al: m.en(al)),
                  run_time=3.0, rate_func=linear)

        m_c = mapa_retorno(orbita_logistica(4.0, 0.2, 160), lado=2.0)
        m_c.move_to(RIGHT * 1.9 + DOWN * 0.4)
        m_r = mapa_retorno(ruido_uniforme(160), lado=2.0,
                           color=COLOR_FASE)
        m_r.move_to(RIGHT * 4.6 + DOWN * 0.4)
        self.play(FadeIn(m_c), FadeIn(m_r), run_time=0.8)
        self.wait(0.6)
