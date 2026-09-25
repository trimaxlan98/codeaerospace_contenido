class Clip3(Scene):
    """6.1.3 - Esta vez el mayorista llega primero: compila un Scan
    completo, barato para sus 149,970 filas. El 501 reusa ese MISMO plan y
    paga el mismo scan completo por solo 191 filas: 22,363 lecturas para
    los dos. Misma composicion que el clip 2, para comparar. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El mayorista primero"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        # --- primera llamada: compila un Scan completo -------------------------
        llamada = S.codigo(["EXEC usp_PedidosCliente 1"], font_size=18)
        llamada.to_corner(UL, buff=0.6).shift(DOWN * 0.5)
        self.play(FadeIn(llamada, shift=RIGHT * 0.2), run_time=0.6)
        et_ll = tag_junto(llamada, "primera llamada", DOWN, buff=0.2)
        self.play(FadeIn(et_ll), run_time=0.4)
        self.wait(1.4)

        scan = S.operador("Scan pedidos", color=C_TITULO, ancho=3.0,
                          alto=0.85, font_size=22)
        scan.move_to(UP * 0.3)
        self.play(FadeIn(scan, shift=UP * 0.15), run_time=0.6)
        et_plan = tag_junto(scan, "plan guardado", DOWN, buff=0.35)
        self.play(FadeIn(et_plan), run_time=0.4)
        self.wait(1.6)

        # --- el 501 reusa el mismo scan completo ---------------------------------
        self.play(FadeOut(llamada), FadeOut(et_ll), run_time=0.4)
        llamada2 = S.codigo(["EXEC usp_PedidosCliente 501"], font_size=18)
        llamada2.to_corner(UL, buff=0.6).shift(DOWN * 0.5)
        self.play(FadeIn(llamada2, shift=RIGHT * 0.2), run_time=0.6)
        et_ll2 = tag_junto(llamada2, "el 501", DOWN, buff=0.2, color=C_MALO)
        self.play(FadeIn(et_ll2), run_time=0.4)
        self.play(Indicate(scan, color=C_MALO, scale_factor=1.06), run_time=0.7)
        self.wait(1.6)

        grupo_plan = VGroup(llamada2, et_ll2, scan, et_plan)
        self.play(FadeOut(grupo_plan), run_time=0.6)

        # --- el duelo: mismo plan, mismo costo para los dos ----------------------
        largo = 7.2
        maximo = SNIFF_1_501[0]
        base_x = LEFT * 3.6

        bar_verde = S.barra_lecturas(SNIFF_1_501[0], maximo, largo=largo,
                                     alto=0.6, color=C_BUENO, log=True)
        bar_verde.shift(base_x + UP * 0.7)
        bar_roja = S.barra_lecturas(SNIFF_1_501[1], maximo, largo=largo,
                                    alto=0.6, color=C_MALO, log=True)
        bar_roja.shift(base_x + DOWN * 1.1)

        base = Line(base_x + UP * 1.5, base_x + DOWN * 1.9,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.6)

        lab_v = tag_junto(bar_verde, "cliente 1", LEFT, buff=0.3,
                          color=C_BUENO)
        self.play(GrowFromEdge(bar_verde, LEFT), FadeIn(lab_v), run_time=0.9)
        tag_v = tag_motor(lecturas(SNIFF_1_501[0]))
        tag_v.next_to(bar_verde, RIGHT, buff=0.22)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(1.6)

        lab_r = tag_junto(bar_roja, "cliente 501", LEFT, buff=0.3,
                          color=C_MALO)
        self.play(GrowFromEdge(bar_roja, LEFT), FadeIn(lab_r), run_time=0.9)
        tag_r = tag_motor(lecturas(SNIFF_1_501[1]))
        tag_r.next_to(bar_roja, RIGHT, buff=0.22)
        self.play(FadeIn(tag_r), run_time=0.4)
        self.wait(2.0)

        et_mismo = tag_junto(VGroup(bar_verde, bar_roja), "mismo costo, dos clientes",
                             DOWN, buff=0.9)
        self.play(FadeIn(et_mismo), run_time=0.5)
        self.play(Indicate(bar_verde, color=C_BUENO, scale_factor=1.06),
                  Indicate(bar_roja, color=C_MALO, scale_factor=1.04),
                  run_time=1.0)
        self.wait(9.0)
