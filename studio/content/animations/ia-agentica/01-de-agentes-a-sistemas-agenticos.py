from manim import *


class DeAgentesASistemasAgenticos(Scene):
    def construct(self):
        titulo = Text("De agentes a sistemas agénticos", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Nivel 1: un agente con una herramienta
        n1_txt = Text("Nivel 1: un agente, una tarea", font_size=20, color=GREY_B)
        n1_txt.move_to(LEFT * 4.2 + UP * 2.0)
        agente = VGroup(
            Circle(radius=0.4, color=BLUE_B, fill_opacity=0.15, fill_color=BLUE_B),
            Text("A", font_size=22, color=BLUE_B),
        ).move_to(LEFT * 5.0 + UP * 0.7)
        herr = Square(side_length=0.45, color=GREY_B).move_to(LEFT * 3.4 + UP * 0.7)
        h_txt = Text("tool", font_size=14, color=GREY_B).move_to(herr)
        union = Line(agente.get_right(), herr.get_left(), color=GREY_B)
        self.play(FadeIn(n1_txt), FadeIn(agente), Create(union), FadeIn(herr),
                  FadeIn(h_txt), run_time=1.8)

        # Nivel 2: pipeline con varios pasos y validaciones
        n2_txt = Text("Nivel 2: flujo con pasos, herramientas y verificación",
                      font_size=20, color=BLUE_B).move_to(LEFT * 2.4 + DOWN * 0.4)
        pasos = VGroup()
        for i, (nombre, color) in enumerate([("planear", YELLOW), ("ejecutar", BLUE_B),
                                             ("verificar", GOLD)]):
            p = VGroup(
                RoundedRectangle(width=1.8, height=0.55, corner_radius=0.1,
                                 color=color, fill_opacity=0.12, fill_color=color),
                Text(nombre, font_size=16, color=color),
            )
            p[1].move_to(p[0])
            p.move_to(LEFT * 4.6 + RIGHT * i * 2.2 + DOWN * 1.5)
            pasos.add(p)
        flechas = VGroup(*[
            Arrow(pasos[i].get_right(), pasos[i + 1].get_left(), color=GREY_B,
                  buff=0.08, stroke_width=3) for i in range(2)
        ])
        retro = CurvedArrow(pasos[2].get_bottom(), pasos[0].get_bottom(),
                            angle=PI / 3, color=RED_D, stroke_width=3)
        retro_txt = Text("falla → replanea", font_size=14, color=RED_D)
        retro_txt.next_to(retro, DOWN, buff=0.08)
        self.play(FadeIn(n2_txt), FadeIn(pasos, lag_ratio=0.2),
                  *[GrowArrow(f) for f in flechas], run_time=2)
        self.play(Create(retro), FadeIn(retro_txt), run_time=1.2)

        # Nivel 3: sistema agentico — varios agentes + humano + politicas
        n3_txt = Text("Nivel 3: sistema agéntico", font_size=21, color=GOLD)
        n3_txt.move_to(RIGHT * 3.8 + UP * 2.0)
        orq = VGroup(
            RoundedRectangle(width=2.2, height=0.6, corner_radius=0.1, color=GOLD,
                             fill_opacity=0.15, fill_color=GOLD),
            Text("orquestador", font_size=16, color=GOLD),
        )
        orq[1].move_to(orq[0])
        orq.move_to(RIGHT * 3.8 + UP * 1.1)
        sub = VGroup()
        for i, nombre in enumerate(["investiga", "codifica", "revisa"]):
            s = VGroup(
                Circle(radius=0.33, color=BLUE_B, fill_opacity=0.12, fill_color=BLUE_B),
                Text(nombre, font_size=12, color=BLUE_B),
            )
            s[1].move_to(s[0])
            s.move_to(RIGHT * (2.4 + i * 1.5) + DOWN * 0.4)
            sub.add(s)
        lineas = VGroup(*[
            Line(orq.get_bottom(), s.get_top(), color=GREY_B, stroke_width=2)
            for s in sub
        ])
        humano = VGroup(
            Circle(radius=0.16, color=YELLOW).shift(UP * 0.25),
            Line(DOWN * 0.35, UP * 0.08, color=YELLOW),
        ).move_to(RIGHT * 5.9 + UP * 1.1)
        hum_txt = Text("humano\naprueba", font_size=13, color=YELLOW, line_spacing=0.8)
        hum_txt.next_to(humano, DOWN, buff=0.12)
        aprobacion = DashedLine(orq.get_right(), humano.get_left() + LEFT * 0.05,
                                color=YELLOW)
        self.play(FadeIn(n3_txt), FadeIn(orq), Create(lineas),
                  FadeIn(sub, lag_ratio=0.2), run_time=2)
        self.play(FadeIn(humano), FadeIn(hum_txt), Create(aprobacion), run_time=1.3)

        # Trabajo en paralelo
        pulsos = VGroup(*[Dot(orq.get_bottom(), color=GOLD, radius=0.06)
                          for _ in sub])
        self.add(pulsos)
        self.play(*[p.animate.move_to(s.get_top()) for p, s in zip(pulsos, sub)],
                  run_time=1)
        self.play(FadeOut(pulsos), *[Flash(s, color=BLUE_B, flash_radius=0.4)
                                     for s in sub], run_time=1)

        cierre = Text("Agéntico: autonomía delegada con límites, verificación y supervisión",
                      font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
