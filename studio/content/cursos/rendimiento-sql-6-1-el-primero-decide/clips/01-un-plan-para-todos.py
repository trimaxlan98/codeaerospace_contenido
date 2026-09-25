class Clip1(Scene):
    """6.1.1 - Un procedimiento con un parametro: la PRIMERA llamada compila
    y el plan se guarda en la cache; las siguientes llamadas, aunque manden
    OTRO valor de id_cliente, reusan ese mismo plan sin volver a decidir
    nada. (~29 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Un plan para todos"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        # --- el procedimiento: un solo parametro ----------------------------
        proc = S.codigo(["CREATE PROCEDURE usp_PedidosCliente",
                         "  @id_cliente INT", "AS SELECT id_pedido, total",
                         "FROM pedidos WHERE id_cliente=@id_cliente"],
                        font_size=18)
        proc.to_corner(UL, buff=0.6).shift(DOWN * 0.5)
        self.play(FadeIn(proc, shift=RIGHT * 0.2), run_time=0.7)
        et_proc = tag_junto(proc, "un parametro", DOWN, buff=0.2)
        self.play(FadeIn(et_proc), run_time=0.4)
        self.wait(1.8)
        self.play(FadeOut(proc), FadeOut(et_proc), run_time=0.5)

        # --- la cache, vacia --------------------------------------------------
        cache = RoundedRectangle(width=4.2, height=3.0, corner_radius=0.16,
                                 stroke_color=C_TENUE, stroke_width=2.0,
                                 fill_color=C_TENUE, fill_opacity=0.06)
        cache.move_to(RIGHT * 0.5 + DOWN * 0.2)
        et_cache = tag_junto(cache, "cache de planes", UP, buff=0.28)
        self.play(FadeIn(cache), FadeIn(et_cache), run_time=0.7)
        self.wait(1.0)

        entrada = cache.get_center() + LEFT * 1.3
        plan = S.operador("Plan", color=C_TITULO, ancho=2.0, alto=0.9,
                          font_size=24)
        plan.move_to(cache.get_center() + RIGHT * 0.3)

        valores = ["501", "2500", "1"]
        for i, v in enumerate(valores):
            llamada = S.codigo([f"EXEC usp_PedidosCliente {v}"],
                               font_size=18)
            llamada.to_corner(UL, buff=0.6).shift(DOWN * 0.5)
            self.play(FadeIn(llamada, shift=RIGHT * 0.2), run_time=0.6)

            color = C_TENUE if i == 0 else C_BUENO
            etiqueta = "compilar" if i == 0 else "reusar"
            flecha = Arrow(llamada.get_bottom() + DOWN * 0.1, entrada,
                          buff=0.05, stroke_width=3.0, color=color,
                          max_tip_length_to_length_ratio=0.15)
            et_fl = tag_junto(flecha, etiqueta, UP, buff=0.16, color=color)
            self.play(Create(flecha), FadeIn(et_fl), run_time=0.6)

            if i == 0:
                self.play(FadeIn(plan, shift=RIGHT * 0.2), run_time=0.6)
            else:
                self.play(Indicate(plan, color=C_BUENO, scale_factor=1.08),
                          run_time=0.6)
            self.wait(1.0)
            self.play(FadeOut(llamada), FadeOut(flecha), FadeOut(et_fl),
                      run_time=0.5)

        et_final = tag_junto(cache, "mismo plan, otro valor", DOWN, buff=0.3)
        self.play(FadeIn(et_final), run_time=0.5)
        self.wait(11.5)
