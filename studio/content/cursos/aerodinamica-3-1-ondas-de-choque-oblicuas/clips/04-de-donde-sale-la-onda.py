class Clip4(Scene):
    """3.1.4 - Generacion por una rampa de compresion.

    La onda no la pone el ingeniero: la pone la pared. Se compara la misma
    corriente contra tres rampas y se ve que beta crece con theta y que el
    suelo de esa subida es el angulo de Mach — una rampa de cero grados
    produce una onda de Mach, que no comprime nada. Cierre de la leccion.
    (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("De dónde sale la onda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # `con_theta` no existe: cada rampa es su propia pieza y se cruzan
        # con ReplacementTransform, que deja los datos coherentes con el
        # dibujo (un Transform conservaria el beta viejo en los atributos).
        actual = onda_oblicua(M_RAMPA, 5.0, largo=3.6, entrada=2.8)
        actual.move_to(DOWN * 0.75)
        ancla = actual.esquina()
        etiqueta = MathTex(rf"\theta = 5^\circ \qquad \beta = "
                           rf"{actual.beta():.1f}^\circ", font_size=34,
                           color=C_SUPER)
        etiqueta.move_to(UP * 1.85)

        self.play(FadeIn(VGroup(actual.pared, actual.choque)), run_time=0.8)
        self.play(FadeIn(actual.flujo_entrada, shift=0.2 * RIGHT),
                  FadeIn(etiqueta), run_time=0.7)
        rot.mostrar(pie_curso("Una rampa suave: la onda va casi tumbada."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Empina la rampa y la onda se levanta con "
                              "ella."), zona="abajo", run_time=0.5)
        self.wait(1.0)
        for theta in (12.0, 20.0):
            nueva = onda_oblicua(M_RAMPA, theta, largo=3.6, entrada=2.8)
            nueva.shift(ancla - nueva.esquina())
            nueva_etiqueta = MathTex(rf"\theta = {theta:g}^\circ \qquad "
                                     rf"\beta = {nueva.beta():.1f}^\circ",
                                     font_size=34, color=C_SUPER)
            nueva_etiqueta.move_to(UP * 1.85)
            self.play(ReplacementTransform(
                VGroup(actual.pared, actual.choque, actual.flujo_entrada),
                VGroup(nueva.pared, nueva.choque, nueva.flujo_entrada)),
                ReplacementTransform(etiqueta, nueva_etiqueta), run_time=1.1)
            actual, etiqueta = nueva, nueva_etiqueta
            self.wait(3.0)

        # --- momento: el suelo de beta -------------------------------------
        rot.mostrar(pie_curso("¿Y si la rampa fuese de cero grados?"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        rot.mostrar(formula_pie(rf"\beta \to \mu = "
                                rf"\operatorname{{arcsen}}\tfrac{{1}}{{M}} = "
                                rf"{MU_RAMPA:.0f}^\circ", color=C_CALCULO),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("El ángulo de Mach de la lección 1.3. Una onda "
                              "que no comprime nada."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(actual.pared, actual.choque,
                                 actual.flujo_entrada, etiqueta)),
                  run_time=0.8)
        cierre = VGroup(
            titulo_marca("La pared decide cuánto gira el aire.",
                         font_size=35, color=C_TITULO),
            titulo_marca("El aire decide con qué onda.", font_size=35,
                         color=C_SUPER)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)
