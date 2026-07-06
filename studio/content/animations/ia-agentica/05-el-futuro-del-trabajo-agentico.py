from manim import *


class ElFuturoDelTrabajoAgentico(Scene):
    def construct(self):
        titulo = Text("El futuro del trabajo agéntico", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Espectro de autonomia: de asistente a delegacion
        linea = NumberLine(x_range=[0, 4, 1], length=10.5, color=GREY_B,
                           include_numbers=False).move_to(UP * 1.7)
        niveles = [
            ("autocompletar", 0, GREY_B),
            ("copiloto\n(sugiere)", 1, BLUE_D),
            ("colaborador\n(ejecuta pasos)", 2, BLUE_B),
            ("delegado\n(tareas enteras)", 3, YELLOW),
            ("flota\n(proyectos)", 4, GOLD),
        ]
        marcas = VGroup()
        for texto, x, color in niveles:
            p = linea.number_to_point(x)
            d = Dot(p, color=color, radius=0.08)
            t = Text(texto, font_size=15, color=color, line_spacing=0.85)
            t.next_to(p, UP, buff=0.2)
            marcas.add(VGroup(d, t))
        self.play(Create(linea), LaggedStart(*[FadeIn(m) for m in marcas],
                                             lag_ratio=0.25), run_time=3)
        cursor = Triangle(color=YELLOW, fill_opacity=1, fill_color=YELLOW).scale(0.12)
        cursor.rotate(PI).next_to(linea.number_to_point(1), DOWN, buff=0.1)
        hoy = Text("2023", font_size=16, color=YELLOW).next_to(cursor, DOWN, buff=0.1)
        self.play(FadeIn(cursor), FadeIn(hoy), run_time=0.8)
        self.play(cursor.animate.next_to(linea.number_to_point(3), DOWN, buff=0.1),
                  hoy.animate.become(
                      Text("hoy", font_size=16, color=YELLOW).next_to(
                          linea.number_to_point(3), DOWN, buff=0.45)),
                  run_time=2)

        # Como cambia el dia de trabajo
        antes = VGroup(
            Text("Antes", font_size=21, color=GREY_B),
            Text("· hacer cada paso", font_size=18, color=GREY_B),
            Text("· una tarea a la vez", font_size=18, color=GREY_B),
            Text("· revisar al final", font_size=18, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(LEFT * 3.8 + DOWN * 1.3)
        despues = VGroup(
            Text("Con agentes", font_size=21, color=GOLD),
            Text("· definir y delegar", font_size=18, color=YELLOW),
            Text("· varias líneas en paralelo", font_size=18, color=YELLOW),
            Text("· revisar y dirigir continuamente", font_size=18, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(RIGHT * 3.2 + DOWN * 1.3)
        flecha = Arrow(antes.get_right(), despues.get_left(), color=GOLD, buff=0.3)
        self.play(FadeIn(antes, lag_ratio=0.15), run_time=1.5)
        self.play(GrowArrow(flecha), FadeIn(despues, lag_ratio=0.15), run_time=1.8)

        # Lo que sigue siendo humano
        humano = Text("Sigue siendo humano: el criterio, el gusto, la responsabilidad y el porqué",
                      font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(FadeIn(humano), run_time=1.5)
        self.play(Circumscribe(humano, color=BLUE_B), run_time=1.2)
        self.wait(2)
