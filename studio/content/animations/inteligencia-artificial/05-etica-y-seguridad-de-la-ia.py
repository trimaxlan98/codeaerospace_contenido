from manim import *


class EticaYSeguridadDeLaIa(Scene):
    def construct(self):
        titulo = Text("Ética y seguridad de la IA", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # El problema de alineacion: objetivo declarado vs comportamiento
        objetivo = Arrow(LEFT * 5.5 + UP * 1.4, LEFT * 0.7 + UP * 1.4, color=BLUE_B,
                         buff=0)
        obj_txt = Text("lo que pedimos", font_size=19, color=BLUE_B)
        obj_txt.next_to(objetivo, UP, buff=0.15)
        conducta = Arrow(LEFT * 5.5 + UP * 1.4, LEFT * 0.9 + UP * 0.3, color=RED_D,
                         buff=0)
        con_txt = Text("lo que el sistema optimiza", font_size=19, color=RED_D)
        con_txt.next_to(conducta.get_end(), DOWN, buff=0.15)
        self.play(GrowArrow(objetivo), FadeIn(obj_txt), run_time=1.2)
        self.play(GrowArrow(conducta), FadeIn(con_txt), run_time=1.2)
        brecha = Angle(conducta, objetivo, radius=1.4, color=YELLOW)
        brecha_txt = Text("alineación: cerrar esta brecha", font_size=19, color=YELLOW)
        brecha_txt.next_to(brecha, RIGHT, buff=0.2).shift(UP * 0.1)
        self.play(Create(brecha), FadeIn(brecha_txt), run_time=1.5)

        # La brecha se cierra con entrenamiento y evaluacion
        self.play(Transform(conducta, Arrow(LEFT * 5.5 + UP * 1.4,
                                            LEFT * 0.7 + UP * 1.15, color=GOLD,
                                            buff=0)),
                  FadeOut(brecha), run_time=2)
        mejor = Text("RLHF, políticas, evaluaciones", font_size=17, color=GOLD)
        mejor.move_to(con_txt)
        self.play(ReplacementTransform(con_txt, mejor), run_time=1)

        # Riesgos concretos
        riesgos = VGroup(
            Text("· Sesgo: el modelo hereda los datos", font_size=19, color=GREY_B),
            Text("· Privacidad: memoriza lo que vio", font_size=19, color=GREY_B),
            Text("· Alucinación: afirma sin saber", font_size=19, color=GREY_B),
            Text("· Mal uso: la capacidad es de doble filo", font_size=19, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        riesgos.move_to(RIGHT * 3.4 + UP * 0.9)
        riesgos_txt = Text("Riesgos", font_size=22, color=RED_D)
        riesgos_txt.next_to(riesgos, UP, buff=0.25).align_to(riesgos, LEFT)
        self.play(FadeIn(riesgos_txt),
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in riesgos],
                              lag_ratio=0.3), run_time=3)

        # Defensas en capas alrededor del modelo
        modelo = RoundedRectangle(width=1.7, height=0.8, corner_radius=0.12,
                                  color=BLUE_B, fill_opacity=0.15, fill_color=BLUE_B)
        modelo.move_to(LEFT * 3.2 + DOWN * 1.9)
        mod_txt = Text("modelo", font_size=18, color=BLUE_B).move_to(modelo)
        capas = VGroup(*[
            SurroundingRectangle(modelo, color=c, buff=b, corner_radius=0.15)
            for c, b in [(GOLD, 0.22), (YELLOW, 0.44), (GREY_B, 0.66)]
        ])
        capas_txt = VGroup(
            Text("entrenamiento seguro", font_size=15, color=GOLD),
            Text("filtros y guardrails", font_size=15, color=YELLOW),
            Text("supervisión humana y auditoría", font_size=15, color=GREY_B),
        )
        for t, c in zip(capas_txt, capas):
            t.next_to(c, RIGHT, buff=0.25)
        self.play(FadeIn(modelo), FadeIn(mod_txt), run_time=1)
        for c, t in zip(capas, capas_txt):
            self.play(Create(c), FadeIn(t), run_time=1)

        cierre = Text("La pregunta no es solo qué puede hacer la IA, sino qué debería — y quién decide",
                      font_size=19, color=GOLD).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.5)
        self.wait(2)
