class Clip4(Scene):
    """4.3.4 - OR entre dos columnas, cada una con su propio indice: el
    motor no revisa nada por fuerza bruta. Plan horizontal, leido de
    derecha a izquierda: dos "Index Seek" (cada uno con su arbol mediano y
    su ruta verde) entran a un operador de Concatenation, que entra a
    Select. Las flechas van de caja a caja (nunca desde las hojas de un
    arbol), y no se cruzan entre si ni con los arboles. Cierre de la
    leccion. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Dos seeks"), zona="arriba", run_time=0.6)
        self.wait(0.6)

        q = S.codigo(["SELECT id_pedido", "FROM pedidos",
                      "WHERE id_cliente = 501",
                      "   OR fecha_pedido >= '2026-09-19'"], font_size=20)
        q.to_corner(UL, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        self.wait(1.6)

        # --- el PLAN: derecha a izquierda. A la derecha del todo, los dos
        # arboles (lo que hay dentro de cada indice); a su izquierda, la
        # caja "Index Seek" que los usa; luego Concatenation; luego Select.
        seek_a = S.operador("Index Seek", color=C_TITULO, ancho=2.6, alto=0.7,
                            font_size=21)
        seek_a.move_to(RIGHT * 1.6 + UP * 1.55)
        tree_a = S.ArbolB(anchos=(1, 3, 6), ancho=2.9, alto=1.5, lado=0.24,
                          color=C_TENUE)
        tree_a.move_to(RIGHT * 4.75 + UP * 1.55)
        guia_a = DashedLine(seek_a.get_right(), tree_a.get_left(),
                            dash_length=0.08, stroke_color=C_TENUE,
                            stroke_width=1.4)

        seek_b = S.operador("Index Seek", color=C_TITULO, ancho=2.6, alto=0.7,
                            font_size=21)
        seek_b.move_to(RIGHT * 1.6 + DOWN * 1.55)
        tree_b = S.ArbolB(anchos=(1, 3, 6), ancho=2.9, alto=1.5, lado=0.24,
                          color=C_TENUE)
        tree_b.move_to(RIGHT * 4.75 + DOWN * 1.55)
        guia_b = DashedLine(seek_b.get_right(), tree_b.get_left(),
                            dash_length=0.08, stroke_color=C_TENUE,
                            stroke_width=1.4)

        self.play(FadeIn(seek_a, shift=LEFT * 0.15), run_time=0.5)
        et_a = tag_junto(seek_a, "indice cliente", UP, buff=0.22)
        self.play(FadeIn(et_a), run_time=0.4)
        self.play(Create(guia_a), FadeIn(tree_a), run_time=0.7)
        ruta_a = tree_a.ruta(2)
        self.play(*[p[0].animate.set_fill(C_BUENO, 0.85).set_stroke(C_BUENO)
                    for p in ruta_a], run_time=0.6)
        self.wait(1.0)

        self.play(FadeIn(seek_b, shift=LEFT * 0.15), run_time=0.5)
        et_b = tag_junto(seek_b, "indice fecha", DOWN, buff=0.22)
        self.play(FadeIn(et_b), run_time=0.4)
        self.play(Create(guia_b), FadeIn(tree_b), run_time=0.7)
        ruta_b = tree_b.ruta(4)
        self.play(*[p[0].animate.set_fill(C_BUENO, 0.85).set_stroke(C_BUENO)
                    for p in ruta_b], run_time=0.6)
        self.wait(1.2)

        # --- se unen: Concatenation, con una flecha de plan por CAJA --------
        concat = S.operador("Concatenation", color=C_TITULO, ancho=2.9,
                            alto=0.7, font_size=20)
        concat.move_to(LEFT * 1.7)
        self.play(FadeIn(concat, shift=LEFT * 0.15), run_time=0.5)

        flecha_a = S.flecha_plan(seek_a.get_left(), concat.get_right(),
                                 C501, color=C_BUENO)
        flecha_b = S.flecha_plan(seek_b.get_left(), concat.get_right(),
                                 FECHA_FILAS, color=C_BUENO)
        self.play(Create(flecha_a), Create(flecha_b), run_time=0.9)
        et_concat = tag_junto(concat, "dos resultados en uno", DOWN,
                              buff=0.22)
        self.play(FadeIn(et_concat), run_time=0.4)
        self.wait(2.0)

        # --- Select, al final del plan (mas a la izquierda) ------------------
        select = S.operador("Select", color=C_TITULO, ancho=2.2, alto=0.7,
                            font_size=21)
        select.move_to(LEFT * 5.0)
        self.play(FadeIn(select, shift=LEFT * 0.15), run_time=0.5)
        flecha_c = S.flecha_plan(concat.get_left(), select.get_right(),
                                 C501 + FECHA_FILAS, color=C_TENUE)
        self.play(Create(flecha_c), run_time=0.6)
        self.wait(1.6)

        rot.mostrar(motor_pie(lecturas(OR_DOS_SEEKS)), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        cierre_leccion(self, rot, "El motor busca rangos.",
                       "Dale rangos que pueda ver.",
                       q, seek_a, tree_a, guia_a, et_a, seek_b, tree_b,
                       guia_b, et_b, concat, flecha_a, flecha_b, et_concat,
                       select, flecha_c, espera=5.5)
