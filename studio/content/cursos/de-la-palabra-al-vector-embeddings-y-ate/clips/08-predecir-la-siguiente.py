class Clip8(Scene):
    """8 - Predecir la siguiente palabra. Un LLM no sabe la respuesta:
    calcula una distribucion de probabilidad y elige, una palabra a la
    vez. Cierra el curso con la tarjeta de marca. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ---------------------------------------------------
        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Predecir la siguiente palabra")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(1.0)

        # --- momento: la frase con un hueco al final --------------------------
        fila = fila_tokens("el gato se subió al")
        fila.move_to(1.6 * LEFT + 0.9 * UP)
        self.play(FadeIn(fila, lag_ratio=0.06), run_time=1.0)

        signo = Text("?", font_size=34, color=C_ACENTO)
        signo.next_to(fila, RIGHT, buff=0.35)
        self.play(FadeIn(signo, scale=0.6), run_time=0.5)
        self.wait(1.4)

        # --- momento: el modelo no sabe, calcula probabilidades ---------------
        opciones = ["tejado", "árbol", "sofá", "coche"]
        probs = [0.46, 0.31, 0.18, 0.05]
        dist = distribucion_siguiente(opciones, probs, resaltar="tejado")
        dist.move_to(1.2 * DOWN)
        self.play(FadeIn(dist, lag_ratio=0.08), run_time=1.0)
        rot.mostrar(pie_curso("El modelo no sabe: calcula probabilidades."),
                    zona="abajo", run_time=0.5)
        self.wait(2.7)

        # --- momento: la opcion ganadora se funde en el hueco ------------------
        # next_to de la fila, no move_to del signo: el "?" es angosto y
        # centrar ahi una ficha ancha la encimaba con la ficha "al".
        ficha_ganadora = ficha_token("tejado", color=C_PROB)
        ficha_ganadora.next_to(fila, RIGHT, buff=0.18)
        fila_ganadora = dist.filas["tejado"]
        resto = VGroup(*[dist.filas[o] for o in dist.orden if o != "tejado"])
        self.play(ReplacementTransform(fila_ganadora, ficha_ganadora),
                  FadeOut(signo), FadeOut(resto), run_time=1.1)
        rot.mostrar(pie_curso("Elige, añade... y vuelve a empezar."),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- momento: segunda vuelta, breve, solo dos opciones ------------------
        frase_larga = VGroup(fila, ficha_ganadora)
        self.play(frase_larga.animate.shift(1.6 * LEFT), run_time=0.7)

        signo_2 = Text("?", font_size=34, color=C_ACENTO)
        signo_2.next_to(frase_larga, RIGHT, buff=0.35)
        self.play(FadeIn(signo_2, scale=0.6), run_time=0.5)

        dist_2 = distribucion_siguiente(["y", "con"], [0.61, 0.39],
                                        resaltar="y")
        dist_2.move_to(1.2 * DOWN)
        self.play(FadeIn(dist_2, lag_ratio=0.1), run_time=0.7)
        self.wait(1.5)

        ficha_ganadora_2 = ficha_token("y", color=C_PROB)
        ficha_ganadora_2.next_to(frase_larga, RIGHT, buff=0.18)
        fila_ganadora_2 = dist_2.filas["y"]
        resto_2 = VGroup(*[dist_2.filas[o] for o in dist_2.orden if o != "y"])
        self.play(ReplacementTransform(fila_ganadora_2, ficha_ganadora_2),
                  FadeOut(signo_2), FadeOut(resto_2), run_time=1.0)
        rot.mostrar(pie_curso("Así, palabra a palabra, escribe un LLM."),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- momento: pantalla limpia para la tarjeta de cierre -----------------
        rot.limpiar(run_time=0.5)
        frase_final = VGroup(frase_larga, ficha_ganadora_2)
        self.play(FadeOut(VGroup(frase_final, modulo)), run_time=1.1)

        # --- momento: tarjeta final, patron exacto del curso hermano ------------
        titulo_final = titulo_marca("De la palabra al vector", font_size=46)
        subtitulo = Text("embeddings y atención", font_size=25,
                         color=C_ACENTO)
        cuerpo = VGroup(titulo_final, subtitulo).arrange(DOWN, buff=0.26)

        subrayado = Line(LEFT, RIGHT, color=C_ACENTO)
        subrayado.set_width(subtitulo.width * 1.1)
        subrayado.next_to(subtitulo, DOWN, buff=0.16)
        brillo_subrayado = con_brillo(subrayado, color=C_ACENTO)

        tarjeta = VGroup(cuerpo, brillo_subrayado)
        tarjeta.move_to(ORIGIN)

        self.play(Write(titulo_final), run_time=1.7)
        self.play(FadeIn(subtitulo, shift=0.15 * UP), run_time=0.9)
        self.wait(0.9)
        self.play(Create(brillo_subrayado), run_time=1.3)
        self.wait(2.3)
