from manim import *
import numpy as np


class ConsensoPaxosYRaft(Scene):
    def construct(self):
        titulo = Text("Consenso: Paxos y Raft", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        meta = Text("Objetivo: que 5 máquinas acuerden un mismo valor aunque algunas fallen",
                    font_size=20, color=GREY_B).next_to(titulo, DOWN, buff=0.25)
        self.play(FadeIn(meta), run_time=1.2)

        # Cinco nodos en circulo (estilo Raft)
        centro = DOWN * 0.9
        pos = [centro + 2.1 * np.array([np.cos(a), np.sin(a), 0])
               for a in np.linspace(PI / 2, PI / 2 + TAU, 5, endpoint=False)]
        nodos = VGroup(*[
            VGroup(Circle(radius=0.42, color=GREY_B, fill_opacity=0.12,
                          fill_color=GREY_B).move_to(p),
                   Text(f"S{i+1}", font_size=19, color=WHITE).move_to(p))
            for i, p in enumerate(pos)
        ])
        self.play(LaggedStart(*[FadeIn(n) for n in nodos], lag_ratio=0.15), run_time=1.8)

        # Eleccion de lider: S1 pide votos
        fase1 = Text("1) Elección: un candidato pide votos; la mayoría decide",
                     font_size=20, color=YELLOW).to_edge(DOWN)
        self.play(FadeIn(fase1), run_time=1)
        self.play(nodos[0][0].animate.set_color(YELLOW), run_time=0.6)
        peticiones = VGroup(*[
            Arrow(pos[0], p, color=YELLOW, buff=0.5, stroke_width=3,
                  max_tip_length_to_length_ratio=0.12)
            for p in pos[1:]
        ])
        self.play(LaggedStart(*[GrowArrow(a) for a in peticiones], lag_ratio=0.15),
                  run_time=1.5)
        votos = VGroup(*[
            Text("sí", font_size=18, color=BLUE_B).move_to(
                pos[i] + (pos[0] - pos[i]) * 0.35)
            for i in [1, 2, 4]
        ])
        self.play(FadeIn(votos, lag_ratio=0.2), run_time=1.2)
        lider = Text("Líder", font_size=18, color=YELLOW).next_to(nodos[0], UP, buff=0.15)
        self.play(FadeIn(lider), FadeOut(peticiones), FadeOut(votos), run_time=1)

        # Replicacion de log
        fase2 = Text("2) Replicación: el líder propaga la entrada; con mayoría, se confirma",
                     font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(fase1, fase2), run_time=1)
        entrada = Text("x←9", font_size=18, color=GOLD).next_to(nodos[0], RIGHT, buff=0.2)
        self.play(FadeIn(entrada), run_time=0.6)
        copias = VGroup(*[Dot(pos[0], color=GOLD, radius=0.08) for _ in range(4)])
        self.add(copias)
        self.play(*[c.animate.move_to(p) for c, p in zip(copias, pos[1:])],
                  run_time=1.3)
        acks = VGroup(*[
            Text("ok", font_size=16, color=BLUE_B).move_to(
                pos[i] + (pos[0] - pos[i]) * 0.35)
            for i in [1, 3, 4]
        ])
        self.play(FadeOut(copias), FadeIn(acks), run_time=1)
        commit = Text("mayoría (3 de 5) → confirmado", font_size=19, color=GOLD)
        commit.move_to(RIGHT * 4.3 + UP * 1.2)
        self.play(FadeIn(commit), FadeOut(acks), run_time=1.2)

        # Falla del lider: nueva eleccion
        fase3 = Text("3) Si el líder cae, se elige otro: el sistema sigue",
                     font_size=20, color=GREY_B).to_edge(DOWN)
        self.play(ReplacementTransform(fase2, fase3), run_time=1)
        cruz = Cross(scale_factor=0.4).move_to(pos[0])
        self.play(Create(cruz), nodos[0].animate.set_opacity(0.3), FadeOut(lider),
                  run_time=1.2)
        self.play(nodos[2][0].animate.set_color(YELLOW), run_time=0.8)
        lider2 = Text("Nuevo líder", font_size=17, color=YELLOW)
        lider2.next_to(nodos[2], DOWN, buff=0.15)
        self.play(FadeIn(lider2), Flash(nodos[2], color=YELLOW), run_time=1)

        cierre = Text("Paxos lo demostró posible; Raft lo hizo entendible. La clave: mayorías",
                      font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(fase3, cierre), run_time=1.2)
        self.wait(2)
