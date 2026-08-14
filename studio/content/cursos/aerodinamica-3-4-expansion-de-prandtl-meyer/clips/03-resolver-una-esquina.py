class Clip3(Scene):
    """3.4.3 - Procedimiento de calculo para una esquina convexa.

    Tres lineas y esta hecho. Es el contraste deliberado con el clip 3 de la
    leccion 3.1: alli hacian falta cuatro pasos y una tabla; aqui basta con
    sumar el giro al contador y volver. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Resolver una esquina")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        abanico = abanico_expansion(M_ESQUINA, THETA_ESQUINA, n_lineas=7,
                                    largo=2.2, entrada=1.8)
        abanico.move_to(LEFT * 3.6 + UP * 0.55)
        self.play(FadeIn(abanico), run_time=0.9)

        # Los tres pasos, colocados de una vez y encendidos por turnos. Todas
        # las cifras salen de `expansion`, incluida la de presion.
        pasos = VGroup(
            MathTex(rf"\nu_1 = \nu({M_ESQUINA:g}) = "
                    rf"{EXPANDIDO['nu1']:.2f}^\circ", font_size=36,
                    color=C_CALCULO),
            MathTex(rf"\nu_2 = {EXPANDIDO['nu1']:.2f} + "
                    rf"{THETA_ESQUINA:g} = {EXPANDIDO['nu2']:.2f}^\circ",
                    font_size=36, color=C_CALCULO),
            MathTex(rf"M_2 = {EXPANDIDO['M2']:.4f}", font_size=36,
                    color=C_SUB))
        pasos.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        pasos.move_to(RIGHT * 2.4 + UP * 0.55)

        pies = ("Entra el contador del flujo que llega.",
                "Le sumas lo que gira la pared. Nada más.",
                "Y lo devuelves a Mach. Se acabó.")
        for paso, pie in zip(pasos, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(paso, shift=0.12 * UP), run_time=0.7)
            self.wait(4.4)

        # --- momento: y la presion, gratis ---------------------------------
        presion = MathTex(rf"\frac{{p_2}}{{p_1}} = {EXPANDIDO['p2/p1']:.4f}",
                          font_size=36, color=C_TRANS)
        presion.next_to(pasos, DOWN, buff=0.55).align_to(pasos, LEFT)
        self.play(FadeIn(presion, shift=0.12 * UP), run_time=0.7)
        rot.mostrar(pie_curso("La presión sale sola: como es isentrópica, la "
                              "de estancamiento no ha cambiado."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Compáralo con el choque oblicuo: cuatro pasos "
                              "y una tabla. Aquí, una suma."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)
