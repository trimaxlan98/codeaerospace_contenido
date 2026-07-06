from manim import *


class PlanificacionYRazonamiento(Scene):
    def construct(self):
        titulo = Text("Planificación y razonamiento", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Objetivo arriba, descompuesto en un arbol de tareas
        objetivo = VGroup(
            RoundedRectangle(width=3.4, height=0.65, corner_radius=0.12, color=GOLD,
                             fill_opacity=0.15, fill_color=GOLD),
            Text("Objetivo: publicar el informe", font_size=18, color=GOLD),
        )
        objetivo[1].move_to(objetivo[0])
        objetivo.move_to(UP * 2.0)
        self.play(FadeIn(objetivo), run_time=1)

        tareas = []
        for texto, x in [("reunir datos", -4.2), ("analizar", -1.4),
                         ("redactar", 1.4), ("publicar", 4.2)]:
            t = VGroup(
                RoundedRectangle(width=2.2, height=0.6, corner_radius=0.12,
                                 color=BLUE_B, fill_opacity=0.12, fill_color=BLUE_B),
                Text(texto, font_size=17, color=BLUE_B),
            )
            t[1].move_to(t[0])
            t.move_to(RIGHT * x + UP * 0.5)
            tareas.append(t)
        ramas = VGroup(*[
            Line(objetivo.get_bottom(), t.get_top(), color=GREY_B, stroke_width=2)
            for t in tareas
        ])
        plan_txt = Text("1) Descomponer: el plan es un árbol de subtareas",
                        font_size=20, color=YELLOW).to_edge(DOWN)
        self.play(FadeIn(plan_txt), Create(ramas),
                  LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in tareas],
                              lag_ratio=0.2), run_time=2.5)

        # Ejecutar en orden, verificando
        ejecutar = Text("2) Ejecutar paso a paso, verificando cada resultado",
                        font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(plan_txt, ejecutar), run_time=1)
        for t in tareas[:2]:
            self.play(t[0].animate.set_fill(BLUE_B, opacity=0.4), run_time=0.6)
            check = Text("✓", font_size=26, color=GOLD).next_to(t, DOWN, buff=0.12)
            self.play(FadeIn(check, scale=1.5), run_time=0.5)

        # Falla en 'redactar': replanificar
        fallo = Cross(scale_factor=0.28).move_to(tareas[2].get_center())
        replan = Text("3) Algo falla → replanificar la rama, no todo el plan",
                      font_size=20, color=RED_D).to_edge(DOWN)
        self.play(ReplacementTransform(ejecutar, replan), run_time=1)
        self.play(tareas[2][0].animate.set_color(RED_D), Create(fallo), run_time=1)

        alternativas = []
        for texto, x in [("borrador corto", 0.5), ("pedir revisión", 3.0)]:
            a = VGroup(
                RoundedRectangle(width=2.0, height=0.55, corner_radius=0.12,
                                 color=YELLOW, fill_opacity=0.12, fill_color=YELLOW),
                Text(texto, font_size=15, color=YELLOW),
            )
            a[1].move_to(a[0])
            a.move_to(RIGHT * x + DOWN * 1.1)
            alternativas.append(a)
        ramas2 = VGroup(*[
            Line(tareas[2].get_bottom(), a.get_top(), color=YELLOW, stroke_width=2)
            for a in alternativas
        ])
        self.play(Create(ramas2), FadeIn(alternativas[0]), FadeIn(alternativas[1]),
                  run_time=1.5)
        self.play(alternativas[0][0].animate.set_fill(YELLOW, opacity=0.4),
                  run_time=0.8)
        check2 = Text("✓", font_size=24, color=GOLD)
        check2.next_to(alternativas[0], DOWN, buff=0.1)
        self.play(FadeIn(check2, scale=1.5), run_time=0.6)
        self.play(tareas[3][0].animate.set_fill(BLUE_B, opacity=0.4), run_time=0.8)
        check3 = Text("✓", font_size=26, color=GOLD).next_to(tareas[3], DOWN, buff=0.12)
        self.play(FadeIn(check3, scale=1.5), Flash(objetivo, color=GOLD), run_time=1)

        cierre = Text("Razonar antes de actuar y corregir sobre la marcha: eso separa a un agente de un script",
                      font_size=18, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(replan, cierre), run_time=1.2)
        self.wait(2)
