class Clip3(Scene):
    """3 - PIRE: la potencia que apunta. El patron de radiacion pasa de
    isotropico (circulo) a lobulo de 45 dB a area visual constante, y la suma
    P + G se arma termino a termino. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("PIRE: la potencia que apunta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        # --- momento: la antena que reparte por igual ---------------------
        # `anclar_en` (no move_to): el emisor va en el VERTICE del lobulo, y
        # ahi se queda mientras el patron se estrecha.
        centro = LEFT * 2.6 + UP * 0.25
        patron = patron_ganancia(0.0, escala=1.05, color=C_SENAL)
        patron.anclar_en(centro)
        emisor = Dot(centro, radius=0.06, color=C_SENAL)

        self.play(Create(patron), FadeIn(emisor), run_time=1.2)
        self.wait(0.5)

        rot.mostrar(pie_curso("Una antena no fabrica potencia: decide hacia "
                              "dónde va."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: el mismo aire, mejor repartido ----------------------
        rot.mostrar(pie_curso("Toda la energía que deja de ir a los lados va "
                              "al frente."), zona="abajo", run_time=0.5)

        medio = patron.con_ganancia(20.0)
        self.play(Transform(patron, medio), run_time=1.3)
        self.wait(2.6)

        estrecho = patron_ganancia(45.0, escala=1.05,
                                   color=C_SENAL).anclar_en(centro)
        self.play(Transform(patron, estrecho), run_time=1.3)
        self.wait(2.2)

        # El satelite aparece justo donde apunta el lobulo, no a ojo.
        destino = estrecho.punta() + RIGHT * 0.75
        sat = satelite(escala=1.0).move_to(destino)
        self.play(FadeIn(sat, shift=0.2 * LEFT), run_time=0.7)
        self.wait(2.8)

        # --- momento: la suma que define la PIRE --------------------------
        rot.mostrar(pie_curso("Los vatios del amplificador y los decibelios "
                              "del plato se suman."), zona="abajo",
                    run_time=0.5)

        terminos = VGroup(
            Text(f"{P_TX_DBW:.0f} dBW", font=FUENTE_HUD, font_size=24,
                 color=C_SENAL),
            Text("+", font=FUENTE_HUD, font_size=24, color=C_TENUE),
            Text(f"{G_TX_DB:.0f} dB", font=FUENTE_HUD, font_size=24,
                 color=C_GANANCIA),
            Text("=", font=FUENTE_HUD, font_size=24, color=C_TENUE),
            Text(f"{PIRE_DBW:.0f} dBW", font=FUENTE_HUD, font_size=26,
                 color=C_MARGEN),
        ).arrange(RIGHT, buff=0.22)
        terminos.move_to(DOWN * 1.75)

        for parte in terminos:
            self.play(FadeIn(parte, shift=0.12 * UP), run_time=0.35)
        self.wait(4.4)

        rot.mostrar(formula_pie(r"\text{PIRE} = P_{tx} + G_{tx}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        rot.mostrar(pie_curso("Veinte vatios bien apuntados pesan como "
                              "cincuenta y ocho decibelios."), zona="abajo",
                    run_time=0.5)
        self.wait(5.4)
