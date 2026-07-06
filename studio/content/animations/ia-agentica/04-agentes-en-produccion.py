from manim import *


class IaAgenticaEnProduccion(Scene):
    def construct(self):
        titulo = Text("IA agéntica en producción", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # El agente en el centro, rodeado de infraestructura de produccion
        agente = VGroup(
            RoundedRectangle(width=2.0, height=0.85, corner_radius=0.14, color=BLUE_B,
                             fill_opacity=0.15, fill_color=BLUE_B),
            Text("agente", font_size=20, color=BLUE_B),
        )
        agente[1].move_to(agente[0])
        agente.move_to(DOWN * 0.6)
        demo = Text("En demo funciona. Producción es otro deporte:",
                    font_size=21, color=GREY_B).next_to(titulo, DOWN, buff=0.25)
        self.play(FadeIn(agente), FadeIn(demo), run_time=1.5)

        # 1) Sandbox y permisos
        caja = SurroundingRectangle(agente, color=GOLD, buff=0.35, corner_radius=0.15)
        caja_txt = Text("sandbox: permisos mínimos, acciones acotadas",
                        font_size=18, color=GOLD)
        caja_txt.next_to(caja, DOWN, buff=0.2)
        self.play(Create(caja), FadeIn(caja_txt), run_time=1.5)

        # 2) Observabilidad
        logs = VGroup(
            Text("traza #4812", font_size=15, color=GREY_B),
            Text("· tool: query_db  · 1.2 s", font_size=15, color=GREY_B),
            Text("· tokens: 8 430  · costo: $0.11", font_size=15, color=GREY_B),
            Text("· resultado: ok", font_size=15, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        logs.move_to(LEFT * 4.6 + DOWN * 0.6)
        logs_caja = SurroundingRectangle(logs, color=GREY_B, buff=0.2)
        logs_txt = Text("observabilidad", font_size=18, color=GREY_B)
        logs_txt.next_to(logs_caja, UP, buff=0.15)
        union1 = DashedLine(logs_caja.get_right(), caja.get_left(), color=GREY_B,
                            stroke_opacity=0.6)
        self.play(FadeIn(logs), Create(logs_caja), FadeIn(logs_txt), Create(union1),
                  run_time=1.8)

        # 3) Limites y aprobacion humana
        limites = VGroup(
            Text("límites duros", font_size=18, color=RED_D),
            Text("presupuesto · timeout · lista de acciones", font_size=15,
                 color=GREY_B),
            Text("acción irreversible → humano aprueba", font_size=15, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        limites.move_to(RIGHT * 4.3 + DOWN * 0.6)
        lim_caja = SurroundingRectangle(limites, color=RED_D, buff=0.2)
        union2 = DashedLine(caja.get_right(), lim_caja.get_left(), color=GREY_B,
                            stroke_opacity=0.6)
        self.play(FadeIn(limites), Create(lim_caja), Create(union2), run_time=1.8)

        # 4) Evaluacion continua antes de desplegar
        pipeline = VGroup()
        for nombre, color in [("cambio", GREY_B), ("evals", YELLOW),
                              ("canario", GOLD), ("100%", BLUE_B)]:
            p = VGroup(
                RoundedRectangle(width=1.45, height=0.5, corner_radius=0.1,
                                 color=color, fill_opacity=0.12, fill_color=color),
                Text(nombre, font_size=15, color=color),
            )
            p[1].move_to(p[0])
            pipeline.add(p)
        pipeline.arrange(RIGHT, buff=0.55).move_to(DOWN * 2.7)
        flechas = VGroup(*[
            Arrow(pipeline[i].get_right(), pipeline[i + 1].get_left(), color=GREY_B,
                  buff=0.05, stroke_width=3) for i in range(3)
        ])
        pipe_txt = Text("cada mejora pasa por evaluaciones y despliegue gradual",
                        font_size=17, color=YELLOW)
        pipe_txt.next_to(pipeline, UP, buff=0.18)
        self.play(FadeOut(caja_txt), FadeIn(pipeline, lag_ratio=0.15),
                  *[GrowArrow(f) for f in flechas], FadeIn(pipe_txt), run_time=2)
        pulso = Dot(pipeline[0].get_center(), color=WHITE, radius=0.07)
        self.play(FadeIn(pulso), run_time=0.3)
        for p in pipeline[1:]:
            self.play(pulso.animate.move_to(p.get_center()), run_time=0.6)
        self.play(FadeOut(pulso), run_time=0.3)

        cierre = Text("La autonomía se gana con evidencia: primero acotado, luego amplio",
                      font_size=20, color=GOLD).to_edge(DOWN).shift(UP * 0.02)
        self.play(ReplacementTransform(demo, cierre), run_time=1.2)
        self.wait(2)
