from manim import *
import numpy as np


class EvaluacionDeAgentes(Scene):
    def construct(self):
        titulo = Text("Evaluación de agentes", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        problema = Text("Un agente no da 'la respuesta': ejecuta trayectorias. ¿Cómo se mide eso?",
                        font_size=20, color=GREY_B).next_to(titulo, DOWN, buff=0.25)
        self.play(FadeIn(problema), run_time=1.2)

        # Suite de tareas con resultado
        tareas = [
            ("reservar un vuelo", True), ("depurar el módulo", True),
            ("migrar la base", False), ("resumir 40 papers", True),
            ("configurar el server", False),
        ]
        filas = VGroup()
        for texto, ok in tareas:
            marca = Text("✓" if ok else "✗", font_size=22,
                         color=GOLD if ok else RED_D)
            t = Text(texto, font_size=18, color=GREY_B)
            filas.add(VGroup(marca, t).arrange(RIGHT, buff=0.3))
        filas.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        filas.move_to(LEFT * 3.9 + DOWN * 0.7)
        suite = Text("Benchmark: muchas tareas reales", font_size=20, color=BLUE_B)
        suite.next_to(filas, UP, buff=0.3)
        self.play(FadeIn(suite), run_time=0.8)
        for f in filas:
            self.play(FadeIn(f, shift=RIGHT * 0.3), run_time=0.55)

        # Tasa de exito
        tasa = VGroup(
            Text("éxito:", font_size=20, color=GREY_B),
            Text("3/5 = 60%", font_size=26, color=YELLOW),
        ).arrange(RIGHT, buff=0.25).next_to(filas, DOWN, buff=0.4)
        self.play(FadeIn(tasa), run_time=1)

        # Pero el exito no basta: dimensiones
        dims = VGroup(
            Text("¿Lo logró?  → corrección", font_size=19, color=GOLD),
            Text("¿A qué costo?  → tokens, tiempo, pasos", font_size=19, color=YELLOW),
            Text("¿Rompió algo?  → seguridad", font_size=19, color=RED_D),
            Text("¿Siempre igual?  → consistencia (pass@k)", font_size=19, color=BLUE_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        dims.move_to(RIGHT * 3.2 + DOWN * 0.1)
        dims_txt = Text("Medir en varias dimensiones:", font_size=20, color=GREY_B)
        dims_txt.next_to(dims, UP, buff=0.3).align_to(dims, LEFT)
        self.play(FadeIn(dims_txt), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(d, shift=RIGHT * 0.3) for d in dims],
                              lag_ratio=0.3), run_time=3)

        # Revision de trayectoria
        lupa = VGroup(
            Circle(radius=0.32, color=BLUE_B),
            Line(ORIGIN, DR * 0.35, color=BLUE_B, stroke_width=5).shift(
                0.32 * np.array([0.707, -0.707, 0])),
        ).move_to(RIGHT * 3.2 + DOWN * 2.3)
        traza = Text("y leer las trazas: dónde dudó, dónde se desvió, dónde reintentó",
                     font_size=18, color=GREY_B).next_to(lupa, LEFT, buff=0.35)
        self.play(FadeIn(lupa), FadeIn(traza), run_time=1.5)

        cierre = Text("Sin evaluación continua, un agente 'mejorado' es solo una anécdota",
                      font_size=20, color=GOLD).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
