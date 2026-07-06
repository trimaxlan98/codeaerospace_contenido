from manim import *
import numpy as np


class SeguimientoDesdeEstacionesTerrenas(Scene):
    def construct(self):
        titulo = Text("Seguimiento desde estaciones terrenas",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Antena parabolica orientable
        base = Rectangle(width=0.35, height=0.9, color=GREY_B, fill_opacity=0.6,
                         fill_color=GREY_B).move_to(DOWN * 2.6 + LEFT * 2.5)
        plato = Arc(radius=0.55, start_angle=PI * 0.75, angle=PI * 0.5, color=BLUE_B,
                    stroke_width=10)
        plato.move_to(base.get_top() + UP * 0.25)
        antena = VGroup(base, plato)
        suelo = Line(LEFT * 7, RIGHT * 7, color=GREY_B).move_to(DOWN * 3.1)
        self.play(Create(suelo), FadeIn(antena), run_time=1.5)

        # Trayectoria del pase LEO
        paso = ArcBetweenPoints(LEFT * 6.5 + DOWN * 2.9, RIGHT * 6.5 + DOWN * 2.9,
                                angle=-PI / 2.2, color=GREY_B)
        self.play(Create(DashedVMobject(paso, num_dashes=35)), run_time=1.5)
        sat = Dot(paso.point_from_proportion(0), color=GOLD, radius=0.1)
        sat_txt = Text("Satélite LEO: cruza el cielo en ~10 min",
                       font_size=20, color=GOLD).to_edge(DOWN)
        self.play(FadeIn(sat), FadeIn(sat_txt), run_time=1)

        # La antena sigue al satelite; lectura de azimut/elevacion
        p = ValueTracker(0.0)
        sat.add_updater(lambda m: m.move_to(paso.point_from_proportion(p.get_value())))
        haz = always_redraw(lambda: Line(
            plato.get_center(), sat.get_center(), color=YELLOW, stroke_opacity=0.8))

        def elevacion():
            v = sat.get_center() - plato.get_center()
            return max(np.degrees(np.arctan2(v[1], abs(v[0]) + 1e-9)), 0)

        lectura = always_redraw(lambda: VGroup(
            Text("El:", font_size=22, color=YELLOW),
            DecimalNumber(elevacion(), num_decimal_places=0, font_size=26, color=YELLOW),
            Text("°", font_size=22, color=YELLOW),
        ).arrange(RIGHT, buff=0.08).to_corner(UR).shift(DOWN * 0.9 + LEFT * 0.5))
        self.add(haz, lectura)

        # el plato rota para mirar al satelite
        plato.add_updater(lambda m: m.become(
            Arc(radius=0.55,
                start_angle=np.arctan2(*(sat.get_center() - base.get_top() - UP * 0.25)[[1, 0]]) + PI * 0.75,
                angle=PI * 0.5, color=BLUE_B, stroke_width=10,
                arc_center=base.get_top() + UP * 0.25)))

        self.play(p.animate.set_value(1.0), run_time=8, rate_func=smooth)
        sat.clear_updaters()
        plato.clear_updaters()

        # Ventanas de contacto: solo unos minutos por orbita
        linea = NumberLine(x_range=[0, 12, 3], length=6, color=GREY_B,
                           include_numbers=False).move_to(UP * 1.8 + RIGHT * 2)
        linea_txt = Text("24 horas", font_size=18, color=GREY_B)
        linea_txt.next_to(linea, DOWN, buff=0.2)
        ventanas = VGroup(*[
            Rectangle(width=0.35, height=0.3, color=GOLD, fill_opacity=0.8,
                      fill_color=GOLD).move_to(linea.number_to_point(x))
            for x in [1.2, 4.1, 6.9, 9.8]
        ])
        vent_txt = Text("Ventanas de contacto: minutos, varias veces al día",
                        font_size=20, color=GOLD).to_edge(DOWN)
        self.play(Create(linea), FadeIn(linea_txt), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(v, scale=1.6) for v in ventanas], lag_ratio=0.25),
                  ReplacementTransform(sat_txt, vent_txt), run_time=2)
        self.wait(2)
