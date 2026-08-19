class Clip4(Scene):
    """5.3.4 - El sitio al que convergen todos los caminos es el vector
    propio de T con autovalor 1: T p* = p*. Cierra la lección. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El equilibrio es un vector propio")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: T, de nuevo, a mano -------------------------------------
        mat = matriz_columnas(T, colores=COLORES_ESTADOS, font_size=28)
        panel = panel_derecha(mat)
        self.play(FadeIn(panel), run_time=0.6)

        rot.mostrar(pie_curso("Sin importar dónde empieces, siempre "
                              "acabas en el mismo lugar. ¿Qué tiene de "
                              "especial ese vector?"), zona="abajo",
                    run_time=0.5)
        b = barras(P_ESTACIONARIO, colores=COLORES_ESTADOS, ancho=0.85,
                  alto=2.5, etiquetas=ESTADOS, font_size=18)
        b.move_to(DOWN * 0.55 + LEFT * 0.6)
        cifras = VGroup(*[tag_hud(fmt(P_ESTACIONARIO[i], 2), font_size=15,
                                  color=COLORES_ESTADOS[i])
                         .next_to(b.barras[i], UP, buff=0.12)
                         for i in range(3)])
        etiqueta_p = tag_hud("p*", font_size=20, color=C_IMG)
        etiqueta_p.next_to(b, LEFT, buff=0.5)
        self.play(FadeIn(b), FadeIn(cifras), FadeIn(etiqueta_p), run_time=0.9)
        self.wait(4.0)

        # --- momento: aplicarle T no lo mueve ----------------------------------
        rot.mostrar(pie_curso("Aplícale T y no cambia. Es un vector "
                              "propio de T, con autovalor uno."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(b, color=C_IMG, scale_factor=1.05), run_time=1.0)
        self.wait(3.2)

        rot.mostrar(formula_pie(r"T\,\vec p^{*} = 1 \cdot \vec p^{*}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        # --- momento: comparado con lo que ya viste al iterar --------------------
        rot.mostrar(pie_curso("Es el mismo límite al que llegaste al "
                              "iterar: la iteración se acerca, el "
                              "autovector es exacto."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(b), FadeOut(cifras), FadeOut(etiqueta_p),
                  run_time=0.5)

        v_iter = vector_columna(ITERADOS_N[PASOS_CLIP2], color=C_TENUE,
                               dec=2, font_size=30)
        for i in range(3):
            v_iter.matriz.get_rows()[i].set_color(COLORES_ESTADOS[i])
        et_iter = Text("tras " + str(PASOS_CLIP2) + " pasos", font_size=15,
                       color=C_TENUE)
        et_iter.next_to(v_iter, UP, buff=0.16)
        col_iter = VGroup(v_iter, et_iter)

        v_est = vector_columna(P_ESTACIONARIO, color=C_TENUE, dec=2,
                              font_size=30)
        for i in range(3):
            v_est.matriz.get_rows()[i].set_color(COLORES_ESTADOS[i])
        et_est = Text("equilibrio p*", font_size=15, color=C_IMG)
        et_est.next_to(v_est, UP, buff=0.16)
        col_est = VGroup(v_est, et_est)

        aprox = MathTex(r"\approx", font_size=32, color=C_TENUE)
        comparacion = VGroup(col_iter, aprox, col_est).arrange(RIGHT, buff=0.5)
        comparacion.move_to(DOWN * 0.5)
        self.play(FadeIn(comparacion, shift=0.15 * UP), run_time=0.8)
        self.wait(3.8)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(self, rot, "El mañana es la matriz por el hoy.",
                       "El equilibrio, su vector propio.",
                       "Ese mismo autovalor uno reaparece al girar en "
                       "tres dimensiones. Siguiente lección.",
                       panel, comparacion)
