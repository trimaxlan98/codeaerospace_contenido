class Clip1(Scene):
    """6.1.1 - El amplificador de a bordo comprime y GIRA la reticula de
    16-QAM (Saleh AM/AM + AM/PM) y el ruido la esparce: lo que llega al
    receptor es una espiral, no una cuadricula. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La constelación deformada")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la reticula que sale del modulador ------------------
        rot.mostrar(pie_curso("16-QAM: dieciseis puntos en el plano I/Q, "
                              "cuatro bits en cada uno."),
                    zona="abajo", run_time=0.5)
        piq = plano_iq(unidad=1.15, alcance=ALCANCE)
        piq.move_to(LEFT * 2.5 + DOWN * 0.25)
        ideal = piq.puntos(P16, color=C_BIT, radio=0.07)
        self.play(FadeIn(piq), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in ideal],
                              lag_ratio=0.05), run_time=1.7)
        panel_ideal = panel_derecha(
            tag_hud("16-QAM ideal", color=C_BIT),
            tag_hud(f"{K_BITS} bits por simbolo", color=C_BIT),
            tag_hud(f"d_min = {fmt(D_MIN_IDEAL, 2)}"))
        self.play(FadeIn(panel_ideal), run_time=0.5)
        self.wait(4.0)

        # --- momento: el amplificador comprime Y gira ---------------------
        rot.mostrar(pie_curso("El amplificador de a bordo (leccion 2.2) "
                              "trabaja al borde: comprime los anillos y "
                              "ademas los GIRA."),
                    zona="abajo", run_time=0.5)
        tenue = piq.puntos(P16, color=C_BIT, radio=0.055)
        tenue.set_fill(opacity=0.28)
        tenue.set_stroke(opacity=0.0)
        deform = piq.puntos(PD, color=C_RUIDO, radio=0.07)
        self.play(FadeIn(tenue), Transform(ideal, deform), run_time=2.0)
        panel_def = panel_derecha(
            tag_hud("tras el amplificador", color=C_RUIDO),
            tag_hud(f"d_min = {fmt(D_MIN_DEFORM, 2)}"),
            tag_hud(f"antes era {fmt(D_MIN_IDEAL, 2)}", color=C_TENUE))
        self.play(FadeOut(panel_ideal), FadeIn(panel_def), run_time=0.6)
        self.wait(4.6)

        # --- momento: el ruido esparce cada simbolo -----------------------
        rot.mostrar(pie_curso("Y el ruido termico esparce cada simbolo "
                              "alrededor de donde el amplificador lo dejo."),
                    zona="abajo", run_time=0.5)
        nube = piq.nube(RX_VIS, color=C_SENAL, maximo=N_VISIBLES,
                        radio=0.026, opacidad=0.8)
        et_nube = tag_hud(f"{N_VISIBLES} de {N_SIM} simbolos dibujados",
                          font_size=16, color=C_TENUE)
        et_nube.next_to(piq, DOWN, buff=0.16)
        self.play(LaggedStart(*[FadeIn(d) for d in nube], lag_ratio=0.004),
                  run_time=2.2)
        self.play(FadeIn(et_nube), run_time=0.4)
        self.wait(3.4)

        # --- momento: la reticula ya no esta donde se la espera -----------
        rot.mostrar(pie_curso("Esto es lo unico que ve el receptor: la "
                              "cuadricula del libro ya no esta donde la "
                              "espera."),
                    zona="abajo", run_time=0.5)
        panel_rx = panel_derecha(
            tag_hud("lo que llega", color=C_SENAL),
            tag_hud(f"Eb/N0 = {fmt(EBN0_DB, 1)} dB"),
            tag_hud(f"{N_SIM} simbolos medidos"))
        self.play(FadeOut(panel_def), FadeIn(panel_rx),
                  ideal.animate.set_fill(opacity=0.5), run_time=0.7)
        self.wait(6.4)
