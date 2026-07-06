from manim import *
import numpy as np


class TransformersYGrandesModelos(Scene):
    def construct(self):
        titulo = Text("Transformers y grandes modelos de lenguaje",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Tokenizacion
        frase = ["El", "satélite", "orbita", "la"]
        tokens = VGroup()
        for palabra in frase:
            caja = RoundedRectangle(width=1.5, height=0.55, corner_radius=0.1,
                                    color=BLUE_B, fill_opacity=0.12, fill_color=BLUE_B)
            t = Text(palabra, font_size=20, color=WHITE).move_to(caja)
            tokens.add(VGroup(caja, t))
        tokens.arrange(RIGHT, buff=0.3).move_to(UP * 1.8)
        tok_txt = Text("1) El texto se corta en tokens", font_size=20, color=GREY_B)
        tok_txt.next_to(tokens, UP, buff=0.3)
        self.play(FadeIn(tok_txt),
                  LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in tokens],
                              lag_ratio=0.2), run_time=2)

        # Atencion: cada token mira a los demas
        att_txt = Text("2) Atención: cada token pondera cuánto le importa cada otro",
                       font_size=20, color=YELLOW).move_to(UP * 0.4)
        self.play(FadeIn(att_txt), run_time=1)
        focal = tokens[2]  # "orbita"
        lineas = VGroup()
        for otro, grosor in [(tokens[0], 2), (tokens[1], 7), (tokens[3], 3.5)]:
            lineas.add(ArcBetweenPoints(
                focal[0].get_top(), otro[0].get_top(), angle=PI / 2.5,
                color=YELLOW, stroke_width=grosor))
        self.play(Indicate(focal, color=YELLOW), run_time=0.8)
        self.play(LaggedStart(*[Create(l) for l in lineas], lag_ratio=0.25),
                  run_time=2)
        peso_txt = Text("'orbita' atiende fuerte a 'satélite'", font_size=18,
                        color=YELLOW).next_to(att_txt, DOWN, buff=0.2)
        self.play(FadeIn(peso_txt), run_time=1)
        self.wait(0.5)
        self.play(FadeOut(lineas), FadeOut(peso_txt), run_time=0.8)

        # Prediccion del siguiente token
        pred_txt = Text("3) El modelo predice el siguiente token con probabilidades",
                        font_size=20, color=BLUE_B).move_to(UP * 0.4)
        self.play(ReplacementTransform(att_txt, pred_txt), run_time=1)
        opciones = [("Tierra", 0.78, GOLD), ("Luna", 0.13, GREY_B),
                    ("órbita", 0.05, GREY_B), ("casa", 0.01, GREY_B)]
        barras = VGroup()
        for i, (palabra, prob, color) in enumerate(opciones):
            barra = Rectangle(width=3.8 * prob + 0.05, height=0.4, color=color,
                              fill_opacity=0.7, fill_color=color)
            etiqueta = Text(palabra, font_size=18, color=color)
            valor = Text(f"{int(prob*100)}%", font_size=16, color=GREY_B)
            fila = VGroup(etiqueta, barra, valor).arrange(RIGHT, buff=0.25)
            barras.add(fila)
        barras.arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(DOWN * 1.5 + LEFT * 2.2)
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.3) for b in barras],
                              lag_ratio=0.25), run_time=2.5)

        elegido = VGroup(
            RoundedRectangle(width=1.5, height=0.55, corner_radius=0.1, color=GOLD,
                             fill_opacity=0.25, fill_color=GOLD),
            Text("Tierra", font_size=20, color=GOLD),
        )
        elegido[1].move_to(elegido[0])
        elegido.next_to(tokens, RIGHT, buff=0.3)
        self.play(ReplacementTransform(barras[0][0].copy(), elegido), run_time=1.2)

        # El bucle autoregresivo y la escala
        loop = Text("…y el token elegido vuelve a entrar: así se escribe palabra a palabra",
                    font_size=19, color=GREY_B).move_to(DOWN * 2.9)
        flecha = CurvedArrow(elegido.get_bottom(), tokens[0][0].get_bottom(),
                             angle=PI / 3, color=GREY_B, stroke_width=3)
        self.play(FadeIn(loop), Create(flecha), run_time=1.5)

        cierre = Text("Un LLM: este mecanismo, miles de millones de pesos, todo Internet como texto",
                      font_size=19, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(loop, cierre), run_time=1.2)
        self.wait(2)
