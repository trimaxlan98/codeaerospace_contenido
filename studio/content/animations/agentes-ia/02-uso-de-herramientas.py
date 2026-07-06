from manim import *


class UsoDeHerramientas(Scene):
    def construct(self):
        titulo = Text("Uso de herramientas (tool use)", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # El LLM solo no puede: ni calcular exacto ni ver datos vivos
        pregunta = Text("¿Cuánto es el 12.4% de 8 763 219?", font_size=21, color=WHITE)
        pregunta.move_to(UP * 2.1)
        self.play(FadeIn(pregunta), run_time=1)

        modelo = RoundedRectangle(width=2.1, height=0.9, corner_radius=0.14,
                                  color=BLUE_B, fill_opacity=0.12, fill_color=BLUE_B)
        modelo.move_to(LEFT * 3.8 + DOWN * 0.3)
        m_txt = Text("LLM", font_size=22, color=BLUE_B).move_to(modelo)
        self.play(FadeIn(modelo), FadeIn(m_txt), run_time=1)
        duda = Text("adivinar ≈ error", font_size=18, color=RED_D)
        duda.next_to(modelo, DOWN, buff=0.25)
        self.play(FadeIn(duda), run_time=0.8)
        self.play(FadeOut(duda), run_time=0.6)

        # Herramientas disponibles
        herramientas = VGroup()
        for nombre, color in [("calculadora", GOLD), ("buscador", GREY_B),
                              ("base de datos", GREY_B)]:
            caja = RoundedRectangle(width=2.1, height=0.6, corner_radius=0.12,
                                    color=color, fill_opacity=0.1, fill_color=color)
            t = Text(nombre, font_size=18, color=color).move_to(caja)
            herramientas.add(VGroup(caja, t))
        herramientas.arrange(DOWN, buff=0.25).move_to(RIGHT * 3.9 + DOWN * 0.3)
        h_txt = Text("herramientas", font_size=19, color=GREY_B)
        h_txt.next_to(herramientas, UP, buff=0.25)
        self.play(FadeIn(h_txt), FadeIn(herramientas, lag_ratio=0.2), run_time=1.5)

        # 1) El modelo emite una llamada estructurada
        llamada = VGroup(
            Text('{ "tool": "calculadora",', font_size=18, color=YELLOW),
            Text('  "input": "8763219 * 0.124" }', font_size=18, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        llamada.move_to(DOWN * 0.3 + RIGHT * 0.0)
        paso1 = Text("1) El modelo no calcula: pide", font_size=20, color=YELLOW)
        paso1.to_edge(DOWN)
        self.play(FadeIn(paso1), Write(llamada), run_time=2)
        f1 = Arrow(modelo.get_right(), llamada.get_left(), color=YELLOW, buff=0.15)
        f2 = Arrow(llamada.get_right(), herramientas[0].get_left(), color=YELLOW,
                   buff=0.15)
        self.play(GrowArrow(f1), GrowArrow(f2), run_time=1.2)
        self.play(Indicate(herramientas[0], color=GOLD), run_time=1)

        # 2) La herramienta ejecuta y devuelve
        paso2 = Text("2) La herramienta ejecuta de verdad y responde", font_size=20,
                     color=GOLD).to_edge(DOWN)
        resultado = Text("1 086 639.16", font_size=20, color=GOLD)
        resultado.next_to(herramientas[0], DOWN, buff=1.1)
        f3 = CurvedArrow(herramientas[0].get_bottom(), modelo.get_bottom(),
                         angle=PI / 4, color=GOLD, stroke_width=3)
        self.play(ReplacementTransform(paso1, paso2), FadeIn(resultado), run_time=1.2)
        self.play(Create(f3), run_time=1.2)

        # 3) El modelo redacta con el dato
        paso3 = Text("3) El modelo integra el resultado en su respuesta", font_size=20,
                     color=BLUE_B).to_edge(DOWN)
        respuesta = Text("El 12.4% de 8 763 219 es 1 086 639.16",
                         font_size=21, color=WHITE)
        respuesta.move_to(UP * 1.35)
        self.play(ReplacementTransform(paso2, paso3), run_time=1)
        self.play(FadeIn(respuesta, shift=UP * 0.2), run_time=1.2)
        self.play(Circumscribe(respuesta, color=GOLD), run_time=1)

        cierre = Text("Las herramientas convierten al modelo en actor: leer, calcular, ejecutar",
                      font_size=20, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(paso3, cierre), run_time=1.2)
        self.wait(2)
