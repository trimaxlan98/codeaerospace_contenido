class Clip1(Scene):
    """6.2.1 - RECOMPILE: el plan se compila EN CADA ejecucion con el valor
    real, asi que cada cliente recibe su propio plan bueno (501 -> Seek +
    Lookup, el mayorista -> Scan). El costo es CPU de compilar cada vez: sin
    medicion de tiempo en la libreria, se dibuja como una barra igual en
    ambas ejecuciones, sin cifra. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Un plan nuevo cada vez"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        q = S.codigo(["SELECT id_pedido, total",
                      "FROM pedidos",
                      "WHERE id_cliente = @id_cliente",
                      "OPTION (RECOMPILE)"], font_size=19)
        q.to_corner(UL, buff=0.55).shift(DOWN * 0.6)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        marco = SurroundingRectangle(q.lineas[3], color=C_TITULO, buff=0.06,
                                     stroke_width=2.2)
        self.play(Create(marco), run_time=0.6)
        self.wait(0.9)

        # --- columnas comunes a las dos filas (lejos del panel de codigo) --
        x_cli, x_bar, x_op = 0.3, 2.2, 4.5

        # --- lane 1: cliente 501 -> compila -> su propio plan bueno --------
        y1 = 1.55
        b501 = caja_cliente("501", color=C_TENUE, ancho=1.4)
        b501.move_to(RIGHT * x_cli + UP * y1)
        et501 = tag_junto(b501, "cliente 501", UP, buff=0.2)
        self.play(FadeIn(b501), FadeIn(et501), run_time=0.6)
        self.wait(0.6)

        bar1 = barra_compilar()
        bar1.move_to(RIGHT * x_bar + UP * y1)
        fl_a1 = Arrow(b501.get_right(), bar1.get_left(), buff=0.1,
                     stroke_width=2.2, color=C_TENUE,
                     max_tip_length_to_length_ratio=0.25)
        self.play(Create(fl_a1), GrowFromEdge(bar1, DOWN), run_time=0.8)
        et_c1 = tag_junto(bar1, "compila", DOWN, buff=0.2)
        self.play(FadeIn(et_c1), run_time=0.4)
        self.wait(0.6)

        op1 = S.operador("Seek + Lookup", color=C_BUENO, ancho=2.8, alto=0.85,
                         font_size=22)
        op1.move_to(RIGHT * x_op + UP * y1)
        fl_b1 = Arrow(bar1.get_right(), op1.get_left(), buff=0.1,
                     stroke_width=2.2, color=C_TENUE,
                     max_tip_length_to_length_ratio=0.25)
        self.play(Create(fl_b1), FadeIn(op1, shift=LEFT * 0.15), run_time=0.7)
        rot.mostrar(motor_pie(lecturas(LOOKUP_501)), zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- lane 2: el mayorista -> compila -> SU propio plan bueno --------
        y2 = -1.55
        b1 = caja_cliente("mayorista", color=C_TENUE, ancho=2.3)
        b1.move_to(RIGHT * x_cli + UP * y2)
        et1 = tag_junto(b1, "el mayorista", UP, buff=0.2)
        self.play(FadeIn(b1), FadeIn(et1), run_time=0.6)
        self.wait(0.6)

        bar2 = barra_compilar()
        bar2.move_to(RIGHT * x_bar + UP * y2)
        fl_a2 = Arrow(b1.get_right(), bar2.get_left(), buff=0.1,
                     stroke_width=2.2, color=C_TENUE,
                     max_tip_length_to_length_ratio=0.25)
        self.play(Create(fl_a2), GrowFromEdge(bar2, DOWN), run_time=0.8)
        et_c2 = tag_junto(bar2, "compila", DOWN, buff=0.2)
        self.play(FadeIn(et_c2), run_time=0.4)
        self.wait(0.6)

        op2 = S.operador("Scan", color=C_BUENO, ancho=2.2, alto=0.85,
                         font_size=22)
        op2.move_to(RIGHT * x_op + UP * y2)
        fl_b2 = Arrow(bar2.get_right(), op2.get_left(), buff=0.1,
                     stroke_width=2.2, color=C_TENUE,
                     max_tip_length_to_length_ratio=0.25)
        self.play(Create(fl_b2), FadeIn(op2, shift=LEFT * 0.15), run_time=0.7)
        rot.mostrar(motor_pie(lecturas(SCAN_1)), zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- moraleja: nunca se reusa nada (centrada, lejos de las cifras) --
        cierre = tag_junto(op1, "no hay plan guardado", DOWN, buff=0.3,
                           color=C_TENUE)
        cierre.move_to(RIGHT * x_bar)
        self.play(FadeIn(cierre), run_time=0.5)
        self.wait(11.0)
