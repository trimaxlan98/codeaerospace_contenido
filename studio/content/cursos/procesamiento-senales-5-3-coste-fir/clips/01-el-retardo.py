class Clip1(Scene):
    """5.3.1 - Un FIR de orden 40 retrasa la señal exactamente N/2 = 20
    muestras: se mide metiendo un impulso y viendo donde sale el pico.
    (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("El retardo"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- el impulso que entra ------------------------------------------
        ent = Secuencia(X_PRUEBA, 0, ancho=9.4, alto=1.5, color=C_MUESTRA,
                        radio=0.05)
        ent.move_to(UP * 1.55)
        et_ent = tag_hud("x[n]", font_size=18, color=C_MUESTRA)
        et_ent.next_to(ent, LEFT, buff=0.24)
        self.play(FadeIn(ent.ejes), FadeIn(et_ent), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(ent.tallo(i))
                                for i in range(N_PRUEBA)], lag_ratio=0.025),
                  LaggedStart(*[FadeIn(ent.punto(i))
                                for i in range(N_PRUEBA)], lag_ratio=0.025),
                  run_time=2.0)
        self.wait(1.2)

        marca_ent = ent.marcar(POS_IMPULSO, color=C_CALCULO)
        self.play(FadeIn(marca_ent, scale=1.5), run_time=0.5)
        self.wait(1.6)

        # --- lo que sale del filtro: la MISMA ventana de n ------------------
        y_ventana = Y_PRUEBA[:N_PRUEBA]
        sal = Secuencia(y_ventana, 0, ancho=9.4, alto=1.5, color=C_SALIDA,
                        radio=0.05)
        sal.move_to(DOWN * 1.35)
        et_sal = tag_hud("y[n]", font_size=18, color=C_SALIDA)
        et_sal.next_to(sal, LEFT, buff=0.24)
        self.play(FadeIn(sal.ejes), FadeIn(et_sal), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(sal.tallo(i))
                                for i in range(N_PRUEBA)], lag_ratio=0.02),
                  LaggedStart(*[FadeIn(sal.punto(i))
                                for i in range(N_PRUEBA)], lag_ratio=0.02),
                  run_time=2.2)
        self.wait(1.4)

        pico = POS_IMPULSO + RETARDO
        marca_sal = sal.marcar(pico, color=C_CALCULO)
        self.play(FadeIn(marca_sal, scale=1.5), run_time=0.5)
        self.wait(1.6)

        # --- las muestras entre un pico y el otro ---------------------------
        l_ent = DashedLine(ent.en(POS_IMPULSO, ent.y1),
                           sal.en(POS_IMPULSO, sal.y0), color=C_MUESTRA,
                           stroke_width=1.6, dash_length=0.08)
        l_sal = DashedLine(ent.en(pico, ent.y1), sal.en(pico, sal.y0),
                           color=C_CALCULO, stroke_width=1.6,
                           dash_length=0.08)
        self.play(Create(l_ent), run_time=0.5)
        self.play(Create(l_sal), run_time=0.5)
        self.wait(0.8)

        y_flecha = (ent.en(0, ent.y0)[1] + sal.en(0, sal.y1)[1]) / 2.0
        flecha = DoubleArrow(
            np.array([ent.en(POS_IMPULSO, 0.0)[0], y_flecha, 0.0]),
            np.array([ent.en(pico, 0.0)[0], y_flecha, 0.0]),
            color=C_CALCULO, buff=0.0, stroke_width=3.0, tip_length=0.16)
        et_flecha = tag_hud(f"{RETARDO} muestras", font_size=19,
                            color=C_CALCULO)
        et_flecha.next_to(flecha, UP, buff=0.14)
        self.play(Create(flecha), FadeIn(et_flecha), run_time=0.8)
        rot.mostrar(cifra_pie(f"retardo = {RETARDO}"), zona="abajo",
                    run_time=0.5)
        self.wait(1.6)

        panel = panel_cifras(f"entra en {POS_IMPULSO}", f"sale en {pico}")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.4)

        rot.mostrar(formula_pie(
            rf"\tau_g = \frac{{N}}{{2}} = \frac{{{ORDEN}}}{{2}} = {RETARDO}"),
            zona="abajo", run_time=0.5)
        self.wait(7.4)
