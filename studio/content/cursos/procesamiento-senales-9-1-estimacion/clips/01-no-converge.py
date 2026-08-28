class Clip1(Scene):
    """9.1.1 - El estimador ingenuo: |DFT|^2 de todo de una vez. El tono
    aparece, pero el piso es un bosque de dientes. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("El periodograma tiembla"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        n_ver = 400
        sec = Secuencia(X_E[:n_ver], 0, None, ancho=10.4, alto=1.5,
                        color=C_SENAL, radio=0.02, eje_y=False)
        sec.move_to(UP * 2.1)
        et_x = tag_hud("x[n]", font_size=19, color=C_SENAL)
        et_x.next_to(sec, LEFT, buff=0.24)
        self.play(FadeIn(sec), FadeIn(et_x), run_time=0.9)
        self.wait(1.4)

        # --- su periodograma ----------------------------------------------
        piso = -25.0
        rf = respuesta_dibujo(F_PER, DB_PER, ancho=10.4, alto=3.0,
                              piso_db=piso, techo_db=float(DB_PER.max()) + 3,
                              color=C_BANDA)
        rf.move_to(DOWN * 1.35)
        et_f = tag_hud("Hz", font_size=18, color=C_TENUE)
        et_f.next_to(rf.en(F_PER[-1], piso), DR, buff=0.10)
        self.play(FadeIn(rf), FadeIn(et_f), run_time=1.2)
        self.wait(1.8)

        # --- el tono se ve; el piso, no ------------------------------------
        marca = rf.marca_w(F_TONO, color=C_CALCULO)
        et_tono = tag_hud(f"{fmt(F_TONO, 0)} Hz", font_size=19,
                          color=C_CALCULO)
        et_tono.next_to(rf.en(F_TONO, float(DB_PER.max())), UR, buff=0.10)
        self.play(Create(marca), FadeIn(et_tono), run_time=0.8)
        self.wait(2.2)

        zona = rf.banda(300.0, 500.0, color=C_RUIDO, opacidad=0.14)
        self.play(FadeIn(zona), run_time=0.7)
        rot.mostrar(cifra_pie(f"dispersion {fmt(DISP_PER, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        panel = panel_cifras(f"N = {N_E}",
                             (f"dispersion {fmt(DISP_PER, 2)} dB", C_RUIDO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)
        rot.mostrar(formula_pie(r"\hat{P}[k] = \frac{1}{N}\,|X[k]|^{2}"),
                    zona="abajo", run_time=0.5)
        self.wait(11.2)
