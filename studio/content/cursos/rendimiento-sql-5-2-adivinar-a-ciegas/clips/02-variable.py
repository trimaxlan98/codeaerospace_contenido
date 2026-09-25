class Clip2(Scene):
    """5.2.2 - Con una variable local el optimizador NO conoce el valor al
    compilar: el histograma se apaga y solo queda la densidad promedio, una
    barra plana que estima ~8 filas (cian sobre dibujo violeta). Con esa
    apuesta elige Seek + Lookup, una flecha delgada. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La variable: estima 8"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el codigo: la variable no revela su valor ----------------------
        q = S.codigo(["DECLARE @c INT = 1", "SELECT id_pedido, total",
                      "FROM pedidos", "WHERE id_cliente = @c"], font_size=20)
        q.move_to(LEFT * 3.9 + UP * 1.75)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        linea = "WHERE id_cliente = @c"
        plano = linea.replace(" ", "")
        i = plano.find("@c")
        marca = SurroundingRectangle(q.lineas[3][i:i + 2], color=C_CREE,
                                     buff=0.06, stroke_width=2.4)
        self.play(Create(marca), run_time=0.6)
        tag_var = tag_junto(q, "valor desconocido", DOWN, buff=0.22,
                            color=C_CREE)
        self.play(FadeIn(tag_var), run_time=0.4)
        self.wait(2.2)

        # --- el histograma se apaga ------------------------------------------
        base_y = -1.9
        barras = torre_histograma(base_y=base_y, color=C_TENUE)
        barras.shift(RIGHT * 2.4)
        base = Line(barras.get_left(), barras.get_right(),
                   stroke_color=C_TENUE, stroke_width=2)
        base.set_y(base_y)
        self.play(Create(base), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(b) for b in barras], lag_ratio=0.04),
                  run_time=1.2)
        for b in barras:
            b.set_fill(C_TENUE, 0.12).set_stroke(C_TENUE, opacity=0.35)
        tag_hist = tag_junto(barras, "no lo puede usar", UP, buff=0.3)
        self.play(FadeIn(tag_hist), run_time=0.5)
        self.wait(1.6)

        # --- la barra plana: la densidad promedio -----------------------------
        plano_bar = Rectangle(width=barras.width, height=0.5,
                              stroke_color=C_CREE, stroke_width=2.2,
                              fill_color=C_CREE, fill_opacity=0.5)
        plano_bar.move_to(barras.get_center())
        plano_bar.align_to(barras, DOWN)
        self.play(FadeIn(plano_bar, shift=UP * 0.15), run_time=0.7)
        tag_prom = tag_junto(plano_bar, "el promedio", DOWN, buff=0.22,
                             color=C_CREE)
        self.play(FadeIn(tag_prom), run_time=0.4)
        cif_est = tag_hud(f"~{round(ESTIMADO)} filas", font_size=20)
        cif_est.next_to(plano_bar, UP, buff=0.28)
        self.play(FadeIn(cif_est), run_time=0.5)
        self.wait(2.4)

        # --- el plan elegido: seek + lookup, una flecha delgada -----------------
        lookup = S.operador("Lookup", color=C_TITULO)
        seek = S.operador("Seek", color=C_TITULO)
        plan = VGroup(lookup, seek)
        plan.arrange(RIGHT, buff=2.0)
        plan.next_to(barras, DOWN, buff=0.7)
        f = S.flecha_plan(seek.get_left(), lookup.get_right(),
                          round(ESTIMADO), color=C_CREE)
        self.play(FadeIn(seek, shift=UP * 0.15), run_time=0.5)
        self.play(Create(f), FadeIn(lookup, shift=UP * 0.15), run_time=0.8)
        tag_plan = tag_junto(plan, "plan elegido", DOWN, buff=0.2)
        self.play(FadeIn(tag_plan), run_time=0.4)
        self.wait(3.2)
        self.play(Indicate(lookup, color=C_CREE, scale_factor=1.05),
                  run_time=0.8)
        self.wait(11.5)
