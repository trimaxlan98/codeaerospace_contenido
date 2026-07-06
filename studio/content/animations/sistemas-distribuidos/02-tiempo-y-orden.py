from manim import *


class TiempoRelojesYOrdenDeEventos(Scene):
    def construct(self):
        titulo = Text("Tiempo, relojes y orden de eventos",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Dos procesos con lineas de tiempo
        y_a, y_b = 1.1, -1.3
        linea_a = Arrow(LEFT * 5.8 + UP * y_a, RIGHT * 5.8 + UP * y_a, color=GREY_B,
                        buff=0, max_tip_length_to_length_ratio=0.02)
        linea_b = Arrow(LEFT * 5.8 + UP * y_b, RIGHT * 5.8 + UP * y_b, color=GREY_B,
                        buff=0, max_tip_length_to_length_ratio=0.02)
        pa = Text("Proceso A", font_size=20, color=BLUE_B)
        pa.next_to(linea_a.get_start(), UP, buff=0.15).shift(RIGHT * 0.7)
        pb = Text("Proceso B", font_size=20, color=GOLD)
        pb.next_to(linea_b.get_start(), DOWN, buff=0.15).shift(RIGHT * 0.7)
        self.play(GrowArrow(linea_a), GrowArrow(linea_b), FadeIn(pa), FadeIn(pb),
                  run_time=1.5)

        problema = Text("Los relojes físicos derivan: 'la misma hora' no existe entre máquinas",
                        font_size=20, color=GREY_B).to_edge(DOWN)
        reloj_a = Text("10:00:00.000", font_size=18, color=BLUE_B)
        reloj_a.next_to(linea_a.get_end(), UP, buff=0.15).shift(LEFT * 1.0)
        reloj_b = Text("10:00:00.047", font_size=18, color=GOLD)
        reloj_b.next_to(linea_b.get_end(), DOWN, buff=0.15).shift(LEFT * 1.0)
        self.play(FadeIn(problema), FadeIn(reloj_a), FadeIn(reloj_b), run_time=1.5)

        # Relojes logicos de Lamport: contar causalidad, no segundos
        lamport = Text("Reloj de Lamport: cada evento suma 1; un mensaje propaga el máximo",
                       font_size=20, color=YELLOW).to_edge(DOWN)
        self.play(ReplacementTransform(problema, lamport), run_time=1.2)

        def evento(x, y, etiqueta, color):
            d = Dot([x, y, 0], color=color, radius=0.09)
            t = Text(etiqueta, font_size=20, color=color)
            t.next_to(d, UP if y > 0 else DOWN, buff=0.15)
            return VGroup(d, t)

        e1 = evento(-4.4, y_a, "1", BLUE_B)
        e2 = evento(-2.6, y_a, "2", BLUE_B)
        e3 = evento(-4.0, y_b, "1", GOLD)
        self.play(FadeIn(e1), FadeIn(e3), run_time=0.8)
        self.play(FadeIn(e2), run_time=0.6)

        # Mensaje de A a B: B toma max(local, recibido) + 1
        msg = Arrow([-2.6, y_a - 0.1, 0], [-0.6, y_b + 0.1, 0], color=YELLOW, buff=0.1)
        self.play(GrowArrow(msg), run_time=1.2)
        e4 = evento(-0.6, y_b, "3 = max(1,2)+1", YELLOW)
        self.play(FadeIn(e4), run_time=1)
        e5 = evento(1.6, y_b, "4", GOLD)
        e6 = evento(0.6, y_a, "3", BLUE_B)
        self.play(FadeIn(e5), FadeIn(e6), run_time=0.8)

        # Causalidad vs concurrencia
        causal = Text("2 → 3: causalmente ordenados", font_size=19, color=YELLOW)
        causal.move_to(RIGHT * 3.9 + UP * 0.2)
        concurrente = Text("3 (en A) y 4 (en B): concurrentes,\nningún orden es 'el verdadero'",
                           font_size=19, color=GREY_B, line_spacing=0.9)
        concurrente.move_to(RIGHT * 3.9 + DOWN * 0.6)
        self.play(FadeIn(causal), run_time=1)
        self.play(Indicate(e2, color=YELLOW), Indicate(e4[0], color=YELLOW), run_time=1.2)
        self.play(FadeIn(concurrente), run_time=1.2)
        self.play(Indicate(e6, color=GREY_B), Indicate(e5, color=GREY_B), run_time=1.2)

        cierre = Text("Sin reloj global, el orden se construye con causalidad (Lamport, vectores)",
                      font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(lamport, cierre), run_time=1.2)
        self.wait(2)
