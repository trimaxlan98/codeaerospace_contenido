class Clip1(Scene):
    """5.2.1 - El circulo unidad bajo CUALQUIER matriz sale siempre elipse.
    Sus semiejes son sigma1 u1 y sigma2 u2: los valores singulares dicen
    cuanto estira la matriz y en que direcciones. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El círculo se vuelve elipse")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: todas las direcciones a la vez ------------------------
        pl = plano_leccion()
        c = circulo_unidad(pl, color=C_VEC)
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("El círculo unidad: todas las direcciones a la "
                              "vez, todas de largo uno."),
                    zona="abajo", run_time=0.5)
        self.play(Create(c), run_time=1.0)
        self.play(GrowArrow(i_hat.flecha), GrowArrow(j_hat.flecha),
                  FadeIn(i_hat.etiqueta), FadeIn(j_hat.etiqueta),
                  run_time=0.8)
        self.wait(3.4)

        # --- momento: la matriz de la leccion -------------------------------
        rot.mostrar(pie_curso("Y una matriz cualquiera: ni giro, ni escala, "
                              "ni nada con nombre."), zona="abajo",
                    run_time=0.5)
        panel = panel_derecha(matriz_columnas(M_LECCION, font_size=34))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.2)

        # --- momento: el movimiento -----------------------------------------
        rot.mostrar(pie_curso("Se mueve el plano entero, y el círculo se "
                              "convierte en una elipse."), zona="abajo",
                    run_time=0.5)
        self.wait(1.0)
        self.play(*pl.anim_matriz(M_LECCION, i_hat, j_hat),
                  Transform(c, c.con_matriz(M_LECCION)), run_time=2.2)
        self.wait(3.2)

        # --- momento: los semiejes ------------------------------------------
        # Las columnas se retiran: la imagen de i cae a 13 grados del semieje
        # mayor y las etiquetas se enciman. La matriz sigue en el panel.
        rot.mostrar(pie_curso("Y esa elipse tiene dos ejes. Ahí está todo lo "
                              "que la matriz hace."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(i_hat), FadeOut(j_hat), run_time=0.5)
        e1 = vector(pl, SEMIEJE_1, color=C_PROPIO, grosor=5.5)
        e2 = vector(pl, SEMIEJE_2, color=C_PROPIO, grosor=5.5)
        cifra_1 = self._cifra(r"\sigma_1 = " + fmt(S_M[0], 2),
                              pl.p(SEMIEJE_1), np.array([0.70, -0.62, 0.0]))
        cifra_2 = self._cifra(r"\sigma_2 = " + fmt(S_M[1], 2),
                              pl.p(SEMIEJE_2), np.array([1.05, 0.62, 0.0]))
        self.play(GrowArrow(e1.flecha), GrowArrow(e2.flecha), run_time=0.9)
        self.play(FadeIn(cifra_1), FadeIn(cifra_2), run_time=0.6)
        self.wait(3.2)

        # --- momento: como se llaman ----------------------------------------
        rot.mostrar(pie_curso("Esos dos números son los valores singulares: "
                              "lo que más estira y lo que menos."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(e1.flecha, color=C_PROPIO, scale_factor=1.06),
                  Indicate(cifra_1, color=C_PROPIO, scale_factor=1.08),
                  run_time=0.9)
        self.wait(4.0)

        rot.mostrar(pie_curso("Círculo dentro, elipse fuera. Siempre. "
                              "¿Y cómo lo consigue?"), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

    # -- la cifra de un semieje, con fondo, colocada fuera de la elipse -----
    def _cifra(self, tex, punta, corrimiento):
        m = MathTex(tex, font_size=30, color=C_PROPIO)
        m.move_to(punta + corrimiento)
        return _con_fondo(m, buff=0.11, opacidad=0.78)
