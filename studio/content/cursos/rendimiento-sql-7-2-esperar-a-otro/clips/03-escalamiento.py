class Clip3(Scene):
    """7.2.3 - Escalamiento: dos carriles de tiempo y, en medio, una
    rejilla grande de candados de fila que crece con A hasta pasar de
    5,000 (dato publico) y se convierte en UN candado sobre la tabla
    entera. B, que solo quiere OTRO pedido, tambien queda atrapado en su
    carril. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Escalamiento"), zona="arriba", run_time=0.6)
        self.wait(0.4)

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

        # --- A: codigo compacto arriba, el UPDATE del mayorista ---------------------
        letra_a = Text("A", font_size=24, color=C_TITULO)
        letra_a.move_to(LEFT * 3.9 + UP * 3.0)
        qa = S.codigo(["UPDATE TOP (10000) pedidos",
                      "SET estatus = 'enviado'",
                      "WHERE id_cliente = 1"], font_size=18)
        qa.next_to(letra_a, DOWN, buff=0.18)
        self.play(FadeIn(letra_a), FadeIn(qa, shift=LEFT * 0.2), run_time=0.7)
        marca_a = SurroundingRectangle(qa.lineas, color=C_MALO, buff=0.06,
                                       stroke_width=2.2)
        self.play(Create(marca_a), run_time=0.6)

        x_begin, x_esc, x_end = -5.6, 0.5, 4.3
        tic_begin = marca_tiempo(x_begin, y_a)
        bar_a = barra_tiempo(x_begin, y_a, color=C_MALO)
        self.play(FadeIn(tic_begin), FadeIn(bar_a), run_time=0.4)
        self.play(bar_a.animate.stretch_to_fit_width(x_esc - x_begin,
                                                      about_edge=LEFT),
                  run_time=1.0)

        # --- la rejilla: candados de fila acumulandose, grande y separada -----------
        grid = RejillaCandados(columnas=30, filas=7, lado=0.16, sep=0.05,
                               color=C_MALO, opacidad=0.0)
        grid.move_to([0.0, -0.35, 0])
        self.play(LaggedStart(*[FadeIn(c) for c in grid], lag_ratio=0.004),
                  run_time=1.2)

        x_thr = grid.get_left()[0] + grid.width * FRAC_UMBRAL
        marca_umbral = DashedLine([x_thr, grid.get_bottom()[1] - 0.06, 0],
                                  [x_thr, grid.get_bottom()[1] - 0.34, 0],
                                  dash_length=0.06, stroke_color=C_TENUE,
                                  stroke_width=2.2)
        self.play(Create(marca_umbral), run_time=0.5)
        rot.mostrar(dato_pie(f"{S.miles(UMBRAL)} bloqueos"), zona="abajo",
                    run_time=0.5)
        self.wait(0.6)

        cont = Contador(0, rotulo="bloqueados", font_size=30, digitos=5,
                        color=C_TENUE)
        cont.move_to([grid.get_right()[0] + 0.4 + cont.width / 2, -0.35, 0])
        self.play(FadeIn(cont), run_time=0.4)
        cont.anim(self, TOP_FILAS, run_time=3.2,
                  extra=[LaggedStart(*grid.encender(range(len(grid)), C_MALO, 0.8),
                                     lag_ratio=0.004)])
        self.wait(1.0)

        # --- escalamiento: UN candado sobre la tabla entera --------------------------
        grande = candado(lado=1.1, color=C_MALO)
        grande.move_to(grid.get_center())
        self.play(FadeOut(grid), FadeOut(cont), FadeOut(marca_umbral),
                  run_time=0.7)
        self.play(FadeIn(grande, scale=0.7), run_time=0.6)
        obj_x = tag_hud("OBJECT X", font_size=22, color=C_TENUE)
        obj_x.next_to(grande, UP, buff=0.22)
        self.play(FadeIn(obj_x), run_time=0.4)
        self.wait(1.0)

        # --- las dos barras siguen creciendo: A no ha soltado nada -------------------
        self.play(bar_a.animate.stretch_to_fit_width(x_end - x_begin,
                                                      about_edge=LEFT),
                  run_time=1.6, rate_func=linear)

        # --- B quiere OTRO pedido, y tambien queda atrapado --------------------------
        letra_b = Text("B", font_size=24, color=C_TITULO)
        letra_b.move_to(RIGHT * 3.9 + UP * 3.0)
        qb = S.codigo(["UPDATE pedidos", "SET estatus = 'enviado'",
                      f"WHERE id_pedido = {ID_OTRO}"], font_size=18)
        qb.next_to(letra_b, DOWN, buff=0.18)
        self.play(FadeIn(letra_b), FadeIn(qb, shift=RIGHT * 0.2), run_time=0.7)
        marca_b = SurroundingRectangle(qb.lineas[2], color=C_TENUE, buff=0.05,
                                       stroke_width=2)
        self.play(Create(marca_b), run_time=0.5)

        tic_esc_b = marca_tiempo(x_esc, y_b)
        bar_b = barra_tiempo(x_esc, y_b, color=C_MALO)
        self.play(FadeIn(tic_esc_b), FadeIn(bar_b), run_time=0.4)
        lck = tag_hud("LCK_M_IX", font_size=22, color=C_TENUE)
        lck.next_to(bar_b, UP, buff=0.18)
        self.play(FadeIn(lck), run_time=0.4)

        self.play(bar_a.animate.stretch_to_fit_width(x_end + 1.0 - x_begin,
                                                      about_edge=LEFT),
                  bar_b.animate.stretch_to_fit_width(x_end + 1.0 - x_esc,
                                                     about_edge=LEFT),
                  run_time=2.2, rate_func=linear)
        self.wait(8.5)
