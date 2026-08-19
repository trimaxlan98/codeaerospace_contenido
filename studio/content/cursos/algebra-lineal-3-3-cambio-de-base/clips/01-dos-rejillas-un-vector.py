class Clip1(Scene):
    """3.3.1 - Las coordenadas no son del vector: son de la rejilla con la
    que lo medimos. El mismo v, dos listas. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Dos rejillas, un vector")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la rejilla de siempre --------------------------------
        pl = plano_leccion()
        # La rejilla canonica (gris) sube de opacidad: cuando la viva se
        # vuelva oblicua tiene que verse CONTRA que se ha torcido.
        pl.fijo.set_stroke(opacity=0.95)
        self.play(FadeIn(pl), run_time=0.9)
        rot.mostrar(pie_curso("Medimos el plano con dos flechas: î a la "
                              "derecha, ĵ hacia arriba."), zona="abajo",
                    run_time=0.5)
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        self.play(GrowArrow(i_hat.flecha), FadeIn(i_hat.etiqueta),
                  run_time=0.6)
        self.play(GrowArrow(j_hat.flecha), FadeIn(j_hat.etiqueta),
                  run_time=0.6)
        self.wait(3.2)

        # --- momento: la lectura canonica ----------------------------------
        lista_can = "(" + fmt(V_DEMO[0], 0) + ", " + fmt(V_DEMO[1], 0) + ")"
        rot.mostrar(pie_curso("Un vector v. Cuatro pasos de î y tres de ĵ: "
                              "la lista es " + lista_can + "."), zona="abajo",
                    run_time=0.5)
        v = vector(pl, V_DEMO, color=C_VEC, nombre=r"\vec v")
        self.play(GrowArrow(v.flecha), run_time=0.9)
        self.play(FadeIn(v.etiqueta), run_time=0.3)
        tramo_x = Line(pl.p(0, 0), pl.p(V_DEMO[0], 0), color=C_I,
                       stroke_width=6.0)
        tramo_y = Line(pl.p(V_DEMO[0], 0), pl.p(V_DEMO), color=C_J,
                       stroke_width=6.0)
        cifra_x = tag_hud(fmt(V_DEMO[0], 0), font_size=22, color=C_I)
        cifra_x.next_to(pl.p(V_DEMO[0] / 2, 0), DOWN, buff=0.18)
        cifra_y = tag_hud(fmt(V_DEMO[1], 0), font_size=22, color=C_J)
        cifra_y.next_to(pl.p(V_DEMO[0], V_DEMO[1] / 2), RIGHT, buff=0.18)
        guias = VGroup(tramo_x, tramo_y, cifra_x, cifra_y)
        self.play(Create(tramo_x), FadeIn(cifra_x), run_time=0.6)
        self.play(Create(tramo_y), FadeIn(cifra_y), run_time=0.6)
        self.wait(3.4)

        # --- momento: otra base, otra rejilla ------------------------------
        rot.mostrar(pie_curso("Pero î y ĵ no son sagradas. Otra base: b1 y "
                              "b2, y su rejilla oblicua."), zona="abajo",
                    run_time=0.5)
        b1 = vector(pl, B1, color=C_I, nombre=r"\vec b_1", etiqueta_dir=DOWN)
        b2 = vector(pl, B2, color=C_J, nombre=r"\vec b_2", etiqueta_dir=LEFT)
        self.play(FadeOut(guias), run_time=0.4)
        self.play(Transform(i_hat, b1), Transform(j_hat, b2),
                  *pl.anim_matriz(P_BASE), run_time=2.0)
        self.wait(3.4)

        # --- momento: la lectura en la rejilla oblicua ---------------------
        rot.mostrar(pie_curso("v no se ha movido. Pero en esta rejilla está "
                              "a un paso de b1 y uno de b2."), zona="abajo",
                    run_time=0.5)
        comb = combinacion(pl, V_B[0], B1, V_B[1], B2, mostrar_res=False)
        et_a = MathTex(fmt(V_B[0], 0) + r"\,\vec b_1", font_size=28, color=C_I)
        et_a.next_to(pl.p(B1 / 2), DOWN + RIGHT, buff=0.14)
        et_b = MathTex(fmt(V_B[1], 0) + r"\,\vec b_2", font_size=28, color=C_J)
        et_b.next_to(pl.p(B1 + B2 / 2), RIGHT, buff=0.16)
        self.play(GrowArrow(comb.au), FadeIn(et_a), run_time=0.8)
        self.play(GrowArrow(comb.bv), FadeIn(et_b), run_time=0.8)
        self.wait(3.2)

        # --- momento: las dos listas, lado a lado --------------------------
        rot.mostrar(pie_curso("La misma flecha, dos listas. Las coordenadas "
                              "son de la rejilla, no del vector."),
                    zona="abajo", run_time=0.5)
        col_can = vector_columna(V_DEMO, color=C_VEC, font_size=32)
        col_can.matriz.get_rows()[0].set_color(C_I)
        col_can.matriz.get_rows()[1].set_color(C_J)
        col_b = vector_columna(V_B, color=C_VEC, font_size=32)
        col_b.matriz.get_rows()[0].set_color(C_I)
        col_b.matriz.get_rows()[1].set_color(C_J)
        bloque_can = VGroup(tag_hud("i, j", font_size=15), col_can)
        bloque_can.arrange(DOWN, buff=0.14)
        bloque_b = VGroup(tag_hud("b1, b2", font_size=15), col_b)
        bloque_b.arrange(DOWN, buff=0.14)
        panel = panel_derecha(VGroup(bloque_can, bloque_b).arrange(RIGHT,
                                                                   buff=0.42))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.0)

        rot.mostrar(pie_curso("Cambiar de base es cambiar de idioma. Falta "
                              "el diccionario: la matriz P."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
