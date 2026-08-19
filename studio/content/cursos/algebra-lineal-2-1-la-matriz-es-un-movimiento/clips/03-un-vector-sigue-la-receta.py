class Clip3(Scene):
    """2.1.3 - Un vector cualquiera es una receta: 3 de i-sombrero y 2 de
    j-sombrero. Su imagen es la MISMA receta con los destinos nuevos, y esa
    cuenta es exactamente el producto matriz por vector. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Un vector cualquiera sigue la receta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # El plano de este clip va un pelo mas pequeño y mas bajo que el de
        # la familia: la imagen M v es alta (su segunda componente sale de
        # MV_DEMO) y con UNIDAD normal la punta se metia bajo el titulo.
        pl = plano_leccion(unidad=0.75, centro=DOWN * 0.5)
        a, b = COMPONENTES
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        v = vector(pl, V_DEMO, color=C_VEC, nombre=r"\vec v")
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Un vector cualquiera, con la rejilla todavía "
                              "quieta."), zona="abajo", run_time=0.5)
        self.play(GrowArrow(i_hat.flecha), FadeIn(i_hat.etiqueta),
                  GrowArrow(j_hat.flecha), FadeIn(j_hat.etiqueta),
                  run_time=0.7)
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.9)
        self.wait(3.0)

        # --- momento: la receta, con i y j de siempre ----------------------
        rot.mostrar(pie_curso("Su receta: tres veces î, y luego dos veces ĵ."),
                    zona="abajo", run_time=0.5)
        receta = combinacion(pl, a, (1, 0), b, (0, 1), mostrar_res=False)
        self.play(GrowArrow(receta.au), run_time=0.5)
        self.play(GrowArrow(receta.bv), run_time=0.5)
        self.wait(3.0)

        # --- momento: mover el plano ---------------------------------------
        rot.mostrar(pie_curso("Movemos el plano. v se va con él, como todo "
                              "lo demás."), zona="abajo", run_time=0.5)
        self.wait(0.8)
        self.play(FadeOut(receta), run_time=0.4)
        self.play(*pl.anim_matriz(M_LECCION, i_hat, j_hat, v), run_time=2.2)
        # Los objetos animados guardan las coords VIEJAS: los gemelos con la
        # matriz traen las nuevas, la prima y (en v) el color de imagen.
        self.play(Transform(i_hat, i_hat.con_matriz(
                      M_LECCION, nombre=r"\hat{\imath}\,'")),
                  Transform(j_hat, j_hat.con_matriz(
                      M_LECCION, nombre=r"\hat{\jmath}\,'")),
                  Transform(v, v.con_matriz(M_LECCION, color=C_IMG,
                                            nombre=r"M\vec v")),
                  run_time=0.6)
        self.wait(3.2)

        # --- momento: la misma receta, con los destinos nuevos --------------
        rot.mostrar(pie_curso("¿Dónde acabó? Donde manda la MISMA receta con "
                              "los nuevos î y ĵ."), zona="abajo",
                    run_time=0.5)
        receta2 = combinacion(pl, a, I_IMG, b, J_IMG, mostrar_res=False)
        et_a = MathTex(fmt(a, 0) + r"\,\hat{\imath}\,'", font_size=26,
                       color=C_I)
        et_a.next_to(pl.p(0.6 * a * I_IMG), DOWN, buff=0.22)
        et_b = MathTex(fmt(b, 0) + r"\,\hat{\jmath}\,'", font_size=26,
                       color=C_J)
        et_b.next_to(pl.p(a * I_IMG + 0.22 * b * J_IMG), RIGHT, buff=0.20)
        # La etiqueta de i' se retira: la de 3i' toma el relevo sobre la
        # misma recta (si no, "i'" y "3i'" quedan pegadas bajo la flecha).
        self.play(FadeOut(i_hat.etiqueta), run_time=0.3)
        self.play(GrowArrow(receta2.au), FadeIn(et_a), run_time=0.8)
        self.play(GrowArrow(receta2.bv), FadeIn(et_b), run_time=0.8)
        self.wait(3.4)

        # --- momento: la cuenta ---------------------------------------------
        rot.mostrar(pie_curso("Esa cuenta tiene nombre: la matriz por el "
                              "vector."), zona="abajo", run_time=0.5)
        mat = matriz_columnas(M_LECCION, font_size=28, h_buff=0.95)
        cv = vector_columna(V_DEMO, color=C_VEC, font_size=28)
        cmv = vector_columna(MV_DEMO, color=C_IMG, font_size=28)
        igual = MathTex("=", font_size=28, color=C_TENUE)
        cuenta = VGroup(mat, cv, igual, cmv).arrange(RIGHT, buff=0.18)
        panel = panel_derecha(cuenta)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.play(Indicate(v.flecha, color=C_IMG, scale_factor=1.06),
                  Indicate(cmv, color=C_IMG, scale_factor=1.10), run_time=0.9)
        self.wait(3.4)

        rot.mostrar(pie_curso("Multiplicar no es un ritual: es repartir el "
                              "vector entre las columnas."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)
