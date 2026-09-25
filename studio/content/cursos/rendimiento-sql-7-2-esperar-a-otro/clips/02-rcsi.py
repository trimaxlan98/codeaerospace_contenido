class Clip2(Scene):
    """7.2.2 - Leer sin esperar (RCSI): dos carriles de tiempo. En A, la
    barra roja de transaccion abierta sigue creciendo; en B, una barra
    corta y VERDE desde el principio: no espera, porque lee la version
    anterior. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Leer sin esperar"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- los dos carriles de tiempo -------------------------------------------
        y_a, y_b = 0.85, -1.75
        carril_a = carril_tiempo(y_a)
        carril_b = carril_tiempo(y_b)
        rot_a = Text("A", font_size=26, color=C_TITULO)
        rot_a.next_to([-6.0, y_a, 0], LEFT, buff=0.25)
        rot_b = Text("B", font_size=26, color=C_TITULO)
        rot_b.next_to([-6.0, y_b, 0], LEFT, buff=0.25)
        self.play(Create(carril_a), Create(carril_b), FadeIn(rot_a),
                  FadeIn(rot_b), run_time=0.7)
        self.wait(1.5)

        # --- A: codigo compacto arriba ---------------------------------------------
        letra_a = Text("A", font_size=24, color=C_TITULO)
        letra_a.move_to(LEFT * 3.9 + UP * 3.0)
        qa = S.codigo(["UPDATE pedidos", "SET estatus = 'enviado'",
                      f"WHERE id_pedido = {ID_PEDIDO}"], font_size=18)
        qa.next_to(letra_a, DOWN, buff=0.18)
        self.play(FadeIn(letra_a), FadeIn(qa, shift=LEFT * 0.2), run_time=0.7)
        self.wait(1.2)

        marca_a = SurroundingRectangle(qa.lineas, color=C_MALO, buff=0.06,
                                       stroke_width=2.2)
        self.play(Create(marca_a), run_time=0.6)

        x_begin, x_evento, x_ahora = -5.6, -0.3, 4.4
        tic_begin = marca_tiempo(x_begin, y_a)
        bar_a = barra_tiempo(x_begin, y_a, color=C_MALO)
        self.play(FadeIn(tic_begin), FadeIn(bar_a), run_time=0.4)
        self.play(bar_a.animate.stretch_to_fit_width(x_evento - x_begin,
                                                      about_edge=LEFT),
                  run_time=0.9)

        # --- A modifica; la version anterior se guarda aparte, en medio de -----------
        # los dos carriles (zona libre: lejos de los paneles y de las barras) --------
        y_mid = -0.45
        resource = RoundedRectangle(width=1.5, height=0.5, corner_radius=0.08,
                                    stroke_color=C_MALO, stroke_width=2.4,
                                    fill_color=C_MALO, fill_opacity=0.30)
        resource.move_to([x_evento - 0.85, y_mid, 0])
        version = resource.copy()
        version.set_stroke(C_TENUE, opacity=0.8).set_fill(C_TENUE, 0.18)
        version.move_to([x_evento + 0.75, y_mid, 0])
        guia_v = DashedLine(resource.get_right(), version.get_left(),
                            dash_length=0.1, stroke_color=C_TENUE,
                            stroke_width=1.6)
        tic_evento_a = marca_tiempo(x_evento, y_a)
        nom_r = Text("pedido", font_size=19, color=C_TITULO)
        nom_r.next_to(resource, UP, buff=0.12)
        self.play(FadeIn(resource, scale=0.7), FadeIn(nom_r),
                  FadeIn(tic_evento_a), run_time=0.6)
        self.play(TransformFromCopy(resource, version), Create(guia_v),
                  run_time=0.8)
        nom_v = Text("version anterior", font_size=22, color=C_TENUE)
        nom_v.next_to(version, UP, buff=0.16)
        almacen = tag_junto(version, "almacen de versiones", DOWN, buff=0.2,
                            color=C_TENUE)
        self.play(FadeIn(nom_v), FadeIn(almacen), run_time=0.4)
        self.wait(2.4)

        # --- A sigue abierta: la barra sigue creciendo -------------------------------
        self.play(bar_a.animate.stretch_to_fit_width(x_ahora - x_begin,
                                                      about_edge=LEFT),
                  run_time=2.4, rate_func=linear)

        # --- B: codigo compacto arriba, lee la version y NO espera -------------------
        letra_b = Text("B", font_size=24, color=C_TITULO)
        letra_b.move_to(RIGHT * 3.9 + UP * 3.0)
        qb = S.codigo(["SELECT estatus", "FROM pedidos",
                      f"WHERE id_pedido = {ID_PEDIDO}"], font_size=18)
        qb.next_to(letra_b, DOWN, buff=0.18)
        self.play(FadeIn(letra_b), FadeIn(qb, shift=RIGHT * 0.2), run_time=0.7)
        marca_b = SurroundingRectangle(qb.lineas[2], color=C_BUENO, buff=0.05,
                                       stroke_width=2.2)
        self.play(Create(marca_b), run_time=0.7)

        tic_evento_b = marca_tiempo(x_evento, y_b)
        bar_b = barra_tiempo(x_evento, y_b, color=C_BUENO)
        self.play(FadeIn(tic_evento_b), run_time=0.2)
        self.play(bar_b.animate.stretch_to_fit_width(0.85, about_edge=LEFT),
                  run_time=0.3)
        continua = tag_junto(bar_b, "no espera", DOWN, buff=0.2, color=C_BUENO)
        self.play(FadeIn(continua), run_time=0.4)
        self.wait(13.0)
