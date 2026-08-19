class Clip2(Scene):
    """4.2.2 - A = P D P^-1: aplicar A es traducir a la base propia (P^-1),
    estirar ahí (D) y traducir de vuelta (P). Las tres piezas, calculadas,
    reconstruyen A. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("A = P D P^-1")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion()
        v = vector(pl, V_GEN, color=C_VEC, nombre=r"\vec v")
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Aplicar A de un tirón parece un solo "
                              "movimiento. Se desarma en tres pasos."),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.8)
        self.wait(3.0)

        rot.mostrar(pie_curso("Paso 1, P^-1: traduce al idioma de los "
                              "vectores propios."), zona="abajo",
                    run_time=0.5)
        self.play(*pl.anim_matriz(PINV_MAT, v), run_time=2.0)
        self.wait(3.2)

        rot.mostrar(pie_curso("Paso 2, D: en ese idioma, A solo estira."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(D_MAT @ PINV_MAT, v), run_time=2.0)
        self.wait(3.2)

        rot.mostrar(pie_curso("Paso 3, P: traduce de vuelta al idioma "
                              "normal."), zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(P_MAT @ D_MAT @ PINV_MAT, v), run_time=2.0)
        self.wait(3.2)

        rot.mostrar(pie_curso("Tres pasos, calculados uno por uno: "
                              "multiplicados en ese orden, dan de vuelta "
                              "exactamente A."), zona="abajo", run_time=0.5)
        fila_p = VGroup(MathTex("P", font_size=18, color=C_CALCULO),
                       matriz_columnas(P_MAT, font_size=18, h_buff=0.7)
                       ).arrange(RIGHT, buff=0.16)
        fila_d = VGroup(MathTex("D", font_size=18, color=C_CALCULO),
                       matriz_columnas(D_MAT, font_size=18, h_buff=0.7)
                       ).arrange(RIGHT, buff=0.16)
        fila_pinv = VGroup(MathTex("P^{-1}", font_size=18, color=C_CALCULO),
                          matriz_columnas(PINV_MAT, font_size=18, h_buff=0.7)
                          ).arrange(RIGHT, buff=0.16)
        fila_check = VGroup(
            MathTex(r"P\,D\,P^{-1}=", font_size=18, color=C_CALCULO),
            matriz_columnas(A_RECOMPUESTA, dec=0, font_size=18, h_buff=0.7)
        ).arrange(RIGHT, buff=0.16)
        panel = panel_derecha(fila_p, fila_d, fila_pinv, fila_check,
                              buff=0.16)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.6)
