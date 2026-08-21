class Clip2(Scene):
    """2.1.2 - BPSK: bits 0/1 voltean la fase 180 grados; en la onda se ven
    los saltos, en el plano IQ dos puntos (+-1). Un bit por simbolo.
    (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("BPSK: un bit por vuelco")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los bits a mandar -----------------------------------
        rot.mostrar(pie_curso("Estos bits hay que meterlos en la fase, "
                              "uno por simbolo."),
                    zona="abajo", run_time=0.5)
        tren = tren_bits(BITS_BPSK, lado=0.46)
        tren.move_to(LEFT * 3.3 + DOWN * 1.95)
        self.play(LaggedStart(*[FadeIn(c) for c in tren.celdas],
                              lag_ratio=0.15),
                  FadeIn(tren.digitos), run_time=1.0)
        self.wait(2.4)

        # --- momento: la escena, las dos vistas -----------------------------
        rot.mostrar(pie_curso("La misma onda, y su reflejo en el plano "
                              "I/Q: dos vistas del mismo simbolo."),
                    zona="abajo", run_time=0.5)
        on = onda(T_BPSK, Y_BPSK, rango_y=(-1.15, 1.15), ancho=6.2, alto=2.3)
        on.move_to(LEFT * 3.3 + UP * 0.65)
        piq = plano_iq(unidad=1.0, alcance=1.6)
        piq.move_to(RIGHT * 3.5 + DOWN * 0.25)
        pares_bpsk = piq.puntos(PUNTOS_BPSK, bits=BITS_TABLA_BPSK,
                                color=C_BIT)
        self.play(FadeIn(on.ejes), FadeIn(piq), FadeIn(pares_bpsk),
                  run_time=0.9)
        self.wait(1.8)

        # --- momento: bit 0 -> fase 0, bit 1 -> fase 180 --------------------
        rot.mostrar(pie_curso("Bit 0: fase 0. Bit 1: fase 180 grados. La "
                              "portadora vuelca."),
                    zona="abajo", run_time=0.5)
        marcador = Dot(piq.p(PUNTOS_BPSK[BITS_BPSK[0]]), radius=0.11,
                       color=C_CIFRA)
        tren.marcar(0, color=C_CIFRA)
        seg0 = on.curva_de(*SEG_BPSK[0], color=C_SENAL)
        self.play(Create(seg0), FadeIn(marcador, scale=0.4), run_time=0.7)
        self.wait(1.8)

        fronteras_dibujadas = []
        for k in range(1, len(BITS_BPSK)):
            seg = on.curva_de(*SEG_BPSK[k], color=C_SENAL)
            hay_vuelco = BITS_BPSK[k] != BITS_BPSK[k - 1]
            frontera = on.vertical_en(
                FRONTERAS_BPSK[k - 1], color=C_CIFRA if hay_vuelco else C_EJE)
            fronteras_dibujadas.append(frontera)
            tren.marcar(k, color=C_CIFRA)
            self.play(Create(frontera), Create(seg),
                      marcador.animate.move_to(
                          piq.p(PUNTOS_BPSK[BITS_BPSK[k]])),
                      run_time=1.0)
            self.wait(0.9)

        # --- momento: cuando el bit se repite, no hay vuelco -----------------
        rot.mostrar(pie_curso("Cuando el bit se repite, la fase no "
                              "cambia: sin vuelco."),
                    zona="abajo", run_time=0.5)
        i_sin_vuelco = next(k for k in range(1, len(BITS_BPSK))
                            if BITS_BPSK[k] == BITS_BPSK[k - 1])
        self.play(Indicate(fronteras_dibujadas[i_sin_vuelco - 1],
                           color=C_EJE, scale_factor=1.3), run_time=0.9)
        self.wait(3.2)

        # --- momento: un bit por simbolo ---------------------------------------
        rot.mostrar(pie_curso("Un bit, un simbolo: la tasa de bits es la "
                              "tasa de simbolos."),
                    zona="abajo", run_time=0.5)
        panel = panel_derecha(
            tag_hud(f"tasa = {fmt(TASA_SIMBOLOS, 1)} simb/s", color=C_BIT),
            tag_hud(f"= {fmt(TASA_BITS_BPSK, 1)} bit/s", color=C_CIFRA))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(5.4)
