from manim import *
import numpy as np

class OrbitLogicShowcase(ThreeDScene):
    def construct(self):
        # 1. Branding: Co.De Aerospace (Formato 16:9)
        # El logo se fija a la cámara en la esquina superior izquierda (UL)
        logo = Text("Co.De Aerospace", font_size=24, weight=BOLD, color=BLUE_B)
        self.add_fixed_in_frame_mobjects(logo)
        logo.to_corner(UL)

        # 2. Rigor Científico: Ecuación Vis-viva
        # MathTex para validar la base científica del video
        ecuacion = MathTex(r"v = \sqrt{\mu \left(\frac{2}{r} - \frac{1}{a}\right)}", font_size=32)
        self.add_fixed_in_frame_mobjects(ecuacion)
        ecuacion.to_corner(UR)

        # 3. Configuración Inicial de Cámara
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES)

        # 4. Construcción del Espacio y la Tierra
        # Uso de BLUE_D para la Tierra según la guía de estilo
        axes = ThreeDAxes(x_range=[-5, 5], y_range=[-5, 5], z_range=[-5, 5])
        tierra = Sphere(radius=1.0, resolution=(32, 64)).set_color(BLUE_D).set_opacity(0.6)

        # Malla para dar textura 3D a la Tierra
        malla_tierra = Surface(
            lambda u, v: axes.c2p(
                1.0 * np.cos(u) * np.cos(v),
                1.0 * np.cos(u) * np.sin(v),
                1.0 * np.sin(u)
            ),
            u_range=[-PI / 2, PI / 2],
            v_range=[0, TAU],
            resolution=(16, 32)
        ).set_style(fill_opacity=0, stroke_width=0.5, stroke_color=BLUE_A)

        self.play(FadeIn(logo), Write(ecuacion))
        self.play(Create(axes), DrawBorderThenFill(tierra), Create(malla_tierra), run_time=2)

        # 5. Definición de Órbitas (LEO y MEO)
        # LEO en GOLD, MEO en RED
        radio_leo = 1.5
        orbita_leo = Circle(radius=radio_leo, color=GOLD).set_shade_in_3d(True)

        radio_meo = 3.0
        orbita_meo = Circle(radius=radio_meo, color=RED).set_shade_in_3d(True)
        # Inclinación de la órbita MEO (45 grados)
        orbita_meo.rotate(45 * DEGREES, axis=RIGHT)

        self.play(Create(orbita_leo), Create(orbita_meo), run_time=2)

        # 6. Satélites y Cinemática (Resolución de Problemas)
        # Evitamos pfp_to_frame_coords y usamos always_redraw con Tracker
        tiempo = ValueTracker(0)

        satelite_leo = always_redraw(lambda: Dot3D(
            point=axes.c2p(
                radio_leo * np.cos(tiempo.get_value() * 2),  # LEO es más rápido
                radio_leo * np.sin(tiempo.get_value() * 2),
                0
            ),
            color=WHITE, radius=0.08
        ))

        # La trayectoria de MEO requiere trigonometría 3D debido a la inclinación
        satelite_meo = always_redraw(lambda: Dot3D(
            point=axes.c2p(
                radio_meo * np.cos(tiempo.get_value()),
                radio_meo * np.cos(45 * DEGREES) * np.sin(tiempo.get_value()),
                radio_meo * np.sin(45 * DEGREES) * np.sin(tiempo.get_value())
            ),
            color=WHITE, radius=0.1
        ))

        self.add(satelite_leo, satelite_meo)

        # 7. Precesión Nodal y Animación Coordinada
        # Simulamos la precesión nodal de la órbita MEO rotándola sobre el eje Z (OUT)
        orbita_meo.add_updater(lambda m, dt: m.rotate(dt * 0.3, axis=OUT))

        # Animación continua de la cámara mientras el tiempo avanza
        self.move_camera(
            phi=55 * DEGREES,
            theta=60 * DEGREES,
            run_time=12,
            added_anims=[
                tiempo.animate.set_value(TAU * 1.5)
            ]
        )

        # Limpieza
        orbita_meo.clear_updaters()
        self.play(
            FadeOut(satelite_leo), FadeOut(satelite_meo),
            FadeOut(orbita_meo), FadeOut(orbita_leo),
            FadeOut(axes), FadeOut(tierra), FadeOut(malla_tierra),
            run_time=2
        )
        self.wait(1)