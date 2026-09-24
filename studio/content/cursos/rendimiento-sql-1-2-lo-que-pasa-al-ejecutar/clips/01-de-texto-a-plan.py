class Clip1(Scene):
    """1.2.1 - De texto a plan: la consulta entra como texto a una tuberia
    de cuatro etapas (analizar, vincular, optimizar, ejecutar) y sale
    convertida en un plan, un arbol de operadores. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("De texto a plan"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        q = S.codigo(["SELECT id_pedido, total", "FROM pedidos",
                      "WHERE id_cliente = 501"], font_size=20)
        q.to_corner(UL, buff=0.6).shift(DOWN * 0.7)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        et_texto = tag_junto(q, "texto", DOWN, buff=0.2)
        self.play(FadeIn(et_texto), run_time=0.4)
        self.wait(1.6)

        # --- la tuberia: cuatro etapas -------------------------------------
        nombres = ["analizar", "vincular", "optimizar", "ejecutar"]
        cajas = VGroup(*[S.operador(n, color=C_TENUE, ancho=2.5, alto=0.85,
                                    font_size=20) for n in nombres])
        cajas.arrange(RIGHT, buff=0.5)
        cajas.move_to(DOWN * 0.4)
        flechas = VGroup(*[Arrow(cajas[i].get_right(), cajas[i + 1].get_left(),
                                 buff=0.06, stroke_width=2.4, color=C_TENUE,
                                 max_tip_length_to_length_ratio=0.25)
                          for i in range(3)])
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in cajas],
                              lag_ratio=0.25), run_time=1.4)
        self.play(LaggedStart(*[Create(f) for f in flechas], lag_ratio=0.3),
                  run_time=1.0)
        self.wait(1.4)

        # --- la consulta atraviesa la tuberia: cada etapa se enciende ------
        # la ficha viaja POR DEBAJO de las cajas (nunca sobre el rotulo) y
        # el borde de cada caja se enciende cuando la ficha llega a su altura.
        ficha = Dot(radius=0.09, color=C_TITULO)
        ficha.move_to(cajas[0].get_bottom() + DOWN * 0.3)
        ficha.set_x(q.get_bottom()[0])
        self.play(FadeIn(ficha), run_time=0.4)
        self.wait(0.4)
        for caja in cajas:
            self.play(ficha.animate.set_x(caja.get_center()[0]),
                      caja.caja.animate.set_stroke(C_BUENO, width=3),
                      run_time=0.9)
            self.wait(0.7)
        self.play(FadeOut(ficha), run_time=0.3)
        self.wait(1.0)

        # --- la tuberia se apaga: ya hizo su trabajo ------------------------
        self.play(FadeOut(cajas), FadeOut(flechas), run_time=0.6)
        self.wait(0.3)

        # --- sale como plan: se lee de DERECHA A IZQUIERDA -------------------
        # (Select <- Filter <- Scan pedidos, como en 1.3); el grosor de cada
        # flecha son las filas de ESTA consulta (id_cliente = 501): C501.
        scan = S.operador("Scan pedidos", color=C_INDICE, ancho=2.6, alto=0.8,
                          font_size=20)
        filtro = S.operador("Filter", color=C_INDICE, ancho=1.9, alto=0.8,
                            font_size=20)
        select = S.operador("Select", color=C_INDICE, ancho=1.9, alto=0.8,
                            font_size=20)
        VGroup(select, filtro, scan).arrange(RIGHT, buff=1.3).move_to(DOWN * 1.0)
        f_sf = S.flecha_plan(scan.get_left(), filtro.get_right(), C501,
                             color=C_INDICE, max_filas=FILAS_PED)
        f_fs = S.flecha_plan(filtro.get_left(), select.get_right(), C501,
                             color=C_INDICE, max_filas=FILAS_PED)
        self.play(FadeIn(scan, shift=UP * 0.2), run_time=0.6)
        self.wait(0.4)
        self.play(Create(f_sf), FadeIn(filtro, shift=UP * 0.2), run_time=0.7)
        self.wait(0.4)
        self.play(Create(f_fs), FadeIn(select, shift=UP * 0.2), run_time=0.7)
        et_plan = tag_junto(VGroup(select, filtro, scan, f_sf, f_fs), "plan",
                            DOWN, buff=0.3)
        self.play(FadeIn(et_plan), run_time=0.4)
        self.wait(8.0)
