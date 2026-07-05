from manim import *
import numpy as np

# Constantes de escala para encuadre perfecto
R_EARTH = 1.0
ALT_LEO = 0.4   # Radio orbital total = 1.4
ALT_MEO = 2.4   # Radio orbital total = 3.4 (Cabe bien en pantalla)

VEL_LEO = 1.5
VEL_MEO = VEL_LEO * np.sqrt((R_EARTH + ALT_LEO)**3 / (R_EARTH + ALT_MEO)**3)

class OrbitLogicEp1V2(ThreeDScene):
    def construct(self):
        # ---------------------------------------------------------
        # 1. Configuración de Cámara y Branding
        # ---------------------------------------------------------
        logo = Text("Co.De Aerospace / Orbit-Logic", font_size=18, color=BLUE_B)
        self.add_fixed_in_frame_mobjects(logo)
        logo.to_corner(UL)

        # Posición inicial de la cámara
        self.set_camera_orientation(phi=65 * DEGREES, theta=-30 * DEGREES)

        # ---------------------------------------------------------
        # 2. El Campo de Vectores Gravitatorio (Sutil)
        # ---------------------------------------------------------
        def gravity_field(p):
            r_norm = np.linalg.norm(p)
            if r_norm < R_EARTH: return np.zeros(3)
            return -p / (r_norm**3)

        field = ArrowVectorField(
            gravity_field,
            x_range=[-4.5, 4.5, 1.0], # Aumentamos el paso (1.0) para menos flechas
            y_range=[-4.5, 4.5, 1.0],
            colors=[BLUE_E, BLUE_A],
            length_func=lambda norm: 0.4 * sigmoid(norm),
            opacity=0.2
        )
        self.add(field)

        # ---------------------------------------------------------
        # 3. Tierra, Órbitas y Satélites
        # ---------------------------------------------------------
        tierra = Sphere(radius=R_EARTH, resolution=(15, 30))
        tierra.set_color(BLUE_D).set_opacity(0.4).set_stroke(GREY_B, width=0.5)
        self.add(tierra)

        orbita_leo = ParametricFunction(
            lambda t: np.array([(R_EARTH + ALT_LEO) * np.cos(t), (R_EARTH + ALT_LEO) * np.sin(t), 0]),
            t_range=[0, TAU], color=GOLD, stroke_opacity=0.4
        )

        inc = 30 * DEGREES # Inclinación moderada para evitar que MEO salga de cuadro
        orbita_meo = ParametricFunction(
            lambda t: np.array([
                (R_EARTH + ALT_MEO) * np.cos(t),
                (R_EARTH + ALT_MEO) * np.sin(t) * np.cos(inc),
                (R_EARTH + ALT_MEO) * np.sin(t) * np.sin(inc)
            ]),
            t_range=[0, TAU], color=RED, stroke_opacity=0.4
        )

        self.play(Create(orbita_leo), Create(orbita_meo))

        tiempo = ValueTracker(0)

        sat_leo = always_redraw(lambda: Dot3D(radius=0.07, color=GOLD).move_to(
            orbita_leo.function(tiempo.get_value() * VEL_LEO % TAU)
        ))
        sat_meo = always_redraw(lambda: Dot3D(radius=0.09, color=RED).move_to(
            orbita_meo.function(tiempo.get_value() * VEL_MEO % TAU)
        ))

        # ---------------------------------------------------------
        # 4. UI Fixed
        # ---------------------------------------------------------
        titulo = Text("Mecánica Orbital: LEO vs MEO", font_size=28).to_edge(UP)
        ecuacion = MathTex(r"\vec{F}_g = -G \frac{Mm}{r^2} \hat{r}", font_size=30).to_corner(DL)
        self.add_fixed_in_frame_mobjects(titulo, ecuacion)

        # ---------------------------------------------------------
        # 5. Animación Combinada (Cámara + Objetos)
        # ---------------------------------------------------------
        self.play(Write(titulo), FadeIn(sat_leo, sat_meo, ecuacion))

        # EXPLICACIÓN: move_camera ejecuta la animación de la cámara.
        # added_anims permite que el satélite se mueva AL MISMO TIEMPO.
        self.move_camera(
            phi=75 * DEGREES,   # Nueva inclinación
            theta=45 * DEGREES,  # Nueva rotación
            run_time=15,
            rate_func=linear,
            added_anims=[
                tiempo.animate.set_value(TAU * 2.5) # Movimiento de los satélites
            ]
        )

        self.wait(2)