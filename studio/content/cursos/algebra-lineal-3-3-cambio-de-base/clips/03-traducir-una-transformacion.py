class Clip3(Scene):
    """3.3.3 - La misma transformacion contada en otra base: P^-1 A P. En el
    idioma de b1 y b2, la A enrevesada resulta ser dos estirones. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Traducir una transformación")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: A en el idioma de siempre ----------------------------
        pl = plano_leccion(unidad=UNIDAD_3, centro=LEFT * 0.6 + DOWN * 0.15)
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Una transformación A. Sus columnas dicen "
                              "dónde acaban î y ĵ."), zona="abajo",
                    run_time=0.5)
        self.play(GrowArrow(i_hat.flecha), FadeIn(i_hat.etiqueta),
                  GrowArrow(j_hat.flecha), FadeIn(j_hat.etiqueta),
                  run_time=0.7)
        bloque_a = VGroup(MathTex("A", font_size=28, color=C_TENUE),
                          matriz_columnas(A_MOV, font_size=26))
        bloque_a.arrange(DOWN, buff=0.14)
        panel = panel_derecha(bloque_a)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.0)

        rot.mostrar(pie_curso("Aplicada, tuerce la rejilla. Así, de frente, "
                              "no se le ve la lógica."), zona="abajo",
                    run_time=0.5)
        self.play(*pl.anim_matriz(A_MOV, i_hat, j_hat), run_time=2.0)
        self.wait(3.2)

        # --- momento: volver y cambiar de idioma ---------------------------
        rot.mostrar(pie_curso("Rebobinamos, y contamos el mismo movimiento "
                              "en el idioma de b1 y b2."), zona="abajo",
                    run_time=0.5)
        self.play(*pl.anim_matriz(np.eye(2), i_hat, j_hat), run_time=1.4)
        self.wait(2.6)

        rot.mostrar(pie_curso("Esta es su rejilla oblicua: b1 y b2 marcan "
                              "las casillas."), zona="abajo", run_time=0.5)
        b1 = vector(pl, B1, color=C_I, nombre=r"\vec b_1", etiqueta_dir=DOWN)
        b2 = vector(pl, B2, color=C_J, nombre=r"\vec b_2", etiqueta_dir=LEFT)
        self.play(Transform(i_hat, b1), Transform(j_hat, b2),
                  *pl.anim_matriz(P_BASE), run_time=1.8)
        self.wait(3.0)

        # --- momento: A sobre la rejilla oblicua ---------------------------
        rot.mostrar(pie_curso("Ahora A otra vez. Mira: b1 y b2 no se salen "
                              "de su recta. Solo estiran."), zona="abajo",
                    run_time=0.5)
        b1_img = vector(pl, A_MOV @ B1, color=C_I,
                        nombre=fmt(D_B[0, 0], 0) + r"\,\vec b_1",
                        etiqueta_dir=DOWN)
        b2_img = vector(pl, A_MOV @ B2, color=C_J,
                        nombre=fmt(D_B[1, 1], 1) + r"\,\vec b_2",
                        etiqueta_dir=LEFT)
        self.play(Transform(i_hat, b1_img), Transform(j_hat, b2_img),
                  *pl.anim_matriz(A_MOV @ P_BASE), run_time=2.2)
        self.wait(3.4)

        # --- momento: la matriz traducida ----------------------------------
        rot.mostrar(pie_curso("En ese idioma, A es solo esto: estirar por 2 "
                              "y encoger a la mitad."), zona="abajo",
                    run_time=0.5)
        a_traducida = P_INV @ A_MOV @ P_BASE
        bloque_a2 = VGroup(MathTex("A", font_size=28, color=C_TENUE),
                           matriz_columnas(A_MOV, font_size=26))
        bloque_a2.arrange(DOWN, buff=0.14)
        bloque_ab = VGroup(MathTex("P^{-1}AP", font_size=28, color=C_TENUE),
                           matriz_columnas(a_traducida, font_size=26))
        bloque_ab.arrange(DOWN, buff=0.14)
        panel2 = panel_derecha(bloque_a2, bloque_ab, buff=0.3)
        self.play(FadeOut(panel), FadeIn(panel2), run_time=0.6)
        self.wait(4.0)

        rot.mostrar(pie_curso("Mismo movimiento, dos matrices. La base "
                              "buena lo deja en la diagonal."), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)
