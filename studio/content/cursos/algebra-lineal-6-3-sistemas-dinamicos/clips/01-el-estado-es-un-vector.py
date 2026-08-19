class Clip1(Scene):
    """6.3.1 - El estado de un sistema (dos temperaturas de un satelite) es
    un vector, y un paso de tiempo es una matriz: repetirla deja un
    rastro. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El estado es un vector")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: dos temperaturas, un punto ---------------------------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.9)
        rot.mostrar(pie_curso("Dos módulos de un satélite, dos temperaturas. "
                              "El estado de hoy cabe en un punto."),
                    zona="abajo", run_time=0.5)
        et_x = Text("módulo A", font_size=19, color=C_TENUE)
        et_x.set_opacity(0.85)
        et_x.move_to(pl.p(3.3, 0) + DOWN * 0.3)
        et_y = Text("módulo B", font_size=19, color=C_TENUE)
        et_y.set_opacity(0.85)
        et_y.move_to(pl.p(0, 2.9) + LEFT * 0.95)
        punto = pl.punto(X0, color=C_VEC, radio=0.09)
        v = vector(pl, X0, color=C_VEC, nombre=r"\vec x_0")
        self.play(FadeIn(et_x), FadeIn(et_y), run_time=0.5)
        self.play(FadeIn(punto, scale=0.4), run_time=0.4)
        self.play(GrowArrow(v.flecha), run_time=0.8)
        self.play(FadeIn(v.etiqueta), run_time=0.3)
        self.wait(3.4)

        # --- momento: un paso de tiempo es una matriz ----------------------
        rot.mostrar(pie_curso("Un paso de tiempo es una matriz: multiplica "
                              "el estado de hoy y sale el de mañana."),
                    zona="abajo", run_time=0.5)
        mat = matriz_columnas(A_CONTRAE, dec=2, font_size=32)
        etq = tag_hud("A: un paso", font_size=17, color=C_TENUE)
        panel = panel_derecha(etq, mat, buff=0.22)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(1.2)

        # El estado de hoy se queda de fantasma rojo; el de mañana sale
        # verde (regla de la familia: lo que sale de la cuenta es verde).
        # La etiqueta se retira ANTES del Transform: morfear "x_0" en
        # "A x_0" (distinto numero de glifos) deja letras rotas por el
        # camino.
        fantasma = vector(pl, X0, color=C_VEC)
        fantasma.flecha.set_stroke(opacity=0.35)
        fantasma.flecha.set_fill(opacity=0.35)
        self.add(fantasma)
        manana = v.con_matriz(A_CONTRAE, color=C_IMG, nombre=r"A\vec x_0")
        self.play(FadeOut(v.etiqueta), run_time=0.25)
        self.play(*pl.anim_matriz(A_CONTRAE),
                  Transform(v.flecha, manana.flecha),
                  Transform(punto, pl.punto(X1, color=C_IMG, radio=0.09)),
                  run_time=2.0)
        self.play(FadeIn(manana.etiqueta), run_time=0.35)
        self.wait(2.0)

        # --- momento: el mismo paso, una y otra vez ------------------------
        rot.mostrar(pie_curso("Y otra vez. Y otra. Siempre la misma matriz, "
                              "aplicada al estado que acaba de salir."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(np.eye(2)), FadeOut(v.flecha),
                  FadeOut(manana.etiqueta), FadeOut(fantasma),
                  FadeOut(punto), run_time=1.2)
        tr = trayectoria(pl, TRAY_1, color=C_VEC, radio=0.07, grosor=2.4)
        self.play(FadeIn(tr.puntos[0], scale=0.5), run_time=0.4)
        self.play(LaggedStart(*[AnimationGroup(Create(tr.segmentos[i]),
                                               FadeIn(tr.puntos[i + 1],
                                                      scale=0.5))
                                for i in range(len(tr.segmentos))],
                              lag_ratio=0.55), run_time=2.6)
        self.wait(1.4)

        # --- momento: el rastro cae al cero --------------------------------
        rot.mostrar(pie_curso(fmt(PASOS_1, 0) + " pasos: el rastro cae en "
                              "espiral hacia el cero. El satélite vuelve al "
                              "nominal."), zona="abajo", run_time=0.5)
        cero = Dot(pl.p(0, 0), radius=0.09, color=C_IMG)
        self.play(FadeIn(cero, scale=0.4),
                  Flash(pl.p(0, 0), color=C_IMG, line_length=0.18,
                        num_lines=12), run_time=0.9)
        self.wait(4.2)

        rot.mostrar(pie_curso("Dónde acabará no lo decide el punto de "
                              "partida: lo decide esa matriz."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(mat, color=C_CALCULO, scale_factor=1.06),
                  run_time=0.9)
        self.wait(4.4)
