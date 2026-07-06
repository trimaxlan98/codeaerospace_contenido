from manim import *
import numpy as np


class SistemasMultiagente(Scene):
    def construct(self):
        titulo = Text("Sistemas multiagente", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Roles especializados en circulo
        centro = DOWN * 0.6 + LEFT * 2.6
        roles = [("planificador", GOLD), ("investigador", BLUE_B),
                 ("programador", BLUE_D), ("crítico", YELLOW)]
        agentes = VGroup()
        pos = []
        for i, (nombre, color) in enumerate(roles):
            ang = PI / 2 + i * TAU / 4
            p = centro + 1.7 * np.array([np.cos(ang), np.sin(ang), 0])
            pos.append(p)
            a = VGroup(
                Circle(radius=0.45, color=color, fill_opacity=0.12, fill_color=color),
                Text(nombre, font_size=14, color=color),
            )
            a[1].move_to(a[0])
            a.move_to(p)
            agentes.add(a)
        self.play(LaggedStart(*[FadeIn(a, scale=0.7) for a in agentes],
                              lag_ratio=0.2), run_time=2)
        espec = Text("Cada agente hace una cosa bien, con su propio contexto",
                     font_size=20, color=GREY_B).to_edge(DOWN)
        self.play(FadeIn(espec), run_time=1)

        # Mensajes entre agentes
        mensajes = [
            (0, 1, "investiga X"), (1, 0, "hallazgos"),
            (0, 2, "implementa"), (2, 3, "¿revisas?"), (3, 2, "2 errores"),
        ]
        for de, a, texto in mensajes:
            flecha = Arrow(pos[de], pos[a], color=GREY_B, buff=0.55, stroke_width=3,
                           max_tip_length_to_length_ratio=0.12)
            t = Text(texto, font_size=14, color=WHITE)
            t.move_to(flecha.get_center() + UP * 0.22)
            self.play(GrowArrow(flecha), FadeIn(t), run_time=0.8)
            self.play(FadeOut(flecha), FadeOut(t), run_time=0.35)

        # Patrones de organizacion
        patrones = VGroup(
            Text("Patrones:", font_size=20, color=GOLD),
            Text("· jerárquico: un orquestador delega", font_size=18, color=GREY_B),
            Text("· debate: proponen y se critican", font_size=18, color=GREY_B),
            Text("· pipeline: cadena de especialistas", font_size=18, color=GREY_B),
            Text("· enjambre: paralelo + fusión", font_size=18, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        patrones.move_to(RIGHT * 3.7 + UP * 0.6)
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.3) for p in patrones],
                              lag_ratio=0.25), run_time=2.5)

        # Debate: dos agentes convergen a mejor respuesta
        debate = Text("El debate filtra errores que un agente solo no ve",
                      font_size=20, color=YELLOW).to_edge(DOWN)
        self.play(ReplacementTransform(espec, debate), run_time=1)
        r1 = Text("v1", font_size=18, color=BLUE_B).move_to(centro + UP * 0.15)
        r2 = Text("v2", font_size=18, color=YELLOW).move_to(centro + DOWN * 0.25)
        self.play(FadeIn(r1), run_time=0.6)
        self.play(FadeIn(r2), run_time=0.6)
        final = Text("v3 ✓", font_size=22, color=GOLD).move_to(centro)
        self.play(ReplacementTransform(VGroup(r1, r2), final), run_time=1)
        self.play(Flash(final, color=GOLD), run_time=0.8)

        # El costo
        cierre = Text("Más agentes = más coordinación: úsalos cuando la tarea de verdad se divide",
                      font_size=19, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(debate, cierre), run_time=1.2)
        self.wait(2)
