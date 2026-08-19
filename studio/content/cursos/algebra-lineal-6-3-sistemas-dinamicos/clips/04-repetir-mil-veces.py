class Clip4(Scene):
    """6.3.4 - El sistema estable converge y la matriz repetida encoge la
    rejilla entera; luego el recap de la familia (la rejilla que se mueve,
    el area del determinante, los ejes propios) y el cierre. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Repetir mil veces")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el sistema estable converge ---------------------------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.9)
        rot.mostrar(pie_curso("Vuelve el sistema estable: cada paso encoge "
                              "el estado y lo gira un poco."),
                    zona="abajo", run_time=0.5)
        tr = trayectoria(pl, TRAY_4, color=C_VEC, radio=0.06, grosor=2.2)
        self.play(FadeIn(tr.puntos[0], scale=0.5), run_time=0.3)
        self.play(LaggedStart(*[AnimationGroup(Create(tr.segmentos[i]),
                                               FadeIn(tr.puntos[i + 1],
                                                      scale=0.5))
                                for i in range(len(tr.segmentos))],
                              lag_ratio=0.35), run_time=2.6)
        self.wait(2.4)

        # --- momento: la matriz elevada a veinte ----------------------------
        rot.mostrar(pie_curso(fmt(PASOS_4, 0) + " pasos son la misma matriz "
                              + fmt(PASOS_4, 0) + " veces: la rejilla entera "
                              "se encoge."), zona="abajo", run_time=0.5)
        mat = matriz_columnas(A_POTENCIA, dec=2, font_size=30)
        etq = tag_hud("A^" + fmt(PASOS_4, 0), font_size=18, color=C_TENUE)
        panel = panel_derecha(etq, mat, buff=0.22)
        cifra = MathTex(r"|\lambda|^{" + fmt(PASOS_4, 0) + r"} = "
                        + fmt(MOD_POTENCIA, 2), font_size=28,
                        color=C_CALCULO)
        caja = _con_fondo(cifra, buff=0.16, opacidad=0.78)
        caja.next_to(panel, DOWN, buff=0.28).align_to(panel, RIGHT)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.play(*pl.anim_matriz(A_POTENCIA), FadeIn(caja), run_time=2.0)
        self.wait(2.4)

        # --- recap de la familia: la rejilla se mueve ------------------------
        rot.mostrar(pie_curso("En esta rejilla cabía todo el curso. Una "
                              "matriz la mueve: eso es una transformación."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(tr.segmentos), FadeOut(tr.puntos), FadeOut(panel),
                  FadeOut(caja), *pl.anim_matriz(np.eye(2)), run_time=1.1)
        self.play(*pl.anim_matriz(M_RECAP), run_time=1.8)
        self.wait(2.4)

        # --- recap: el determinante ------------------------------------------
        rot.mostrar(pie_curso("El determinante mide cuánto se abre el área: "
                              "aquí, por " + fmt(DET_RECAP, 1) + "."),
                    zona="abajo", run_time=0.5)
        par = paralelogramo(pl, M_RECAP)
        cifra_det = MathTex(r"\det = " + fmt(abs(par.area), 1), font_size=32,
                            color=C_AREA)
        caja_det = _con_fondo(cifra_det, buff=0.16, opacidad=0.8)
        caja_det.move_to(pl.p(3.0, 2.3))
        self.play(FadeIn(par), run_time=0.8)
        self.play(FadeIn(caja_det), run_time=0.5)
        self.wait(3.8)

        # --- recap: los ejes propios -----------------------------------------
        rot.mostrar(pie_curso("Y sus ejes propios dicen adónde va todo "
                              "cuando el paso se repite."),
                    zona="abajo", run_time=0.5)
        e1 = span_recta(pl, EJES_RECAP[:, 0], color=C_PROPIO, opacidad=0.55)
        e2 = span_recta(pl, EJES_RECAP[:, 1], color=C_PROPIO, opacidad=0.55)
        w1 = vector(pl, V_RECAP_1, color=C_PROPIO)
        w2 = vector(pl, V_RECAP_2, color=C_PROPIO)
        self.play(FadeOut(par), FadeOut(caja_det),
                  *pl.anim_matriz(np.eye(2)), run_time=1.0)
        # Create sobre un VGroup escalona los submobjects: la segunda recta
        # llegaba medio segundo tarde. Dos Create sueltos entran a la vez.
        self.play(Create(e1), Create(e2), GrowArrow(w1.flecha),
                  GrowArrow(w2.flecha), run_time=0.9)
        self.play(*pl.anim_matriz(M_RECAP, w1, w2), run_time=1.8)
        self.wait(2.0)

        # --- cierre de la leccion (y de la familia) --------------------------
        cierre_leccion(self, rot,
                       "El tiempo es una matriz aplicada mil veces.",
                       "Sus ejes propios dicen el final.",
                       "Aquí se cierra el curso: una flecha, un movimiento, "
                       "un área y un eje.",
                       pl, e1, e2, w1, w2, espera=4.8)
