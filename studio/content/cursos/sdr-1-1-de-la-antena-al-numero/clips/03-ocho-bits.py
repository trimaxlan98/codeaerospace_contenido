class Clip3(Scene):
    """1.1.3 - El ADC convierte la onda en escalones; con 8 bits el error
    ya casi no se ve. SQNR medida frente a 6.02 b + 1.76. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Ocho bits"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        t = np.linspace(0.0, 1.0, 72)
        x = 0.92 * np.sin(2 * np.pi * 1.5 * t + 0.3)
        esc4 = S.Escalera(t, x, 4, ancho=8.4, alto=3.2, alto_err=1.2)
        esc4.move_to(UP * 0.35 + LEFT * 2.2)

        def pintar(e):
            e.curva.set_stroke(C_SENAL, width=3.2)
            e.pasos.set_stroke(C_TITULO, width=2.2)
            e.error_caja[1].set_stroke(C_RUIDO, width=2.2)
            return e

        pintar(esc4)
        self.play(Create(esc4.ejes), run_time=0.6)
        self.play(Create(esc4.curva), run_time=1.8)
        t_onda = tag_junto(esc4.curva, "la onda", UP, buff=0.12,
                           font_size=22, color=C_SENAL)
        t_onda.align_to(esc4, LEFT).shift(RIGHT * 0.3)
        self.play(FadeIn(t_onda), run_time=0.4)
        self.wait(1.4)

        # --- 4 bits: escalones gruesos -------------------------------------
        self.play(Create(esc4.pasos), run_time=2.0)
        n4 = tag_hud(f"4 bits = {2 ** 4} niveles", font_size=22,
                     color=C_TITULO)
        n4.move_to(RIGHT * 4.6 + UP * 1.7)
        self.play(FadeIn(n4), run_time=0.4)
        self.wait(1.2)
        self.play(Create(esc4.error_caja), run_time=1.4)
        t_err = tag_junto(esc4.error_caja, "error", UP, buff=0.16,
                          font_size=22, color=C_RUIDO)
        t_err.align_to(esc4, LEFT).shift(RIGHT * 0.3)
        self.play(FadeIn(t_err), run_time=0.4)
        self.wait(2.2)

        # --- 8 bits: la gemela en la MISMA escala de error ---------------
        esc8 = pintar(esc4.con_bits(8))
        n8 = tag_hud(f"8 bits = {2 ** 8} niveles", font_size=22,
                     color=C_TITULO)
        n8.move_to(n4)
        self.play(Transform(esc4.pasos, esc8.pasos),
                  Transform(esc4.error_caja, esc8.error_caja),
                  Transform(n4, n8), run_time=2.2)
        self.add(t_onda, t_err)
        self.wait(1.6)

        rot.mostrar(cifra_pie(f"SQNR medida = {fmt(SQNR8, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)
        rot.mostrar(formula_pie(r"6.02\,b + 1.76 = "
                                + fmt(S.sqnr_teorica(8), 1)
                                + r"\ \mathrm{dB}"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        panel = VGroup(tag_hud("SQNR medida", font_size=20, color=C_TENUE),
                       tag_hud(f" 8 bits: {fmt(SQNR8, 1)} dB", font_size=24),
                       tag_hud(f"12 bits: {fmt(SQNR12, 0)} dB", font_size=24)
                       ).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        panel.next_to(n4, DOWN, buff=0.7).align_to(n4, LEFT)
        self.play(FadeIn(panel), run_time=0.6)
        rot.mostrar(cifra_pie("6 dB por cada bit"), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
