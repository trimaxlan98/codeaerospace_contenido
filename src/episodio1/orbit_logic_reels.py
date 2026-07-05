from manim import *
import numpy as np

# Configuración de escala para formato vertical 9:16
R_EARTH = 0.8
ALT_LEO = 0.4   # Radio total = 1.2
ALT_MEO = 1.8   # Radio total = 2.6 (Cabe justo en el ancho de un Reel)

VEL_LEO = 1.5
VEL_MEO = VEL_LEO * np.sqrt((R_EARTH + ALT_LEO)**3 / (R_EARTH + ALT_MEO)**3)

class OrbitLogicEp1Reels(ThreeDScene):
    def construct(self):
        # ---------------------------------------------------------
        # 1. Branding Co.De Aerospace (Abajo Derecha)
        # ---------------------------------------------------------
        logo = Text("Co.De Aerospace / Orbit-Logic", font_size=20, color=BLUE_B)
        self.add_fixed_in_frame_mobjects(logo)
        logo.to_corner(DR, buff=0.5)

        # 2. Configuración de Cámara Inicial
        self.set_camera_orientation(phi=65 * DEGREES, theta=-35 * DEGREES)

        # 3. Tierra y Órbitas
        tierra = Sphere(radius=R_EARTH, resolution=(15, 30))
        tierra.set_color(BLUE_D).set_opacity(0.4).set_stroke(GREY_B, width=0.5)
        self.add(tierra)

        orbita_leo = ParametricFunction(
            lambda t: np.array([(R_EARTH + ALT_LEO) * np.cos(t), (R_EARTH + ALT_LEO) * np.sin(t), 0]),
            t_range=[0, TAU], color=GOLD, stroke_opacity=0.3
        )

        inc = 25 * DEGREES
        orbita_meo = ParametricFunction(
            lambda t: np.array([
                (R_EARTH + ALT_MEO) * np.cos(t),
                (R_EARTH + ALT_MEO) * np.sin(t) * np.cos(inc),
                (R_EARTH + ALT_MEO) * np.sin(t) * np.sin(inc)
            ]),
            t_range=[0, TAU], color=RED, stroke_opacity=0.3
        )
        self.add(orbita_leo, orbita_meo)

        # ---------------------------------------------------------
        # 4. Satélites y Etiquetas (Labels)
        # ---------------------------------------------------------
        tiempo = ValueTracker(0)

        # Satélites
        sat_leo = always_redraw(lambda: Dot3D(radius=0.08, color=GOLD).move_to(
            orbita_leo.function(tiempo.get_value() * VEL_LEO % TAU)
        ))
        sat_meo = always_redraw(lambda: Dot3D(radius=0.1, color=RED).move_to(
            orbita_meo.function(tiempo.get_value() * VEL_MEO % TAU)
        ))

        # ETIQUETAS: Las movemos en el espacio 3D junto al satélite.
        # Para que no se vean "acostadas", NO las agregamos a fixed_in_frame,
        # sino que las dejamos en la escena 3D.
        label_leo = always_redraw(lambda:
            Text("LEO", font_size=20, color=GOLD)
            .move_to(sat_leo.get_center() + [0, 0, 0.3]) # Un poco arriba en Z
        )

        label_meo = always_redraw(lambda:
            Text("MEO", font_size=20, color=RED)
            .move_to(sat_meo.get_center() + [0, 0, 0.4])
        )

        self.add(sat_leo, sat_meo, label_leo, label_meo)

        # 5. Título y Ecuación (HUD 2D)
        titulo = Text("Mecánica Orbital:\nLEO vs MEO", font_size=36).to_edge(UP, buff=1)
        ecuacion = MathTex(r"v \approx \sqrt{\frac{GM}{r}}", font_size=32).to_edge(LEFT, buff=0.5).shift(DOWN*2)

        self.add_fixed_in_frame_mobjects(titulo, ecuacion)

        # ---------------------------------------------------------
        # 6. Animación Final
        # ---------------------------------------------------------
        self.play(Write(titulo), FadeIn(ecuacion))

        # Rotación de cámara y movimiento satelital coordinado
        self.move_camera(
            phi=75 * DEGREES,
            theta=20 * DEGREES,
            run_time=12,
            rate_func=linear,
            added_anims=[
                tiempo.animate.set_value(TAU * 2.0)
            ]
        )
        self.wait(2)