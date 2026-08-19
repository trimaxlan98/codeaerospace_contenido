class Clip3(Scene):
    """3.2.3 - El nucleo: los vectores que la matriz manda al origen. No es
    uno suelto: es una recta entera la que cae a cero. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El núcleo: lo que va a cero")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: vuelve la matriz que aplasta --------------------------
        rot.mostrar(pie_curso("Vuelve la matriz que aplasta el plano sobre "
                              "una recta."), zona="abajo", run_time=0.5)
        pl = plano_leccion()
        v = vector(pl, V_STAR, color=C_VEC, nombre=r"\vec v",
                   etiqueta_dir=RIGHT)
        panel_a = panel_derecha(matriz_columnas(A_PLANA),
                                tag_hud("rango " + fmt(RANGO_PLANA, 0)
                                        + " de " + fmt(N_PLANO, 0)))
        self.play(FadeIn(pl), run_time=0.8)
        self.play(FadeIn(panel_a, shift=0.15 * LEFT), run_time=0.5)
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.7)
        self.wait(3.2)

        # --- momento: tres flechas sobre una misma recta --------------------
        rot.mostrar(pie_curso("Estas tres flechas comparten una misma "
                              "recta."), zona="abajo", run_time=0.5)
        nucs = [vector(pl, k * DIR_NUC, color=C_PROPIO) for k in ESCALAS_NUC]
        self.play(*[GrowArrow(n.flecha) for n in nucs], run_time=0.9)
        # La recta del nucleo: una copia tenue se queda (es el conjunto de
        # ENTRADAS) y otra viva se ira al origen con las flechas.
        linea_nuc = span_recta(pl, DIR_NUC, color=C_PROPIO, grosor=2.2,
                               opacidad=0.4)
        linea_cae = span_recta(pl, DIR_NUC, color=C_PROPIO, grosor=3.0,
                               opacidad=0.9)
        self.play(Create(linea_nuc), Create(linea_cae), run_time=0.8)
        self.wait(2.9)

        # --- momento: la caida ----------------------------------------------
        rot.mostrar(pie_curso("Mira lo que les pasa cuando aplico A."),
                    zona="abajo", run_time=0.5)
        cero = Dot(pl.p(0, 0), radius=0.11, color=C_PROPIO)
        self.play(*pl.anim_matriz(A_PLANA, v, *nucs),
                  Transform(linea_cae, cero), run_time=2.2)
        self.wait(2.6)

        # --- momento: no eran ellas tres, era la recta entera ---------------
        rot.mostrar(pie_curso("Las tres han caído al origen; la recta "
                              "entera, con ellas."), zona="abajo",
                    run_time=0.5)
        fantasmas = VGroup(*[flecha_libre(pl, (0, 0), k * DIR_NUC,
                                          color=C_PROPIO, opacidad=0.45)
                             for k in ESCALAS_NUC])
        et_nuc = tag_hud("nucleo de A", font_size=17, color=C_PROPIO)
        et_nuc.next_to(pl.p(-1.55 * DIR_NUC), LEFT, buff=0.14)
        self.play(FadeIn(fantasmas), FadeIn(et_nuc), run_time=0.7)
        self.wait(3.9)

        # --- momento: la cuenta ---------------------------------------------
        rot.mostrar(pie_curso("Ese es el núcleo de A: lo que la matriz "
                              "manda a cero."), zona="abajo", run_time=0.5)
        panel_b = panel_derecha(matriz_columnas(A_PLANA),
                                vector_columna(DIR_NUC, color=C_PROPIO,
                                               font_size=30),
                                tag_hud("nucleo: dim " + fmt(NUL_PLANA, 0)))
        self.play(FadeOut(panel_a), run_time=0.3)
        self.play(FadeIn(panel_b, shift=0.15 * LEFT), run_time=0.6)
        self.wait(4.4)

        rot.mostrar(pie_curso("Imagen y núcleo: lo que queda y lo que se "
                              "pierde."), zona="abajo", run_time=0.5)
        self.wait(4.2)
