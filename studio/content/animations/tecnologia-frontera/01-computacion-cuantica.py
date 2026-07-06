from manim import *
import numpy as np


class ComputacionCuantica(Scene):
    def construct(self):
        titulo = Text("Computación cuántica", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Bit clasico vs qubit
        bit_txt = Text("Bit: 0 o 1", font_size=22, color=GREY_B)
        bit_txt.move_to(LEFT * 4.4 + UP * 2.0)
        bit = Square(side_length=0.6, color=GREY_B).move_to(LEFT * 4.4 + UP * 0.9)
        bit_val = Text("0", font_size=26, color=WHITE).move_to(bit)
        self.play(FadeIn(bit_txt), Create(bit), FadeIn(bit_val), run_time=1.2)
        uno = Text("1", font_size=26, color=WHITE).move_to(bit)
        self.play(Transform(bit_val, uno), run_time=0.6)

        # Qubit: superposicion en un circulo
        qubit_txt = Text("Qubit: superposición de ambos", font_size=22, color=BLUE_B)
        qubit_txt.move_to(RIGHT * 0.6 + UP * 2.0)
        circulo = Circle(radius=0.95, color=BLUE_B).move_to(RIGHT * 0.3 + UP * 0.5)
        eje0 = Text("|0⟩", font_size=22, color=GREY_B)
        eje0.next_to(circulo.get_top(), UP, buff=0.1)
        eje1 = Text("|1⟩", font_size=22, color=GREY_B)
        eje1.next_to(circulo.get_bottom(), DOWN, buff=0.1)
        estado = Arrow(circulo.get_center(),
                       circulo.get_center() + 0.95 * np.array(
                           [np.sin(PI / 5), np.cos(PI / 5), 0]),
                       color=YELLOW, buff=0)
        self.play(FadeIn(qubit_txt), Create(circulo), FadeIn(eje0), FadeIn(eje1),
                  run_time=1.5)
        self.play(GrowArrow(estado), run_time=1)
        formula = MathTex(r"|\psi\rangle = \alpha|0\rangle + \beta|1\rangle",
                          font_size=34, color=YELLOW)
        formula.next_to(circulo, DOWN, buff=0.45)
        self.play(Write(formula), run_time=1.5)
        self.play(Rotate(estado, angle=PI / 3,
                         about_point=circulo.get_center()), run_time=1.5)

        # Medir colapsa
        medir = Text("Medir lo colapsa a 0 o 1, con probabilidades |α|², |β|²",
                     font_size=20, color=GREY_B).to_edge(DOWN)
        self.play(FadeIn(medir), run_time=1)
        self.play(Rotate(estado, angle=-PI / 3 - PI / 5,
                         about_point=circulo.get_center()), Flash(circulo, color=YELLOW),
                  run_time=1.2)

        # La escala exponencial: n qubits = 2^n amplitudes
        expo = VGroup(
            Text("1 qubit → 2 amplitudes", font_size=19, color=BLUE_B),
            Text("2 qubits → 4", font_size=19, color=BLUE_B),
            Text("10 qubits → 1 024", font_size=19, color=YELLOW),
            Text("300 qubits → más que átomos\nen el universo", font_size=19,
                 color=GOLD, line_spacing=0.85),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        expo.move_to(RIGHT * 4.5 + UP * 0.5)
        self.play(LaggedStart(*[FadeIn(e, shift=RIGHT * 0.3) for e in expo],
                              lag_ratio=0.3), run_time=3)

        # Aplicaciones y estado del arte
        cierre = Text("Promesa: química, materiales y optimización — el reto: el ruido (corrección de errores)",
                      font_size=18, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(medir, cierre), run_time=1.2)
        self.wait(2)
