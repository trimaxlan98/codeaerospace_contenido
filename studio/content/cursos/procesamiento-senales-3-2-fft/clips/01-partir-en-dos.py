class Clip1(Scene):
    """3.2.1 - La DFT de 8 se parte en dos DFT de 4: los pares por un
    lado, los impares por otro, y una recombinacion con giros. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Partir en dos"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- las 8 muestras -----------------------------------------------
        sec = Secuencia(X_FFT, 0, (-1.1, 1.1), ancho=6.8, alto=1.7,
                        color=C_SENAL)
        sec.move_to(UP * 1.75)
        et_x = tag_hud("x[n]", font_size=19, color=C_SENAL)
        et_x.next_to(sec, LEFT, buff=0.30)
        self.play(FadeIn(sec.ejes), FadeIn(et_x), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in range(N_FFT)],
                              lag_ratio=0.07),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in range(N_FFT)],
                              lag_ratio=0.07), run_time=1.7)
        self.wait(0.9)

        # --- pares e impares ------------------------------------------------
        m_par = VGroup(*[sec.marcar(i, C_MUESTRA)
                         for i in range(0, N_FFT, 2)])
        rot.mostrar(cifra_pie("pares: 0 2 4 6", color=C_MUESTRA),
                    zona="abajo", run_time=0.5)
        self.play(LaggedStart(*[Create(m) for m in m_par], lag_ratio=0.14),
                  run_time=1.1)
        self.wait(1.5)

        m_imp = VGroup(*[sec.marcar(i, C_SALIDA)
                         for i in range(1, N_FFT, 2)])
        rot.mostrar(cifra_pie("impares: 1 3 5 7", color=C_SALIDA),
                    zona="abajo", run_time=0.5)
        self.play(LaggedStart(*[Create(m) for m in m_imp], lag_ratio=0.14),
                  run_time=1.1)
        self.wait(1.5)

        # --- dos secuencias de 4 ---------------------------------------------
        sec_p = Secuencia(PARES, 0, (-1.1, 1.1), ancho=4.4, alto=1.4,
                          color=C_MUESTRA)
        sec_p.move_to(LEFT * 3.5 + DOWN * 1.35)
        sec_i = Secuencia(IMPARES, 0, (-1.1, 1.1), ancho=4.4, alto=1.4,
                          color=C_SALIDA)
        sec_i.move_to(RIGHT * 3.5 + DOWN * 1.35)
        et_p = tag_hud("pares", font_size=19, color=C_MUESTRA)
        et_p.next_to(sec_p, DOWN, buff=0.26)
        et_i = tag_hud("impares", font_size=19, color=C_SALIDA)
        et_i.next_to(sec_i, DOWN, buff=0.26)
        self.play(FadeOut(m_par), FadeOut(m_imp), run_time=0.4)
        self.play(FadeIn(sec_p, shift=0.25 * DOWN),
                  FadeIn(sec_i, shift=0.25 * DOWN),
                  FadeIn(et_p), FadeIn(et_i), run_time=1.1)
        rot.mostrar(cifra_pie(f"dos senales de {N_FFT // 2}"), zona="abajo",
                    run_time=0.5)
        self.wait(1.9)

        # --- cada mitad con su propia DFT de 4 --------------------------------
        bp = barras(np.abs(X_PARES), ancho=4.0, alto=1.4, color=C_CALCULO,
                    rango_y=(0.0, 1.95))
        bp.move_to(LEFT * 3.5 + DOWN * 1.35)
        bi = barras(np.abs(X_IMPARES), ancho=4.0, alto=1.4, color=C_CALCULO,
                    rango_y=(0.0, 1.95))
        bi.move_to(RIGHT * 3.5 + DOWN * 1.35)
        et_bp = tag_hud("|X pares|", font_size=19, color=C_CALCULO)
        et_bp.next_to(bp, DOWN, buff=0.26)
        et_bi = tag_hud("|X impares|", font_size=19, color=C_CALCULO)
        et_bi.next_to(bi, DOWN, buff=0.26)
        self.play(FadeOut(sec_p), FadeOut(sec_i), FadeOut(et_p),
                  FadeOut(et_i), run_time=0.5)
        rot.mostrar(cifra_pie(f"DFT de 4: {ops_dft(N_FFT // 2)} mult"),
                    zona="abajo", run_time=0.45)
        self.play(FadeIn(bp), FadeIn(bi), FadeIn(et_bp), FadeIn(et_bi),
                  run_time=1.0)
        self.wait(2.6)

        # --- recombinar: X_pares +- W * X_impares -----------------------------
        bc = barras(np.abs(X_RECOMPUESTA), ancho=6.2, alto=1.6,
                    color=C_CALCULO, rango_y=(0.0, 3.25))
        bc.move_to(UP * 1.75)
        et_bc = tag_hud("|X[k]| de 8", font_size=19, color=C_CALCULO)
        et_bc.next_to(bc, LEFT, buff=0.30)
        fl_p = Arrow(bp.get_top() + UP * 0.05, bc.get_corner(DL) + DOWN * 0.05,
                     color=C_MUESTRA, stroke_width=3.0, buff=0.16,
                     max_tip_length_to_length_ratio=0.10)
        fl_i = Arrow(bi.get_top() + UP * 0.05, bc.get_corner(DR) + DOWN * 0.05,
                     color=C_SALIDA, stroke_width=3.0, buff=0.16,
                     max_tip_length_to_length_ratio=0.10)
        self.play(FadeOut(sec), FadeOut(et_x), run_time=0.6)
        self.play(GrowArrow(fl_p), GrowArrow(fl_i), run_time=0.9)
        self.play(FadeIn(bc), FadeIn(et_bc), run_time=1.1)
        self.wait(2.0)

        rot.mostrar(formula_pie(r"X_{par}[k] \pm W_N^{k}\,X_{impar}[k]"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        rot.mostrar(cifra_pie(f"error = {ERROR_PARTIR:.1e}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        panel = panel_cifras((f"DFT 8: {ops_dft(N_FFT)} mult", C_RUIDO),
                             (f"dos de 4: {2 * ops_dft(N_FFT // 2)}",
                              C_SALIDA))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(4.2)
