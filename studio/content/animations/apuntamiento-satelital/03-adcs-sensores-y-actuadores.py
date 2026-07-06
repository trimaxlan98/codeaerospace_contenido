from manim import *


class AdcsSensoresYActuadores(Scene):
    def construct(self):
        titulo = Text("ADCS: sensores y actuadores", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Satelite desapuntado en el centro
        sat = VGroup(
            Rectangle(width=1.2, height=0.8, color=BLUE_D, fill_opacity=0.3,
                      fill_color=BLUE_D),
            Arrow(ORIGIN, UP * 1.1, color=YELLOW, buff=0),
        )
        sat[1].put_start_and_end_on(sat[0].get_center(), sat[0].get_center() + UP * 1.1)
        sat.move_to(DOWN * 0.6)
        sat.rotate(PI / 5)
        objetivo = DashedLine(sat[0].get_center(), sat[0].get_center() + UP * 1.6,
                              color=GOLD)
        obj_txt = Text("Apuntamiento deseado", font_size=18, color=GOLD)
        obj_txt.next_to(objetivo.get_end(), UP, buff=0.15)
        self.play(FadeIn(sat), Create(objetivo), FadeIn(obj_txt), run_time=1.5)

        # Lazo de control: sensores -> computadora -> actuadores
        sensores = VGroup(
            Text("Sensores", font_size=24, color=BLUE_B),
            Text("· sensor solar", font_size=18, color=GREY_B),
            Text("· rastreador de estrellas", font_size=18, color=GREY_B),
            Text("· giróscopos / magnetómetro", font_size=18, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(LEFT * 4.6 + UP * 1.2)
        caja_s = SurroundingRectangle(sensores, color=BLUE_B, buff=0.25)

        actuadores = VGroup(
            Text("Actuadores", font_size=24, color=YELLOW),
            Text("· ruedas de reacción", font_size=18, color=GREY_B),
            Text("· magnetorques", font_size=18, color=GREY_B),
            Text("· propulsores", font_size=18, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(RIGHT * 4.4 + UP * 1.2)
        caja_a = SurroundingRectangle(actuadores, color=YELLOW, buff=0.25)

        computo = VGroup(
            Text("Computadora", font_size=22, color=GOLD),
            Text("estimar + controlar", font_size=17, color=GREY_B),
        ).arrange(DOWN, buff=0.1).move_to(UP * 2.4)
        caja_c = SurroundingRectangle(computo, color=GOLD, buff=0.22)

        self.play(FadeIn(sensores), Create(caja_s), run_time=1.3)
        self.play(FadeIn(computo), Create(caja_c), run_time=1.1)
        self.play(FadeIn(actuadores), Create(caja_a), run_time=1.3)

        f1 = Arrow(caja_s.get_top(), caja_c.get_left(), color=BLUE_B, buff=0.1)
        f1_txt = Text("¿dónde apunto?", font_size=17, color=BLUE_B)
        f1_txt.next_to(f1.get_center(), UL, buff=0.1)
        f2 = Arrow(caja_c.get_right(), caja_a.get_top(), color=GOLD, buff=0.1)
        f2_txt = Text("orden de giro", font_size=17, color=GOLD)
        f2_txt.next_to(f2.get_center(), UR, buff=0.1)
        f3 = Arrow(caja_a.get_bottom(), sat.get_right() + RIGHT * 0.2, color=YELLOW, buff=0.1)
        self.play(GrowArrow(f1), FadeIn(f1_txt), run_time=1)
        self.play(GrowArrow(f2), FadeIn(f2_txt), run_time=1)
        self.play(GrowArrow(f3), run_time=1)

        # El lazo corrige el error de actitud
        lazo = Text("Lazo cerrado: medir → calcular error → girar → volver a medir",
                    font_size=21, color=GREY_B).to_edge(DOWN)
        self.play(FadeIn(lazo), run_time=1)
        self.play(Rotate(sat, angle=-PI / 5 * 0.7), run_time=2)
        self.play(Rotate(sat, angle=-PI / 5 * 0.25), run_time=1.2)
        self.play(Rotate(sat, angle=-PI / 5 * 0.05), run_time=0.8)
        self.play(Flash(sat[1].get_end(), color=GOLD, flash_radius=0.4), run_time=0.8)

        cierre = Text("Precisión típica: de grados (CubeSat) a segundos de arco (telescopios)",
                      font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(lazo, cierre), run_time=1.2)
        self.wait(2)
