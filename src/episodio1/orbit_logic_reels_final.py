from manim import *
import numpy as np

# Optimized scales for 9:16 Vertical (Reels/TikTok)
R_EARTH = 0.8
ALT_LEO = 0.4   # Radio total = 1.2
ALT_MEO = 2.0   # Radio total = 2.8 (Utilizes vertical space efficiently)

VEL_LEO = 1.5
VEL_MEO = VEL_LEO * np.sqrt((R_EARTH + ALT_LEO)**3 / (R_EARTH + ALT_MEO)**3)

class OrbitLogicEp1ReelsFinal(ThreeDScene):
    def construct(self):
        # ---------------------------------------------------------
        # 1. Configuración de Cámara (Format: Vertical) y Branding
        # ---------------------------------------------------------
        # Logo Co.De Aerospace / Orbit-Logic Ep. 1 (Bottom Right, DR)
        logo = Text("Co.De Aerospace / Orbit-Logic Ep. 1", font_size=20, color=BLUE_B)
        self.add_fixed_in_frame_mobjects(logo)
        logo.to_corner(DR, buff=0.5)

        # Set initial orientation: Phi is adjusted to make the system
        # look tall and fill the full vertical column.
        self.set_camera_orientation(
            phi=72 * DEGREES, # Higher tilt to show system depth
            theta=-25 * DEGREES, # Light rotation
        )

        # ---------------------------------------------------------
        # 2. El Campo de Vectores Gravitatorio (Sutil Gravity Field)
        # ---------------------------------------------------------
        # This is the technical rigor that positions Co.De as experts.
        def gravity_field(p):
            r_norm = np.linalg.norm(p)
            if r_norm < R_EARTH: return np.zeros(3)
            return -p / (r_norm**3)

        field = ArrowVectorField(
            gravity_field,
            x_range=[-4, 4, 1.0], # Less horizontal range
            y_range=[-6, 6, 1.0], # More vertical range (9:16)
            colors=[BLUE_E, BLUE_A],
            length_func=lambda norm: 0.3 * sigmoid(norm),
            opacity=0.15
        )
        self.add(field)

        # ---------------------------------------------------------
        # 3. Tierra y Órbitas
        # ---------------------------------------------------------
        # Stylyzed Earth sphere with visible mesh
        tierra = Sphere(radius=R_EARTH, resolution=(15, 30))
        tierra.set_color(BLUE_D).set_opacity(0.4).set_stroke(GREY_B, width=0.5)
        self.add(tierra)

        orbita_leo = ParametricFunction(
            lambda t: np.array([(R_EARTH + ALT_LEO) * np.cos(t), (R_EARTH + ALT_LEO) * np.sin(t), 0]),
            t_range=[0, TAU], color=GOLD, stroke_opacity=0.3
        )

        # The MEO orbit is crucial for filling the height of the Reel.
        inc = 30 * DEGREES # Specific inclination for better framing
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
        # 4. Satélites y LABELS Legibles
        # ---------------------------------------------------------
        tiempo = ValueTracker(0)

        # Satellite dots (LEO dorada, MEO roja)
        sat_leo = always_redraw(lambda: Dot3D(radius=0.08, color=GOLD).move_to(
            orbita_leo.function(tiempo.get_value() * VEL_LEO % TAU)
        ))
        sat_meo = always_redraw(lambda: Dot3D(radius=0.1, color=RED).move_to(
            orbita_meo.function(tiempo.get_value() * VEL_MEO % TAU)
        ))

        # LABELS: We position them in the 3D scene but force them to float
        # directly over the satellites, which gives a clean "AR telemetría" look.
        label_leo = always_redraw(lambda:
            Text("LEO", font_size=20, color=GOLD)
            .move_to(sat_leo.get_center() + [0, 0, 0.3]) # Float over satellite
        )

        label_meo = always_redraw(lambda:
            Text("MEO", font_size=20, color=RED)
            .move_to(sat_meo.get_center() + [0, 0, 0.4])
        )

        self.add(sat_leo, sat_meo, label_leo, label_meo)

        # ---------------------------------------------------------
        # 5. UI Fixed (HUD 2D)
        # ---------------------------------------------------------
        # Title (Top UP) and Equation (Bottom Left DL) are always readable.
        titulo = Text("Mecánica Orbital:\nLEO vs MEO", font_size=36).to_edge(UP, buff=1.0)

        # Sutil equation positioned DL for technical authority
        ecuacion = MathTex(r"\vec{F}_g = -G \frac{Mm}{r^2} \hat{r}", font_size=32).to_corner(DL, buff=0.5)

        self.add_fixed_in_frame_mobjects(titulo, ecuacion)

        # ---------------------------------------------------------
        # 6. Animación Final de 15 segundos
        # ---------------------------------------------------------
        self.play(Write(titulo))
        self.play(FadeIn(ecuacion))

        # Coordinated camera and satellite motion. Camera rotates slowly
        # around the column to appreciate the 3D system, while the time moves
        # the satellites 2 full orbits, showcasing the velocity difference.
        self.move_camera(
            phi=68 * DEGREES, # Rotate back slightly to reveal the system
            theta=15 * DEGREES, # Slow rotation
            run_time=15,
            rate_func=linear,
            added_anims=[
                tiempo.animate.set_value(TAU * 2.0) # 2 complete orbits for LEO
            ]
        )

        self.wait(2)