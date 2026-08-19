class Clip2(Scene):
    """3.3.2 - P tiene a b1 y b2 por columnas: multiplicar por P traduce del
    idioma nuevo al canonico, y P^-1 hace el viaje de vuelta. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La matriz de cambio de base")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la rejilla oblicua otra vez --------------------------
        pl = plano_leccion(centro=LEFT * 0.8 + DOWN * 0.15)
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        b1 = vector(pl, B1, color=C_I, nombre=r"\vec b_1", etiqueta_dir=DOWN)
        b2 = vector(pl, B2, color=C_J, nombre=r"\vec b_2", etiqueta_dir=LEFT)
        self.play(FadeIn(pl), run_time=0.8)
        self.play(GrowArrow(i_hat.flecha), FadeIn(i_hat.etiqueta),
                  GrowArrow(j_hat.flecha), FadeIn(j_hat.etiqueta),
                  run_time=0.7)
        rot.mostrar(pie_curso("La base nueva otra vez: b1 y b2 llevan la "
                              "rejilla a su forma oblicua."), zona="abajo",
                    run_time=0.5)
        self.play(Transform(i_hat, b1), Transform(j_hat, b2),
                  *pl.anim_matriz(P_BASE), run_time=1.8)
        self.wait(2.8)

        # --- momento: P, columna a columna ---------------------------------
        rot.mostrar(pie_curso("Escribe b1 y b2 en columnas, en el idioma de "
                              "siempre, y ya tienes P."), zona="abajo",
                    run_time=0.5)
        etiqueta_p = MathTex("P =", font_size=30, color=C_TENUE)
        mat_p = matriz_columnas(P_BASE, font_size=28)
        fila_p = VGroup(etiqueta_p, mat_p).arrange(RIGHT, buff=0.14)
        panel = panel_derecha(fila_p)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.play(Indicate(mat_p.columna(0), color=C_I, scale_factor=1.1),
                  Indicate(i_hat, color=C_I, scale_factor=1.05), run_time=0.8)
        self.play(Indicate(mat_p.columna(1), color=C_J, scale_factor=1.1),
                  Indicate(j_hat, color=C_J, scale_factor=1.05), run_time=0.8)
        self.wait(2.6)

        # --- momento: la ida (coordenadas nuevas -> canonicas) -------------
        rot.mostrar(pie_curso("v es (1, 1) en el idioma nuevo. ¿Cómo se dice "
                              "eso en el de siempre?"), zona="abajo",
                    run_time=0.5)
        v = vector(pl, V_DEMO, color=C_VEC, nombre=r"\vec v")
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.9)
        self.wait(3.4)

        col_b = vector_columna(V_B, color=C_VEC, font_size=26)
        col_b.matriz.get_rows()[0].set_color(C_I)
        col_b.matriz.get_rows()[1].set_color(C_J)
        col_can = vector_columna(V_DEMO, color=C_VEC, font_size=26)
        col_can.matriz.get_rows()[0].set_color(C_I)
        col_can.matriz.get_rows()[1].set_color(C_J)
        cuenta = VGroup(matriz_columnas(P_BASE, font_size=26), col_b,
                        MathTex("=", font_size=28, color=C_TENUE), col_can)
        cuenta.arrange(RIGHT, buff=0.2)
        cuenta.to_edge(DOWN, buff=MARGEN_PIE)
        rot.mostrar(_con_fondo(cuenta), zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: la vuelta (P^-1 deshace el viaje) --------------------
        rot.mostrar(pie_curso("Y al revés: la inversa de P devuelve la "
                              "rejilla —y las listas— a su sitio."),
                    zona="abajo", run_time=0.5)
        self.play(Transform(i_hat, b1.con_matriz(P_INV,
                                                 nombre=r"\hat{\imath}")),
                  Transform(j_hat, b2.con_matriz(P_INV,
                                                 nombre=r"\hat{\jmath}")),
                  *pl.anim_matriz(np.eye(2)), run_time=1.8)
        etiqueta_pi = MathTex("P^{-1} =", font_size=30, color=C_TENUE)
        mat_pi = matriz_columnas(P_INV, font_size=28)
        fila_pi = VGroup(etiqueta_pi, mat_pi).arrange(RIGHT, buff=0.14)
        fila_p2 = VGroup(MathTex("P =", font_size=30, color=C_TENUE),
                         matriz_columnas(P_BASE, font_size=28))
        fila_p2.arrange(RIGHT, buff=0.14)
        panel2 = panel_derecha(fila_p2, fila_pi, buff=0.3)
        self.play(FadeOut(panel), FadeIn(panel2), run_time=0.6)
        self.wait(3.0)

        # --- momento: el diccionario, en las dos direcciones ---------------
        col_b2 = vector_columna(V_B, color=C_VEC, font_size=26)
        col_b2.matriz.get_rows()[0].set_color(C_I)
        col_b2.matriz.get_rows()[1].set_color(C_J)
        col_can2 = vector_columna(V_DEMO, color=C_VEC, font_size=26)
        col_can2.matriz.get_rows()[0].set_color(C_I)
        col_can2.matriz.get_rows()[1].set_color(C_J)
        izq = VGroup(col_b2, tag_hud("b1, b2", font_size=15))
        izq.arrange(DOWN, buff=0.14)
        der = VGroup(col_can2, tag_hud("i, j", font_size=15))
        der.arrange(DOWN, buff=0.14)
        ida = Arrow(ORIGIN, RIGHT * 1.3, buff=0.0, color=C_TENUE,
                    stroke_width=3.0, tip_length=0.16,
                    max_tip_length_to_length_ratio=0.5)
        et_ida = MathTex("P", font_size=26, color=C_CALCULO)
        et_ida.next_to(ida, UP, buff=0.06)
        vuelta = Arrow(RIGHT * 1.3, ORIGIN, buff=0.0, color=C_TENUE,
                       stroke_width=3.0, tip_length=0.16,
                       max_tip_length_to_length_ratio=0.5)
        et_vuelta = MathTex("P^{-1}", font_size=26, color=C_CALCULO)
        et_vuelta.next_to(vuelta, DOWN, buff=0.06)
        medio = VGroup(VGroup(ida, et_ida), VGroup(vuelta, et_vuelta))
        medio.arrange(DOWN, buff=0.22)
        diagrama = VGroup(izq, medio, der).arrange(RIGHT, buff=0.34)
        diagrama.to_edge(DOWN, buff=MARGEN_PIE - 0.14)
        rot.mostrar(_con_fondo(diagrama), zona="abajo", run_time=0.5)
        self.wait(4.6)
