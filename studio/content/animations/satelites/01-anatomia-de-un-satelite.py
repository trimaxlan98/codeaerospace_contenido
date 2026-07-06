from manim import *


class AnatomiaDeUnSatelite(Scene):
    def construct(self):
        titulo = Text("Anatomía de un satélite", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Bus: la estructura que sostiene todo
        bus = Rectangle(width=1.6, height=1.6, color=GREY_B,
                        fill_opacity=0.15, fill_color=GREY_B).shift(DOWN * 0.4)
        bus_txt = Text("Bus (estructura)", font_size=20, color=GREY_B)
        bus_txt.next_to(bus, DOWN, buff=0.25)
        self.play(Create(bus), FadeIn(bus_txt), run_time=1.5)

        def etiqueta(texto, objeto, direccion, color):
            t = Text(texto, font_size=19, color=color)
            t.next_to(objeto, direccion, buff=0.5)
            flecha = Arrow(t.get_edge_center(-direccion), objeto.get_edge_center(direccion),
                           buff=0.08, color=color, stroke_width=3,
                           max_tip_length_to_length_ratio=0.15)
            return VGroup(t, flecha)

        # Paneles solares: energia
        panel_izq = Rectangle(width=1.8, height=0.9, color=BLUE_D,
                              fill_opacity=0.7, fill_color=BLUE_D)
        panel_izq.next_to(bus, LEFT, buff=0.15)
        panel_der = panel_izq.copy().next_to(bus, RIGHT, buff=0.15)
        e1 = etiqueta("Paneles solares: energía", panel_der, UR * 0.7 + RIGHT, BLUE_B)
        self.play(FadeIn(panel_izq, shift=RIGHT * 0.3),
                  FadeIn(panel_der, shift=LEFT * 0.3), run_time=1.2)
        self.play(FadeIn(e1), run_time=1)

        # Antena: comunicaciones
        antena = VGroup(
            Line(bus.get_top(), bus.get_top() + UP * 0.5, color=GOLD),
            Arc(radius=0.35, start_angle=PI, angle=PI, color=GOLD)
            .move_to(bus.get_top() + UP * 0.7),
        )
        e2 = etiqueta("Antena: comunicaciones", antena, UP + RIGHT * 2, GOLD)
        self.play(Create(antena), run_time=1)
        self.play(FadeIn(e2), run_time=1)

        # Computadora de a bordo
        obc = Square(side_length=0.45, color=YELLOW).move_to(bus.get_center() + UP * 0.35)
        e3 = etiqueta("Computadora de a bordo", obc, LEFT * 2.6 + UP, YELLOW)
        self.play(Create(obc), FadeIn(e3), run_time=1.5)

        # Propulsion
        tobera = Triangle(color=RED_D, fill_opacity=0.8, fill_color=RED_D)
        tobera.stretch_to_fit_width(0.4).stretch_to_fit_height(0.35)
        tobera.rotate(PI).next_to(bus, DOWN, buff=0.02).shift(RIGHT * 0.45)
        e4 = etiqueta("Propulsión: mantener la órbita", tobera, DR + RIGHT, RED_D)
        self.play(FadeIn(tobera), FadeIn(e4), run_time=1.5)

        # Sensores / carga util
        sensor = Circle(radius=0.18, color=BLUE_B).move_to(bus.get_center() + DOWN * 0.35)
        e5 = etiqueta("Carga útil: la razón de la misión", sensor, LEFT * 2.6 + DOWN, BLUE_B)
        self.play(Create(sensor), FadeIn(e5), run_time=1.5)
        self.play(Circumscribe(sensor, color=BLUE_B), run_time=1)

        # Todo funciona como un sistema
        sat = VGroup(bus, panel_izq, panel_der, antena, obc, tobera, sensor)
        cierre = Text("Subsistemas al servicio de una carga útil",
                      font_size=24, color=GOLD).to_edge(DOWN)
        self.play(FadeOut(VGroup(e1, e2, e3, e4, e5, bus_txt)), run_time=1)
        self.play(Rotate(sat, angle=PI / 12), FadeIn(cierre), run_time=1.5)
        self.play(Rotate(sat, angle=-PI / 6), run_time=2)
        self.wait(2)
