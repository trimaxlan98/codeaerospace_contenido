from manim import *
import numpy as np


class GeometriaDeApuntamiento(Scene):
    def construct(self):
        titulo = Text("Geometría de apuntamiento", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Estacion sobre la superficie y su horizonte local
        estacion = Dot(DOWN * 2.2 + LEFT * 1.5, color=BLUE_B, radius=0.1)
        est_txt = Text("Estación terrena", font_size=20, color=BLUE_B)
        est_txt.next_to(estacion, DOWN, buff=0.25)
        horizonte = Line(estacion.get_center() + LEFT * 4.5,
                         estacion.get_center() + RIGHT * 5.5, color=GREY_B)
        hor_txt = Text("Horizonte local", font_size=18, color=GREY_B)
        hor_txt.next_to(horizonte, DOWN, buff=0.15).shift(RIGHT * 3.5)
        self.play(FadeIn(estacion), Create(horizonte), FadeIn(est_txt), FadeIn(hor_txt),
                  run_time=1.5)

        # Satelite pasando: trayectoria en el cielo
        paso = ArcBetweenPoints(
            estacion.get_center() + LEFT * 4 + UP * 0.7,
            estacion.get_center() + RIGHT * 5 + UP * 0.9,
            angle=-PI / 3, color=GREY_B,
        )
        sat = Dot(paso.point_from_proportion(0), color=GOLD, radius=0.1)
        self.play(Create(DashedVMobject(paso, num_dashes=30)), FadeIn(sat), run_time=1.5)

        # Linea de vista, rango y elevacion en vivo
        p = ValueTracker(0.0)
        sat.add_updater(lambda m: m.move_to(paso.point_from_proportion(p.get_value())))
        vista = always_redraw(lambda: Line(
            estacion.get_center(), sat.get_center(), color=YELLOW))

        def elev():
            v = sat.get_center() - estacion.get_center()
            return np.degrees(np.arctan2(v[1], abs(v[0]) + 1e-9))

        lectura = always_redraw(lambda: VGroup(
            Text("Elevación: ", font_size=22, color=YELLOW),
            DecimalNumber(elev(), num_decimal_places=0, font_size=28, color=YELLOW),
            MathTex(r"^\circ", font_size=28, color=YELLOW),
        ).arrange(RIGHT, buff=0.08).to_corner(UR).shift(DOWN * 0.9 + LEFT * 0.4))
        angulo = always_redraw(lambda: Angle(
            Line(estacion.get_center(), estacion.get_center() + RIGHT),
            Line(estacion.get_center(), sat.get_center()),
            radius=0.7, color=YELLOW,
        ) if sat.get_center()[0] > estacion.get_center()[0] + 0.1 else VMobject())
        self.add(vista, lectura, angulo)

        etiquetas = VGroup(
            Text("Elevación: altura sobre el horizonte", font_size=21, color=YELLOW),
            Text("Azimut: rumbo sobre el plano local", font_size=21, color=BLUE_B),
            Text("Rango: distancia en línea de vista", font_size=21, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(DOWN)
        self.play(FadeIn(etiquetas), run_time=1.2)

        # El pase: elevacion sube, culmina y baja
        self.play(p.animate.set_value(0.5), run_time=3.5, rate_func=smooth)
        culmina = Text("Culminación: máxima elevación", font_size=20, color=GOLD)
        culmina.next_to(sat, UP, buff=0.3)
        self.play(FadeIn(culmina), run_time=0.8)
        self.play(FadeOut(culmina), p.animate.set_value(1.0), run_time=3.5,
                  rate_func=smooth)
        sat.clear_updaters()

        # Mascara de elevacion minima
        mascara = Line(estacion.get_center(),
                       estacion.get_center() + 5 * np.array([np.cos(PI / 18), np.sin(PI / 18), 0]),
                       color=RED_D)
        masc_txt = Text("Elevación mínima (~10°): debajo, la atmósfera y los obstáculos degradan el enlace",
                        font_size=19, color=RED_D).to_edge(DOWN)
        self.play(Create(mascara), ReplacementTransform(etiquetas, masc_txt), run_time=1.5)
        self.wait(2)
