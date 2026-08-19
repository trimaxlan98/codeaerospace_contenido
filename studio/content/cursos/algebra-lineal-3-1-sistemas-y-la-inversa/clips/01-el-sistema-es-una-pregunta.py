class Clip1(Scene):
    """3.1.1 - El sistema Ax = b como pregunta geometrica: la rejilla se
    deforma con A y buscamos que x, en la rejilla original, aterriza justo
    sobre b. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El sistema es una pregunta geométrica")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el sistema, como ecuaciones --------------------------
        def termino(c, var):
            return var if abs(float(c) - 1.0) < 1e-9 else fmt(c, 0) + var

        sistema = (r"\begin{cases}"
                   + termino(A[0, 0], "x") + " + " + termino(A[0, 1], "y")
                   + " = " + fmt(B_VEC[0], 0) + r" \\ "
                   + termino(A[1, 0], "x") + " + " + termino(A[1, 1], "y")
                   + " = " + fmt(B_VEC[1], 0) + r"\end{cases}")
        rot.mostrar(formula_pie(sistema), zona="abajo", run_time=0.6)
        self.wait(3.6)

        # --- momento: el mismo sistema, en la rejilla -----------------------
        pl = plano_leccion(vivo=True)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("En el idioma de la rejilla, A mueve el "
                              "plano entero de una sola vez."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(A), run_time=2.0)
        self.wait(2.0)

        # --- momento: b es fijo ---------------------------------------------
        b = vector(pl, B_VEC, color=C_IMG, nombre=r"\vec b")
        rot.mostrar(pie_curso("Ahí está b: fijo, quieto. La pregunta es "
                              "qué x aterriza en él."), zona="abajo",
                    run_time=0.5)
        self.play(GrowArrow(b.flecha), FadeIn(b.etiqueta), run_time=0.9)
        self.wait(3.2)

        # --- momento: volver a la rejilla original y soltar x ---------------
        rot.mostrar(pie_curso("Volvamos a la rejilla original para verlo "
                              "entrar."), zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(np.eye(2)), run_time=1.6)
        # etiqueta_dir fijo (no perpendicular recalculado): x aterriza sobre
        # b al final del clip y, sin esto, las dos etiquetas coincidirian.
        x = vector(pl, X_SOL, color=C_VEC, nombre=r"\vec x",
                  etiqueta_dir=DOWN)
        self.play(GrowArrow(x.flecha), FadeIn(x.etiqueta), run_time=0.9)
        self.wait(2.4)

        # --- momento: aplicar A y verlo aterrizar ----------------------------
        rot.mostrar(pie_curso("Al aplicar A, x cae exactamente sobre b."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(A, x), run_time=2.2)
        # No reasignar x = x.con_matriz(A): el Transform de arriba ya mutó
        # el objeto EN SITIO; un gemelo nuevo aqui nunca se anadiria a la
        # escena hasta que el Indicate de abajo lo cuela por su cuenta (un
        # segundo par de flechas fantasma). No volvemos a leer x.coords.
        self.wait(0.8)
        self.play(Indicate(x.flecha, color=C_VEC, scale_factor=1.05),
                  Indicate(b.flecha, color=C_IMG, scale_factor=1.05),
                  run_time=0.9)
        self.wait(3.0)

        rot.mostrar(formula_pie(r"\text{Aterrizar en } \vec b: \quad "
                                r"\vec x = A^{-1}\vec b"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
