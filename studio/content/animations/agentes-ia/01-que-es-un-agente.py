from manim import *
import numpy as np


class QueEsUnAgenteDeIa(Scene):
    def construct(self):
        titulo = Text("Qué es un agente de IA", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Chatbot: una pregunta, una respuesta, fin
        chat_txt = Text("Chatbot: responde y termina", font_size=21, color=GREY_B)
        chat_txt.move_to(LEFT * 3.6 + UP * 2.0)
        usuario = Dot(LEFT * 5.6 + UP * 0.8, color=BLUE_B, radius=0.12)
        u_txt = Text("tú", font_size=18, color=BLUE_B).next_to(usuario, DOWN, buff=0.15)
        modelo = RoundedRectangle(width=1.5, height=0.7, corner_radius=0.12,
                                  color=GREY_B, fill_opacity=0.12, fill_color=GREY_B)
        modelo.move_to(LEFT * 2.2 + UP * 0.8)
        m_txt = Text("LLM", font_size=19, color=GREY_B).move_to(modelo)
        ida = Arrow(usuario.get_right(), modelo.get_left(), color=BLUE_B, buff=0.1)
        vuelta = Arrow(modelo.get_left() + DOWN * 0.15, usuario.get_right() + DOWN * 0.15,
                       color=GREY_B, buff=0.1)
        self.play(FadeIn(chat_txt), FadeIn(usuario), FadeIn(u_txt), FadeIn(modelo),
                  FadeIn(m_txt), run_time=1.5)
        self.play(GrowArrow(ida), run_time=0.8)
        self.play(GrowArrow(vuelta), run_time=0.8)

        # Agente: percibe -> razona -> actua, en bucle con el entorno
        agente_txt = Text("Agente: persigue un objetivo actuando en un entorno",
                          font_size=21, color=GOLD).move_to(RIGHT * 2.8 + UP * 2.0)
        self.play(FadeIn(agente_txt), run_time=1)

        centro = RIGHT * 2.8 + DOWN * 0.8
        radios = 1.5
        etapas = [("percibir", PI / 2, BLUE_B), ("razonar", PI / 2 + TAU / 3, YELLOW),
                  ("actuar", PI / 2 + 2 * TAU / 3, GOLD)]
        nodos = VGroup()
        for nombre, ang, color in etapas:
            p = centro + radios * np.array([np.cos(ang), np.sin(ang), 0])
            c = Circle(radius=0.42, color=color, fill_opacity=0.12, fill_color=color)
            c.move_to(p)
            t = Text(nombre, font_size=17, color=color).move_to(c)
            nodos.add(VGroup(c, t))
        arcos = VGroup(*[
            CurvedArrow(
                nodos[i][0].point_at_angle(etapas[i][1] - 1.9),
                nodos[(i + 1) % 3][0].point_at_angle(etapas[(i + 1) % 3][1] + 1.9),
                angle=-TAU / 8, color=GREY_B, stroke_width=3,
            )
            for i in range(3)
        ])
        self.play(LaggedStart(*[FadeIn(n) for n in nodos], lag_ratio=0.25), run_time=1.8)
        self.play(LaggedStart(*[Create(a) for a in arcos], lag_ratio=0.25), run_time=1.8)

        entorno = SurroundingRectangle(VGroup(nodos, arcos), color=GREY_B, buff=0.45,
                                       corner_radius=0.2)
        env_txt = Text("entorno", font_size=17, color=GREY_B)
        env_txt.next_to(entorno, DOWN, buff=0.15)
        self.play(Create(entorno), FadeIn(env_txt), run_time=1.2)

        # El bucle gira varias veces
        pulso = Dot(nodos[0][0].get_center(), color=WHITE, radius=0.08)
        self.play(FadeIn(pulso), run_time=0.3)
        for _ in range(2):
            for i in [1, 2, 0]:
                self.play(pulso.animate.move_to(nodos[i][0].get_center()),
                          run_time=0.55, rate_func=linear)
        self.play(FadeOut(pulso), run_time=0.3)

        # Las piezas que lo hacen agente
        piezas = VGroup(
            Text("objetivo + herramientas + memoria + autonomía",
                 font_size=20, color=YELLOW),
        ).to_edge(DOWN).shift(UP * 0.55)
        cierre = Text("Un agente no contesta: decide qué hacer a continuación",
                      font_size=21, color=BLUE_B).to_edge(DOWN)
        self.play(FadeIn(piezas), run_time=1.2)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
