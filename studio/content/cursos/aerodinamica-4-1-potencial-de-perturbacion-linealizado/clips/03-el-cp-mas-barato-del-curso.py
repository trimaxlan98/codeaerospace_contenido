class Clip3(Scene):
    """4.1.3 - Coeficiente de presion linealizado.

    La recompensa de la linealizacion: el cp deja de necesitar la ecuacion de
    la energia y se vuelve proporcional a la perturbacion longitudinal. Una
    linea, y con ella se resuelve medio modulo 4. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El cp más barato del curso")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        exacto = MathTex(r"c_p = \frac{2}{\gamma M_\infty^2}"
                         r"\left[\left(1 + \tfrac{\gamma-1}{2}M_\infty^2"
                         r"\left(1 - \tfrac{V^2}{V_\infty^2}\right)\right)"
                         r"^{\frac{\gamma}{\gamma-1}} - 1\right]",
                         font_size=32, color=C_TENUE)
        exacto.move_to(UP * 1.35)
        self.play(Write(exacto), run_time=1.6)
        rot.mostrar(pie_curso("Este es el coeficiente de presión exacto. "
                              "Correcto, y poco manejable."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Mete la hipótesis de perturbaciones pequeñas "
                              "y tira los cuadrados."), zona="abajo",
                    run_time=0.5)
        self.wait(1.2)

        lineal = MathTex(r"c_p = -\frac{2u'}{V_\infty}", font_size=56,
                         color=C_CALCULO)
        lineal.move_to(UP * 0.25)
        self.play(TransformMatchingShapes(exacto.copy(), lineal),
                  run_time=1.4)
        self.play(FadeOut(exacto), run_time=0.4)
        self.wait(3.0)

        rot.mostrar(pie_curso("Eso es todo. La presión ya solo depende de "
                              "cuánto acelera el aire por encima del perfil."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: lo que se ha ganado ----------------------------------
        ganancia = VGroup(
            Text("ni energía", font_size=21, color=C_SUB),
            Text("ni densidad", font_size=21, color=C_SUB),
            Text("ni temperatura", font_size=21, color=C_SUB)).arrange(
                RIGHT, buff=0.75)
        ganancia.move_to(DOWN * 1.35)
        self.play(LaggedStart(*[FadeIn(g, shift=0.12 * UP) for g in ganancia],
                              lag_ratio=0.35), run_time=1.2)
        rot.mostrar(pie_curso("Ya no hace falta la ecuación de la energía "
                              "para calcular una presión."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Con esta línea se resuelve casi todo lo que "
                              "queda de curso."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)
