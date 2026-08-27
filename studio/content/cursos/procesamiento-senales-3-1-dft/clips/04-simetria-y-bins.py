class Clip4(Scene):
    """3.1.4 - Que frecuencia es cada bin, por que la mitad de arriba es
    un espejo, y que pasa si el tono no cae en un bin. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Simetria y bins"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        bar = barras(MAG, ancho=8.6, alto=2.5, rango_y=(0.0, 9.0))
        bar.move_to(DOWN * 0.15)
        et_k = VGroup(*[tag_hud(str(k), font_size=17, color=C_TENUE)
                        for k in range(N_DFT)])
        for i, e in enumerate(et_k):
            e.next_to(bar.barra(i), DOWN, buff=0.12)
        self.play(FadeIn(bar), LaggedStart(*[FadeIn(e) for e in et_k],
                                           lag_ratio=0.03), run_time=1.4)
        self.wait(1.4)

        # --- el bin y su frecuencia -----------------------------------------
        marca = bar.barra(K_BUENO).copy().set_fill(C_CALCULO, opacity=0.9)
        self.play(FadeIn(marca), run_time=0.5)
        rot.mostrar(cifra_pie(f"bin {K_BUENO} = {fmt(F_BIN_BUENO, 0)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- el espejo -------------------------------------------------------
        espejo = bar.barra(K_ESPEJO).copy().set_fill(C_MUESTRA, opacity=0.9)
        flecha = CurvedArrow(bar.cima(K_BUENO) + UP * 0.28,
                             bar.cima(K_ESPEJO) + UP * 0.28,
                             color=C_MUESTRA, angle=-0.9,
                             tip_length=0.16)
        self.play(FadeIn(espejo), Create(flecha), run_time=1.0)
        rot.mostrar(cifra_pie(f"bin {K_ESPEJO} = bin {K_BUENO}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)
        rot.mostrar(formula_pie(r"X[N-k] = X^{*}[k]"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        # --- y si el tono NO cae en un bin ----------------------------------
        gem = bar.con_valores(MAG_ENTRE)
        self.play(FadeOut(marca), FadeOut(espejo), FadeOut(flecha),
                  run_time=0.5)
        self.play(Transform(bar, gem), run_time=1.6)
        rot.mostrar(cifra_pie(f"tono en {fmt(BIN_ENTRE, 1)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)
        panel = panel_cifras((f"|X[3]| = {fmt(MAG_3, 2)}", C_CALCULO),
                             (f"|X[4]| = {fmt(MAG_4, 2)}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(3.0)

        cierre_leccion(self, rot, "La DFT no descompone en ondas.",
                       "Proyecta sobre giros.",
                       bar, et_k, panel)
