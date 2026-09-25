class Clip2(Scene):
    """5.1.2 - Se revela lo que "sigue" en el clip anterior: sin recortar,
    el paso del cliente 1 es una torre casi 20 veces la pared del resto
    (escala lineal real, sin log). El EQ_ROWS que da el histograma
    (cian) coincide con el que midio el motor (ambar): es el UNICO paso
    validado contra SQL Server. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El paso del mayorista"), zona="arriba",
                    run_time=0.6)
        self.wait(0.7)

        # --- acercamiento a los primeros pasos, esta vez sin recortar: -----
        # la torre real del cliente 1 (escala lineal, sin log). Menos pasos
        # y mas anchos que en el clip 1 para que la torre llene el cuadro.
        barras, _ = barras_histograma(HISTO[:34], ancho=6.6, alto_pared=2.7,
                                      base_y=-1.9, color=C_CREE,
                                      indice_recortado=None)
        barras.shift(RIGHT * 1.7)
        torre = barras[IDX_C1]
        resto = VGroup(*[b for i, b in enumerate(barras) if i != IDX_C1])

        base = Line(barras.get_corner(DL) + LEFT * 0.3,
                   barras.get_corner(DL) + RIGHT * (barras.width + 0.3),
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        modelo = tag_junto(base, "modelo del histograma", DOWN, buff=0.28)
        self.play(FadeIn(resto), FadeIn(modelo), run_time=0.9)
        self.wait(0.4)

        torre.save_state()
        torre.stretch_to_fit_height(0.06, about_edge=DOWN)
        self.play(FadeIn(torre), run_time=0.3)
        self.play(Restore(torre), run_time=2.1)
        self.wait(0.8)

        nom = tag_junto(torre, "cliente 1", UP, buff=0.55)
        self.play(FadeIn(nom), run_time=0.4)
        self.wait(1.6)

        cif_modelo = tag_hud(f"{S.miles(C1_MODELO)} EQ_ROWS", font_size=24)
        cif_modelo.next_to(nom, UP, buff=0.26)
        self.play(FadeIn(cif_modelo), run_time=0.5)
        self.wait(2.2)

        coincide = tag_junto(cif_modelo, "coincide con el motor", UP,
                             buff=0.26)
        self.play(FadeIn(coincide), run_time=0.5)
        self.wait(2.0)

        # --- un vistazo corto al comando que muestra el histograma --------
        q = S.codigo(["DBCC SHOW_STATISTICS(", "'pedidos', ix_cliente)"],
                    font_size=22)
        q.next_to(torre, RIGHT, buff=1.1).align_to(torre, DOWN).shift(UP * 1.1)
        self.play(FadeIn(q, shift=LEFT * 0.2), run_time=0.7)
        self.wait(3.4)

        rot.mostrar(motor_pie(f"{S.miles(EQ_C1_MOTOR)} EQ_ROWS"),
                    zona="abajo", run_time=0.5)
        self.wait(10.5)
