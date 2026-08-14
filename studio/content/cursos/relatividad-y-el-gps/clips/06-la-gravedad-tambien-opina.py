class Clip6(Scene):
    """6 - La gravedad tambien opina. Relatividad general: los relojes
    hondos en el pozo laten mas despacio. La curva estrella: deriva neta
    contra altura, cruzando cero en la altura de empate. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 06")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La gravedad también opina")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: el pozo -----------------------------------------------
        rot.mostrar(pie_curso("Einstein, 1915: cuanto más hondo en el "
                              "pozo, más despacio late tu reloj."),
                    zona="abajo", run_time=0.5)
        pozo = pozo_potencial().scale(0.82)
        pozo.shift(np.array([0.0, 0.55, 0.0]) - pozo.get_center())
        self.play(Create(pozo.curva[0]), Create(pozo.curva[1]),
                  run_time=1.4)
        self.play(FadeIn(pozo.tierra, scale=0.6), run_time=0.6)

        tu_reloj = Dot(pozo.en(1.06), radius=0.07, color=C_TIERRA)
        tag_tu = tag_junto(tu_reloj, "tú", DOWN + RIGHT, buff=0.10,
                           font_size=16)
        sat_reloj = Dot(pozo.en(4.1), radius=0.07, color=C_SATELITE)
        tag_sat = tag_junto(sat_reloj, "el GPS", UP, buff=0.12,
                            font_size=16)
        self.play(FadeIn(tu_reloj, scale=0.5), FadeIn(tag_tu),
                  run_time=0.6)
        self.play(FadeIn(sat_reloj, scale=0.5), FadeIn(tag_sat),
                  run_time=0.6)
        self.wait(1.6)

        # --- momento: la cifra de la general --------------------------------
        rot.mostrar(pie_curso("El reloj del GPS, alto y lejos de la "
                              "Tierra, adelanta 46 µs cada día."),
                    zona="abajo", run_time=0.5)
        cifra_gr = tag_hud(f"{DERIVA_GR:+.2f} µs/día", font_size=17,
                           color=C_GRAVEDAD)
        cifra_gr.next_to(sat_reloj, RIGHT, buff=0.22)
        self.play(FadeIn(cifra_gr, shift=0.15 * RIGHT), run_time=0.7)
        self.wait(2.6)

        # --- momento: las dos opinan a la vez -------------------------------
        rot.mostrar(pie_curso("¿Y la velocidad? Las dos relatividades "
                              "opinan a la vez: todo depende de la "
                              "altura."), zona="abajo", run_time=0.5)
        self.play(FadeOut(pozo), FadeOut(tu_reloj), FadeOut(tag_tu),
                  FadeOut(sat_reloj), FadeOut(tag_sat),
                  FadeOut(cifra_gr), run_time=0.7)

        deriva = curva_deriva()
        deriva.shift(np.array([0.2, 0.45, 0.0]) - deriva.get_center())
        etiq_x = tag_junto(deriva.cero, "altura (escala log)", UP,
                           buff=0.10, font_size=13)
        etiq_x.align_to(deriva.cero, RIGHT).shift(LEFT * 0.05)
        etiq_y = tag_junto(deriva.ejes[0], "µs/día", UP, buff=0.10,
                           font_size=13)
        self.play(Create(deriva.ejes[0]), Create(deriva.cero),
                  FadeIn(etiq_y), FadeIn(etiq_x), run_time=0.8)
        self.play(Create(deriva.curva), run_time=1.9)
        self.wait(1.0)

        # --- momento: ISS, empate, GPS --------------------------------------
        pie_empate = pie_curso(f"A {H_EMPATE/1000:.0f} km de altura se "
                               "empatan: por debajo gana la velocidad, "
                               "por encima la gravedad.")
        rot.mostrar(pie_empate, zona="abajo", run_time=0.5)

        p_iss = Dot(deriva.en(ALTURA_ISS), radius=0.06, color=C_ERROR)
        t_iss = tag_hud(f"ISS  {DERIVA_ISS:+.1f}", font_size=14,
                        color=C_ERROR)
        t_iss.next_to(p_iss, DOWN + RIGHT, buff=0.10)
        self.play(FadeIn(p_iss, scale=0.4), FadeIn(t_iss), run_time=0.7)
        self.wait(1.0)

        p_emp = Dot(deriva.en(H_EMPATE), radius=0.06, color=C_TIERRA)
        t_emp = tag_hud(f"empate  {H_EMPATE/1000:.0f} km", font_size=14,
                        color=C_TIERRA)
        t_emp.next_to(p_emp, DOWN + RIGHT, buff=0.12)
        self.play(FadeIn(p_emp, scale=0.4), FadeIn(t_emp), run_time=0.7)
        self.wait(1.3)

        p_gps = Dot(deriva.en(RADIO_GPS - RADIO_TIERRA), radius=0.06,
                    color=C_SATELITE)
        t_gps = tag_hud(f"GPS  {DERIVA_NETA:+.1f} µs/día", font_size=14)
        t_gps.next_to(p_gps, DOWN + LEFT, buff=0.12)
        self.play(FadeIn(p_gps, scale=0.4), FadeIn(t_gps), run_time=0.7)
        self.wait(2.2)

        # --- momento: la sintesis -------------------------------------------
        rot.mostrar(pie_curso("Los astronautas de la ISS envejecen "
                              "menos; el reloj del GPS gana tiempo. "
                              "La misma física."), zona="abajo",
                    run_time=0.5)
        self.wait(5.4)
