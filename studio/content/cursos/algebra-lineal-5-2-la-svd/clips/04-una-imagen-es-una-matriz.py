class Clip4(Scene):
    """5.2.4 - Quedarse con los primeros valores singulares es quedarse con
    lo que mas estira: en el plano aplasta la elipse contra su eje mayor; en
    una imagen de 12x12 la reconstruye con cada vez menos error. Cierra la
    leccion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Una imagen es una matriz")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: recordar la elipse -------------------------------------
        pl = plano_leccion()
        c = circulo_unidad(pl, color=C_VEC)
        panel_m = panel_derecha(matriz_columnas(M_LECCION, font_size=30))
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Nuestra matriz estiraba mucho por un lado y "
                              "poco por el otro."), zona="abajo",
                    run_time=0.5)
        self.play(Create(c), FadeIn(panel_m, shift=0.15 * LEFT),
                  run_time=0.8)
        self.wait(0.4)
        self.play(*pl.anim_matriz(M_LECCION),
                  Transform(c, c.con_matriz(M_LECCION)), run_time=1.8)
        self.wait(2.0)

        # --- momento: tirar el valor singular pequeño -------------------------
        rot.mostrar(pie_curso("¿Y si tiramos el pequeño? Queda otra matriz: "
                              "la elipse se aplasta contra su eje mayor."),
                    zona="abajo", run_time=0.5)
        panel_1 = panel_derecha(matriz_columnas(RANGO1_M, font_size=30),
                                MathTex(r"\text{error} = "
                                        + fmt(ERR_RANGO1_M, 2), font_size=28,
                                        color=C_PROPIO), buff=0.28)
        self.play(FadeOut(panel_m), FadeIn(panel_1), run_time=0.5)
        self.play(*pl.anim_matriz(RANGO1_M),
                  Transform(c, c.con_matriz(RANGO1_M)), run_time=1.8)
        self.wait(3.0)

        # --- momento: una imagen tambien es una matriz ------------------------
        rot.mostrar(pie_curso("Una imagen en grises también es una matriz: "
                              "doce por doce números entre 0 y 1."),
                    zona="abajo", run_time=0.5)
        original = pixeles(IMG, lado=0.24)
        original.move_to(LEFT * 3.3 + UP * 0.35)
        tag_original = tag_hud("original 12 x 12", font_size=19,
                               color=C_TENUE)
        tag_original.next_to(original, DOWN, buff=0.24)
        self.play(FadeOut(pl), FadeOut(c), FadeOut(panel_1), run_time=0.7)
        self.play(FadeIn(original), FadeIn(tag_original), run_time=0.9)
        self.wait(3.4)

        # --- momento: la aproximacion de rango 1 ------------------------------
        rot.mostrar(pie_curso("Con un solo valor singular ya se adivina: es "
                              "la parte que más pesa."), zona="abajo",
                    run_time=0.5)
        aprox_m, aprox_err = APROX[0]
        aprox = pixeles(aprox_m, lado=0.24)
        aprox.move_to(RIGHT * 3.3 + UP * 0.35)
        casi = MathTex(r"\approx", font_size=54, color=C_TENUE)
        casi.move_to(UP * 0.35)
        tag_rango = tag_hud("rango k = " + str(RANGOS[0]), font_size=21)
        tag_rango.next_to(aprox, DOWN, buff=0.24)
        tag_error = tag_hud("error = " + fmt(aprox_err, 2), font_size=21,
                            color=C_PROPIO)
        tag_error.next_to(tag_rango, DOWN, buff=0.16)
        self.play(FadeIn(casi), FadeIn(aprox), FadeIn(tag_rango),
                  FadeIn(tag_error), run_time=0.8)
        self.wait(4.0)

        # --- momento: 2, 3 y 5 ------------------------------------------------
        rot.mostrar(pie_curso("Cada valor singular que añadimos afina el "
                              "dibujo y baja el error."), zona="abajo",
                    run_time=0.5)
        for k, (m_k, err_k) in zip(RANGOS[1:], APROX[1:]):
            nuevo_rango = tag_hud("rango k = " + str(k), font_size=21)
            nuevo_rango.move_to(tag_rango)
            nuevo_error = tag_hud("error = " + fmt(err_k, 2), font_size=21,
                                  color=C_PROPIO)
            nuevo_error.move_to(tag_error)
            self.play(Transform(aprox, aprox.con_valores(m_k)),
                      Transform(tag_rango, nuevo_rango),
                      Transform(tag_error, nuevo_error), run_time=1.1)
            self.wait(1.5)

        # --- cierre de la leccion ---------------------------------------------
        cierre_leccion(self, rot, "Toda matriz es girar, estirar, girar.",
                       "Quédate con lo que más estira.",
                       "Y si esa matriz se aplica una y otra vez, ¿a dónde "
                       "acaba llevando? Siguiente lección.",
                       original, aprox, casi, tag_original, tag_rango,
                       tag_error, espera=4.2)
