class Clip3(Scene):
    """1.2.3 - Si v es multiplo de u, toda combinacion a*u + b*v cae en la
    misma recta: el span pierde una dimension. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Cuando se alinean")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: recordar que antes el span era el plano ---------------
        pl = plano_leccion(vivo=False)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Antes, u y v no alineados generaban el "
                              "plano entero. ¿Y si SI se alinean?"),
                    zona="abajo", run_time=0.5)
        manto = Rectangle(width=config.frame_width, height=config.frame_height,
                          color=C_IMG, fill_color=C_IMG, fill_opacity=0.1,
                          stroke_width=0)
        manto.move_to(ORIGIN)
        self.play(FadeIn(manto), run_time=1.0)
        self.wait(2.8)

        # --- momento: v se vuelve multiplo de u ------------------------------
        u = vector(pl, U_COMB, color=C_VEC, nombre=r"\vec u")
        v2 = vector(pl, V_COLINEAL, color=C_VEC_2, nombre=r"\vec v")
        rot.mostrar(pie_curso("v = -1.5 u: mismo carril que u, sentido "
                              "contrario, mas largo."), zona="abajo",
                    run_time=0.5)
        self.play(GrowArrow(u.flecha), FadeIn(u.etiqueta), run_time=0.8)
        self.play(GrowArrow(v2.flecha), FadeIn(v2.etiqueta), run_time=0.8)
        self.wait(2.6)

        # --- momento: el plano se pierde -------------------------------------
        rot.mostrar(pie_curso("El plano que teniamos se pierde: ya no hay "
                              "adonde escapar de la recta."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(manto), run_time=1.2)
        recta_u = span_recta(pl, U_COMB, color=C_IMG, opacidad=0.55)
        self.play(Create(recta_u), run_time=1.2)
        self.wait(2.4)

        # --- momento: cualquier (a, b) cae en la recta -----------------------
        rot.mostrar(pie_curso("Prueba cualquier (a, b): la combinacion cae "
                              "siempre en esa recta."), zona="abajo",
                    run_time=0.5)
        self.wait(0.5)
        for (a, b) in PAREJAS_COLINEAL:
            comb = combinacion(pl, a, U_COMB, b, V_COLINEAL, color_res=C_IMG,
                               color_u=C_VEC, color_v=C_VEC_2,
                               mostrar_res=False)
            punto = pl.punto(a * U_COMB + b * V_COLINEAL, color=C_IMG,
                             radio=0.06)
            self.play(GrowArrow(comb.au), GrowArrow(comb.bv), FadeIn(punto),
                      run_time=1.1)
            self.play(FadeOut(comb), run_time=0.4)
            self.wait(1.0)

        rot.mostrar(pie_curso("Dos vectores alineados solo generan una "
                              "dimension: la recta, no el plano."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
