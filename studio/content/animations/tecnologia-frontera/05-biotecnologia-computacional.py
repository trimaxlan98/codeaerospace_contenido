from manim import *
import numpy as np


class BiotecnologiaComputacional(Scene):
    def construct(self):
        titulo = Text("Biotecnología computacional", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # ADN como doble helice esquematica
        adn_txt = Text("El ADN es información: 4 letras", font_size=20, color=BLUE_B)
        adn_txt.move_to(LEFT * 4.0 + UP * 2.0)
        hebra1 = FunctionGraph(lambda x: 0.4 * np.sin(2.4 * x) + 0.7,
                               x_range=[-6.3, -1.7], color=BLUE_B)
        hebra2 = FunctionGraph(lambda x: -0.4 * np.sin(2.4 * x) + 0.7,
                               x_range=[-6.3, -1.7], color=BLUE_D)
        peldanos = VGroup(*[
            Line([x, 0.4 * np.sin(2.4 * x) + 0.7, 0],
                 [x, -0.4 * np.sin(2.4 * x) + 0.7, 0],
                 color=GREY_B, stroke_width=2)
            for x in np.linspace(-6.1, -1.9, 9)
        ])
        self.play(FadeIn(adn_txt), Create(hebra1), Create(hebra2), run_time=1.8)
        self.play(Create(peldanos), run_time=1.2)

        # Secuencia digital
        seq = Text("...ATGCGTACGATCCTAG...", font_size=22, color=YELLOW, font="monospace")
        seq.move_to(LEFT * 4.0 + DOWN * 0.5)
        flecha1 = Arrow(LEFT * 4.0 + UP * 0.2, seq.get_top() + UP * 0.05, color=GREY_B,
                        buff=0.05, stroke_width=3)
        lectura = Text("secuenciar: leerlo como texto (hoy, <$500 el genoma)",
                       font_size=17, color=GREY_B).next_to(seq, DOWN, buff=0.15)
        self.play(GrowArrow(flecha1), Write(seq), run_time=1.8)
        self.play(FadeIn(lectura), run_time=1)

        # Plegamiento de proteinas: cadena que se pliega en estructura
        prot_txt = Text("De la secuencia a la forma: plegamiento de proteínas",
                        font_size=20, color=GOLD).move_to(RIGHT * 3.3 + UP * 2.0)
        self.play(FadeIn(prot_txt), run_time=1)
        rng = np.random.default_rng(5)
        n = 10
        cadena_pts = [np.array([1.4 + i * 0.42, 0.8, 0]) for i in range(n)]
        cadena = VMobject(color=GOLD)
        cadena.set_points_as_corners(cadena_pts)
        bolas = VGroup(*[Dot(p, color=GOLD, radius=0.07) for p in cadena_pts])
        self.play(Create(cadena), FadeIn(bolas), run_time=1.5)

        # plegado deterministico hacia una forma compacta
        angulos = np.linspace(0, 2.4 * PI, n)
        centro_pleg = np.array([3.3, 0.2, 0])
        plegado_pts = [centro_pleg + (0.35 + 0.07 * i) * np.array(
            [np.cos(a), np.sin(a), 0]) for i, a in enumerate(angulos)]
        cadena2 = VMobject(color=GOLD)
        cadena2.set_points_as_corners(plegado_pts)
        self.play(Transform(cadena, cadena2),
                  *[b.animate.move_to(p) for b, p in zip(bolas, plegado_pts)],
                  run_time=2.5)
        alphafold = Text("AlphaFold: una red neuronal predice la forma\nen minutos (antes: años de laboratorio)",
                         font_size=17, color=GREY_B, line_spacing=0.9)
        alphafold.next_to(centro_pleg, DOWN, buff=0.8).shift(RIGHT * 0.4)
        self.play(FadeIn(alphafold), run_time=1.2)

        # El ciclo de diseño
        ciclo = VGroup(
            Text("diseñar", font_size=18, color=BLUE_B),
            Text("→ simular", font_size=18, color=YELLOW),
            Text("→ sintetizar", font_size=18, color=GOLD),
            Text("→ medir", font_size=18, color=GREY_B),
            Text("→ aprender ↺", font_size=18, color=BLUE_B),
        ).arrange(RIGHT, buff=0.25).to_edge(DOWN).shift(UP * 0.65)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in ciclo],
                              lag_ratio=0.25), run_time=2.5)

        cierre = Text("La biología se volvió una disciplina de datos: se lee, se modela y se diseña",
                      font_size=19, color=BLUE_B).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
