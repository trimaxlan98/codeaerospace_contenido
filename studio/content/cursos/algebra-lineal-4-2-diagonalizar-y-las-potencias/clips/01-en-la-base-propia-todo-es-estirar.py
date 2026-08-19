class Clip1(Scene):
    """4.2.1 - Bajo A, un vector cualquiera cambia de dirección. Pero dos
    direcciones no giran: son los vectores propios. En esa base, A ya no
    gira ni cizalla: solo estira cada eje por su cuenta (D). (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("En la base propia todo es estirar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.9)
        rot.mostrar(pie_curso("Bajo A, un vector cualquiera cambia de "
                              "dirección: gira."), zona="abajo",
                    run_time=0.5)
        w = vector(pl, V_GEN, color=C_VEC, nombre=r"\vec w")
        self.play(GrowArrow(w.flecha), FadeIn(w.etiqueta), run_time=0.9)
        self.wait(1.2)
        self.play(*pl.anim_matriz(A, w), run_time=2.0)
        self.wait(3.0)

        rot.mostrar(pie_curso("Pero dos direcciones no giran. Volvamos y "
                              "busquémoslas."), zona="abajo", run_time=0.5)
        self.play(FadeOut(w), *pl.anim_matriz(np.eye(2)), run_time=1.6)
        self.wait(0.6)

        rot.mostrar(pie_curso("Esa es la rejilla propia de A: inclinada, "
                              "pero fija bajo A."), zona="abajo",
                    run_time=0.5)
        u1 = vector(pl, U1, color=C_PROPIO, nombre=r"\vec u_1",
                   etiqueta_dir=UP)
        u2 = vector(pl, U2, color=C_PROPIO, nombre=r"\vec u_2",
                   etiqueta_dir=DOWN)
        self.play(*pl.anim_matriz(P_MAT), GrowArrow(u1.flecha),
                  GrowArrow(u2.flecha), run_time=1.8)
        self.play(FadeIn(u1.etiqueta), FadeIn(u2.etiqueta), run_time=0.3)
        self.wait(3.0)

        rot.mostrar(pie_curso("Ahí A no gira ni cizalla: solo estira cada "
                              "eje por su cuenta."), zona="abajo",
                    run_time=0.5)
        self.play(*pl.anim_matriz(A @ P_MAT),
                  Transform(u1, u1.con_matriz(A)),
                  Transform(u2, u2.con_matriz(A)), run_time=2.2)
        u1 = u1.con_matriz(A)
        u2 = u2.con_matriz(A)
        self.wait(3.6)

        rot.mostrar(pie_curso("Uno se triplica, el otro se queda clavado: "
                              "esa es la matriz diagonal D."),
                    zona="abajo", run_time=0.5)
        l1 = MathTex(r"\lambda_1 = " + fmt(VAL_A[0], 0), font_size=28,
                    color=C_CALCULO)
        l2 = MathTex(r"\lambda_2 = " + fmt(VAL_A[1], 0), font_size=28,
                    color=C_CALCULO)
        etiquetas = VGroup(l1, l2).arrange(RIGHT, buff=0.5)
        mat_d = matriz_columnas(D_MAT, dec=0)
        panel = panel_derecha(etiquetas, mat_d)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.2)

        rot.mostrar(pie_curso("Encontrar esa base es diagonalizar. Es el "
                              "atajo de todo lo que sigue."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)
