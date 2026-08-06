import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from satelites import (ConstelacionWalker, AnimarWalker, enlaces_walker,
                       imagen_mapa, subsatelites_walker, animar_cobertura)


class SatelitesYCobertura(Scene):
    """Demo de satelites.py: constelacion Walker 3D + cobertura en el mapa."""

    def construct(self):
        titulo = Text("Constelación Walker + cobertura NTN", font_size=30,
                      color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Constelacion proyectada con oclusion tras el disco terrestre
        cons = ConstelacionWalker(planos=5, sats_por_plano=8, frames=180,
                                  vueltas=0.35, escala=1.25)
        cons.shift(LEFT * 3.6 + DOWN * 0.5)
        cons._colocar(0)
        self.play(FadeIn(cons.tierra, scale=0.7), run_time=0.7)
        self.play(LaggedStart(*[Create(o) for o in cons.orbitas],
                              lag_ratio=0.15), run_time=1.4)
        self.play(FadeIn(cons.sats), run_time=0.8)
        enlaces = enlaces_walker(cons)
        self.play(FadeIn(enlaces), run_time=0.7)

        # Cobertura de la misma constelacion sobre el mapa estilizado
        mapa = imagen_mapa((512, 256), alto_escena=3.4)
        mapa.move_to(RIGHT * 3.4 + DOWN * 0.5)
        self.play(FadeIn(mapa), run_time=0.8)

        trazas = subsatelites_walker(frames=90, planos=5, sats_por_plano=8,
                                     altitud_km=550, vueltas=0.35,
                                     duracion_s=2000)
        # Ambas animaciones a la vez no: la cobertura ya lleva su play.
        self.play(AnimarWalker(cons), run_time=5)
        animar_cobertura(self, trazas, altitud_km=550, duracion=5.0,
                         res=(512, 256), imagen=mapa)
        for e in enlaces:
            e.clear_updaters()
        self.wait(0.6)
