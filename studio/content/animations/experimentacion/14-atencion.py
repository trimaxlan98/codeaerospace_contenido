import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from atencion import (COLOR_EJE, COLOR_MECANISMO, COLOR_PROB, COLOR_TENUE,
                      COLOR_TOKEN, COLOR_VECTOR, abanico_atencion,
                      arco_similitud, distribucion_siguiente, fila_tokens,
                      flecha_vector, mapa_embeddings, pesos_atencion,
                      similitud_coseno)


class DemoAtencion(Scene):
    """Demo de atencion.py: tokens, abanico de atencion, mapa y prediccion.

    Los pesos del abanico son los reales de `pesos_atencion` sobre la query
    'banco': 'cobra' y 'comisiones' se llevan los arcos gruesos. Todo el
    calculo es numpy determinista sobre los embeddings fijos de la libreria.
    """

    def construct(self):
        titulo = Text("Atención: quién mira a quién", font_size=30,
                      color=COLOR_MECANISMO).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=0.7)

        # --- acto 1: la frase, y a quien atiende 'banco' ---
        frase = "el banco cobra comisiones al cliente"
        fila = fila_tokens(frase).move_to(DOWN * 1.05)
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.2) for f in fila.fichas],
                              lag_ratio=0.12), run_time=1.2)

        pesos = pesos_atencion(frase, 1)          # query = 'banco'
        fila.fichas[1].caja.set_stroke(color=COLOR_MECANISMO)
        abanico = abanico_atencion(fila, 1, pesos)
        self.play(Create(abanico), run_time=1.4)

        pie = Text("«banco» pesa 'cobra' y 'comisiones'", font_size=21,
                   color=COLOR_TENUE).to_edge(DOWN, buff=0.45)
        self.play(FadeIn(pie), run_time=0.5)
        self.wait(1.1)
        self.play(FadeOut(abanico), FadeOut(fila), FadeOut(pie), run_time=0.6)

        # --- acto 2: el mapa del significado (5 palabras) ---
        plano = Axes(x_range=[-2.2, 2.2, 2.2], y_range=[-2.2, 2.2, 2.2],
                     x_length=4.6, y_length=4.6, tips=False,
                     axis_config={"stroke_width": 2.5, "color": COLOR_EJE,
                                  "include_ticks": False})
        plano.shift(LEFT * 3.3 + DOWN * 0.35)
        self.play(Create(plano), run_time=0.7)

        palabras = ["perro", "gato", "felino", "sol", "luna"]
        mapa = mapa_embeddings(plano, palabras, colores=COLOR_VECTOR,
                               direcciones={"perro": UR, "gato": DR,
                                            "felino": LEFT, "sol": UL,
                                            "luna": DL})
        self.play(LaggedStart(*[FadeIn(p, scale=0.6) for p in mapa],
                              lag_ratio=0.18), run_time=1.1)

        f_gato = flecha_vector(plano, (0, 0), "gato")
        f_luna = flecha_vector(plano, (0, 0), "luna", color=COLOR_TENUE,
                               grosor=3.5)
        arco = arco_similitud(plano, "gato", "luna", radio=0.7)
        cos = Text(f"cos(gato, luna) = {similitud_coseno('gato', 'luna'):.2f}",
                   font_size=20, color=COLOR_MECANISMO)
        cos.next_to(plano, DOWN, buff=0.18)
        self.play(GrowArrow(f_gato), GrowArrow(f_luna), run_time=0.7)
        self.play(Create(arco), FadeIn(cos), run_time=0.7)
        self.wait(0.7)

        # --- acto 3: y con eso, la siguiente palabra ---
        dist = distribucion_siguiente(["tejado", "árbol", "sofá", "coche"],
                                      [0.46, 0.31, 0.18, 0.05], ancho_max=3.2,
                                      resaltar="tejado")
        dist.move_to(RIGHT * 3.4 + DOWN * 0.35)
        rotulo = Text("el gato se subió al...", font_size=22, color=COLOR_TOKEN)
        rotulo.next_to(dist, UP, buff=0.5)
        self.play(FadeIn(rotulo, shift=DOWN * 0.15), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.25) for f in dist],
                              lag_ratio=0.2), run_time=1.2)
        self.play(Indicate(dist.filas["tejado"], color=COLOR_PROB,
                           scale_factor=1.08), run_time=0.8)
        self.wait(1.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
