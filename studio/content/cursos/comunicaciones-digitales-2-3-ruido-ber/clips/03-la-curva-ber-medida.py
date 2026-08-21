class Clip3(Scene):
    """2.3.3 - La curva BER: los puntos Monte Carlo (2e5 simbolos por
    punto) caen SOBRE la curva teorica Q, y la cascada se lee sola.
    (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La curva BER medida")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el eje donde vive la tasa de error ------------------
        rot.mostrar(pie_curso("Contar quinientos simbolos no basta: "
                              "repetimos el conteo para cada Eb/N0."),
                    zona="abajo", run_time=0.5)
        cb = curva_ber(x0=0.0, x1=14.0, exp_min=5, ancho=5.6, alto=3.4)
        cb.move_to(LEFT * 2.9 + DOWN * 0.15)
        et_n = tag_hud(f"n = {N_MC:,} simbolos por punto".replace(",", " "),
                       font_size=20)
        et_n.move_to(cb.en(7.0, 1.0) + UP * 0.52)
        self.play(FadeIn(cb), run_time=1.0)
        self.play(FadeIn(et_n, shift=0.12 * DOWN), run_time=0.5)
        self.wait(4.5)

        # --- momento: lo que dice la teoria -------------------------------
        rot.mostrar(pie_curso("La teoria la predice con la funcion Q: la "
                              "cola de la campana que cruza la frontera."),
                    zona="abajo", run_time=0.5)
        formula = panel_derecha(
            MathTex(r"P_b = Q\!\left(\sqrt{2E_b/N_0}\right)",
                    font_size=34, color=C_CALCULO))
        curva_teorica = cb.curva(lambda db: ber_teorica_qam(4, db),
                                 color=C_CIFRA)
        self.play(FadeIn(formula), run_time=0.6)
        self.play(Create(curva_teorica), run_time=1.7)
        self.wait(4.3)

        # --- momento: los puntos MEDIDOS ----------------------------------
        rot.mostrar(pie_curso("Y esto es lo MEDIDO: un punto por cada "
                              "Eb/N0, contando bits errados."),
                    zona="abajo", run_time=0.5)
        medidos = cb.puntos_medidos(BER_QPSK, color=C_COD, radio=0.075)
        leyenda = VGroup(
            tag_hud("teoria: funcion Q", font_size=18, color=C_CIFRA),
            tag_hud("medido: Monte Carlo", font_size=18, color=C_COD),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        leyenda.move_to(RIGHT * 2.0 + DOWN * 1.15)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in medidos],
                              lag_ratio=0.35), run_time=1.7)
        self.play(FadeIn(leyenda), run_time=0.5)
        self.wait(4.4)

        # --- momento: la cascada ------------------------------------------
        rot.mostrar(pie_curso(f"Cuatro dB mas de senal y la tasa cae "
                              f"{fmt(RAZON_4_8, 0)} veces: eso es la "
                              f"cascada."),
                    zona="abajo", run_time=0.5)
        v4 = cb.vertical_en(4.0, color=C_EJE)
        v8 = cb.vertical_en(8.0, color=C_EJE)
        et4 = MathTex(sci(BER_4), font_size=28, color=C_CALCULO)
        et4.next_to(cb.en(4.0, BER_4), UR, buff=0.13)
        et8 = MathTex(sci(BER_8), font_size=28, color=C_CALCULO)
        et8.next_to(cb.en(8.0, BER_8), UR, buff=0.13)
        self.play(Create(v4), Create(v8), run_time=0.9)
        self.play(FadeIn(et4), FadeIn(et8), run_time=0.7)
        razon = MathTex(r"\frac{%s}{%s} \approx %s"
                        % (sci(BER_4), sci(BER_8), fmt(RAZON_4_8, 0)),
                        font_size=34, color=C_CALCULO)
        razon.next_to(formula, DOWN, buff=0.45)
        et_razon = tag_hud("veces menos errores", font_size=19)
        et_razon.next_to(razon, DOWN, buff=0.22)
        self.play(FadeIn(razon, shift=0.15 * UP), FadeIn(et_razon),
                  run_time=0.7)
        self.wait(5.4)
