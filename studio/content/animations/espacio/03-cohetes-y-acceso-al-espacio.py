from manim import *


class CohetesYAccesoAlEspacio(Scene):
    def construct(self):
        titulo = Text("Cohetes y acceso al espacio", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Ecuacion de Tsiolkovsky: la ley que gobierna el acceso al espacio
        ecuacion = MathTex(r"\Delta v = v_e \,\ln\frac{m_0}{m_f}",
                           font_size=44, color=BLUE_B)
        ecuacion.next_to(titulo, DOWN, buff=0.4)
        self.play(Write(ecuacion), run_time=2)

        # Cohete de dos etapas
        suelo = Line(LEFT * 6.5, RIGHT * 0.5, color=GREY_B).shift(DOWN * 3.2)
        etapa1 = Rectangle(width=0.5, height=1.2, color=GREY_B,
                           fill_opacity=1, fill_color=GREY_B)
        etapa2 = Rectangle(width=0.5, height=0.8, color=BLUE_D,
                           fill_opacity=1, fill_color=BLUE_D).next_to(etapa1, UP, buff=0)
        punta = Triangle(color=GOLD, fill_opacity=1, fill_color=GOLD)
        punta.stretch_to_fit_width(0.5).stretch_to_fit_height(0.4)
        punta.next_to(etapa2, UP, buff=0)
        cohete = VGroup(etapa1, etapa2, punta).move_to(LEFT * 4 + DOWN * 2.4)
        self.play(Create(suelo), FadeIn(cohete), run_time=1.2)

        # Barra de velocidad hasta velocidad orbital
        barra_fondo = Rectangle(width=0.35, height=4.5, color=GREY_B).shift(RIGHT * 5.6 + DOWN * 0.4)
        v = ValueTracker(0.0)
        barra = always_redraw(lambda: Rectangle(
            width=0.35, height=max(v.get_value() / 7.8 * 4.5, 0.001),
            color=YELLOW, fill_opacity=1, fill_color=YELLOW,
        ).align_to(barra_fondo, DOWN).align_to(barra_fondo, LEFT))
        lectura = always_redraw(lambda: VGroup(
            DecimalNumber(v.get_value(), num_decimal_places=1, font_size=28, color=YELLOW),
            Text("km/s", font_size=20, color=GREY_B),
        ).arrange(RIGHT, buff=0.15).next_to(barra_fondo, UP, buff=0.25))
        meta = Text("7.8 km/s: velocidad orbital", font_size=20, color=BLUE_B)
        meta.next_to(barra_fondo, LEFT, buff=0.3).shift(UP * 2)
        self.play(Create(barra_fondo), FadeIn(lectura), FadeIn(meta), run_time=1)
        self.add(barra)

        # Ascenso con giro gravitacional: encendido de etapa 1
        llama = Triangle(color=YELLOW, fill_opacity=1, fill_color=YELLOW)
        llama.stretch_to_fit_width(0.3).stretch_to_fit_height(0.45)
        llama.rotate(PI).next_to(etapa1, DOWN, buff=0.02)
        cohete_llama = VGroup(cohete, llama)
        self.play(FadeIn(llama), run_time=0.4)
        self.play(
            cohete_llama.animate.shift(UP * 2 + RIGHT * 1).rotate(-PI / 10),
            v.animate.set_value(3.0),
            run_time=3, rate_func=rush_into,
        )

        # Separacion de etapa: la masa que sobra se descarta
        sep = Text("Separación de etapa: menos masa muerta", font_size=22, color=GREY_B)
        sep.to_edge(DOWN)
        self.play(FadeIn(sep), run_time=0.8)
        cohete_llama.remove(llama)
        cohete.remove(etapa1)
        self.play(
            etapa1.animate.shift(DOWN * 1.5 + LEFT * 0.5).rotate(PI / 6).set_opacity(0.3),
            FadeOut(llama),
            run_time=1.5,
        )

        # Etapa 2 completa la insercion orbital
        self.play(
            cohete.animate.shift(UP * 1.6 + RIGHT * 3.2).rotate(-PI / 5),
            v.animate.set_value(7.8),
            run_time=3.5, rate_func=smooth,
        )
        self.play(Flash(lectura, color=YELLOW), run_time=1)

        cierre = Text("Cada kg en órbita exige quemar decenas de kg de propelente",
                      font_size=22, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(sep, cierre), run_time=1.2)
        self.wait(2)
