class Clip4(Scene):
    """3.5.4 - Calculo de cl y cd de onda; origen del arrastre de onda.

    Se juntan los dos perfiles y sus numeros, y se separa el arrastre en sus
    dos fuentes: el de sustentacion (que la placa plana ya tenia) y el de
    espesor (que solo aparece con un cuerpo grueso). Dos sumandos que no
    compiten: se suman. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("De dónde sale el arrastre de onda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Los tres casos del modulo, en columnas. Todas las cifras salen del
        # style_block, que a su vez las saca de la libreria.
        casos = (("placa plana", f"α = {ALFA:g}°", PLACA["cl"], PLACA["cd"],
                  C_SUB),
                 ("rombo", f"α = {ALFA:g}°", ROMBO["cl"], ROMBO["cd"],
                  C_TRANS),
                 ("rombo", "α = 0°", ROMBO_SIN_ALFA["cl"],
                  ROMBO_SIN_ALFA["cd"], C_CALCULO))
        columnas = VGroup()
        for nombre, angulo, cl, cd, color in casos:
            columna = VGroup(
                Text(nombre, font_size=21, color=color),
                Text(angulo, font_size=18, color=C_TENUE),
                Text(f"cl = {cl:+.4f}", font=FUENTE_HUD, font_size=19,
                     color=color),
                Text(f"cd = {cd:.4f}", font=FUENTE_HUD, font_size=19,
                     color=color)).arrange(DOWN, buff=0.18)
            columnas.add(columna)
        columnas.arrange(RIGHT, buff=1.05).move_to(UP * 0.75)

        pies = ("La placa plana: sustenta, y arrastra solo por sustentar.",
                "El rombo al mismo ángulo: sustenta parecido y arrastra "
                "bastante más.",
                "Y el mismo rombo sin ángulo: no sustenta nada, pero sigue "
                "arrastrando.")
        for columna, pie in zip(columnas, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(columna, shift=0.12 * UP), run_time=0.8)
            self.wait(4.6)

        # --- momento: los dos sumandos -------------------------------------
        suma = MathTex(r"c_{d,\text{onda}} = "
                       r"c_{d,\text{sustentación}} + c_{d,\text{espesor}}",
                       font_size=38, color=C_SUPER)
        suma.move_to(DOWN * 1.65)
        self.play(Write(suma), run_time=1.1)
        rot.mostrar(pie_curso("El arrastre de onda tiene dos fuentes, y no "
                              "compiten: se suman."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Por eso un perfil supersónico es delgado como "
                              "una cuchilla. Cada milímetro de espesor se "
                              "paga."), zona="abajo", run_time=0.5)
        self.wait(5.4)
