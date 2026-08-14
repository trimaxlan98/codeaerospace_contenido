class Clip1(Scene):
    """4.2.1 - Regla de Prandtl-Glauert.

    La consecuencia mas util de la ecuacion linealizada, y la unica que sale
    directamente de ella: un dato medido en tunel a baja velocidad se
    convierte en el de alta dividiendo por una raiz. Un tunel lento sirve
    para diseñar un avion rapido. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La regla de Prandtl-Glauert")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        rot.mostrar(pie_curso("Mides un perfil en un túnel lento y obtienes "
                              "su cp. ¿Y a Mach 0.7?"), zona="abajo",
                    run_time=0.5)
        self.wait(1.2)

        formula = MathTex(r"c_p = \frac{c_{p,0}}{\sqrt{1 - M_\infty^2}}",
                          font_size=54, color=C_CALCULO)
        formula.move_to(UP * 1.15)
        self.play(Write(formula), run_time=1.2)
        self.wait(3.4)

        rot.mostrar(pie_curso("Divides por una raíz. Y ya está."),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        # --- momento: el caso concreto -------------------------------------
        # Las tres cifras salen del style_block, que las saca de la libreria.
        cuentas = VGroup(
            MathTex(rf"c_{{p,0}} = {CP0:.2f}", font_size=38, color=C_TENUE),
            MathTex(rf"\sqrt{{1 - {M_COMPARA:g}^2}} = "
                    rf"{np.sqrt(1 - M_COMPARA ** 2):.3f}", font_size=38,
                    color=C_TENUE),
            MathTex(rf"c_p = {PG:.3f}", font_size=44,
                    color=C_CALCULO)).arrange(DOWN, buff=0.30)
        cuentas.move_to(DOWN * 0.95)

        pies = ("El dato del túnel, medido despacio.",
                "La raíz, con el Mach al que quieres volar.",
                "Y la succión que de verdad va a tener.")
        for cuenta, pie in zip(cuentas, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(cuenta, shift=0.12 * UP), run_time=0.7)
            self.wait(4.2)

        rot.mostrar(pie_curso(f"Un {abs(PG / CP0 - 1) * 100:.0f} % más de "
                              "succión, solo por ir más rápido."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Un túnel lento sirve para diseñar un avión "
                              "rápido. Eso vale mucho dinero."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
