class Clip2(Scene):
    """3.1.2 - El telegrafista: modela la linea como una escalera de
    bobinas (guardan corriente) y condensadores (guardan tension), celda
    a celda. De ahi sale Z0 = sqrt(L/C): un precio en ohmios que NO
    depende del largo de la linea. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El telegrafista: Z0 = raiz(L/C)")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la escalera LC ----------------------------------------
        rot.mostrar(pie_curso("El telegrafista modelo la linea como una "
                              "escalera: una celda tras otra."),
                    zona="abajo", run_time=0.5)
        lin = linea_lc(n_celdas=6, largo=6.4, color_l=C_B, color_c=C_E)
        lin.move_to(UP * 0.15)
        self.play(FadeIn(lin.rail), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(c, scale=1.15) for c in lin.celdas],
                              lag_ratio=0.15), run_time=1.8)
        self.wait(3.6)

        tag_l = tag_junto(lin.celda(0), "L: guarda corriente", UP,
                          buff=0.14, font_size=16, color=C_B)
        tag_c = tag_junto(lin.celda(0), "C: guarda tension", DOWN,
                          buff=0.28, font_size=16, color=C_E)
        rot.mostrar(pie_curso("Arriba, las bobinas guardan corriente. "
                              "Abajo, los condensadores guardan tension."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(tag_l, shift=0.1 * UP),
                  FadeIn(tag_c, shift=0.1 * DOWN), run_time=0.6)
        self.wait(4.6)

        # --- momento: el pulso saltando celda a celda -----------------------
        rot.mostrar(pie_curso("La señal avanza CARGANDO cada celda, una "
                              "detras de la otra."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(tag_l), FadeOut(tag_c), run_time=0.4)
        pulso = Dot(lin.punto_celda(0), radius=0.09, color=C_CALCULO)
        self.play(FadeIn(pulso, scale=1.8), run_time=0.4)
        for i in range(1, 6):
            self.play(pulso.animate.move_to(lin.punto_celda(i)),
                      run_time=0.4, rate_func=linear)
        self.wait(3.6)

        # --- momento: Z0 = sqrt(L/C), el precio fijo -------------------------
        rot.mostrar(pie_curso("Cada salto cobra el MISMO precio: la "
                              "linea entera vale una sola impedancia."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(pulso), run_time=0.4)
        rot.mostrar(formula_pie(r"Z_0 = \sqrt{\,L/C\,}"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

        # --- momento: las dos monedas de la RF -------------------------------
        rot.mostrar(pie_curso("Y en ohmios, la radiofrecuencia solo usa "
                              "dos monedas."), zona="abajo", run_time=0.5)
        moneda_rf = tag_hud(f"{Z0_RF:.0f} ohm", font_size=26,
                            color=C_CALCULO)
        etiqueta_rf = tag_junto(moneda_rf, "radiofrecuencia", DOWN,
                                buff=0.16, font_size=15)
        moneda_tv = tag_hud(f"{Z0_TV:.0f} ohm", font_size=26,
                            color=C_CALCULO)
        etiqueta_tv = tag_junto(moneda_tv, "television / satelite", DOWN,
                                buff=0.16, font_size=15)
        grupo_rf = VGroup(moneda_rf, etiqueta_rf).move_to(LEFT * 2.1
                                                           + DOWN * 1.7)
        grupo_tv = VGroup(moneda_tv, etiqueta_tv).move_to(RIGHT * 2.1
                                                           + DOWN * 1.7)
        self.play(FadeIn(grupo_rf, shift=0.15 * UP),
                  FadeIn(grupo_tv, shift=0.15 * UP), run_time=0.7)
        self.wait(4.8)

        rot.mostrar(pie_curso("Un precio fijo, en ohmios, que no depende "
                              "de lo larga que sea la linea."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
