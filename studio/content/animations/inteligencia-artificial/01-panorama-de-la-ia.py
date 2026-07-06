from manim import *


class PanoramaDeLaIaModerna(Scene):
    def construct(self):
        titulo = Text("Panorama de la IA moderna", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Circulos anidados: IA > ML > DL > IA generativa
        conjuntos = [
            ("Inteligencia Artificial", 2.6, GREY_B),
            ("Aprendizaje automático", 1.95, BLUE_D),
            ("Aprendizaje profundo", 1.3, BLUE_B),
            ("IA generativa", 0.65, GOLD),
        ]
        centro = LEFT * 3.4 + DOWN * 0.7
        circulos = VGroup()
        for i, (nombre, r, color) in enumerate(conjuntos):
            c = Circle(radius=r, color=color).move_to(centro + UP * (2.6 - r))
            t = Text(nombre, font_size=17, color=color)
            t.move_to(c.get_bottom() + UP * 0.28)
            circulos.add(VGroup(c, t))
            self.play(Create(c), FadeIn(t), run_time=1)

        # Linea de tiempo de paradigmas
        eras = [
            ("1960-90", "reglas escritas a mano", GREY_B),
            ("1990-2012", "ML: aprender de datos", BLUE_D),
            ("2012-2017", "deep learning + GPUs", BLUE_B),
            ("2017-hoy", "transformers y LLMs", GOLD),
        ]
        filas = VGroup()
        for anio, texto, color in eras:
            fila = VGroup(
                Text(anio, font_size=18, color=color),
                Text(texto, font_size=18, color=GREY_B),
            ).arrange(RIGHT, buff=0.35)
            filas.add(fila)
        filas.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        filas.move_to(RIGHT * 3.3 + UP * 1.2)
        self.play(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.3) for f in filas],
                              lag_ratio=0.3), run_time=3)

        # El motor del salto: escala
        escala = VGroup(
            Text("El motor del salto reciente:", font_size=20, color=YELLOW),
            Text("más datos + más cómputo + un modelo simple que escala",
                 font_size=19, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        escala.move_to(RIGHT * 3.3 + DOWN * 0.9)
        self.play(FadeIn(escala), run_time=1.5)

        barras = VGroup(*[
            Rectangle(width=0.4, height=h, color=GOLD, fill_opacity=0.7,
                      fill_color=GOLD)
            for h in [0.15, 0.3, 0.6, 1.2, 2.4]
        ]).arrange(RIGHT, buff=0.3, aligned_edge=DOWN)
        barras.move_to(RIGHT * 3.3 + DOWN * 2.4, aligned_edge=DOWN)
        barras_txt = Text("cómputo de entrenamiento (×10 cada pocos años)",
                          font_size=15, color=GREY_B).next_to(barras, DOWN, buff=0.15)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in barras],
                              lag_ratio=0.2), FadeIn(barras_txt), run_time=2.5)

        cierre = Text("La IA dejó de programarse regla por regla: ahora se entrena y se dirige",
                      font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
