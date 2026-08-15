class Clip1(Scene):
    """1.3.1 - La rendija que ensancha. La luz que pasa por una rendija no
    sigue recta: se abre, y cuanto mas angosta es la rendija mas ancho es el
    patron (el patron de a/3 es tres veces mas ancho que el de a). El primer
    cero cae en sin(theta) = lambda/a: encerrar la luz la abre. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("La rendija que ensancha"), zona="arriba",
                    run_time=0.6)

        # La pieza: rendija a la izquierda, patron sinc^2 a la derecha. El
        # ancho A_ANCHA = 9 lambda se divide EXACTO entre 3, asi que el
        # rotulo de la libreria ("a = 3 lambda") no miente al redondear.
        A_ANCHA, A_ANGOSTA = 9.0, 3.0
        rp = rendija_patron(A_ANCHA, lam=LAMBDA_HENE, ancho=7.0, alto=2.8)
        rp.move_to(DOWN * 0.25)
        # El rotulo ASCII "sin theta = lambda / a" de la libreria se retira:
        # esa frase la dice el MathTex del tercer momento, en grande.
        rp.rotulos.remove(rp.rotulos[1])

        # --- momento: la luz que pasa se abre --------------------------------
        rot.mostrar(pie_curso("La luz que pasa por una rendija no sigue "
                              "recta: se abre."), zona="abajo", run_time=0.5)
        self.play(FadeIn(rp.entrada, shift=0.18 * RIGHT),
                  FadeIn(rp.rendija), run_time=0.8)
        self.play(FadeIn(rp.ejes), FadeIn(rp.rotulos), run_time=0.5)
        self.play(Create(rp.curva), run_time=1.3)
        self.play(FadeIn(rp.ceros), run_time=0.5)
        t_ancho = tag_hud("a", font_size=20, color=C_TENUE)
        t_ancho.next_to(rp.rendija, UP, buff=0.24)
        self.play(FadeIn(t_ancho), run_time=0.4)
        self.wait(4.4)

        # --- momento: mas angosta, mas ancho ---------------------------------
        rot.mostrar(pie_curso("Cuanto más angosta la rendija, más ancho el "
                              "patrón."), zona="abajo", run_time=0.5)
        # El patron viejo se queda como fantasma: los DOS anchos conviven.
        fantasma = rp.curva.copy().set_stroke(color=C_FRANJA, opacity=0.30,
                                              width=2.2)
        self.add(fantasma)
        p_f = rp.primer_cero(1)          # el cero del patron ancho (a = 9 lam)
        t_fantasma = tag_hud("patron con a", font_size=14, color=C_TENUE)
        t_fantasma.move_to(np.array([p_f[0], p_f[1] - 0.34, 0.0]))

        gemela = rp.con_ancho(A_ANGOSTA)
        gemela.rotulos.remove(gemela.rotulos[1])
        t_angosto = tag_hud("a/3", font_size=20, color=C_FRANJA)
        t_angosto.next_to(gemela.rendija, UP, buff=0.24)
        self.play(ReplacementTransform(rp, gemela),
                  ReplacementTransform(t_ancho, t_angosto), run_time=1.5)
        rp = gemela
        self.play(FadeIn(t_fantasma), run_time=0.4)
        self.wait(4.2)

        # --- momento: donde cae el primer cero -------------------------------
        rot.mostrar(pie_curso("El primer cero cae en seno de theta igual a "
                              "lambda sobre a."), zona="abajo", run_time=0.5)
        ley = MathTex(r"\sin\theta = \lambda / a", font_size=40,
                      color=C_ACENTO)
        ley.move_to(np.array([0.95, 2.15, 0.0]))
        self.play(Write(ley), run_time=1.1)
        cero = Dot(rp.primer_cero(1), radius=0.075, color=C_MEDIDA)
        t_cero = tag_hud("primer cero", font_size=14, color=C_MEDIDA)
        t_cero.next_to(rp.ceros[1], UP, buff=0.16)
        self.play(FadeIn(cero, scale=1.6), FadeIn(t_cero), run_time=0.6)
        self.wait(4.4)

        # --- cierre -----------------------------------------------------------
        rot.mostrar(pie_curso("Encerrar la luz la abre. Ésa es la "
                              "difracción."), zona="abajo", run_time=0.5)
        self.wait(5.0)
