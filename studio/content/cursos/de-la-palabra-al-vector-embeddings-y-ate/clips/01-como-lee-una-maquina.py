class Clip1(Scene):
    """1 - Como lee una maquina. Portada del curso, una frase que se parte
    en tokens y el numero arbitrario que esconde cada uno: 'gato' y
    'felino' no se parecen en nada para la maquina. El gancho para todo
    el curso."""

    def construct(self):
        rot = Rotulos(self)

        # --- Portada del curso -----------------------------------------
        portada = VGroup(
            titulo_marca("De la palabra al vector", font_size=46),
            Text("embeddings y atención", font_size=25, color=C_ACENTO),
        ).arrange(DOWN, buff=0.26)
        portada.move_to(ORIGIN)

        self.play(Write(portada[0]), run_time=1.3)
        self.play(FadeIn(portada[1], shift=0.18 * UP), run_time=0.7)
        self.wait(1.6)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.play(FadeOut(portada, shift=0.5 * UP), run_time=0.7)

        # --- Titulo del clip ---------------------------------------------
        titulo = titulo_curso("¿Cómo lee una máquina?")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        # --- La frase, palabra por palabra --------------------------------
        frase_txt = Text("el gato duerme en el parque", font_size=30,
                         color=C_TOKEN)
        frase_txt.move_to(ORIGIN)
        self.play(Write(frase_txt), run_time=1.4)
        self.wait(1.2)

        fila = fila_tokens("el gato duerme en el parque")
        fila.move_to(ORIGIN)
        self.play(ReplacementTransform(frase_txt, fila), run_time=1.2)
        rot.mostrar(pie_curso("Primero, partir el texto en piezas: tokens."),
                   zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- Cada token es solo un numero -----------------------------------
        codigos = ["4821", "93", "2005", "61", "4821", "7340"]
        numeros = VGroup(*[Text(codigo, font_size=17, color=C_TENUE)
                           for codigo in codigos])
        for numero, ficha in zip(numeros, fila.fichas):
            numero.next_to(ficha, DOWN, buff=0.14)
        self.play(FadeIn(numeros, lag_ratio=0.15), run_time=1.0)
        rot.mostrar(pie_curso("Para la máquina, cada token es solo un "
                              "número."), zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- Entra 'felino': mismo significado, otro numero -----------------
        felino = ficha_token("felino", color=C_TOKEN)
        felino.next_to(fila.fichas[-1], RIGHT, buff=0.18)
        self.play(FadeIn(felino, shift=0.3 * LEFT), run_time=0.6)

        numero_felino = Text("1177", font_size=17, color=C_TENUE)
        numero_felino.next_to(felino, DOWN, buff=0.14)
        self.play(FadeIn(numero_felino), run_time=0.4)

        elementos = VGroup(fila, numeros, felino, numero_felino)
        self.play(elementos.animate.move_to(ORIGIN), run_time=0.6)
        self.wait(1.0)

        # --- El problema: numeros totalmente distintos -----------------------
        numero_gato = numeros[1]
        self.play(Indicate(numero_gato, color=C_MAL),
                  Indicate(numero_felino, color=C_MAL), run_time=1.1)
        rot.mostrar(pie_curso("El problema: 'gato' y 'felino' no se "
                              "parecen en nada."), zona="abajo",
                   run_time=0.5)
        self.wait(2.8)

        # --- Cierre / gancho -------------------------------------------------
        self.play(FadeOut(numeros), FadeOut(numero_felino), run_time=0.6)
        rot.mostrar(pie_curso("Necesitamos que el significado viva en los "
                              "números."), zona="abajo", run_time=0.5)
        self.wait(4.0)
