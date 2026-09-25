class Clip2(Scene):
    """6.1.2 - El 501 llega primero: compila Seek + Lookup, un plan barato
    para 191 filas. El mayorista reusa ese MISMO plan sin recompilar, y le
    sale carisimo: 459,555 lecturas contra 597. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El 501 primero"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        # --- primera llamada: compila Seek + Lookup ---------------------------
        llamada = S.codigo(["EXEC usp_PedidosCliente 501"], font_size=18)
        llamada.to_corner(UL, buff=0.6).shift(DOWN * 0.5)
        self.play(FadeIn(llamada, shift=RIGHT * 0.2), run_time=0.6)
        et_ll = tag_junto(llamada, "primera llamada", DOWN, buff=0.2)
        self.play(FadeIn(et_ll), run_time=0.4)
        self.wait(1.4)

        lookup = S.operador("Lookup", color=C_TITULO, ancho=2.3, alto=0.85,
                            font_size=22)
        seek = S.operador("Seek", color=C_TITULO, ancho=2.0, alto=0.85,
                          font_size=22)
        plan = VGroup(lookup, seek)
        plan.arrange(RIGHT, buff=1.8).move_to(UP * 0.3)
        f = S.flecha_plan(seek.get_left(), lookup.get_right(), C501,
                          color=C_INDICE, max_filas=FILAS_PED)
        self.play(FadeIn(seek, shift=UP * 0.15), run_time=0.5)
        self.play(Create(f), FadeIn(lookup, shift=UP * 0.15), run_time=0.7)
        et_plan = tag_junto(plan, "plan guardado", DOWN, buff=0.35)
        self.play(FadeIn(et_plan), run_time=0.4)
        self.wait(1.6)

        # --- el mayorista reusa el mismo plan, sin recompilar ------------------
        self.play(FadeOut(llamada), FadeOut(et_ll), run_time=0.4)
        llamada2 = S.codigo(["EXEC usp_PedidosCliente 1"], font_size=18)
        llamada2.to_corner(UL, buff=0.6).shift(DOWN * 0.5)
        self.play(FadeIn(llamada2, shift=RIGHT * 0.2), run_time=0.6)
        et_ll2 = tag_junto(llamada2, "el mayorista", DOWN, buff=0.2,
                           color=C_MALO)
        self.play(FadeIn(et_ll2), run_time=0.4)
        self.play(Indicate(plan, color=C_MALO, scale_factor=1.06), run_time=0.7)
        self.wait(1.6)

        grupo_plan = VGroup(llamada2, et_ll2, seek, lookup, f, et_plan)
        self.play(FadeOut(grupo_plan), run_time=0.6)

        # --- el duelo: mismo plan, dos costos muy distintos --------------------
        largo = 7.2
        maximo = SNIFF_501_1[1]
        base_x = LEFT * 3.6

        bar_verde = S.barra_lecturas(SNIFF_501_1[0], maximo, largo=largo,
                                     alto=0.6, color=C_BUENO, log=True)
        bar_verde.shift(base_x + UP * 0.7)
        bar_roja = S.barra_lecturas(SNIFF_501_1[1], maximo, largo=largo,
                                    alto=0.6, color=C_MALO, log=True)
        bar_roja.shift(base_x + DOWN * 1.1)

        base = Line(base_x + UP * 1.5, base_x + DOWN * 1.9,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.6)

        lab_v = tag_junto(bar_verde, "cliente 501", LEFT, buff=0.3,
                          color=C_BUENO)
        self.play(GrowFromEdge(bar_verde, LEFT), FadeIn(lab_v), run_time=0.9)
        tag_v = tag_motor(lecturas(SNIFF_501_1[0]))
        tag_v.next_to(bar_verde, RIGHT, buff=0.22)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(1.6)

        lab_r = tag_junto(bar_roja, "cliente 1", LEFT, buff=0.3,
                          color=C_MALO)
        self.play(GrowFromEdge(bar_roja, LEFT), FadeIn(lab_r), run_time=0.9)
        tag_r = tag_motor(lecturas(SNIFF_501_1[1]))
        tag_r.next_to(bar_roja, RIGHT, buff=0.22)
        self.play(FadeIn(tag_r), run_time=0.4)
        self.wait(2.0)

        razon = S.razon(SNIFF_501_1[1], SNIFF_501_1[0])
        rot.mostrar(cifra_pie(f"{S.miles(round(razon))}x mas lecturas"),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(bar_verde, color=C_BUENO, scale_factor=1.06),
                  Indicate(bar_roja, color=C_MALO, scale_factor=1.04),
                  run_time=1.0)
        self.wait(9.0)
