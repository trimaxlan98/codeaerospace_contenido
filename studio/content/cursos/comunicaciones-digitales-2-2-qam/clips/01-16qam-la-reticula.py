class Clip1(Scene):
    """2.2.1 - 16-QAM: 16 puntos, 4 bits por simbolo, a la MISMA energia
    que QPSK; d_min MEDIDA baja de 1.414 a 0.632: el precio de la
    densidad. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("16-QAM: la retícula")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: QPSK, cuatro puntos en el circulo de energia --------
        rot.mostrar(pie_curso("QPSK vive en cuatro puntos, todos a la "
                              "misma energía: el mismo círculo."),
                    zona="abajo", run_time=0.5)
        plano = plano_iq(unidad=1.6, alcance=1.75)
        plano.move_to(LEFT * 1.3 + DOWN * 0.15)
        self.play(FadeIn(plano), run_time=0.8)
        pq = plano.puntos(QPSK, color=C_BIT, radio=0.09)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in pq],
                              lag_ratio=0.15), run_time=1.0)
        self.wait(3.0)

        # --- momento: la distancia entre puntos vecinos --------------------
        rot.mostrar(pie_curso("La distancia entre puntos vecinos, d_min, "
                              "mide cuánto aguanta el ruido."),
                    zona="abajo", run_time=0.5)
        i, j = PAR_QPSK
        seg_q = Line(plano.p(QPSK[i]), plano.p(QPSK[j]), color=C_CIFRA,
                    stroke_width=3.0)
        cifra_q = tag_hud(f"d_min = {fmt(D_QPSK, 3)}", font_size=19)
        cifra_q.next_to(seg_q, RIGHT, buff=0.22)
        self.play(Create(seg_q), FadeIn(cifra_q), run_time=1.0)
        self.wait(3.2)

        # --- momento: panel de cifras (misma energia) ----------------------
        et_e = tag_hud(f"E[QPSK] = {fmt(E_QPSK, 3)}", font_size=18)
        panel = panel_derecha(et_e)
        self.play(FadeIn(panel), run_time=0.5)
        self.wait(2.0)

        # --- momento: 16-QAM mete cuatro veces mas puntos -------------------
        rot.mostrar(pie_curso("16-QAM mete 16 puntos en la MISMA energía: "
                              "cuatro bits por símbolo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(pq), FadeOut(seg_q), FadeOut(cifra_q),
                  run_time=0.6)
        p16 = plano.puntos(QAM16, BITS_QAM16, color=C_BIT, radio=0.065,
                           font_size=12)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in p16],
                              lag_ratio=0.04), run_time=1.6)
        et_e16 = tag_hud(f"E[16-QAM] = {fmt(E_QAM16, 3)}", font_size=18)
        panel16 = panel_derecha(et_e16)
        panel16.move_to(panel)
        self.play(Transform(panel, panel16), run_time=0.6)
        self.wait(2.6)

        # --- momento: d_min baja: el precio de la densidad ------------------
        rot.mostrar(pie_curso("Los puntos se acercan: el precio de la "
                              "densidad."), zona="abajo", run_time=0.5)
        i2, j2 = PAR_QAM16
        seg_16 = Line(plano.p(QAM16[i2]), plano.p(QAM16[j2]),
                     color=C_CIFRA, stroke_width=3.0)
        et_d16 = tag_hud(f"d_min = {fmt(D_QAM16, 3)}", font_size=18,
                         color=C_CIFRA)
        panel16b = panel_derecha(et_e16, et_d16)
        # los rotulos de bits ya cumplieron su papel: se apagan para que
        # la linea de d_min no los pise.
        etiquetas16 = p16[16:]
        self.play(FadeOut(etiquetas16), FadeOut(panel), FadeIn(panel16b),
                  run_time=0.6)
        self.play(Create(seg_16), run_time=0.7)
        self.wait(3.6)

        rot.mostrar(pie_curso("Misma energía, cuatro bits por símbolo: "
                              "d_min cae de 1.414 a 0.632."),
                    zona="abajo", run_time=0.5)
        self.wait(5.8)
