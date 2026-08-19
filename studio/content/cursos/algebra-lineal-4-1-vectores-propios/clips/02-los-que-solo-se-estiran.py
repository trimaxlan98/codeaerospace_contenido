class Clip2(Scene):
    """4.1.2 - Sobre las rectas propias la matriz solo estira: A v = lambda v,
    con lambda = 3 en una y lambda = 1 en la otra. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Los que solo se estiran")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: una flecha sobre cada recta propia --------------------
        pl = plano_leccion()
        rectas = VGroup(span_recta(pl, DIR_ESTIRA, color=C_PROPIO,
                                   opacidad=0.55),
                        span_recta(pl, DIR_QUIETA, color=C_PROPIO,
                                   opacidad=0.55))
        v = vector(pl, V_ESTIRA, color=C_PROPIO, nombre=r"\vec v_1")
        w = vector(pl, V_QUIETA, color=C_PROPIO, nombre=r"\vec v_2")
        self.play(FadeIn(pl), Create(rectas), run_time=1.0)
        rot.mostrar(pie_curso("Volvemos a las dos rectas que no giraron, "
                              "con una flecha sobre cada una."),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(v.flecha), GrowArrow(w.flecha), run_time=0.9)
        self.play(FadeIn(v.etiqueta), FadeIn(w.etiqueta), run_time=0.3)
        self.wait(3.4)

        # --- momento: la misma matriz de antes ------------------------------
        rot.mostrar(pie_curso("La matriz es la misma de antes. Vamos a "
                              "aplicársela solo a ellas dos."),
                    zona="abajo", run_time=0.5)
        mat = matriz_columnas(A_PROPIA, font_size=38)
        panel = panel_derecha(mat)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.0)

        # --- momento: se estiran, no giran ----------------------------------
        rot.mostrar(pie_curso("Ninguna de las dos abandona su recta. Solo "
                              "cambia lo que miden."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(A_PROPIA, v, w), run_time=2.0)
        self.wait(3.2)

        # --- momento: los dos factores --------------------------------------
        rot.mostrar(pie_curso("La primera es " + fmt(LAMBDAS[0], 0)
                              + " veces más larga. La segunda ni se movió."),
                    zona="abajo", run_time=0.5)
        # La ecuacion va en el fucsia de las direcciones propias y la CIFRA
        # en cian (regla de la familia: las cifras calculadas son cianas).
        # Los dos lambda salen de autos(A_PROPIA), nunca escritos a mano; la
        # tercera linea los nombra para que "lambda" deje de ser una letra
        # suelta cuando aparezca la ecuacion general en el pie.
        f1 = MathTex(r"A\vec v_1 =", fmt(LAMBDAS[0], 0), r"\,\vec v_1",
                     font_size=30, color=C_PROPIO)
        f1[1].set_color(C_CALCULO)
        f2 = MathTex(r"A\vec v_2 =", fmt(LAMBDAS[1], 0), r"\,\vec v_2",
                     font_size=30, color=C_PROPIO)
        f2[1].set_color(C_CALCULO)
        f3 = MathTex(r"\lambda_1 = " + fmt(LAMBDAS[0], 0)
                     + r"\qquad \lambda_2 = " + fmt(LAMBDAS[1], 0),
                     font_size=28, color=C_CALCULO)
        # Segunda caja DEBAJO del panel (un Transform del panel a otro con
        # mas piezas deja medio segundo de glifos a medio morphar).
        caja = _con_fondo(VGroup(f1, f2, f3).arrange(DOWN, buff=0.24),
                          buff=0.18, opacidad=0.78)
        caja.next_to(panel, DOWN, buff=0.28).align_to(panel, RIGHT)
        self.play(FadeIn(caja, shift=0.15 * LEFT), run_time=0.8)
        self.play(Indicate(v.flecha, color=C_PROPIO, scale_factor=1.04),
                  run_time=0.8)
        self.play(Indicate(w.flecha, color=C_PROPIO, scale_factor=1.04),
                  run_time=0.8)
        self.wait(2.6)

        # --- momento: la ecuacion -------------------------------------------
        rot.mostrar(pie_curso("La dirección se llama vector propio; el "
                              "factor que la estira, valor propio."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(formula_pie(r"A\,\vec v = \lambda\,\vec v"),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
