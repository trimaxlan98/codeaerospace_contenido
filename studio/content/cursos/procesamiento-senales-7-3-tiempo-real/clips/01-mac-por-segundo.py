class Clip1(Scene):
    """7.3.1 - N_TAPS coeficientes, MACS multiplicaciones por muestra
    gracias a la simetria: a FS_AUDIO son MMAC_S millones por segundo, una
    fraccion medida de dos procesadores. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("MAC por segundo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el filtro: N_TAPS coeficientes --------------------------------
        bar_h = Barras(H, ancho=9.6, alto=1.9, color=C_MUESTRA)
        bar_h.move_to(UP * 1.55)
        et_h = tag_hud(f"{N_TAPS} coefs", font_size=19, color=C_MUESTRA)
        et_h.next_to(bar_h, UP, buff=0.24)
        self.play(FadeIn(bar_h.ejes), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(b) for b in bar_h.barras],
                              lag_ratio=0.02),
                  FadeIn(et_h), run_time=1.6)
        self.wait(1.8)

        # --- la simetria: pares que comparten multiplicacion ---------------
        pares = VGroup()
        for i in range(4):
            j = N_TAPS - 1 - i
            arc = ArcBetweenPoints(bar_h.cima(i), bar_h.cima(j),
                                   angle=-TAU / 8, color=C_CALCULO,
                                   stroke_width=2.2)
            pares.add(arc)
        self.play(LaggedStart(*[Create(a) for a in pares], lag_ratio=0.18),
                  run_time=1.6)
        rot.mostrar(cifra_pie(f"{N_TAPS} coefs {MACS} macs"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)
        self.play(FadeOut(pares), run_time=0.4)

        # --- el contador que sube -------------------------------------------
        self.play(FadeOut(bar_h), FadeOut(et_h), run_time=0.5)
        cont = tag_hud("0.000 MMAC/s", font_size=30, color=C_CALCULO)
        cont.move_to(UP * 0.9)
        self.play(FadeIn(cont), run_time=0.4)
        for frac in (0.12, 0.34, 0.58, 0.80, 1.0):
            nuevo = tag_hud(f"{fmt(MMAC_S * frac, 3)} MMAC/s", font_size=30,
                            color=C_CALCULO)
            nuevo.move_to(cont.get_center())
            self.play(Transform(cont, nuevo), run_time=0.16)
            self.wait(0.14)
        rot.mostrar(cifra_pie(f"{FS_AUDIO} Hz muestreo"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)

        # --- ocupacion en dos procesadores -----------------------------------
        claves = list(OCUPACION.keys())
        vals = [OCUPACION[k] for k in claves]
        bar_o = Barras(vals, ancho=4.6, alto=2.3, color=C_SALIDA,
                       rango_y=(0.0, max(vals) * 1.4))
        bar_o.move_to(DOWN * 1.05)
        etiquetas = VGroup()
        for i, k in enumerate(claves):
            t = tag_hud(k, font_size=17, color=C_TENUE)
            t.next_to(bar_o.barra(i), DOWN, buff=0.16)
            etiquetas.add(t)
        self.play(FadeOut(cont), FadeIn(bar_o), FadeIn(etiquetas),
                  run_time=0.9)
        tops = VGroup()
        for i, k in enumerate(claves):
            top = tag_hud(f"{fmt(OCUPACION[k], 2)} %", font_size=18,
                         color=C_SALIDA)
            top.next_to(bar_o.barra(i), UP, buff=0.12)
            tops.add(top)
            rot.mostrar(cifra_pie(f"{k} {fmt(OCUPACION[k], 2)} %"),
                        zona="abajo", run_time=0.42)
            self.play(FadeIn(top), run_time=0.6)
            self.wait(2.6)
        self.wait(3.6)
