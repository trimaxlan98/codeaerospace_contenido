from manim import *
import numpy as np


class ApuntamientoDeAntenasGeo(Scene):
    def construct(self):
        titulo = Text("Apuntamiento de antenas a GEO", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Tierra y cinturon geoestacionario
        centro = DOWN * 1.2 + LEFT * 2.8
        tierra = Circle(radius=1.0, color=BLUE_D, fill_opacity=1, fill_color=BLUE_D)
        tierra.move_to(centro)
        ecuador = DashedLine(centro + LEFT * 1.15, centro + RIGHT * 4.6, color=GREY_B)
        geo = Arc(radius=3.4, start_angle=-PI / 8, angle=PI / 3, color=GOLD,
                  arc_center=centro)
        geo_txt = Text("Cinturón GEO · 35 786 km", font_size=19, color=GOLD)
        geo_txt.next_to(geo, RIGHT, buff=0.2).shift(UP * 0.4)
        self.play(GrowFromCenter(tierra), Create(ecuador), run_time=1.2)
        self.play(Create(geo), FadeIn(geo_txt), run_time=1.5)

        # El satelite GEO parece clavado en el cielo
        sat = Dot(centro + 3.4 * np.array([np.cos(PI / 8), np.sin(PI / 8), 0]),
                  color=GOLD, radius=0.11)
        fijo = Text("Gira con la Tierra: visto desde el suelo, no se mueve",
                    font_size=21, color=GREY_B).to_edge(DOWN)
        self.play(FadeIn(sat), FadeIn(fijo), run_time=1)
        self.play(Rotate(VGroup(tierra, sat), angle=PI / 10, about_point=centro),
                  run_time=2.5, rate_func=there_and_back)

        # Antena en una latitud media
        lat = PI / 3.2
        punto_ant = centro + 1.0 * np.array([np.cos(lat), np.sin(lat), 0])
        antena = Triangle(color=BLUE_B, fill_opacity=1, fill_color=BLUE_B).scale(0.16)
        antena.move_to(punto_ant + 0.14 * np.array([np.cos(lat), np.sin(lat), 0]))
        ant_txt = Text("Tu antena", font_size=19, color=BLUE_B)
        ant_txt.next_to(antena, UP, buff=0.35).shift(LEFT * 0.9)
        self.play(FadeIn(antena), FadeIn(ant_txt), run_time=1)

        # Linea de vista y angulos de instalacion
        vista = Line(antena.get_center(), sat.get_center(), color=YELLOW)
        local = DashedLine(antena.get_center(),
                           antena.get_center() + 1.7 * np.array(
                               [np.cos(lat), np.sin(lat), 0]), color=GREY_B)
        self.play(Create(vista), Create(local), run_time=1.5)
        elev = Angle(Line(antena.get_center(), antena.get_center() + RIGHT * 2),
                     vista, radius=0.55, color=YELLOW)
        elev_txt = Text("elevación", font_size=18, color=YELLOW)
        elev_txt.next_to(elev, RIGHT, buff=0.12).shift(UP * 0.1)
        self.play(Create(elev), FadeIn(elev_txt), run_time=1.2)

        pasos = VGroup(
            Text("Con tu latitud y la longitud del satélite se calculan:",
                 font_size=20, color=GREY_B),
            Text("azimut (rumbo), elevación (altura) y polarización (giro del LNB)",
                 font_size=20, color=YELLOW),
        ).arrange(DOWN, buff=0.15).to_edge(DOWN)
        self.play(ReplacementTransform(fijo, pasos), run_time=1.3)

        # Ajuste fino: maximizar la senal
        barra_fondo = Rectangle(width=2.6, height=0.3, color=GREY_B)
        barra_fondo.to_corner(UR).shift(DOWN * 1.0 + LEFT * 0.3)
        s = ValueTracker(0.35)
        barra = always_redraw(lambda: Rectangle(
            width=max(2.6 * s.get_value(), 0.01), height=0.3, color=YELLOW,
            fill_opacity=1, fill_color=YELLOW,
        ).align_to(barra_fondo, LEFT).align_to(barra_fondo, DOWN))
        senal_txt = Text("Señal", font_size=18, color=GREY_B)
        senal_txt.next_to(barra_fondo, UP, buff=0.15)
        self.play(Create(barra_fondo), FadeIn(senal_txt), run_time=0.8)
        self.add(barra)
        self.play(Rotate(antena, angle=PI / 40), s.animate.set_value(0.6), run_time=1.2)
        self.play(Rotate(antena, angle=-PI / 60), s.animate.set_value(0.97), run_time=1.2)
        self.play(Flash(barra_fondo.get_right(), color=YELLOW), run_time=0.8)

        cierre = Text("Una vez alineada, queda fija: esa es la gran ventaja de GEO",
                      font_size=21, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(pasos, cierre), run_time=1.2)
        self.wait(2)
