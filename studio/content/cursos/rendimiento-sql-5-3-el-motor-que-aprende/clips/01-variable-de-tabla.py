class Clip1(Scene):
    """5.3.1 - Una variable de tabla @t se llena con los pedidos del cliente
    1 (149,970 filas, cian). Pero con el nivel de compatibilidad viejo el
    optimizador SIEMPRE supone que una variable de tabla tiene 1 fila, sin
    importar cuantas le lleguen: el plan (Join <- Scan @t) se dibuja con
    una flecha delgada, violeta, rotulada "cree 1 fila". (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Variable de tabla"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el codigo: se llena la variable de tabla -----------------------
        q = S.codigo(["DECLARE @t TABLE(id INT)", "INSERT INTO @t",
                      "SELECT id_pedido FROM pedidos",
                      "WHERE id_cliente = 1"], font_size=20)
        q.move_to(LEFT * 3.5 + UP * 1.75)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        linea = "DECLARE @t TABLE(id INT)"
        plano = linea.replace(" ", "")
        i = plano.find("@t")
        marca = SurroundingRectangle(q.lineas[0][i:i + 2], color=C_TITULO,
                                     buff=0.06, stroke_width=2.4)
        self.play(Create(marca), run_time=0.6)
        tag_var = tag_junto(q, "una variable de tabla", DOWN, buff=0.24)
        self.play(FadeIn(tag_var), run_time=0.4)
        self.wait(1.8)

        # --- la caja @t se llena con las filas reales -------------------------
        caja = caja_tabla("@t", ancho=3.0, alto=1.7, color=C_TITULO,
                          font_size=28)
        caja.move_to(RIGHT * 3.2 + UP * 1.3)
        self.play(FadeIn(caja, shift=LEFT * 0.2), run_time=0.6)

        relleno = Rectangle(width=caja.caja.width - 0.3,
                           height=caja.caja.height - 0.4, stroke_width=0,
                           fill_color=C_CALCULO, fill_opacity=0.22)
        relleno.move_to(caja.caja).align_to(caja.caja, DOWN).shift(UP * 0.08)
        self.play(GrowFromEdge(relleno, DOWN), run_time=1.2)
        cif_c1 = tag_hud(f"{S.miles(C1)} filas", font_size=21)
        cif_c1.next_to(caja, DOWN, buff=0.3)
        self.play(FadeIn(cif_c1), run_time=0.5)
        tag_cli = tag_junto(caja, "cliente 1", RIGHT, buff=0.3,
                            color=C_CALCULO)
        self.play(FadeIn(tag_cli), run_time=0.4)
        self.wait(2.2)

        # --- el plan: el optimizador supone 1 fila, sin importar cuantas ------
        scan_op = S.operador("Scan @t", color=C_TITULO, ancho=2.6)
        join_op = S.operador("Join", color=C_TITULO)
        scan_op.move_to(RIGHT * 2.6 + DOWN * 1.7)
        join_op.move_to(LEFT * 1.2 + DOWN * 1.7)
        flecha = S.flecha_plan(scan_op.get_left(), join_op.get_right(),
                               SUPUESTO_TVAR, color=C_CREE)
        self.play(FadeIn(scan_op, shift=UP * 0.15), run_time=0.5)
        self.play(Create(flecha), FadeIn(join_op, shift=UP * 0.15),
                  run_time=0.8)
        tag_cree = tag_junto(flecha, "cree 1 fila", DOWN, buff=0.22,
                             color=C_CREE)
        self.play(FadeIn(tag_cree), run_time=0.4)
        self.wait(2.6)

        self.play(Indicate(flecha, color=C_CREE, scale_factor=1.4),
                  run_time=0.9)
        self.wait(17.0)
