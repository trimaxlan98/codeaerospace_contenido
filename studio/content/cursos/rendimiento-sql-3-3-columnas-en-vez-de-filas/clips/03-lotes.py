class Clip3(Scene):
    """3.3.3 - Modo fila (un renglon por vuelta) contra modo batch (lotes de
    ~900): mismo recorrido, pasos de tamano muy distinto. Sin tiempos
    inventados: solo las vueltas que hacen falta. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Una fila o un lote"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        largo = 9.6
        pista_fila = Line(LEFT * largo / 2, RIGHT * largo / 2,
                          stroke_color=C_TENUE, stroke_width=2.4).shift(UP * 1.6)
        pista_lote = pista_fila.copy().shift(DOWN * 3.0)
        marcas_fila = VGroup(*[
            Line(UP * 0.1, DOWN * 0.1, stroke_color=C_TENUE, stroke_width=1.6)
            .move_to(pista_fila.point_from_proportion(t))
            for t in np.linspace(0, 1, 26)])
        marcas_lote = marcas_fila.copy().shift(DOWN * 3.0)

        et_fila = Text("modo fila", font_size=26, color=C_TITULO)
        et_fila.next_to(pista_fila, UP, buff=0.4).align_to(pista_fila, LEFT)
        et_lote = Text("modo batch", font_size=26, color=C_TITULO)
        et_lote.next_to(pista_lote, UP, buff=0.4).align_to(pista_lote, LEFT)

        self.play(FadeIn(et_fila), Create(pista_fila), FadeIn(marcas_fila),
                  run_time=0.9)
        self.play(FadeIn(et_lote), Create(pista_lote), FadeIn(marcas_lote),
                  run_time=0.9)
        self.wait(0.8)

        ficha_fila = Dot(pista_fila.get_start(), radius=0.12, color=C_TENUE)
        ficha_lote = Square(0.26, fill_color=C_INDICE, fill_opacity=0.85,
                            stroke_width=0).move_to(pista_lote.get_start())
        self.play(FadeIn(ficha_fila), FadeIn(ficha_lote), run_time=0.5)
        self.wait(0.6)

        et_1x1 = tag_junto(pista_fila, "una fila por vuelta", DOWN, buff=0.26)
        self.play(FadeIn(et_1x1), run_time=0.4)
        for t in np.linspace(0, 1, 26)[1:]:
            self.play(ficha_fila.animate.move_to(
                pista_fila.point_from_proportion(t)), run_time=0.2)
        self.wait(1.4)

        et_lotewd = tag_junto(pista_lote, "~900 por lote", DOWN, buff=0.26,
                              color=C_DATO)
        self.play(FadeIn(et_lotewd), run_time=0.4)
        for t in [0.16, 0.33, 0.5, 0.66, 0.83, 1.0]:
            self.play(ficha_lote.animate.move_to(
                pista_lote.point_from_proportion(t)), run_time=0.55)
            self.wait(0.3)
        self.wait(1.6)

        rot.mostrar(cifra_pie(f"{S.miles(DET)} vueltas"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)
        rot.mostrar(cifra_pie(f"~{S.miles(round(LOTES, -2))} lotes"), zona="abajo",
                    run_time=0.5)
        self.wait(6.5)
