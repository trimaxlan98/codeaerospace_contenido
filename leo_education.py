from manim import *
import numpy as np

class LEOSatelliteEducation(ThreeDScene):
    def construct(self):
        # ==========================================
        # 1. BRANDING Y CONFIGURACIÓN INICIAL
        # ==========================================
        # Logo fijo en la esquina superior izquierda (UL) para formato 16:9
        logo = Text("Co.De Aerospace", font_size=24, weight=BOLD, color=BLUE_B)
        self.add_fixed_in_frame_mobjects(logo)
        logo.to_corner(UL)

        # Orientación inicial de la cámara 3D
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)

        # Funciones auxiliares para crear cajas de texto explicativas (Divulgación)
        def create_text_box(texto):
            box = VGroup()
            text = Text(texto, font_size=20, line_spacing=1).set_color(WHITE)
            bg = BackgroundRectangle(text, color=BLACK, fill_opacity=0.7, buff=0.2)
            box.add(bg, text)
            box.to_corner(DL) # Esquina inferior izquierda
            return box

        # ==========================================
        # 2. CONSTRUCCIÓN DEL ESCENARIO 3D
        # ==========================================
        axes = ThreeDAxes(x_range=[-5, 5], y_range=[-5, 5], z_range=[-5, 5])

        # Tierra usando BLUE_D como exige la guía de estilo
        tierra = Sphere(radius=1.5, resolution=(32, 64)).set_color(BLUE_D).set_opacity(0.8)
        malla_tierra = Surface(
            lambda u, v: axes.c2p(
                1.5 * np.cos(u) * np.cos(v),
                1.5 * np.cos(u) * np.sin(v),
                1.5 * np.sin(u)
            ),
            u_range=[-PI / 2, PI / 2],
            v_range=[0, TAU],
            resolution=(16, 32)
        ).set_style(fill_opacity=0, stroke_width=0.3, stroke_color=BLUE_A)

        # Órbita LEO en GOLD
        radio_leo = 2.5
        orbita_leo = Circle(radius=radio_leo, color=GOLD).set_shade_in_3d(True)

        self.play(FadeIn(logo))

        # === TEXTO 1: Concepto LEO ===
        t1 = create_text_box("Órbita Terrestre Baja (LEO)\nAltitud: 160 km - 2,000 km")
        self.add_fixed_in_frame_mobjects(t1)

        self.play(FadeIn(t1), Create(axes), DrawBorderThenFill(tierra), Create(malla_tierra), run_time=3)
        self.play(Create(orbita_leo), run_time=2)
        self.wait(2)
        self.play(FadeOut(t1))

        # ==========================================
        # 3. SATÉLITE Y RIGOR MATEMÁTICO
        # ==========================================
        # Ecuación de velocidad orbital para dar rigor científico
        ecuacion = MathTex(r"v = \sqrt{\frac{G M_E}{r}} \approx 7.8 \text{ km/s}", font_size=28)
        self.add_fixed_in_frame_mobjects(ecuacion)
        ecuacion.to_corner(UR)

        tiempo = ValueTracker(0)

        # Evitamos pfp_to_frame_coords, usamos always_redraw con Tracker
        satelite = always_redraw(lambda: Dot3D(
            point=axes.c2p(
                radio_leo * np.cos(tiempo.get_value()),
                radio_leo * np.sin(tiempo.get_value()),
                0
            ),
            color=WHITE, radius=0.1
        ))

        # === TEXTO 2: Velocidad ===
        t2 = create_text_box("Para no caer por la gravedad,\nel satélite viaja a ~28,000 km/h.")
        self.add_fixed_in_frame_mobjects(t2)

        self.play(FadeIn(t2), Write(ecuacion), FadeIn(satelite), run_time=2)

        # Hacemos que el satélite dé una vuelta parcial mientras la cámara se mueve
        self.move_camera(
            phi=55 * DEGREES, theta=-10 * DEGREES, run_time=5,
            added_anims=[tiempo.animate.set_value(PI)]
        )
        self.wait(1)
        self.play(FadeOut(t2))

        # ==========================================
        # 4. COMUNICACIÓN Y LÍNEA DE VISIÓN (LoS)
        # ==========================================
        # Ubicamos una estación terrestre en la superficie de la Tierra
        angulo_gs = PI / 4
        gs_point = axes.c2p(1.5 * np.cos(angulo_gs), 1.5 * np.sin(angulo_gs), 0)
        ground_station = Dot3D(point=gs_point, color=GREEN, radius=0.12)

        # Anillo para resaltar la estación
        gs_ring = always_redraw(lambda: Circle(radius=0.2, color=GREEN).move_to(gs_point).set_shade_in_3d(True))

        # === TEXTO 3: Línea de Visión ===
        t3 = create_text_box("La comunicación requiere\nLínea de Visión Directa (LoS).")
        self.add_fixed_in_frame_mobjects(t3)

        self.play(FadeIn(t3), FadeIn(ground_station), Create(gs_ring))
        self.wait(3)
        self.play(FadeOut(t3))

        # === LÓGICA DEL ENLACE DE SEÑAL ===
        # La señal (una línea amarilla) solo aparece cuando el satélite está "cerca" (ángulo favorable)
        senal = Line(satelite.get_center(), gs_point, color=YELLOW)

        def update_senal(mob):
            mob.put_start_and_end_on(satelite.get_center(), gs_point)
            # Calculamos la distancia para determinar si hay línea de visión
            dist = np.linalg.norm(satelite.get_center() - gs_point)
            # Si la distancia es menor a la distancia máxima de visibilidad tangencial
            if dist < 1.7:
                mob.set_opacity(0.8)
                mob.set_color(YELLOW)
            else:
                mob.set_opacity(0)

        senal.add_updater(update_senal)
        self.add(senal)

        # === TEXTO 4: Ventana de Conexión ===
        t4 = create_text_box("Ventana de Conexión: Solo hay unos\nminutos para descargar telemetría.")
        self.add_fixed_in_frame_mobjects(t4)
        self.play(FadeIn(t4))

        # Animación principal continua (Demostración visual del enlace)
        # El satélite da 1.5 vueltas más. La señal se encenderá y apagará automáticamente.
        self.move_camera(
            phi=45 * DEGREES, theta=60 * DEGREES, run_time=12,
            added_anims=[tiempo.animate.set_value(PI + TAU * 1.5)]
        )

        # ==========================================
        # 5. OUTRO Y LIMPIEZA
        # ==========================================
        self.play(FadeOut(t4))
        senal.clear_updaters()

        self.play(
            FadeOut(satelite), FadeOut(senal), FadeOut(ground_station), FadeOut(gs_ring),
            FadeOut(orbita_leo), FadeOut(ecuacion), FadeOut(axes),
            FadeOut(tierra), FadeOut(malla_tierra),
            run_time=3
        )
        self.wait(1)