from manim import *


class SdnYVirtualizacionDeRed(Scene):
    def construct(self):
        titulo = Text("SDN y virtualización de red", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Antes: control distribuido en cada equipo
        antes = Text("Red clásica: cada equipo decide solo (control distribuido)",
                     font_size=21, color=GREY_B).to_edge(DOWN)
        switches = VGroup()
        posiciones = [LEFT * 4.2 + DOWN * 1.3, LEFT * 1.4 + DOWN * 1.9,
                      RIGHT * 1.4 + DOWN * 1.1, RIGHT * 4.2 + DOWN * 1.8]
        for p in posiciones:
            cuerpo = Rectangle(width=1.15, height=0.6, color=BLUE_D,
                               fill_opacity=0.2, fill_color=BLUE_D).move_to(p)
            cerebro = Circle(radius=0.13, color=YELLOW, fill_opacity=0.8,
                             fill_color=YELLOW).move_to(p + UP * 0.12)
            datos = Rectangle(width=0.85, height=0.16, color=GREY_B,
                              fill_opacity=0.5, fill_color=GREY_B).move_to(p + DOWN * 0.14)
            switches.add(VGroup(cuerpo, cerebro, datos))
        enlaces = VGroup(*[
            Line(posiciones[i], posiciones[i + 1], color=GREY_B, stroke_opacity=0.5,
                 z_index=-1)
            for i in range(3)
        ])
        self.play(FadeIn(antes), Create(enlaces),
                  LaggedStart(*[FadeIn(s) for s in switches], lag_ratio=0.15),
                  run_time=2.5)
        nota_cerebro = Text("control + datos juntos", font_size=17, color=YELLOW)
        nota_cerebro.next_to(switches[0], UP, buff=0.25)
        self.play(FadeIn(nota_cerebro), run_time=0.8)
        self.wait(0.5)

        # SDN: el control se extrae a un controlador central
        despues = Text("SDN: el plano de control se separa y centraliza",
                       font_size=21, color=GOLD).to_edge(DOWN)
        controlador = Rectangle(width=2.4, height=0.75, color=GOLD, fill_opacity=0.2,
                                fill_color=GOLD).move_to(UP * 1.7)
        ctrl_txt = Text("Controlador SDN", font_size=19, color=GOLD).move_to(controlador)
        self.play(ReplacementTransform(antes, despues), run_time=1)
        cerebros = VGroup(*[s[1] for s in switches])
        self.play(
            *[c.animate.move_to(controlador.get_center() + LEFT * 0.8 + RIGHT * 0.5 * i)
              for i, c in enumerate(cerebros)],
            FadeIn(controlador), FadeIn(ctrl_txt), FadeOut(nota_cerebro),
            run_time=2,
        )
        self.play(FadeOut(cerebros), run_time=0.6)

        # API southbound: reglas de flujo bajando a los switches
        flechas = VGroup(*[
            DashedLine(controlador.get_bottom(), s.get_top(), color=GOLD,
                       stroke_opacity=0.7)
            for s in switches
        ])
        regla = Text("regla: flujo video → puerto 2, prioridad alta",
                     font_size=18, color=YELLOW)
        regla.next_to(controlador, RIGHT, buff=0.4)
        self.play(Create(flechas), FadeIn(regla), run_time=1.8)
        pulsos = VGroup(*[Dot(controlador.get_bottom(), color=YELLOW, radius=0.06)
                          for _ in switches])
        self.add(pulsos)
        self.play(*[p.animate.move_to(s.get_top())
                    for p, s in zip(pulsos, switches)], run_time=1.2)
        self.play(FadeOut(pulsos), run_time=0.5)

        # Virtualizacion: varias redes logicas sobre el mismo hierro
        overlay1 = VMobject(color=BLUE_B).set_points_as_corners(
            [posiciones[0] + UP * 0.45, posiciones[1] + UP * 0.45,
             posiciones[2] + UP * 0.45])
        overlay2 = VMobject(color=RED_D).set_points_as_corners(
            [posiciones[1] + UP * 0.6, posiciones[2] + UP * 0.6,
             posiciones[3] + UP * 0.6])
        virt = Text("Virtualización: varias redes lógicas aisladas sobre la misma física",
                    font_size=20, color=BLUE_B).to_edge(DOWN)
        o1_txt = Text("red A", font_size=16, color=BLUE_B).next_to(overlay1, LEFT, buff=0.15)
        o2_txt = Text("red B", font_size=16, color=RED_D).next_to(overlay2, RIGHT, buff=0.15)
        self.play(ReplacementTransform(despues, virt), run_time=1)
        self.play(Create(overlay1), FadeIn(o1_txt), run_time=1.2)
        self.play(Create(overlay2), FadeIn(o2_txt), run_time=1.2)

        cierre = Text("La red se programa como software: la base de la nube y del 5G",
                      font_size=21, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(virt, cierre), run_time=1.2)
        self.wait(2)
