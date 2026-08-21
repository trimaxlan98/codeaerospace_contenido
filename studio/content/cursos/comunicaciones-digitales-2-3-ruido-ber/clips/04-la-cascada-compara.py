class Clip4(Scene):
    """2.3.4 - QPSK y 16-QAM en el mismo eje: la densa lleva el doble de
    bits por simbolo y paga por ellos casi 4 dB. Cierre de leccion.
    (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La cascada compara familias")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la cascada de QPSK, ya conocida ---------------------
        rot.mostrar(pie_curso("La cascada de QPSK, medida y teorica, "
                              "vuelve al eje."),
                    zona="abajo", run_time=0.5)
        cb = curva_ber(x0=0.0, x1=14.0, exp_min=5, ancho=5.6, alto=3.4)
        cb.move_to(LEFT * 2.9 + DOWN * 0.15)
        c_qpsk = cb.curva(lambda db: ber_teorica_qam(4, db), color=C_CIFRA)
        m_qpsk = cb.puntos_medidos(BER_QPSK, color=C_COD, radio=0.075)
        leyenda = panel_derecha(
            tag_hud(f"QPSK: {K_QPSK} bits/simbolo", font_size=20,
                    color=C_CIFRA),
            tag_hud(f"16-QAM: {K_QAM16} bits/simbolo", font_size=20,
                    color=C_BANDA),
            buff=0.26)
        self.play(FadeIn(cb), run_time=0.8)
        self.play(Create(c_qpsk), run_time=1.2)
        self.play(FadeIn(m_qpsk), run_time=0.6)
        self.play(FadeIn(leyenda), run_time=0.5)
        self.wait(3.6)

        # --- momento: la densa, en el mismo eje ---------------------------
        rot.mostrar(pie_curso("Al lado, 16-QAM: el doble de bits en cada "
                              "simbolo, la misma energia media."),
                    zona="abajo", run_time=0.5)
        c_qam = cb.curva(lambda db: ber_teorica_qam(16, db), color=C_BANDA)
        m_qam = cb.puntos_medidos(BER_QAM16, color=C_COD, radio=0.075)
        self.play(Create(c_qam), run_time=1.6)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in m_qam],
                              lag_ratio=0.25), run_time=1.3)
        self.wait(4.2)

        # --- momento: el precio, medido en dB -----------------------------
        rot.mostrar(pie_curso("A la MISMA tasa de error, la densa pide "
                              "mas senal. Cuanta, exactamente."),
                    zona="abajo", run_time=0.5)
        nivel = DashedLine(cb.en(0.0, BER_OBJ), cb.en(DB_OBJ_QAM16, BER_OBJ),
                           color=C_EJE, stroke_width=1.6, dash_length=0.07)
        et_nivel = MathTex(r"\mathrm{BER} = 10^{-4}", font_size=30,
                           color=C_CALCULO)
        et_nivel.move_to(cb.en(3.4, BER_OBJ) + UP * 0.28)
        v_qpsk = cb.vertical_en(DB_OBJ_QPSK, color=C_CIFRA)
        v_qam = cb.vertical_en(DB_OBJ_QAM16, color=C_BANDA)
        self.play(Create(nivel), FadeIn(et_nivel), run_time=0.8)
        self.play(Create(v_qpsk), Create(v_qam), run_time=0.9)
        tramo = Line(cb.en(DB_OBJ_QPSK, 1.0), cb.en(DB_OBJ_QAM16, 1.0),
                     stroke_opacity=0.0)
        brecha = llave(tramo, f"{fmt(BRECHA_DB, 1)} dB", direccion=UP,
                       font_size=24)
        detalle = VGroup(
            tag_hud("a BER = 10^-4", font_size=19),
            tag_hud(f"QPSK: {fmt(DB_OBJ_QPSK, 1)} dB", font_size=19,
                    color=C_CIFRA),
            tag_hud(f"16-QAM: {fmt(DB_OBJ_QAM16, 1)} dB", font_size=19,
                    color=C_BANDA),
            tag_hud(f"precio = {fmt(BRECHA_DB, 1)} dB", font_size=19),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        detalle.next_to(leyenda, DOWN, buff=0.45)
        self.play(GrowFromCenter(brecha), run_time=0.8)
        self.play(FadeIn(detalle, shift=0.12 * UP), run_time=0.6)
        self.wait(4.6)

        # --- cierre de leccion --------------------------------------------
        cierre_leccion(
            self, rot,
            "El ruido no se negocia.",
            "Se mide, y se le hace sitio.",
            "Siguiente leccion: el precio de la distancia.",
            cb, c_qpsk, m_qpsk, c_qam, m_qam, leyenda, nivel, et_nivel,
            v_qpsk, v_qam, brecha, detalle)
