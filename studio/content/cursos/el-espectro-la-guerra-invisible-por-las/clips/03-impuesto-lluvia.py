class Clip3(Scene):
    """3 - El impuesto de la lluvia. El mismo campo de gotas contra una
    onda larga (banda L, pasa de largo) y una onda corta (banda Ka, choca)
    y la curva de atenuacion por lluvia con los mismos GHz marcados en
    relevo: la misma tormenta pesa distinto segun la banda."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo -------------------------------------------
        modulo = hud_modulo("Modulo 03")
        titulo = titulo_curso("El impuesto de la lluvia")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.35)
        rot.mostrar(titulo, zona="arriba", run_time=0.35)
        self.wait(0.3)

        # --- momento: banda L, la onda larga pasa de largo --------------------
        rot.mostrar(pie_curso("Para una onda larga, una gota es nada: "
                              "pasa de largo."), zona="abajo", run_time=0.35)
        campo_l = gotas_y_onda(lambda_rel=1.0)
        campo_l.move_to(np.array([-3.3, 0.9, 0.0]))
        tag_l = tag_junto(campo_l, "banda L", direccion=LEFT, buff=0.3)
        self.play(FadeIn(campo_l), run_time=0.6)
        self.play(FadeIn(tag_l, shift=0.12 * RIGHT), run_time=0.35)
        self.wait(5.0)

        # --- momento: banda Ka, la onda choca ----------------------------------
        rot.mostrar(pie_curso("A 20 GHz la onda mide como la gota: choca, "
                              "se absorbe, se dispersa."), zona="abajo",
                   run_time=0.35)
        campo_ka = gotas_y_onda(lambda_rel=0.15)
        campo_ka.move_to(np.array([-3.3, -1.1, 0.0]))
        tag_ka = tag_junto(campo_ka, "banda Ka", direccion=DOWN, buff=0.3)
        self.play(FadeIn(campo_ka), run_time=0.6)
        self.play(FadeIn(tag_ka, shift=0.12 * UP), run_time=0.35)
        self.wait(5.2)

        # --- momento: la curva de lluvia se dibuja -----------------------------
        rot.mostrar(pie_curso("La industria lo modela con una ley "
                              "simple..."), zona="abajo", run_time=0.35)
        lluvia = curva_lluvia()
        lluvia.move_to(np.array([2.9, -0.1, 0.0]))
        self.play(FadeIn(lluvia), run_time=0.7)
        self.wait(4.5)
        rot.mostrar(formula_pie("\\gamma_R = k\\,R^{\\alpha}"), zona="abajo",
                   run_time=0.35)
        self.wait(2.0)

        # --- momento: dos puntos en relevo, Ku contra Ka -----------------------
        rot.mostrar(pie_curso("La misma tormenta: en Ku molesta, en Ka "
                              "manda."), zona="abajo", run_time=0.35)
        punto_12 = punto_brillante(lluvia.punto_de(12.0, intensa=True),
                                   color=C_PERDIDA, radio=0.07)
        tag_12 = tag_junto(punto_12, "3.0 dB/km", direccion=UP, buff=0.32,
                          font_size=16, color=C_PERDIDA)
        self.play(FadeIn(punto_12), FadeIn(tag_12), run_time=0.4)
        self.wait(1.3)
        punto_20 = punto_brillante(lluvia.punto_de(20.0, intensa=True),
                                   color=C_PERDIDA, radio=0.07)
        tag_20 = tag_junto(punto_20, "6.9 dB/km", direccion=UP, buff=0.35,
                          font_size=16, color=C_PERDIDA)
        self.play(FadeOut(punto_12), FadeOut(tag_12),
                 FadeIn(punto_20), FadeIn(tag_20), run_time=0.4)
        self.wait(5.5)

        # --- momento: cierre -----------------------------------------------------
        rot.mostrar(pie_curso("Por eso la banda se elige ANTES de "
                              "construir."), zona="abajo", run_time=0.35)
        self.wait(5.6)
