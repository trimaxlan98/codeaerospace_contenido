class Clip2(Scene):
    """2.2.2 - 64-QAM: 6 bits por simbolo, d_min MEDIDA otra vez; la
    escalera QPSK->16-QAM->64-QAM con sus d_min rotuladas y la regla de
    los ~6 dB por escalon (medida, no de memoria). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("64-QAM y la escalera de densidades")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: 64-QAM, un piso mas denso -----------------------------
        rot.mostrar(pie_curso("64-QAM aprieta aún más: seis bits por "
                              "símbolo, 64 puntos en la misma energía."),
                    zona="abajo", run_time=0.5)
        plano = plano_iq(unidad=1.55, alcance=1.75)
        plano.move_to(DOWN * 0.15)
        self.play(FadeIn(plano), run_time=0.7)
        p64 = plano.puntos(QAM64, color=C_BIT, radio=0.045)
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in p64],
                              lag_ratio=0.02), run_time=1.8)
        i, j = PAR_QAM64
        seg = Line(plano.p(QAM64[i]), plano.p(QAM64[j]), color=C_CIFRA,
                  stroke_width=2.6)
        cifra = tag_hud(f"d_min = {fmt(D_QAM64, 3)}", font_size=18)
        panel = panel_derecha(cifra)
        self.play(Create(seg), FadeIn(panel), run_time=0.9)
        self.wait(5.5)

        # --- momento: la escalera completa ----------------------------------
        rot.mostrar(pie_curso("Cada escalón cuesta: comparemos los tres "
                              "pisos, uno junto al otro."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(plano), FadeOut(p64), FadeOut(seg),
                  FadeOut(panel), run_time=0.7)

        pasos = [
            ("QPSK", QPSK, BITS_QPSK, D_QPSK, LEFT * 4.35 + UP * 0.95),
            ("16-QAM", QAM16, BITS_QAM16, D_QAM16, ORIGIN),
            ("64-QAM", QAM64, BITS_QAM64, D_QAM64, RIGHT * 4.35 + DOWN * 0.95),
        ]
        escalera = VGroup()
        rotulos_paso = VGroup()
        for nombre, pts, bits, dmin, pos in pasos:
            mini = plano_iq(unidad=0.5, alcance=1.75)
            mini.move_to(pos)
            radio_pt = 0.075 if nombre == "QPSK" else \
                (0.05 if nombre == "16-QAM" else 0.03)
            pmini = mini.puntos(pts, color=C_BIT, radio=radio_pt)
            et_n = tag_hud(f"{nombre} - {bits.shape[1]} bits/símbolo",
                          font_size=15)
            et_n.next_to(mini, UP, buff=0.14)
            et_d = tag_hud(f"d_min = {fmt(dmin, 3)}", font_size=15,
                          color=C_CIFRA)
            et_d.next_to(mini, DOWN, buff=0.14)
            escalera.add(VGroup(mini, pmini))
            rotulos_paso.add(et_n, et_d)
        self.play(LaggedStart(*[FadeIn(g) for g in escalera],
                              lag_ratio=0.25), FadeIn(rotulos_paso),
                  run_time=1.8)
        self.wait(4.2)

        # --- momento: la regla medida, 6 dB por escalon ---------------------
        rot.mostrar(pie_curso("Cada doblez de densidad cuesta cerca de "
                              "6 dB de energía para no perder margen."),
                    zona="abajo", run_time=0.5)
        f1 = tag_hud(f"{fmt(D_QPSK, 3)} / {fmt(D_QAM16, 3)} -> "
                    f"{fmt(DB_QPSK_A_QAM16, 1)} dB",
                    font_size=16, color=C_CIFRA)
        f1.next_to(VGroup(escalera[0], escalera[1]), DOWN, buff=0.55)
        f2 = tag_hud(f"{fmt(D_QAM16, 3)} / {fmt(D_QAM64, 3)} -> "
                    f"{fmt(DB_QAM16_A_QAM64, 1)} dB",
                    font_size=16, color=C_CIFRA)
        f2.next_to(VGroup(escalera[1], escalera[2]), DOWN, buff=0.55)
        self.play(FadeIn(f1, shift=0.1 * UP), run_time=0.5)
        self.wait(1.0)
        self.play(FadeIn(f2, shift=0.1 * UP), run_time=0.5)
        self.wait(8.5)
