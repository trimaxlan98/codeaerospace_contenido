class Clip6(Scene):
    """6 - La cascada. El clip central: los cinco terminos del presupuesto
    entran uno a uno, cada barra colgando de donde acabo la anterior, y la
    barra cian del saldo cierra la cuenta. (~43 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))

        titulo = titulo_curso("La cascada")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        rot.mostrar(pie_curso("Todo el enlace cabe en una fila de sumas y "
                              "restas."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: los terminos, uno por uno ---------------------------
        # Los valores salen del style_block: esta cascada es el mismo enlace
        # que el clip 1 mostro en vatios.
        casc = cascada_db([("PIRE", PIRE_DBW), ("FSPL", -FSPL_DB),
                           ("ATM", -L_ATM_DB), ("G/T", GT_DB), ("-k", K_DBW)],
                          ancho=6.4, alto=2.7)
        casc.move_to(DOWN * 0.15)
        self.play(FadeIn(casc[0]), run_time=0.5)   # la linea base del cero

        self.play(casc.aparecer(0), run_time=0.8)
        self.wait(1.6)

        rot.mostrar(pie_curso("Verde suma, rojo resta."), zona="abajo",
                    run_time=0.5)
        self.play(casc.aparecer(1), run_time=0.9)
        self.wait(3.0)

        for i in (2, 3, 4):
            self.play(casc.aparecer(i), run_time=0.8)
            self.wait(1.5)
        self.wait(2.2)

        # --- momento: lo que sobra ----------------------------------------
        rot.mostrar(pie_curso("Lo que sobra al final es lo único que "
                              "importa."), zona="abajo", run_time=0.5)
        self.play(casc.aparecer_saldo(), run_time=1.0)
        self.wait(4.8)

        rot.mostrar(formula_pie(r"C/N_0 = \text{PIRE} - \text{FSPL} - "
                                r"L_{atm} + G/T - 10\log_{10} k",
                                font_size=30), zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: de potencia a bits ----------------------------------
        rot.mostrar(pie_curso("Repartido entre los bits por segundo, dice si "
                              "el mensaje se entiende."), zona="abajo",
                    run_time=0.5)

        # El saldo y la conversion salen de la cascada y del style_block.
        conversion = VGroup(
            Text(f"{casc.acumulado(-1):.1f} dBHz", font=FUENTE_HUD,
                 font_size=22, color=C_MARGEN),
            Text("−  10 log Rb", font=FUENTE_HUD, font_size=22,
                 color=C_TENUE),
            Text(f"=  Eb/N0  {EBN0_DB:.1f} dB", font=FUENTE_HUD,
                 font_size=22, color=C_GANANCIA),
        ).arrange(RIGHT, buff=0.34)
        conversion.next_to(casc, UP, buff=0.30)
        if conversion.width > config.frame_width - 1.6:
            conversion.scale_to_fit_width(config.frame_width - 1.6)

        for parte in conversion:
            self.play(FadeIn(parte, shift=0.1 * UP), run_time=0.45)
        self.wait(5.4)
