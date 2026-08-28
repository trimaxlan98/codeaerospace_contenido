class Clip1(Scene):
    """9.3.1 - Para medir la fase hace falta una referencia: un oscilador
    local (NCO). El fasor de la señal (X_PLL) gira a su ritmo real; el NCO
    arranca en F_INI y no se corrige: el angulo entre los dos crece sin
    parar. Eso es lo que el lazo tendra que anular. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("El oscilador propio"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        pz = plano_z([], [], unidad=2.15, alcance=1.35)
        pz.move_to(ORIGIN + DOWN * 0.15)
        self.play(FadeIn(pz), run_time=1.0)
        self.wait(1.2)

        # Fase continua de cada fasor en funcion de la muestra k (sin
        # indexar arrays: son las mismas F_INI/DERIVA del style_block,
        # integradas a mano). La señal parte con la MISMA frecuencia que
        # el NCO (F_REAL[0] == F_INI): arrancan en fase.
        def fase_senal(k):
            return 2 * np.pi * (F_INI * k + 0.5 * DERIVA * k ** 2)

        def fase_nco(k):
            return 2 * np.pi * F_INI * k

        kt = ValueTracker(0.0)

        def fasor(angulo, color):
            punta = pz.en(np.exp(1j * angulo))
            return Arrow(pz.en(0), punta, buff=0, color=color,
                        stroke_width=6, max_tip_length_to_length_ratio=0.22)

        arco = always_redraw(
            lambda: pz.arco(fase_nco(kt.get_value()), fase_senal(kt.get_value()),
                            color=C_CALCULO, grosor=3.0))

        f_senal_0 = fasor(fase_senal(0.0), C_SENAL)
        f_nco_0 = fasor(fase_nco(0.0), C_MUESTRA)
        self.play(GrowArrow(f_senal_0), GrowArrow(f_nco_0), run_time=0.7)
        self.remove(f_senal_0, f_nco_0)
        f_senal = always_redraw(
            lambda: fasor(fase_senal(kt.get_value()), C_SENAL))
        f_nco = always_redraw(
            lambda: fasor(fase_nco(kt.get_value()), C_MUESTRA))
        self.add(f_senal, f_nco)
        et_senal = tag_hud("senal", font_size=19, color=C_SENAL)
        et_senal.move_to(pz.en(0) + LEFT * 2.55 + UP * 1.55)
        et_nco = tag_hud("nco local", font_size=19, color=C_MUESTRA)
        et_nco.move_to(pz.en(0) + LEFT * 2.55 + UP * 1.05)
        self.play(FadeIn(et_senal), FadeIn(et_nco), run_time=0.6)
        panel = panel_cifras((f"f_ini {fmt(F_INI, 2)}", C_MUESTRA))
        self.play(FadeIn(panel), run_time=0.5)
        self.wait(0.8)

        # --- fase 1: arrancan pegados, casi no se nota ---------------------
        self.play(kt.animate.set_value(130), run_time=6.0, rate_func=linear)
        self.wait(0.6)
        self.add(arco)
        rot.mostrar(cifra_pie("la brecha empieza a abrirse"), zona="abajo",
                    run_time=0.5)
        self.wait(1.4)

        # --- fase 2: la brecha se abre sin parar ---------------------------
        self.play(kt.animate.set_value(260), run_time=7.0, rate_func=linear)
        self.wait(1.0)

        rot.mostrar(cifra_pie("el angulo crece sin parar"), zona="abajo",
                    run_time=0.5)
        self.wait(6.0)
