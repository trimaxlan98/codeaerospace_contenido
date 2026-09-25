class Clip1(Scene):
    """7.2.1 - El bloqueo: dos carriles de tiempo. En A, una barra roja de
    transaccion abierta desde BEGIN hasta COMMIT; en B, una barra de espera
    (LCK_M_S) que crece mientras esta bloqueada y se vuelve verde cuando
    pasa. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El bloqueo"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- los dos carriles de tiempo, a lo ancho del cuadro ------------------
        y_a, y_b = 0.3, -2.0
        carril_a = carril_tiempo(y_a)
        carril_b = carril_tiempo(y_b)
        rot_a = Text("A", font_size=26, color=C_TITULO)
        rot_a.next_to([-6.0, y_a, 0], LEFT, buff=0.25)
        rot_b = Text("B", font_size=26, color=C_TITULO)
        rot_b.next_to([-6.0, y_b, 0], LEFT, buff=0.25)
        self.play(Create(carril_a), Create(carril_b), FadeIn(rot_a),
                  FadeIn(rot_b), run_time=0.7)
        self.wait(1.0)

        # --- A: codigo compacto arriba -------------------------------------------
        letra_a = Text("A", font_size=24, color=C_TITULO)
        letra_a.move_to(LEFT * 3.9 + UP * 3.0)
        qa = S.codigo(["BEGIN TRAN", "UPDATE pedidos",
                      "SET estatus = 'enviado'",
                      f"WHERE id_pedido = {ID_PEDIDO}", "COMMIT"], font_size=18)
        qa.next_to(letra_a, DOWN, buff=0.18)
        self.play(FadeIn(letra_a), FadeIn(qa, shift=LEFT * 0.2), run_time=0.7)
        self.wait(0.6)

        marca_a1 = SurroundingRectangle(qa.lineas[0], color=C_TENUE, buff=0.05,
                                        stroke_width=2)
        self.play(Create(marca_a1), run_time=0.5)

        x_begin, x_evento, x_fin = -5.6, -1.1, 3.2
        tic_begin = marca_tiempo(x_begin, y_a)
        bar_a = barra_tiempo(x_begin, y_a, color=C_MALO)
        self.play(FadeIn(tic_begin), FadeIn(bar_a), run_time=0.4)
        self.play(bar_a.animate.stretch_to_fit_width(x_evento - x_begin,
                                                      about_edge=LEFT),
                  run_time=0.8)

        marca_a2 = SurroundingRectangle(VGroup(*qa.lineas[1:4]), color=C_MALO,
                                        buff=0.06, stroke_width=2.2)
        self.play(ReplacementTransform(marca_a1, marca_a2), run_time=0.6)
        cand = candado(lado=0.5, color=C_MALO)
        cand.move_to([x_evento, y_a + 0.55, 0])
        tic_evento_a = marca_tiempo(x_evento, y_a)
        self.play(FadeIn(tic_evento_a), FadeIn(cand, scale=0.7), run_time=0.6)
        etq = tag_junto(cand, "bloqueado", UP, buff=0.14, color=C_MALO)
        self.play(FadeIn(etq), run_time=0.4)
        self.wait(1.4)

        # --- B: codigo compacto arriba, intenta leer y espera --------------------
        letra_b = Text("B", font_size=24, color=C_TITULO)
        letra_b.move_to(RIGHT * 3.9 + UP * 3.0)
        qb = S.codigo(["SELECT estatus", "FROM pedidos",
                      f"WHERE id_pedido = {ID_PEDIDO}"], font_size=18)
        qb.next_to(letra_b, DOWN, buff=0.18)
        self.play(FadeIn(letra_b), FadeIn(qb, shift=RIGHT * 0.2), run_time=0.7)
        marca_b = SurroundingRectangle(qb.lineas[2], color=C_TENUE, buff=0.05,
                                       stroke_width=2)
        self.play(Create(marca_b), run_time=0.5)

        tic_evento_b = marca_tiempo(x_evento, y_b)
        bar_b = barra_tiempo(x_evento, y_b, color=C_MALO)
        self.play(FadeIn(tic_evento_b), FadeIn(bar_b), run_time=0.4)
        lck = tag_hud("LCK_M_S", font_size=22, color=C_TENUE)
        lck.next_to(bar_b, UP, buff=0.18)
        self.play(FadeIn(lck), run_time=0.4)
        self.wait(1.0)

        # --- las dos barras crecen juntas hasta que A libera ---------------------
        self.play(bar_a.animate.stretch_to_fit_width(x_fin - x_begin,
                                                      about_edge=LEFT),
                  bar_b.animate.stretch_to_fit_width(x_fin - x_evento,
                                                     about_edge=LEFT),
                  run_time=3.0, rate_func=linear)
        self.wait(1.6)

        # --- A libera: COMMIT ------------------------------------------------
        tic_fin = marca_tiempo(x_fin, y_a)
        marca_a3 = SurroundingRectangle(qa.lineas[4], color=C_BUENO, buff=0.05,
                                        stroke_width=2.2)
        self.play(ReplacementTransform(marca_a2, marca_a3), FadeIn(tic_fin),
                  run_time=0.6)
        self.play(FadeOut(cand), FadeOut(etq),
                  bar_a.animate.set_fill(C_TENUE, 0.6),
                  run_time=0.7)

        # --- B pasa: la barra se vuelve verde ----------------------------------
        marca_b2 = SurroundingRectangle(qb.lineas[2], color=C_BUENO, buff=0.05,
                                        stroke_width=2.2)
        self.play(ReplacementTransform(marca_b, marca_b2), FadeOut(lck),
                  bar_b.animate.set_fill(C_BUENO), run_time=0.7)
        continua = tag_junto(bar_b, "continua", UP, buff=0.18, color=C_BUENO)
        self.play(FadeIn(continua), run_time=0.4)
        self.wait(10.7)
