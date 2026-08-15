class Clip2(Scene):
    """4.3.2 - Escuchar el frio del cielo: la temperatura de ruido. Al
    cenit la antena ve 20 K; hacia el horizonte, los 290 K del planeta.
    N = k T B pone la cifra: -131.3 dBW de suelo de ruido. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Escuchar el frío del cielo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        arriba = cielo_ruido("cielo", t_cielo=T_CIELO, t_suelo=T_SUELO)
        abajo = cielo_ruido("suelo", t_cielo=T_CIELO, t_suelo=T_SUELO)
        # El cono de la antena rasante cruza por donde nace el termometro:
        # se aparta el termometro, no el haz (el haz es el dato).
        abajo.termometro.shift(RIGHT * 1.15)
        for pieza in (arriba, abajo):
            pieza.cono.set_stroke(width=2.4, opacity=1.0)
            pieza.scale(0.82)
        arriba.move_to(LEFT * 3.7 + DOWN * 0.55)
        abajo.move_to(RIGHT * 2.5 + DOWN * 0.55)
        # Los dos platos se apoyan a la misma altura: la comparacion se lee
        # sola cuando la linea de base coincide.
        abajo.shift(UP * (arriba.plato[1].get_bottom()[1]
                          - abajo.plato[1].get_bottom()[1]))

        tag_arriba = tag_hud(f"{arriba.t_antena():.0f} K", font_size=19,
                             color=C_CALCULO)
        tag_arriba.next_to(arriba.termometro, UP, buff=0.16)
        tag_abajo = tag_hud(f"{abajo.t_antena():.0f} K", font_size=19,
                            color=C_CARGA)
        tag_abajo.next_to(abajo.termometro, UP, buff=0.16)
        pie_arriba = tag_junto(arriba.plato, "al cenit", DOWN, buff=0.22)
        pie_abajo = tag_junto(abajo.plato, "al horizonte", DOWN, buff=0.22)

        # --- momento: la antena que escucha el cielo ------------------------
        rot.mostrar(pie_curso("Contra la lluvia se pelea. Contra el ruido "
                              "no: el ruido es el suelo del mundo."),
                    zona="abajo", run_time=0.45)
        self.play(FadeIn(arriba), FadeIn(pie_arriba), run_time=0.7)
        self.wait(4.6)

        rot.mostrar(pie_curso("Apuntada al cenit, la antena escucha el "
                              "fondo frío del universo: veinte kelvin."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.play(FadeIn(tag_arriba, shift=0.1 * UP), run_time=0.5)
        self.wait(4.6)

        # --- momento: bajar la mira ensucia la antena -----------------------
        rot.mostrar(pie_curso("Baja la mira al horizonte y entra el "
                              "planeta: doscientos noventa kelvin."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.play(FadeIn(abajo), FadeIn(pie_abajo), FadeIn(tag_abajo),
                  run_time=0.8)
        self.wait(4.6)

        # --- momento: la formula que convierte grados en vatios -------------
        rot.mostrar(formula_pie(r"N = k\,T\,B"), zona="abajo",
                    run_time=0.45, salida=0.25)
        self.wait(4.6)

        # --- momento: la cifra ---------------------------------------------
        cifra = tag_hud(f"{N_DBW:.1f} dBW", font_size=30)
        cifra.move_to(UP * 1.55)
        detalle = tag_hud(f"T = {T_SISTEMA:.0f} K   B = "
                          f"{B_TRANSPONDEDOR / 1e6:.0f} MHz",
                          font_size=17, color=C_TENUE)
        detalle.next_to(cifra, DOWN, buff=0.20)
        rot.mostrar(pie_curso("Ciento cincuenta kelvin de sistema y un "
                              "transpondedor de treinta y seis megahercios."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.play(FadeIn(cifra, scale=1.15), FadeIn(detalle), run_time=0.7)
        self.wait(4.6)

        rot.mostrar(pie_curso("Ese es el suelo. Toda señal que baja del "
                              "cielo tiene que asomar por encima."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.wait(4.8)
