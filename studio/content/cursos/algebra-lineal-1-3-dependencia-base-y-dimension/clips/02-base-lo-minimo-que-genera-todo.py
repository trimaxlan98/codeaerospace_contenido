class Clip2(Scene):
    """1.3.2 - Una base es lo minimo que alcanza cualquier punto: el mismo
    punto se lee con dos parejas de coeficientes distintas, segun la base.
    (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Base: lo mínimo que lo genera todo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el punto a alcanzar ------------------------------------
        pl = plano_leccion(vivo=False)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Un punto cualquiera del plano. Dos "
                              "vectores no alineados bastan para "
                              "alcanzarlo."), zona="abajo", run_time=0.5)
        p = vector(pl, P2, color=C_VEC, nombre=r"\vec P")
        self.play(GrowArrow(p.flecha), FadeIn(p.etiqueta), run_time=0.9)
        self.wait(3.2)

        # --- momento: con la base canonica ------------------------------------
        rot.mostrar(pie_curso("Con la base canónica: tres veces î, dos "
                              "veces ĵ."), zona="abajo", run_time=0.5)
        comb1 = combinacion(pl, COEF_CANONICA[0], (1, 0), COEF_CANONICA[1],
                            (0, 1), color_u=C_I, color_v=C_J,
                            mostrar_res=False)
        et_a1 = MathTex(fmt(COEF_CANONICA[0], 0) + r"\hat{\imath}",
                        font_size=28, color=C_I)
        et_a1.move_to(pl.p(COEF_CANONICA[0] * 0.5, 0) + 0.4 * DOWN)
        et_b1 = MathTex(fmt(COEF_CANONICA[1], 0) + r"\hat{\jmath}",
                        font_size=28, color=C_J)
        et_b1.move_to(pl.p(COEF_CANONICA[0], COEF_CANONICA[1] * 0.5)
                      + 0.4 * RIGHT)
        self.play(GrowArrow(comb1.au), FadeIn(et_a1), run_time=0.8)
        self.play(GrowArrow(comb1.bv), FadeIn(et_b1), run_time=0.8)
        self.wait(2.6)

        columna1 = vector_columna(np.array(COEF_CANONICA), color=C_VEC,
                                  dec=0, font_size=32)
        cap1 = Text("Canónica", font_size=18, color=C_TENUE)
        grupo1 = VGroup(cap1, columna1).arrange(DOWN, buff=0.12)
        panel = panel_derecha(grupo1)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.0)

        # --- momento: con la otra base ------------------------------------
        rot.mostrar(pie_curso("Quitamos esa lectura y probamos con otra "
                              "base: B = { b1, b2 }."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(comb1.au), FadeOut(comb1.bv), FadeOut(et_a1),
                  FadeOut(et_b1), run_time=0.6)
        self.wait(0.4)

        coef_b = resolver(MATRIZ_B, P2)
        rot.mostrar(pie_curso("Se resuelve b1·x + b2·y = P: salen otros "
                              "coeficientes."), zona="abajo", run_time=0.5)
        comb2 = combinacion(pl, coef_b[0], B1, coef_b[1], B2, color_u=C_I,
                            color_v=C_J, mostrar_res=False)
        et_a2 = MathTex(fmt(coef_b[0], 2) + r"\,\vec b_1", font_size=28,
                        color=C_I)
        et_a2.move_to(pl.p(coef_b[0] * B1 * 0.5) + 0.4 * DOWN)
        et_b2 = MathTex(fmt(coef_b[1], 2) + r"\,\vec b_2", font_size=28,
                        color=C_J)
        # bv es un tramo corto (coeficiente pequeño) que aterriza justo en
        # la punta de P: un offset fijo lo dejaba pegado a la etiqueta de
        # P (que sale arriba-izquierda de su punta). A la derecha del
        # propio segmento hay hueco de sobra.
        et_b2.next_to(comb2.bv, RIGHT, buff=0.18)
        self.play(GrowArrow(comb2.au), FadeIn(et_a2), run_time=0.8)
        self.play(GrowArrow(comb2.bv), FadeIn(et_b2), run_time=0.8)
        self.wait(2.8)

        rot.mostrar(pie_curso("Distinto número, el mismo punto: aterriza "
                              "otra vez en la punta de P."), zona="abajo",
                    run_time=0.5)
        columna2 = vector_columna(coef_b, color=C_VEC, dec=2, font_size=32)
        cap2 = Text("Base B", font_size=18, color=C_TENUE)
        grupo2 = VGroup(cap2, columna2).arrange(DOWN, buff=0.12)
        panel2 = panel_derecha(grupo1, grupo2)
        # Transform(panel, panel2) morfaba glifos entre estructuras muy
        # distintas (una columna -> dos columnas) y se veian caracteres
        # rotos a medio camino; un cruce de opacidad es limpio.
        self.play(FadeOut(panel, run_time=0.3))
        self.play(FadeIn(panel2, shift=0.15 * LEFT), run_time=0.6)
        self.play(Indicate(p.flecha, color=C_VEC, scale_factor=1.05),
                  run_time=0.8)
        self.wait(4.0)

        rot.mostrar(pie_curso("Una base es lo mínimo que lo genera todo: "
                              "ni un vector de más, ni de menos."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)
