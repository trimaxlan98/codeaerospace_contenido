class Clip4(Scene):
    """4.3.4 - De la carga al bit: el recap de la familia entera. Las
    siete etapas se encienden una a una, cada una con la frase de su
    leccion, y la familia cierra a pantalla limpia. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("De la carga al bit")
        rot.mostrar(titulo, zona="arriba", run_time=0.5)

        arco = arco_familia()
        arco.move_to(UP * 0.35)
        # Los pies de cada etapa comparten linea base: colgados de cada
        # icono quedarian a alturas distintas (los iconos no miden igual).
        y_base = arco.get_bottom()[1] - 0.34
        y_alto = arco.get_top()[1] + 0.34
        nombres = ["la carga", "el campo", "la onda", "la línea",
                   "la antena", "el espacio", "el bit"]
        lecciones = ["1.1", "1.2-1.3", "2.1-2.3", "3.1-3.2", "3.3",
                     "4.1-4.2", "4.3"]
        etiquetas = VGroup()
        for i, nombre in enumerate(nombres):
            x = arco.etapa(i).get_center()[0]
            t = Text(nombre, font_size=19, color=C_TENUE)
            t.set_opacity(0.9)
            t.move_to([x, y_base, 0.0])
            n = tag_hud(lecciones[i], font_size=15, color=C_TENUE)
            n.set_opacity(0.75)
            n.move_to([x, y_alto, 0.0])
            etiquetas.add(VGroup(t, n))

        def encender(i, espera):
            """Enciende la etapa i (y la flecha que la trae) y respira."""
            anims = [FadeIn(arco.etapa(i), scale=1.2),
                     FadeIn(etiquetas[i], shift=0.1 * UP)]
            if i > 0:
                anims.append(GrowArrow(arco.flecha(i - 1)))
            self.play(*anims, run_time=0.45)
            self.wait(espera)

        # --- 1.1: la carga --------------------------------------------------
        rot.mostrar(pie_curso("Empezamos con una carga quieta y su ley "
                              "del cuadrado. Nada más."),
                    zona="abajo", run_time=0.45)
        encender(0, 4.6)

        # --- 1.2 y 1.3: el campo --------------------------------------------
        rot.mostrar(pie_curso("Esa carga llenó el espacio de campo; una "
                              "corriente lo llenó de magnetismo."),
                    zona="abajo", run_time=0.45, salida=0.25)
        encender(1, 4.6)

        # --- módulo 2: la onda ----------------------------------------------
        rot.mostrar(pie_curso("Maxwell los casó, y del matrimonio salió "
                              "algo que se marcha solo: la onda."),
                    zona="abajo", run_time=0.45, salida=0.25)
        encender(2, 4.6)

        # --- módulo 3: la línea y la antena ---------------------------------
        rot.mostrar(pie_curso("La línea la guía sin dejarla escapar; la "
                              "antena la suelta al aire."),
                    zona="abajo", run_time=0.45, salida=0.25)
        encender(3, 2.4)
        encender(4, 2.4)

        # --- 4.1 y 4.2: el espacio ------------------------------------------
        rot.mostrar(pie_curso("Cruza la ionosfera y se reparte por una "
                              "esfera de treinta y seis mil kilómetros."),
                    zona="abajo", run_time=0.45, salida=0.25)
        encender(5, 4.6)

        # --- 4.3: el bit ----------------------------------------------------
        rot.mostrar(pie_curso("Y lo que llega, apenas por encima del "
                              "ruido y con su margen, es un bit."),
                    zona="abajo", run_time=0.45, salida=0.25)
        encender(6, 4.6)

        # --- cierre de la familia entera ------------------------------------
        self.play(FadeOut(arco), FadeOut(etiquetas), run_time=0.7)
        rot.limpiar(run_time=0.4)
        linea1 = Text("De una carga quieta", font_size=40, color=C_TITULO)
        linea2 = Text("al bit que baja del cielo.", font_size=40,
                      color=C_CALCULO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.65)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.65)
        self.wait(4.8)
