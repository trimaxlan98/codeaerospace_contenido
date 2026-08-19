class Clip4(Scene):
    """1.1.4 - i-sombrero y j-sombrero: todo vector es una mezcla de los
    dos, y sus coordenadas dicen cuanto de cada uno. Cierra la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Todo vector es î y ĵ")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion(vivo=False)
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Dos flechas especiales: î apunta a la "
                              "derecha, ĵ hacia arriba. Miden uno."),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(i_hat.flecha), FadeIn(i_hat.etiqueta),
                  run_time=0.7)
        self.play(GrowArrow(j_hat.flecha), FadeIn(j_hat.etiqueta),
                  run_time=0.7)
        self.wait(3.6)

        # --- momento: construir (3, 2) con i y j -----------------------------
        rot.mostrar(pie_curso("Tres veces î, y luego dos veces ĵ desde su "
                              "punta: llegas justo a (3, 2)."),
                    zona="abajo", run_time=0.5)
        a, b = COMPONENTES
        comb = combinacion(pl, a, (1, 0), b, (0, 1), color_res=C_VEC,
                           mostrar_res=False)
        et_a = MathTex(fmt(a, 0) + r"\,\hat{\imath}", font_size=30, color=C_I)
        et_a.next_to(pl.p(a / 2, 0), DOWN, buff=0.18)
        et_b = MathTex(fmt(b, 0) + r"\,\hat{\jmath}", font_size=30, color=C_J)
        et_b.next_to(pl.p(a, b / 2), RIGHT, buff=0.18)
        # Las etiquetas de i y j se retiran: las de 3i y 2j toman el relevo
        # (si no, "i" y "3i" quedan pegadas bajo el eje).
        self.play(FadeOut(i_hat.etiqueta), FadeOut(j_hat.etiqueta),
                  run_time=0.3)
        self.play(GrowArrow(comb.au), FadeIn(et_a), run_time=0.9)
        self.play(GrowArrow(comb.bv), FadeIn(et_b), run_time=0.9)
        self.wait(2.6)

        v = vector(pl, V_DEMO, color=C_VEC, nombre=r"\vec v")
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.9)
        rot.mostrar(formula_pie(r"\vec v = " + fmt(a, 0)
                                + r"\,\hat{\imath} + " + fmt(b, 0)
                                + r"\,\hat{\jmath}"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

        # --- momento: las coordenadas eran esto -----------------------------
        rot.mostrar(pie_curso("Las coordenadas no eran otra cosa: cuánto î "
                              "y cuánto ĵ. Los dos idiomas eran uno."),
                    zona="abajo", run_time=0.5)
        columna = vector_columna(V_DEMO, color=C_VEC, font_size=40)
        columna.matriz.get_rows()[0].set_color(C_I)
        columna.matriz.get_rows()[1].set_color(C_J)
        panel = panel_derecha(columna)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.play(Indicate(comb.au, color=C_I, scale_factor=1.04),
                  Indicate(columna.matriz.get_rows()[0], color=C_I),
                  run_time=0.8)
        self.play(Indicate(comb.bv, color=C_J, scale_factor=1.04),
                  Indicate(columna.matriz.get_rows()[1], color=C_J),
                  run_time=0.8)
        self.wait(3.4)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(self, rot, "Una flecha es una lista.",
                       "Una lista es una flecha.",
                       "Y si mezclamos flechas cualesquiera, ¿hasta dónde "
                       "llegamos? Siguiente lección.",
                       pl, i_hat, j_hat, comb, et_a, et_b, v, panel)
