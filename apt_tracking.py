from manim import *
import numpy as np

class SatelliteTracking(Scene):
    def construct(self):
        # 1. Elementos de Identidad (Branding)
        logo_text = Text("Co.De Aerospace", font_size=24, color=BLUE_B).to_corner(UR)
        titulo = Text("Sistema de Seguimiento (APT)", font_size=32).to_edge(UP)
        self.add(logo_text, titulo)

        # 2. Configuración de la Tierra y la Órbita
        tierra = Circle(radius=1.8, color=BLUE_D, fill_opacity=0.5)
        tierra_label = Text("TIERRA", font_size=18).move_to(tierra.get_center())

        # Órbita circular (parámetro 'r' de tu tesis)
        orbita = Circle(radius=3.5, color=WHITE).set_stroke(opacity=0.3, width=2)

        # Estación Terrena (en la superficie)
        gs_point = tierra.point_at_angle(90 * DEGREES)
        estacion = Dot(gs_point, color=RED)
        gs_label = Text("GS-01", font_size=14, color=RED).next_to(estacion, UP, buff=0.1)

        # 3. El Satélite y el Tracker de movimiento
        # Usamos un ValueTracker para manejar el ángulo orbital suavemente
        theta = ValueTracker(0)

        satelite = always_redraw(lambda:
            Dot(orbita.point_at_angle(theta.get_value() * DEGREES), color=GOLD, radius=0.1)
        )

        # 4. El "Core" de tu tesis: Vector de Seguimiento (Pointing)
        # Este vector se redibuja automáticamente cada frame
        vector_seguimiento = always_redraw(lambda:
            Line(
                start=estacion.get_center(),
                end=satelite.get_center(),
                color=GOLD_A,
                stroke_width=2
            ).set_opacity(0.6)
        )

        # 5. Visualización de Datos (Telemetría)
        # Calculamos la distancia euclidiana entre GS y SAT
        distancia_val = always_redraw(lambda:
            DecimalNumber(
                np.linalg.norm(satelite.get_center() - estacion.get_center()),
                num_decimal_places=2,
                color=GOLD
            ).next_to(satelite, UR, buff=0.2)
        )
        dist_label = Text("Distancia:", font_size=16).next_to(distancia_val, LEFT, buff=0.1)

        # 6. Ecuación Matemática (LaTeX)
        ecuacion = MathTex(
            r"\vec{r}_{rel} = \vec{r}_{sat} - \vec{r}_{gs}",
            font_size=34
        ).to_corner(DL, buff=1)

        # --- ANIMACIÓN ---
        self.play(
            Create(tierra),
            Write(tierra_label),
            run_time=2
        )
        self.play(Create(orbita), FadeIn(estacion, gs_label))
        self.play(FadeIn(satelite, vector_seguimiento, distancia_val, dist_label, ecuacion))

        # Simulamos 1.5 órbitas con velocidad constante
        self.play(
            theta.animate.set_value(360 + 180),
            run_time=10,
            rate_func=linear
        )

        self.wait(2)