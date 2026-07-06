from manim import *
import numpy as np


class MegaconstelacionesLEO(Scene):
    def construct(self):
        titulo = Text("Megaconstelaciones LEO", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        centro = DOWN * 0.4 + LEFT * 3
        tierra = Circle(radius=0.8, color=BLUE_D, fill_opacity=1, fill_color=BLUE_D)
        tierra.move_to(centro)
        self.play(GrowFromCenter(tierra), run_time=1)

        # Un satelite GEO no da baja latencia; muchos LEO si
        idea = Text("Un GEO cubre mucho pero lejos;\nmuchos LEO cubren cerca",
                    font_size=21, color=GREY_B, line_spacing=0.9)
        idea.move_to(RIGHT * 3.6 + UP * 1.8)
        self.play(FadeIn(idea), run_time=1.2)

        # Varios planos orbitales inclinados con satelites
        planos = VGroup()
        sats = VGroup()
        angulos = [0, PI / 5, 2 * PI / 5, 3 * PI / 5, 4 * PI / 5]
        for ang in angulos:
            plano = Ellipse(width=4.4, height=1.7, color=GREY_B, stroke_opacity=0.5)
            plano.move_to(centro).rotate(ang, about_point=centro)
            planos.add(plano)
            for p in np.linspace(0, 1, 4, endpoint=False):
                sats.add(Dot(plano.point_from_proportion(p), color=BLUE_B, radius=0.055))
        self.play(LaggedStart(*[Create(p) for p in planos], lag_ratio=0.2), run_time=3)
        self.play(FadeIn(sats, lag_ratio=0.05), run_time=1.5)
        n_txt = VGroup(Text("Satélites:", font_size=20, color=GREY_B),
                       Integer(20, font_size=28, color=YELLOW)).arrange(RIGHT, buff=0.2)
        n_txt.move_to(RIGHT * 3.6 + UP * 0.7)
        self.play(FadeIn(n_txt), run_time=0.8)

        # Usuario en tierra con handover entre satelites que pasan
        usuario = Triangle(color=YELLOW, fill_opacity=1, fill_color=YELLOW).scale(0.18)
        usuario.move_to(centro + DOWN * 1.0)
        self.play(FadeIn(usuario), run_time=0.5)

        objetivo1 = sats[2]
        objetivo2 = sats[6]
        objetivo3 = sats[10]
        enlace = Line(usuario.get_top(), objetivo1.get_center(), color=YELLOW)
        handover = Text("Handover: el enlace salta al satélite más cercano",
                        font_size=21, color=YELLOW).to_edge(DOWN)
        self.play(Create(enlace), FadeIn(handover), run_time=1.2)
        for objetivo in [objetivo2, objetivo3]:
            self.play(Transform(
                enlace, Line(usuario.get_top(), objetivo.get_center(), color=YELLOW)),
                run_time=1.4)
            self.play(Flash(objetivo, color=YELLOW, flash_radius=0.25), run_time=0.6)

        # Enlaces laser entre satelites
        isl = VGroup(
            DashedLine(sats[2].get_center(), sats[6].get_center(), color=GOLD),
            DashedLine(sats[6].get_center(), sats[10].get_center(), color=GOLD),
            DashedLine(sats[10].get_center(), sats[14].get_center(), color=GOLD),
        )
        isl_txt = Text("Enlaces láser entre satélites:\nla red viaja por el espacio",
                       font_size=21, color=GOLD, line_spacing=0.9)
        isl_txt.move_to(RIGHT * 3.6 + DOWN * 0.6)
        self.play(Create(isl), FadeIn(isl_txt), run_time=2)

        cierre = Text("Miles de satélites coordinados actúan como una sola red global",
                      font_size=22, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(handover, cierre), run_time=1.2)
        self.wait(2)
