from manim import *


class ProtocolosEInteroperabilidad(Scene):
    def construct(self):
        titulo = Text("Protocolos e interoperabilidad (MCP y más)",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # El problema N x M: cada app integra cada servicio a mano
        apps = VGroup(*[
            VGroup(RoundedRectangle(width=1.5, height=0.55, corner_radius=0.1,
                                    color=BLUE_B, fill_opacity=0.12, fill_color=BLUE_B),
                   Text(n, font_size=15, color=BLUE_B))
            for n in ["app IA 1", "app IA 2", "app IA 3"]
        ])
        for a in apps:
            a[1].move_to(a[0])
        apps.arrange(DOWN, buff=0.5).move_to(LEFT * 4.8 + DOWN * 0.5)
        servicios = VGroup(*[
            VGroup(RoundedRectangle(width=1.5, height=0.55, corner_radius=0.1,
                                    color=GOLD, fill_opacity=0.12, fill_color=GOLD),
                   Text(n, font_size=15, color=GOLD))
            for n in ["GitHub", "base datos", "Slack"]
        ])
        for s in servicios:
            s[1].move_to(s[0])
        servicios.arrange(DOWN, buff=0.5).move_to(LEFT * 0.9 + DOWN * 0.5)
        self.play(FadeIn(apps, lag_ratio=0.15), FadeIn(servicios, lag_ratio=0.15),
                  run_time=1.8)

        cables = VGroup(*[
            Line(a.get_right(), s.get_left(), color=RED_D, stroke_width=2,
                 stroke_opacity=0.7)
            for a in apps for s in servicios
        ])
        problema = Text("Sin estándar: 3×3 = 9 integraciones distintas que mantener",
                        font_size=20, color=RED_D).to_edge(DOWN)
        self.play(Create(cables), FadeIn(problema), run_time=2)
        self.play(Wiggle(cables), run_time=1.2)

        # Con protocolo: N + M
        solucion = Text("Con un protocolo (MCP): cada pieza se conecta una sola vez",
                        font_size=20, color=YELLOW).to_edge(DOWN)
        bus = Rectangle(width=0.5, height=3.2, color=YELLOW, fill_opacity=0.15,
                        fill_color=YELLOW).move_to(RIGHT * 3.0 + DOWN * 0.5)
        bus_txt = Text("MCP", font_size=19, color=YELLOW).move_to(bus)
        self.play(ReplacementTransform(problema, solucion), FadeOut(cables),
                  run_time=1.2)
        apps2 = apps.copy().move_to(RIGHT * 1.2 + DOWN * 0.5)
        servicios2 = servicios.copy().move_to(RIGHT * 5.0 + DOWN * 0.5)
        self.play(Transform(apps, apps2), Transform(servicios, servicios2),
                  FadeIn(bus), FadeIn(bus_txt), run_time=1.5)
        conexiones = VGroup(*[
            Line(a.get_right(), [bus.get_left()[0], a.get_center()[1], 0],
                 color=BLUE_B, stroke_width=3)
            for a in apps
        ] + [
            Line([bus.get_right()[0], s.get_center()[1], 0], s.get_left(),
                 color=GOLD, stroke_width=3)
            for s in servicios
        ])
        self.play(Create(conexiones), run_time=1.5)
        cuenta = Text("3 + 3 = 6 conexiones, y todas hablan igual",
                      font_size=19, color=YELLOW)
        cuenta.move_to(UP * 1.8 + RIGHT * 3.0)
        self.play(FadeIn(cuenta), run_time=1)

        # Que expone un servidor MCP
        expone = VGroup(
            Text("Un servidor MCP expone:", font_size=19, color=GREY_B),
            Text("herramientas · recursos · plantillas", font_size=19, color=GOLD),
        ).arrange(DOWN, buff=0.12).move_to(LEFT * 3.9 + UP * 1.8)
        self.play(FadeIn(expone), run_time=1.2)

        # Un mensaje viaja por el protocolo
        msg = Dot(apps[0].get_right(), color=WHITE, radius=0.07)
        self.play(FadeIn(msg), run_time=0.3)
        self.play(msg.animate.move_to(bus.get_center()), run_time=0.7)
        self.play(msg.animate.move_to(servicios[0].get_left()), run_time=0.7)
        self.play(Flash(servicios[0], color=GOLD), FadeOut(msg), run_time=0.8)

        cierre = Text("Los protocolos hacen por los agentes lo que HTTP hizo por la web",
                      font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(solucion, cierre), run_time=1.2)
        self.wait(2)
