class Clip4(Scene):
    """4 - El problema del contexto. Un mismo token, 'banco', aparece en dos
    frases con significados distintos: un unico punto en el mapa no alcanza
    para representarlos a ambos; la pista esta en las palabras vecinas."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: titulo y HUD del modulo ------------------------------
        titulo = titulo_curso("El problema del contexto")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.wait(1.6)

        # --- momento: dos frases con la misma palabra 'banco' ----------------
        fila1 = fila_tokens("me siento en el banco", color=C_TOKEN)
        fila1.move_to(np.array([0.0, 1.35, 0.0]))
        fila2 = fila_tokens("el banco cobra comisiones", color=C_TOKEN)
        fila2.move_to(np.array([0.0, -0.15, 0.0]))
        self.play(FadeIn(fila1, shift=0.18 * UP), run_time=0.8)
        self.play(FadeIn(fila2, shift=0.18 * DOWN), run_time=0.8)
        self.wait(1.3)

        # --- momento: 'banco' pulsa en ambas frases ---------------------------
        banco1 = fila1.fichas[4]
        banco2 = fila2.fichas[1]
        self.play(Indicate(banco1, color=C_TOKEN), Indicate(banco2, color=C_TOKEN),
                  run_time=1.0)
        rot.mostrar(pie_curso("La misma palabra... ¿el mismo significado?"),
                   zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- momento: un unico punto entre ambas frases ------------------------
        punto = Dot(np.array([0.0, 0.6, 0.0]), radius=0.07, color=C_VECTOR)
        etiqueta = Text("banco", font_size=18, color=C_VECTOR)
        etiqueta.next_to(punto, RIGHT, buff=0.12)
        signo = Text("?", font_size=22, color=C_ACENTO)
        signo.next_to(punto, UP, buff=0.1)
        self.play(FadeIn(punto, scale=0.5), FadeIn(etiqueta, shift=0.1 * RIGHT),
                  run_time=0.8)
        self.play(FadeIn(signo, shift=0.1 * UP), run_time=0.5)
        self.wait(1.7)

        # --- momento: el punto tiembla y se tiñe de rojo ------------------------
        self.play(Wiggle(punto), run_time=1.1)
        self.play(punto.animate.set_color(C_MAL),
                  etiqueta.animate.set_color(C_MAL), run_time=0.6)
        rot.mostrar(pie_curso("Un solo punto no puede ser dos cosas a la vez."),
                   zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- momento: las palabras vecinas dan la pista, una tras otra -----------
        vecino1 = fila1.fichas[1]  # 'siento'
        vecino2 = fila2.fichas[3]  # 'comisiones'
        self.play(Indicate(vecino1, color=C_PROB), run_time=0.9)
        self.wait(0.4)
        self.play(Indicate(vecino2, color=C_PROB), run_time=0.9)
        rot.mostrar(pie_curso("La pista está en las palabras de alrededor."),
                   zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- momento: cierre / gancho -------------------------------------
        rot.mostrar(pie_curso("Hace falta que cada palabra MIRE a las demás."),
                   zona="abajo", run_time=0.5)
        self.wait(6.0)
