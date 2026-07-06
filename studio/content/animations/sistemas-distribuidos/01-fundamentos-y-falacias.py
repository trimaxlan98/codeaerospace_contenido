from manim import *


class FundamentosYLasOchoFalacias(Scene):
    def construct(self):
        titulo = Text("Sistemas distribuidos: las 8 falacias",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Un sistema distribuido: varios nodos y una red que los une
        pos = [LEFT * 4.6 + UP * 0.8, LEFT * 4.6 + DOWN * 1.6,
               LEFT * 1.8 + DOWN * 0.4, LEFT * 2.2 + UP * 1.9]
        nodos = VGroup(*[
            VGroup(Circle(radius=0.4, color=BLUE_B, fill_opacity=0.15,
                          fill_color=BLUE_B).move_to(p),
                   Text(f"N{i+1}", font_size=19, color=BLUE_B).move_to(p))
            for i, p in enumerate(pos)
        ])
        enlaces = VGroup(*[
            Line(pos[i], pos[j], color=GREY_B, stroke_opacity=0.6, z_index=-1)
            for i, j in [(0, 1), (0, 2), (1, 2), (0, 3), (2, 3)]
        ])
        self.play(Create(enlaces), LaggedStart(*[FadeIn(n) for n in nodos],
                                               lag_ratio=0.15), run_time=2)
        defin = Text("Varias máquinas que cooperan como si fueran una sola",
                     font_size=21, color=GREY_B).to_edge(DOWN)
        self.play(FadeIn(defin), run_time=1)

        # Las 8 falacias, en lista
        falacias = VGroup(*[
            Text(t, font_size=19, color=GREY_B) for t in [
                "1. La red es fiable",
                "2. La latencia es cero",
                "3. El ancho de banda es infinito",
                "4. La red es segura",
                "5. La topología no cambia",
                "6. Hay un solo administrador",
                "7. Transportar datos no cuesta",
                "8. La red es homogénea",
            ]
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(RIGHT * 3.6 + DOWN * 0.3)
        fal_titulo = Text("Lo que NO puedes suponer:", font_size=21, color=YELLOW)
        fal_titulo.next_to(falacias, UP, buff=0.3)
        self.play(FadeIn(fal_titulo),
                  LaggedStart(*[FadeIn(f, shift=RIGHT * 0.3) for f in falacias],
                              lag_ratio=0.15), run_time=3.5)

        # Falacia 1 en accion: un enlace se corta
        self.play(Indicate(falacias[0], color=YELLOW), run_time=1)
        corte = Cross(scale_factor=0.25).move_to(enlaces[1].get_center())
        self.play(Create(corte), enlaces[1].animate.set_stroke(opacity=0.15),
                  run_time=1)

        # Falacia 2 en accion: un mensaje tarda
        self.play(Indicate(falacias[1], color=YELLOW), run_time=1)
        msg = Dot(pos[0], color=YELLOW, radius=0.09)
        reloj = Text("t = 340 ms", font_size=18, color=YELLOW)
        reloj.next_to(enlaces[3].get_center(), UP, buff=0.4)
        self.play(FadeIn(msg), run_time=0.4)
        self.play(msg.animate.move_to(pos[3]), FadeIn(reloj), run_time=2.2,
                  rate_func=rush_from)
        self.play(FadeOut(msg), run_time=0.4)

        cierre = Text("Diseñar distribuido = asumir fallas, demoras y desorden como lo normal",
                      font_size=20, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(defin, cierre), run_time=1.2)
        self.wait(2)
