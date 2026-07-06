from manim import *
import numpy as np


class RedesNoTerrestresNtn(Scene):
    def construct(self):
        titulo = Text("Redes no terrestres (NTN) en 6G", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Suelo y usuario remoto
        suelo = Line(LEFT * 7, RIGHT * 7, color=GREY_B).move_to(DOWN * 3.1)
        ciudad = VGroup(*[
            Rectangle(width=0.35, height=h, color=GREY_B, fill_opacity=0.5,
                      fill_color=GREY_B).move_to(LEFT * (5.8 - i * 0.45) + DOWN * (3.1 - h / 2))
            for i, h in enumerate([0.7, 1.1, 0.9, 1.3])
        ])
        torre = Line(LEFT * 4.2 + DOWN * 3.1, LEFT * 4.2 + DOWN * 1.9, color=BLUE_B,
                     stroke_width=5)
        celda = Arc(radius=1.1, start_angle=PI / 6, angle=2 * PI / 3, color=BLUE_B,
                    arc_center=LEFT * 4.2 + DOWN * 1.9)
        usuario = Triangle(color=YELLOW, fill_opacity=1, fill_color=YELLOW).scale(0.15)
        usuario.move_to(RIGHT * 4.8 + DOWN * 2.9)
        usr_txt = Text("Zona remota: sin torres", font_size=18, color=YELLOW)
        usr_txt.next_to(usuario, UP, buff=0.25)
        self.play(Create(suelo), FadeIn(ciudad), Create(torre), Create(celda),
                  FadeIn(usuario), FadeIn(usr_txt), run_time=2.5)

        # Capas de la red no terrestre
        capas = [
            ("HAPS · 20 km\n(globos y drones estratosféricos)", UP * 0.0, GREY_B),
            ("LEO · 500-1200 km", UP * 1.1, BLUE_B),
            ("GEO · 35 786 km", UP * 2.1, GOLD),
        ]
        elementos = VGroup()
        for texto, y, color in capas:
            linea = DashedLine(LEFT * 6.8, RIGHT * 3.2, color=color,
                               stroke_opacity=0.4).shift(y)
            t = Text(texto, font_size=16, color=color, line_spacing=0.85)
            t.next_to(linea, RIGHT, buff=0.15).shift(y * 0)
            elementos.add(VGroup(linea, t))
        self.play(LaggedStart(*[FadeIn(e) for e in elementos], lag_ratio=0.3),
                  run_time=2.5)

        haps = Ellipse(width=0.5, height=0.22, color=GREY_B, fill_opacity=0.6,
                       fill_color=GREY_B).move_to(LEFT * 1.5 + UP * 0.0)
        leo = Dot(LEFT * 2.5 + UP * 1.1, color=BLUE_B, radius=0.1)
        geo = Dot(RIGHT * 0.5 + UP * 2.1, color=GOLD, radius=0.1)
        self.play(FadeIn(haps), FadeIn(leo), FadeIn(geo), run_time=1.2)

        # El usuario remoto se conecta directo al LEO
        enlace = Line(usuario.get_top(), leo.get_center(), color=YELLOW)
        conexion = Text("El teléfono se conecta directo al satélite: una celda que vuela",
                        font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(Create(enlace), FadeIn(conexion), run_time=1.5)
        self.play(Flash(usuario, color=YELLOW, flash_radius=0.4), run_time=0.8)

        # El LEO se mueve: la red conmuta a otro satelite o a HAPS
        leo2 = Dot(LEFT * 0.2 + UP * 1.1, color=BLUE_B, radius=0.1)
        self.play(leo.animate.shift(LEFT * 2.2), FadeIn(leo2), run_time=2)
        self.play(Transform(enlace, Line(usuario.get_top(), leo2.get_center(),
                                         color=YELLOW)), run_time=1.2)

        # Integracion: una sola red 3D
        malla = VGroup(
            DashedLine(leo2.get_center(), geo.get_center(), color=GREY_B,
                       stroke_opacity=0.7),
            DashedLine(leo2.get_center(), haps.get_center(), color=GREY_B,
                       stroke_opacity=0.7),
            DashedLine(haps.get_center(), torre.get_end(), color=GREY_B,
                       stroke_opacity=0.7),
        )
        integra = Text("6G integra tierra, estratosfera y órbita en una sola red 3D",
                       font_size=20, color=GOLD).to_edge(DOWN)
        self.play(Create(malla), ReplacementTransform(conexion, integra), run_time=2)
        self.wait(2)
