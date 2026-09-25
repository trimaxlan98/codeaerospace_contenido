class Clip4(Scene):
    """8.2.4 - El diagrama del arreglo (S.factor_arreglo) para 2 y 8
    antenas, gemelas en la MISMA escala (grados, dB), barriendo el
    apuntamiento de -60 a +60: el haz de 8 antenas es mucho mas
    estrecho. Anchos a -3 dB medidos con malla fina (2 -> 60 grados,
    8 -> 13 grados). Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El barrido"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- las dos gemelas: MISMA escala (grados, dB) ----------------------
        PISO, TECHO = -30.0, 0.0
        th0, db0 = S.factor_arreglo(-60.0, 0.5, 2)
        esp_top = S.Espectro(th0, db0, piso=PISO, techo=TECHO, ancho=11.2,
                             alto=1.7, color=C_CALCULO, area=False)
        esp_top.shift(UP * 1.45)
        th0b, db0b = S.factor_arreglo(-60.0, 0.5, 8)
        esp_bot = S.Espectro(th0b, db0b, piso=PISO, techo=TECHO, ancho=11.2,
                             alto=1.7, color=C_CALCULO, area=False)
        esp_bot.shift(DOWN * 1.35)

        marcas = esp_bot.marcas([-90, -60, -30, 0, 30, 60, 90], font_size=18)
        et_grados = tag_junto(marcas, "grados", RIGHT, buff=0.18,
                              font_size=18)
        et_db_top = tag_junto(esp_top, "dB", LEFT, buff=0.3, font_size=18)

        # fila entre el titulo y el panel de arriba: "2 antenas" (dato) a la
        # izquierda; fila entre los dos paneles: "8 antenas" a la izquierda.
        d_n2 = tag_dato("2 antenas", font_size=18)
        d_n2.next_to(esp_top, UP, buff=0.16).align_to(esp_top, LEFT)
        d_n8 = tag_dato("8 antenas", font_size=18)
        d_n8.next_to(esp_bot, UP, buff=0.16).align_to(esp_bot, LEFT)

        self.play(Create(esp_top.ejes), Create(esp_bot.ejes), FadeIn(marcas),
                  FadeIn(et_grados), FadeIn(et_db_top), FadeIn(d_n2),
                  FadeIn(d_n8), run_time=1.0)
        self.wait(0.5)
        self.play(Create(esp_top.curva), Create(esp_bot.curva), run_time=1.2)
        self.wait(1.2)

        # --- el apuntamiento barre de -60 a +60, las curvas reaccionan -------
        apunta = ValueTracker(-60.0)
        curva_top = always_redraw(
            lambda: esp_top.con_db(
                S.factor_arreglo(apunta.get_value(), 0.5, 2)[1]).curva)
        curva_bot = always_redraw(
            lambda: esp_bot.con_db(
                S.factor_arreglo(apunta.get_value(), 0.5, 8)[1]).curva)
        marca_top = always_redraw(
            lambda: esp_top.marca_f(apunta.get_value(), color=C_DATO,
                                    ancho=1.6))
        marca_bot = always_redraw(
            lambda: esp_bot.marca_f(apunta.get_value(), color=C_DATO,
                                    ancho=1.6))
        # el rotulo del barrido, CENTRADO sobre el panel de arriba (no a un
        # lado: ahi viven "2 antenas" y, mas tarde, el ancho medido).
        et_apunta = tag_dato("apuntamiento", font_size=16)
        et_apunta.next_to(esp_top, UP, buff=0.16)
        self.remove(esp_top.curva, esp_bot.curva)
        self.add(curva_top, curva_bot, marca_top, marca_bot)
        self.play(FadeIn(et_apunta), run_time=0.4)
        self.wait(0.6)

        self.play(apunta.animate.set_value(60.0), run_time=5.0,
                  rate_func=linear)
        self.wait(1.0)
        self.play(apunta.animate.set_value(0.0), run_time=2.2,
                  rate_func=linear)
        self.wait(0.8)

        curva_top.clear_updaters()
        curva_bot.clear_updaters()
        marca_top.clear_updaters()
        marca_bot.clear_updaters()
        self.play(FadeOut(marca_top), FadeOut(marca_bot), FadeOut(et_apunta),
                  run_time=0.5)

        # --- el ancho a -3 dB, medido con malla fina (estable) ----------------
        def hpbw(n_ant):
            th, db = S.factor_arreglo(0.0, 0.5, n_ant, puntos=3601)
            idx = np.where(db >= -3.0)[0]
            return float(th[idx[-1]] - th[idx[0]])

        ancho2, ancho8 = hpbw(2), hpbw(8)
        et_a2 = tag_hud(f"{fmt(ancho2, 0)} grados", font_size=20)
        et_a2.next_to(esp_top, UP, buff=0.16).align_to(esp_top, RIGHT)
        et_a8 = tag_hud(f"{fmt(ancho8, 0)} grados", font_size=20)
        et_a8.next_to(esp_bot, UP, buff=0.16).align_to(esp_bot, RIGHT)
        self.play(FadeIn(et_a2), FadeIn(et_a8), run_time=0.7)
        rot.mostrar(cifra_pie(f"{fmt(ancho2, 0)} y {fmt(ancho8, 0)} "
                              f"grados"), zona="abajo", run_time=0.5)
        self.wait(5.6)

        cierre_leccion(
            self, rot, "Dos antenas bastan", "para saber de donde viene.",
            esp_top, esp_bot, curva_top, curva_bot, marcas, et_grados,
            et_db_top, d_n2, d_n8, et_a2, et_a8)
