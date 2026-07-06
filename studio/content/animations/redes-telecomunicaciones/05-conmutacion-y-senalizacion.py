from manim import *


class ConmutacionYSenalizacion(Scene):
    def construct(self):
        titulo = Text("Conmutación y señalización", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Red de nodos compartida por ambos ejemplos
        pos = {
            "A": LEFT * 5.5 + DOWN * 0.6, "B": RIGHT * 5.5 + DOWN * 0.6,
            "n1": LEFT * 2.6 + UP * 1.0, "n2": ORIGIN + UP * 1.4,
            "n3": RIGHT * 2.6 + UP * 1.0, "n4": LEFT * 2.2 + DOWN * 1.8,
            "n5": RIGHT * 2.2 + DOWN * 1.8,
        }
        nodos = VGroup(*[Dot(p, color=GREY_B, radius=0.11) for p in pos.values()])
        a_txt = Text("A", font_size=24, color=BLUE_B).next_to(pos["A"], LEFT, buff=0.2)
        b_txt = Text("B", font_size=24, color=BLUE_B).next_to(pos["B"], RIGHT, buff=0.2)
        aristas = [("A", "n1"), ("A", "n4"), ("n1", "n2"), ("n2", "n3"),
                   ("n1", "n4"), ("n4", "n5"), ("n5", "n3"), ("n3", "B"),
                   ("n5", "B"), ("n2", "n5")]
        lineas = VGroup(*[
            Line(pos[u], pos[v], color=GREY_B, stroke_opacity=0.5)
            for u, v in aristas
        ])
        self.play(Create(lineas), FadeIn(nodos), FadeIn(a_txt), FadeIn(b_txt),
                  run_time=2)

        # Conmutacion de circuitos: camino dedicado
        cc_txt = Text("Circuitos (telefonía clásica): un camino reservado de punta a punta",
                      font_size=20, color=YELLOW).to_edge(DOWN)
        camino = VGroup(
            Line(pos["A"], pos["n1"], color=YELLOW, stroke_width=7),
            Line(pos["n1"], pos["n2"], color=YELLOW, stroke_width=7),
            Line(pos["n2"], pos["n3"], color=YELLOW, stroke_width=7),
            Line(pos["n3"], pos["B"], color=YELLOW, stroke_width=7),
        )
        self.play(FadeIn(cc_txt), run_time=0.8)
        self.play(Create(camino), run_time=2)
        senal = Dot(pos["A"], color=WHITE, radius=0.08)
        self.play(FadeIn(senal), run_time=0.3)
        for destino in ["n1", "n2", "n3", "B"]:
            self.play(senal.animate.move_to(pos[destino]), run_time=0.5,
                      rate_func=linear)
        self.play(FadeOut(senal), camino.animate.set_stroke(opacity=0.25), run_time=0.8)

        # Conmutacion de paquetes: cada paquete busca su ruta
        cp_txt = Text("Paquetes (Internet): cada fragmento viaja por su propia ruta",
                      font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(cc_txt, cp_txt), run_time=1)
        rutas = [
            ["A", "n1", "n2", "n5", "B"],
            ["A", "n4", "n5", "B"],
            ["A", "n1", "n2", "n3", "B"],
        ]
        paquetes = VGroup(*[
            Square(side_length=0.16, color=BLUE_B, fill_opacity=1, fill_color=BLUE_B)
            .move_to(pos["A"]) for _ in rutas
        ])
        self.play(FadeIn(paquetes), run_time=0.5)
        for salto in range(4):
            anims = []
            for paq, ruta in zip(paquetes, rutas):
                if salto + 1 < len(ruta):
                    anims.append(paq.animate.move_to(pos[ruta[salto + 1]]))
            self.play(*anims, run_time=0.8, rate_func=linear)

        # Senalizacion: el plano de control
        sen_txt = Text("Señalización: los mensajes de control que montan y liberan la llamada",
                       font_size=20, color=GOLD).to_edge(DOWN)
        setup = VGroup(
            Text("INVITE →", font_size=20, color=GOLD),
            Text("← 180 Ringing", font_size=20, color=GREY_B),
            Text("← 200 OK", font_size=20, color=BLUE_B),
            Text("ACK →", font_size=20, color=GOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(UP * 2.3 + RIGHT * 4.2)
        sip = Text("(SIP / SS7)", font_size=18, color=GREY_B).next_to(setup, DOWN, buff=0.2)
        self.play(ReplacementTransform(cp_txt, sen_txt), run_time=1)
        self.play(LaggedStart(*[FadeIn(s, shift=LEFT * 0.3) for s in setup],
                              lag_ratio=0.35), FadeIn(sip), run_time=2.5)
        self.wait(2)
