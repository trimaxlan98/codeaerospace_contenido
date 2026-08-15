class Clip4(Scene):
    """1.3.4 - El haz que se abre. Un laser tampoco es una recta: con una
    cintura de 5 cm a 1550 nm se abre 9.87 urad, y a 5000 km eso son casi cien
    metros de mancha. Cierra la leccion (y el modulo) con la frase doble.
    (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("El haz que se abre"), zona="arriba",
                    run_time=0.6)

        # El eje llega a 6000 km para que el plano lejano de 5000 km caiga
        # DENTRO del dibujo (`a_distancia` lo lleva ahi en el tercer momento).
        Z_MAX = 6.0e6
        haz = haz_gaussiano(w0=W0_ISL, lam=LAMBDA_ISL, z_max=Z_MAX, ancho=5.8,
                            alto=2.2)
        haz.move_to(UP * 0.10)

        # Las cifras las pone el clip con las constantes del style_block, asi
        # que los rotulos gemelos de la libreria (theta y la lectura de la
        # huella) se desmontan; el plano y la asintota llegan mas tarde.
        t_theta = tag_hud(f"theta = {DIV_ISL_URAD:.2f} urad", font_size=17)
        t_theta.move_to(haz.rotulos[1].get_left(), aligned_edge=LEFT)
        haz.rotulos.remove(haz.rotulos[1])
        haz.remove(haz.asintota, haz.marcador, haz.lectura)

        # --- momento: el laser tambien se abre ---------------------------------
        rot.mostrar(pie_curso("Un láser también se abre: la cintura marca "
                              "cuánto."), zona="abajo", run_time=0.5)
        self.play(Create(haz.eje), run_time=0.4)
        self.play(FadeIn(haz.relleno), Create(haz.superior),
                  Create(haz.inferior), run_time=1.4)
        self.play(FadeIn(haz.cintura), FadeIn(haz.rotulos), run_time=0.6)
        self.wait(4.4)

        # --- momento: cuanto se abre --------------------------------------------
        rot.mostrar(pie_curso("A 1550 nanómetros y 5 centímetros de cintura, "
                              "el haz se abre 9.9 microrradianes."),
                    zona="abajo", run_time=0.5)
        ley = MathTex(r"\theta = \frac{\lambda}{\pi w_0}", font_size=44,
                      color=C_ACENTO)
        ley.move_to(np.array([-4.55, 1.05, 0.0]))
        self.play(Write(ley), run_time=1.2)
        self.play(FadeIn(haz.asintota), FadeIn(t_theta), run_time=0.8)
        self.wait(4.4)

        # --- momento: la huella a 5000 km ---------------------------------------
        rot.mostrar(pie_curso("Parece nada. A cinco mil kilómetros son cien "
                              "metros de mancha."), zona="abajo",
                    run_time=0.5)
        haz.a_distancia(R_ISL_KM * 1e3)     # lleva el plano marcador a 5000 km
        haz.remove(haz.lectura)             # la cifra la pone el tag de abajo
        km = f"{R_ISL_KM:,.0f}".replace(",", " ")
        t_huella = tag_hud(f"huella a {km} km: {HUELLA_ISL_M:.0f} m",
                           font_size=17, color=C_MEDIDA)
        t_huella.move_to(np.array([2.85, 1.62, 0.0]), aligned_edge=RIGHT)
        # el plano marcador cruza el sitio del rotulo de theta: se lo aparta
        # hacia la cintura antes de que entre el plano.
        self.play(t_theta.animate.next_to(haz.rotulos[0], UP, buff=0.40,
                                          aligned_edge=LEFT),
                  run_time=0.5)
        self.play(FadeIn(haz.marcador), FadeIn(t_huella), run_time=0.9)
        self.wait(4.6)

        # --- cierre de la leccion -------------------------------------------------
        self.play(FadeOut(VGroup(haz, haz.marcador, haz.asintota, ley, t_theta,
                                 t_huella)),
                  run_time=0.7)
        rot.limpiar(run_time=0.4)
        linea1 = Text("Ni el láser es una recta.", font_size=40,
                      color=C_TITULO)
        linea2 = Text("Todo haz se abre.", font_size=40, color=C_HAZ)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.65)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.65)
        self.wait(5.0)
