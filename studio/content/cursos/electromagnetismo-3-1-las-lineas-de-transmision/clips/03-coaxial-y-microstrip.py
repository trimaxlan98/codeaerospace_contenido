class Clip3(Scene):
    """3.1.3 - Coaxial y microstrip: dos formas de guiar una señal, con
    el campo dentro. Z0 sale de la geometria (D/d en el coaxial, ancho y
    sustrato en la microstrip) — nunca de una resistencia escondida.
    (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Coaxial y microstrip")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el corte del coaxial -----------------------------------
        rot.mostrar(pie_curso("Corta el coaxial por la mitad: un alma al "
                              "centro, una malla alrededor."),
                    zona="abajo", run_time=0.5)
        cox = corte_coaxial(d_sobre_d=6.52, er=2.25, radio_ext=1.15,
                            color_e=C_E, color_b=C_B)
        cox.move_to(LEFT * 3.1 + DOWN * 0.35)
        self.play(FadeIn(cox.dielectrico), FadeIn(cox.conductores),
                  run_time=0.7)
        self.wait(4.0)

        rot.mostrar(pie_curso("El campo electrico va radial, del alma a "
                              "la malla."), zona="abajo", run_time=0.5)
        self.play(FadeIn(cox.flechas_e), run_time=0.8)
        self.wait(4.2)

        rot.mostrar(pie_curso("El magnetico se cierra en circulos "
                              "alrededor del alma."), zona="abajo",
                    run_time=0.5)
        self.play(Create(cox.lineas_b), run_time=0.9)
        self.wait(4.2)

        cifra_cox = tag_hud(f"Z0 = {cox.z0():.0f} ohm", font_size=18,
                            color=C_CALCULO)
        cifra_cox.next_to(cox, DOWN, buff=0.35)
        rot.mostrar(pie_curso("Esta geometria, calculada, da exactamente "
                              "setenta y cinco ohmios."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(cifra_cox, shift=0.1 * UP), run_time=0.6)
        self.wait(4.4)

        # --- momento: la microstrip, la placa del LNB --------------------------
        rot.mostrar(pie_curso("Esta es la otra forma de guiar una señal: "
                              "la microstrip."), zona="abajo",
                    run_time=0.5)
        strip = corte_microstrip(z0_ohm=Z0_RF, color_e=C_E, color_b=C_B)
        strip.scale(0.62)
        strip.move_to(RIGHT * 2.8 + DOWN * 0.35)
        self.play(FadeIn(strip.dielectrico), FadeIn(strip.conductores),
                  run_time=0.6)
        self.play(FadeIn(strip.flechas_e), Create(strip.lineas_b),
                  run_time=0.8)
        self.wait(4.4)

        etiqueta_strip = tag_junto(strip, "pista, sustrato, plano de "
                                   "masa: la placa del LNB de un plato",
                                   DOWN, buff=0.3, font_size=15)
        self.play(FadeIn(etiqueta_strip, shift=0.1 * UP), run_time=0.6)
        self.wait(4.6)

        rot.mostrar(pie_curso("Coaxial o microstrip: la impedancia es "
                              "GEOMETRIA, no una resistencia escondida."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
