import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from agentes import (COLOR_ACCION, COLOR_AGENTE, COLOR_OK, COLOR_PELIGRO,
                     COLOR_TENUE, escala_autonomia, girar_lazo, lazo_agente,
                     tarjeta_json, traza_react)


class DemoAgentes(Scene):
    """Demo de agentes.py: el lazo, una traza ReAct, el contrato y la autonomia.

    Todo es geometria determinista: los arcos del lazo se recortan por el
    semiangulo que ocupa cada nodo (nunca lo tocan) y `girar_lazo` anima
    COPIAS de esos arcos, asi que no deja updaters en la escena.
    """

    def construct(self):
        titulo = Text("Agentes: percibir, razonar, actuar", font_size=30,
                      color=COLOR_ACCION).to_edge(UP, buff=0.35)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=0.6)

        # --- acto 1: el lazo gira ---
        lazo = lazo_agente().scale(0.9).move_to(DOWN * 0.4)
        self.play(LaggedStart(*[FadeIn(n, scale=0.7) for n in lazo.nodos],
                              lag_ratio=0.18), run_time=1.0)
        self.play(*[Create(f) for f in lazo.flechas], run_time=0.8)
        self.play(girar_lazo(lazo, vueltas=2, run_time=2.2))
        self.play(FadeOut(lazo), run_time=0.5)

        # --- acto 2: la traza ReAct junto al lazo pequeno ---
        traza = traza_react([
            ("pensamiento", "¿Cuándo pasa NOAA-19 sobre la estación?"),
            ("accion", "consultar_tle(NOAA-19)"),
            ("observacion", "TLE fresco, época de hoy"),
        ], ancho_max=4.8, font_size=17)
        traza.move_to(LEFT * 3.1 + DOWN * 0.3)
        chico = lazo_agente(radio=1.15, font_size=13).move_to(RIGHT * 3.3
                                                              + DOWN * 0.3)
        self.play(FadeIn(chico), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2)
                                for b in traza.burbujas],
                              lag_ratio=0.35), run_time=1.6)
        self.play(girar_lazo(chico, vueltas=1, run_time=1.1))
        self.play(FadeOut(traza), FadeOut(chico), run_time=0.5)

        # --- acto 3: el contrato JSON, aceptado y rechazado ---
        buena = tarjeta_json(['{ "sat": "NOAA-19",', '  "elev_min": 10 }'],
                             valida=True).move_to(LEFT * 2.8 + DOWN * 0.2)
        mala = tarjeta_json(['{ "sat": 42,', '  "elev_min": "alta" }'],
                            valida=False).move_to(RIGHT * 2.8 + DOWN * 0.2)
        pie = Text("el contrato se valida antes de tocar nada", font_size=20,
                   color=COLOR_TENUE).to_edge(DOWN, buff=0.55)
        self.play(FadeIn(buena, shift=UP * 0.2), run_time=0.6)
        self.play(FadeIn(mala, shift=UP * 0.2), run_time=0.6)
        self.play(FadeIn(pie), run_time=0.4)
        self.play(Indicate(buena.marca, color=COLOR_OK, scale_factor=1.5),
                  Indicate(mala.marca, color=COLOR_PELIGRO, scale_factor=1.5),
                  run_time=0.9)
        self.play(FadeOut(buena), FadeOut(mala), FadeOut(pie), run_time=0.5)

        # --- acto 4: autonomia con frenos ---
        escala = escala_autonomia(nivel=0).move_to(DOWN * 0.3)
        rotulo = Text("autonomía: de L0 a L5", font_size=21,
                      color=COLOR_AGENTE).next_to(escala, UP, buff=0.9)
        self.play(Create(escala.linea),
                  *[FadeIn(m) for m in escala.muescas], run_time=0.6)
        self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.1)
                                for e in escala.etiquetas], lag_ratio=0.12),
                  FadeIn(escala.marcador, shift=DOWN * 0.2),
                  FadeIn(rotulo), run_time=0.9)
        self.play(escala.marcador.animate.move_to(escala.pos_nivel(2)),
                  run_time=0.7)
        self.play(escala.marcador.animate.move_to(escala.pos_nivel(4)),
                  run_time=0.7)
        self.wait(0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)
