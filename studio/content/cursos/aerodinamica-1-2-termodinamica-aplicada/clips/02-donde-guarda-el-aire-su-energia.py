class Clip2(Scene):
    """1.2.2 - Energia interna, entalpia y los calores especificos cp, cv, gamma.

    cp = cv + R no se enuncia: se dibuja. Las dos filas de barras miden lo
    mismo porque los numeros reales del aire lo dicen, y de ese cociente sale
    gamma = 1.4 sin postularlo. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Dónde guarda el aire su energía")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        barras = barras_calores()
        barras.move_to(UP * 0.35)

        # --- momento: la energia interna ----------------------------------
        self.play(FadeIn(barras.barra(0)), FadeIn(barras.etiquetas[0]),
                  run_time=0.8)
        rot.mostrar(pie_curso("La energía que el aire ya tiene guardada es su "
                              "temperatura, con un factor."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(formula_pie(r"e = c_v\,T"), zona="abajo", run_time=0.5)
        self.wait(4.2)

        # --- momento: el trabajo de flujo ---------------------------------
        rot.mostrar(pie_curso("Pero un flujo no solo lleva energía: además "
                              "empuja al aire que tiene delante."),
                    zona="abajo", run_time=0.5)
        self.wait(1.0)
        self.play(FadeIn(barras.barra(1), shift=0.14 * RIGHT),
                  FadeIn(barras.etiquetas[1]), run_time=0.8)
        self.wait(3.8)

        rot.mostrar(formula_pie(r"h = e + \frac{p}{\rho} = c_v T + R T"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: la suma es cp ---------------------------------------
        # Las dos filas miden exactamente lo mismo porque cv + R = cp con los
        # valores reales; la libreria las escala con el mismo factor.
        self.play(FadeIn(barras.barra(2), shift=0.14 * UP),
                  FadeIn(barras.etiquetas[2]), run_time=0.9)
        rot.mostrar(pie_curso("Los dos trozos juntos son cp. Por eso "
                              "cp = cv + R, siempre."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: gamma ------------------------------------------------
        gamma = MathTex(rf"\gamma = \frac{{c_p}}{{c_v}} = "
                        rf"\frac{{{barras.valor('cp'):.0f}}}"
                        rf"{{{barras.valor('cv'):.0f}}} = "
                        rf"{barras.valor('gamma'):.1f}",
                        font_size=44, color=C_SUPER)
        gamma.move_to(DOWN * 1.55)
        self.play(Write(gamma), run_time=1.1)
        rot.mostrar(pie_curso("Y su cociente es gamma."), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)

        rot.mostrar(pie_curso("Un uno coma cuatro que va a salir en cada "
                              "fórmula del curso."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
