class Clip1(Scene):
    """2.3.1 - La convolucion VOLTEA la plantilla; la correlacion NO, y por
    eso su pico cae donde esta la copia. Luego la autocorrelacion: el ruido
    no se parece a nada y el codigo PN tampoco, salvo a si mismo. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Correlar no es convolucionar"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- ejemplo corto: la plantilla escondida dentro de x ------------
        H = np.array([0.30, 0.90, 0.60, 0.20])
        X = np.array([0.00, 0.25, 0.00, 0.30, 0.90, 0.60, 0.20, 0.00])
        Y_CONV = convolucion(X, H)
        L_CORR, Y_CORR = correlacion(X, H)
        N_CONV = int(np.argmax(Y_CONV))
        I_CORR = int(np.argmax(Y_CORR))
        K_CORR = int(L_CORR[I_CORR])

        PASO = 0.66                  # misma rejilla en los tres carriles
        RY, RR = (-0.26, 1.06), (-0.34, 1.46)

        def alinear(pieza, n_pieza, x_ref):
            pieza.shift(RIGHT * (x_ref - pieza.en(n_pieza, 0.0)[0]))
            return pieza

        sx = Secuencia(X, 0, RY, ancho=PASO * len(X), alto=1.10,
                       color=C_SENAL)
        sx.move_to(UP * 1.85)
        x0 = sx.en(0, 0.0)[0]
        et_x = tag_junto(sx, "x[n]", LEFT, buff=0.20, font_size=20,
                         color=C_SENAL)

        sh = Secuencia(H, 0, RY, ancho=PASO * len(H), alto=0.95,
                       color=C_MUESTRA)
        sh.move_to(UP * 0.44)
        alinear(sh, 0, x0)
        gem_volteada = sh.con_valores(H[::-1])
        gem_derecha = sh.con_valores(H)
        et_h = tag_junto(sh, "h[n]", LEFT, buff=0.20, font_size=20,
                         color=C_MUESTRA)

        s_conv = Secuencia(Y_CONV, 0, RR, ancho=PASO * len(Y_CONV),
                           alto=1.20, color=C_SALIDA)
        s_conv.move_to(DOWN * 1.42)
        alinear(s_conv, 0, x0)
        s_corr = Secuencia(Y_CORR, int(L_CORR[0]), RR,
                           ancho=PASO * len(Y_CORR), alto=1.20,
                           color=C_CALCULO)
        s_corr.move_to(DOWN * 1.42)
        alinear(s_corr, 0, x0)

        self.play(FadeIn(sx.ejes), FadeIn(et_x), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sx.tallo(i)) for i in range(len(X))],
                              lag_ratio=0.09),
                  LaggedStart(*[FadeIn(sx.punto(i)) for i in range(len(X))],
                              lag_ratio=0.09), run_time=1.5)
        self.play(FadeIn(sh), FadeIn(et_h), run_time=0.7)
        self.wait(1.1)

        # --- la convolucion voltea ---------------------------------------
        et_v = tag_junto(sh, "volteada", UP, buff=0.12, font_size=19,
                         color=C_MUESTRA)
        self.play(Transform(sh.tallos, gem_volteada.tallos),
                  Transform(sh.puntos, gem_volteada.puntos),
                  FadeIn(et_v), run_time=1.1)
        self.wait(0.9)

        et_c1 = tag_junto(s_conv, "convolucion", LEFT, buff=0.20,
                          font_size=20, color=C_SALIDA)
        self.play(FadeIn(s_conv.ejes), FadeIn(et_c1), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(s_conv.tallo(i))
                                for i in range(len(Y_CONV))], lag_ratio=0.08),
                  LaggedStart(*[FadeIn(s_conv.punto(i))
                                for i in range(len(Y_CONV))], lag_ratio=0.08),
                  run_time=1.7)
        marca_c = s_conv.marcar(N_CONV, color=C_SALIDA)
        self.play(Create(marca_c), run_time=0.6)
        rot.mostrar(cifra_pie(f"pico en n = {N_CONV}", color=C_SALIDA),
                    zona="abajo", run_time=0.5)
        self.wait(2.2)

        # --- la correlacion NO voltea ------------------------------------
        et_s = tag_junto(sh, "sin voltear", UP, buff=0.12, font_size=19,
                         color=C_MUESTRA)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeOut(et_v), FadeOut(marca_c), run_time=0.4)
        self.play(Transform(sh.tallos, gem_derecha.tallos),
                  Transform(sh.puntos, gem_derecha.puntos),
                  FadeIn(et_s), run_time=1.1)
        self.wait(0.6)

        et_c2 = tag_junto(s_corr, "correlacion", LEFT, buff=0.20,
                          font_size=20, color=C_CALCULO)
        self.play(FadeOut(et_c1), run_time=0.3)
        self.play(Transform(s_conv.ejes, s_corr.ejes),
                  Transform(s_conv.tallos, s_corr.tallos),
                  Transform(s_conv.puntos, s_corr.puntos),
                  FadeIn(et_c2), run_time=1.6)
        self.wait(0.8)

        marca_r = s_corr.marcar(I_CORR, color=C_CALCULO)
        marca_x = sx.marcar(K_CORR, color=C_CALCULO)
        guia = DashedLine(s_corr.punto(I_CORR).get_center(),
                          sx.punto(K_CORR).get_center(), color=C_CALCULO,
                          stroke_width=1.8, dash_length=0.08)
        self.play(Create(marca_r), run_time=0.5)
        self.play(Create(guia), Create(marca_x), run_time=1.0)
        rot.mostrar(cifra_pie(f"pico en k = {K_CORR}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- la autocorrelacion del ruido --------------------------------
        viejo = VGroup(sx, et_x, sh, et_h, et_s, s_conv, et_c2, marca_r,
                       marca_x, guia)
        self.play(FadeOut(viejo), run_time=0.8)

        o_ru = Onda(np.arange(len(R_RUIDO)), R_RUIDO, (-95.0, 435.0),
                    ancho=9.6, alto=1.85, color=C_RUIDO, grosor=2.0)
        o_ru.move_to(UP * 1.45)
        et_ru = tag_junto(o_ru, "ruido", LEFT, buff=0.20, font_size=20,
                          color=C_RUIDO)
        self.play(FadeIn(o_ru.ejes), FadeIn(et_ru), run_time=0.5)
        self.play(Create(o_ru.curva), run_time=2.0)
        rot.mostrar(cifra_pie(f"pico {fmt(PICO_RUIDO, 0)} lateral "
                              f"{fmt(LATERAL_RUIDO, 0)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        # --- y la del codigo PN -------------------------------------------
        o_pn = Onda(np.arange(len(R_PN)), R_PN, (-30.0, 140.0), ancho=9.6,
                    alto=1.85, color=C_MUESTRA, grosor=2.2)
        o_pn.move_to(DOWN * 1.38)
        et_pn = tag_junto(o_pn, "codigo PN", LEFT, buff=0.20, font_size=20,
                          color=C_MUESTRA)
        self.play(FadeIn(o_pn.ejes), FadeIn(et_pn), run_time=0.5)
        self.play(Create(o_pn.curva), run_time=1.9)
        rot.mostrar(cifra_pie(f"pico {fmt(PICO_PN, 0)} lateral "
                              f"{fmt(LATERAL_PN, 0)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        rot.mostrar(cifra_pie(f"{fmt(PICO_PN, 0)} contra "
                              f"{fmt(LATERAL_PN, 0)}", font_size=36),
                    zona="abajo", run_time=0.5)
        self.wait(3.6)
