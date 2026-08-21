class Clip4(Scene):
    """4.3.4 - A un paso del techo: la cascada de la QPSK sin codigo, la
    pared de Shannon para tasa 1/2 y los ~9.6 dB que un codigo puede
    ganar. Cierre de leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("A un paso del techo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        c = curva_ber(x0=BER_X0, x1=BER_X1, exp_min=5, ancho=5.6, alto=3.2)
        c.move_to(POS_BER)

        # --- momento: la cascada sin codigo -------------------------------
        rot.mostrar(pie_curso("Asi cae la QPSK sin codigo: la curva "
                              "teorica, y encima los errores contados."),
                    zona="abajo", run_time=0.5)
        curva = c.curva(lambda x: ber_teorica_qam(4, x), color=C_CIFRA)
        medidos = c.puntos_medidos(PARES_MC, color=C_COD)
        cab = tag_hud("QPSK sin codigo  BER contada", font_size=15,
                      color=C_TENUE)
        cifras = VGroup(
            tag_hud(f"{fmt(EBN0_MC[1], 0)} dB : {fmt_ber(BER_4DB)}",
                    font_size=17),
            tag_hud(f"{fmt(EBN0_MC[3], 0)} dB : {fmt_ber(BER_8DB)}",
                    font_size=17),
            tag_hud(f"{ERR_4DB} errores / {NBITS_4DB} bits", font_size=15,
                    color=C_TENUE),
        ).arrange(DOWN, buff=0.14)
        panel = panel_derecha(cab, cifras, buff=0.24)
        self.play(FadeIn(c), run_time=0.8)
        self.play(Create(curva), run_time=1.8)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in medidos],
                              lag_ratio=0.2), FadeIn(panel), run_time=1.2)
        self.wait(3.8)

        # --- momento: el precio de un error por cada cien mil -------------
        rot.mostrar(pie_curso("Para un error por cada cien mil bits, la "
                              "QPSK desnuda exige casi diez decibelios."),
                    zona="abajo", run_time=0.5)
        p_obj = c.en(EBN0_SIN_CODIGO, BER_OBJETIVO)
        d_obj = Dot(p_obj, radius=0.07, color=C_CIFRA)
        v_obj = c.vertical_en(EBN0_SIN_CODIGO, color=C_CIFRA)
        et_obj = tag_hud(f"{fmt(EBN0_SIN_CODIGO, 1)} dB para 10^-5",
                         font_size=17)
        # arriba del punto (a la altura de 10^-3): la flecha de la brecha
        # llega a este mismo dB y las dos cifras se pisarian al ras.
        et_obj.next_to(c.en(EBN0_SIN_CODIGO, 1e-3), RIGHT, buff=0.14)
        self.play(Create(v_obj), FadeIn(d_obj), FadeIn(et_obj),
                  run_time=1.0)
        self.wait(4.4)

        # --- momento: la pared de Shannon ---------------------------------
        rot.mostrar(pie_curso("El curso 21 prometio un techo. Con tasa "
                              "1/2, nadie puede hablar por debajo de esta "
                              "raya."),
                    zona="abajo", run_time=0.5)
        v_sh = c.vertical_en(EBN0_SHANNON, color=C_TECHO)
        et_sh = VGroup(
            Text("límite de Shannon, tasa 1/2", font_size=21,
                 color=C_TECHO),
            MathTex(r"E_b/N_0 = 0\ \mathrm{dB}", font_size=28,
                    color=C_TECHO),
        ).arrange(DOWN, buff=0.1)
        et_sh.next_to(c.en(EBN0_SHANNON, 1.0), UP, buff=0.16)
        self.play(Create(v_sh), FadeIn(et_sh), run_time=1.1)
        self.wait(4.6)

        # --- momento: la brecha que el codigo puede cobrar ----------------
        rot.mostrar(pie_curso("Entre la pared y la QPSK desnuda cabe todo "
                              "lo que un codigo puede ganar."),
                    zona="abajo", run_time=0.5)
        y_br = 3e-5
        flecha = DoubleArrow(c.en(EBN0_SHANNON, y_br),
                             c.en(EBN0_SIN_CODIGO, y_br),
                             color=C_COD, stroke_width=3.0,
                             tip_length=0.16, buff=0.0)
        et_br = tag_hud(f"{fmt(BRECHA_DB, 1)} dB de premio", font_size=17,
                        color=C_COD)
        et_br.next_to(flecha, UP, buff=0.1)
        self.play(GrowFromCenter(flecha), FadeIn(et_br), run_time=1.0)
        self.wait(4.2)

        # --- momento: DVB-S2 se los cobra ---------------------------------
        rot.mostrar(pie_curso(f"DVB-S2 se los cobra casi enteros: "
                              f"{N_DVBS2} bits murmurando, a un decibelio "
                              f"del techo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- cierre de leccion --------------------------------------------
        cierre_leccion(
            self, rot,
            "Nadie corrige solo.",
            "El mensaje se corrige en comunidad.",
            "Siguiente modulo: compartir el cielo entre mil terminales.",
            c, curva, medidos, panel, d_obj, v_obj, et_obj, v_sh, et_sh,
            flecha, et_br)
