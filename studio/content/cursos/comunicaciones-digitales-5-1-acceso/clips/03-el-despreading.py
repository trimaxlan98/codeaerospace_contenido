class Clip3(Scene):
    """5.1.3 - El despreading: correlar con el codigo de u1 recupera SUS
    8 bits exactos (contador 8/8); con el codigo de u3 (no usado) todo
    da 0.0. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El despreading")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los 64 chips mezclados, arriba ------------------------
        rot.mostrar(pie_curso("Ahí siguen los 64 chips mezclados. El "
                              "receptor no separa por tiempo ni "
                              "frecuencia: separa por CÓDIGO."),
                    zona="abajo", run_time=0.5)
        mezcla = onda(T_CHIPS, Y_CHIPS, rango_y=(-2.7, 2.7), ancho=9.0,
                      alto=1.0, color=C_SENAL)
        mezcla.move_to(UP * 2.25)
        self.play(FadeIn(mezcla), run_time=0.9)
        self.wait(3.6)

        # --- momento: correlar con el codigo de u1 --------------------------
        rot.mostrar(pie_curso("Correlar chip a chip con el código de "
                              "u1, bloque por bloque, recupera sus "
                              "bits, uno a uno."),
                    zona="abajo", run_time=0.5)
        ks = np.arange(N_CHIPS_W, dtype=float)
        corr1 = onda(ks, COR_U1, rango_y=(-1.4, 1.4), ancho=6.2, alto=1.7,
                     color=C_CIFRA)
        corr1.move_to(UP * 0.30 + LEFT * 1.9)
        barras1 = corr1.muestras(ks, COR_U1, color=C_CIFRA, radio=0.05)
        et_c1 = tag_junto(corr1, "correlación con el código de u1",
                          direccion=DOWN, buff=0.16, font_size=15)
        self.play(FadeIn(corr1.ejes), FadeIn(et_c1), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(b) for b in barras1], lag_ratio=0.1),
                  run_time=1.6)
        self.wait(3.4)

        # --- momento: bits enviados vs bits recuperados ----------------------
        rot.mostrar(pie_curso("Los signos de esa correlación SON sus "
                              "bits: los ocho, exactos."),
                    zona="abajo", run_time=0.5)
        tren_env = tren_bits(BITS_U1_01, lado=0.4, color=C_BIT)
        tren_env.move_to(DOWN * 1.2 + RIGHT * 2.0)
        et_env = tag_junto(tren_env, "bits enviados", direccion=UP,
                           buff=0.12, font_size=15, color=C_BIT)
        tren_rec = tren_bits(SGN_U1_01, lado=0.4, color=C_CIFRA)
        tren_rec.move_to(DOWN * 2.1 + RIGHT * 2.0)
        et_rec = tag_junto(tren_rec, "bits recuperados", direccion=DOWN,
                           buff=0.12, font_size=15, color=C_CIFRA)
        self.play(FadeIn(tren_env), FadeIn(et_env), run_time=0.6)
        self.play(FadeIn(tren_rec, shift=0.15 * UP), FadeIn(et_rec),
                  run_time=1.1)
        aciertos = tag_hud(f"aciertos = {ACIERTOS_U1}/{N_CHIPS_W}",
                           font_size=20)
        aciertos.next_to(tren_env, RIGHT, buff=0.35)
        self.play(FadeIn(aciertos, shift=0.12 * LEFT), run_time=0.5)
        self.wait(4.6)

        # --- momento: el codigo ajeno, cero ----------------------------------
        rot.mostrar(pie_curso("Con el código de un usuario que nunca "
                              "transmitió, la correlación es CERO."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(tren_env), FadeOut(et_env), FadeOut(tren_rec),
                  FadeOut(et_rec), FadeOut(aciertos), FadeOut(corr1.ejes),
                  FadeOut(barras1), FadeOut(et_c1), run_time=0.5)
        corr3 = onda(ks, COR_U3, rango_y=(-1.4, 1.4), ancho=6.6, alto=1.9,
                     color=C_RUIDO)
        corr3.move_to(DOWN * 0.55)
        barras3 = corr3.muestras(ks, COR_U3, color=C_RUIDO, radio=0.05)
        et_c3 = tag_junto(corr3, "correlación con el código de u3 (no "
                          "usado)", direccion=DOWN, buff=0.16,
                          font_size=15)
        self.play(FadeIn(corr3.ejes), FadeIn(et_c3), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(b) for b in barras3], lag_ratio=0.1),
                  run_time=1.2)
        et_cero = tag_hud(f"pico = {fmt(COR_U3_PICO, 1)}", font_size=20,
                          color=C_RUIDO)
        et_cero.next_to(corr3, RIGHT, buff=0.35)
        self.play(FadeIn(et_cero), run_time=0.5)
        self.wait(4.8)
