class Clip3(Scene):
    """9.3.3 - Lo que hace util al PLL: la frecuencia real se va (el
    Doppler de un pase, DERIVA por muestra) y la estimada del lazo la
    sigue pegada. F_REAL y FREC_PLL casi no se separan. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("La deriva"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        idx = np.arange(N_PLL)
        piso = float(min(F_REAL.min(), FREC_PLL.min())) - 0.002
        techo = float(max(F_REAL.max(), FREC_PLL.max())) + 0.002
        rf = respuesta_dibujo(idx, F_REAL, ancho=10.2, alto=3.2,
                              piso_db=piso, techo_db=techo, color=C_SENAL)
        rf.move_to(DOWN * 0.35)
        self.play(FadeIn(rf.ejes), Create(rf.curva), run_time=1.8)
        et_real = tag_hud("f real", font_size=19, color=C_SENAL)
        et_real.next_to(rf.en(0, F_REAL[0]), LEFT, buff=0.20)
        self.play(FadeIn(et_real), run_time=0.5)
        rot.mostrar(cifra_pie(f"deriva {DERIVA:.1e} por muestra"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        rf2 = rf.con_mag(FREC_PLL, color=C_CALCULO)
        curva_pll = DashedVMobject(rf2.curva, num_dashes=90)
        self.play(Create(curva_pll), run_time=1.8)
        self.add(curva_pll)
        et_pll = tag_hud("f pll", font_size=19, color=C_CALCULO)
        et_pll.next_to(rf.en(0, F_REAL[0]), LEFT, buff=0.20).shift(DOWN * 0.4)
        self.play(FadeIn(et_pll), run_time=0.5)
        rot.mostrar(cifra_pie("van pegadas"), zona="abajo", run_time=0.5)
        self.wait(3.0)

        p1 = Dot(rf.en(N_PLL - 1, FREC_REAL_FINAL), radius=0.07,
                 color=C_SENAL)
        p2 = Dot(rf.en(N_PLL - 1, FREC_FINAL), radius=0.07, color=C_CALCULO)
        self.play(FadeIn(p1), FadeIn(p2), run_time=0.6)
        self.wait(1.0)

        panel = panel_cifras((f"real {fmt(FREC_REAL_FINAL, 5)}", C_SENAL),
                             (f"pll {fmt(FREC_FINAL, 5)}", C_CALCULO),
                             (f"error {ERR_FREC:.1e}", C_RUIDO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(4.5)

        rot.mostrar(formula_pie(r"\hat{f}_k = f_0 + k_i \sum_{i \le k} e_i"),
                    zona="abajo", run_time=0.5)
        self.wait(9.5)
