class Clip4(Scene):
    """7.2.4 - Optimized locking: dos carriles de tiempo. En A, la misma
    barra grande del clip anterior pero VERDE (un candado de intencion y
    uno de transaccion, no miles); en B, una barra corta y verde: pasa de
    inmediato. Cierre. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Optimized locking"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- los dos carriles de tiempo -------------------------------------------
        y_a, y_b = 0.85, -2.05
        carril_a = carril_tiempo(y_a)
        carril_b = carril_tiempo(y_b)
        rot_a = Text("A", font_size=26, color=C_TITULO)
        rot_a.next_to([-6.0, y_a, 0], LEFT, buff=0.25)
        rot_b = Text("B", font_size=26, color=C_TITULO)
        rot_b.next_to([-6.0, y_b, 0], LEFT, buff=0.25)
        self.play(Create(carril_a), Create(carril_b), FadeIn(rot_a),
                  FadeIn(rot_b), run_time=0.7)
        self.wait(0.8)

        # --- A: el mismo UPDATE grande, ahora con optimized locking -----------------
        letra_a = Text("A", font_size=24, color=C_TITULO)
        letra_a.move_to(LEFT * 3.9 + UP * 3.0)
        qa = S.codigo(["UPDATE TOP (10000) pedidos",
                      "SET estatus = 'enviado'",
                      "WHERE id_cliente = 1"], font_size=18)
        qa.next_to(letra_a, DOWN, buff=0.18)
        self.play(FadeIn(letra_a), FadeIn(qa, shift=LEFT * 0.2), run_time=0.7)
        marca_a = SurroundingRectangle(qa.lineas, color=C_BUENO, buff=0.06,
                                       stroke_width=2.2)
        self.play(Create(marca_a), run_time=0.6)

        x_begin, x_esc, x_end = -5.6, 0.5, 4.3
        tic_begin = marca_tiempo(x_begin, y_a)
        bar_a = barra_tiempo(x_begin, y_a, color=C_BUENO)
        self.play(FadeIn(tic_begin), FadeIn(bar_a), run_time=0.4)
        self.play(bar_a.animate.stretch_to_fit_width(x_esc - x_begin,
                                                      about_edge=LEFT),
                  run_time=1.0)

        # --- UN candado de intencion sobre la tabla (no la bloquea) ------------------
        obj_ix = candado(lado=0.85, color=C_BUENO)
        obj_ix.move_to([-0.9, -0.4, 0])
        tag_ix = tag_hud("OBJECT IX", font_size=22, color=C_TENUE)
        tag_ix.next_to(obj_ix, UP, buff=0.2)
        self.play(FadeIn(obj_ix, scale=0.7), FadeIn(tag_ix), run_time=0.7)
        self.wait(1.2)

        # --- y UN solo bloqueo de transaccion, no miles ------------------------------
        xact = candado(lado=0.5, color=C_BUENO)
        xact.move_to([1.0, -0.4, 0])
        tag_xact = tag_hud("XACT", font_size=22, color=C_TENUE)
        tag_xact.next_to(xact, UP, buff=0.2)
        self.play(FadeIn(xact, scale=0.7), FadeIn(tag_xact), run_time=0.6)
        self.wait(1.4)

        # --- las dos barras siguen creciendo: A sigue trabajando --------------------
        self.play(bar_a.animate.stretch_to_fit_width(x_end - x_begin,
                                                      about_edge=LEFT),
                  run_time=1.6, rate_func=linear)

        # --- B actualiza otro pedido y pasa de inmediato -----------------------------
        letra_b = Text("B", font_size=24, color=C_TITULO)
        letra_b.move_to(RIGHT * 3.9 + UP * 3.0)
        qb = S.codigo(["UPDATE pedidos", "SET estatus = 'enviado'",
                      f"WHERE id_pedido = {ID_OTRO}"], font_size=18)
        qb.next_to(letra_b, DOWN, buff=0.18)
        self.play(FadeIn(letra_b), FadeIn(qb, shift=RIGHT * 0.2), run_time=0.7)
        marca_b = SurroundingRectangle(qb.lineas[2], color=C_BUENO, buff=0.05,
                                       stroke_width=2.2)
        self.play(Create(marca_b), run_time=0.6)

        tic_esc_b = marca_tiempo(x_esc, y_b)
        bar_b = barra_tiempo(x_esc, y_b, color=C_BUENO)
        self.play(FadeIn(tic_esc_b), run_time=0.2)
        self.play(bar_b.animate.stretch_to_fit_width(0.85, about_edge=LEFT),
                  run_time=0.3)
        continua = tag_junto(bar_b, "de inmediato", DOWN, buff=0.2, color=C_BUENO)
        self.play(FadeIn(continua), run_time=0.4)
        self.wait(4.2)

        cierre_leccion(self, rot, "Leer no deberia esperar", "a escribir.",
                       carril_a, carril_b, rot_a, rot_b, letra_a, qa, marca_a,
                       tic_begin, bar_a, obj_ix, tag_ix, xact, tag_xact,
                       letra_b, qb, marca_b, tic_esc_b, bar_b, continua,
                       espera=9.2)
