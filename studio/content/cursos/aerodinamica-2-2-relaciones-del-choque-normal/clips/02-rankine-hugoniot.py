class Clip2(Scene):
    """2.2.2 - Ecuaciones de Rankine-Hugoniot.

    De las tres cuentas del clip anterior sale un sistema con dos
    soluciones: la trivial (no pasa nada) y el choque. Que exista la segunda
    es lo sorprendente, y que la primera no sea la unica es lo que hace
    posible todo el modulo. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Rankine y Hugoniot")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        rot.mostrar(pie_curso("Junta las tres, elimina las velocidades y "
                              "queda una sola ecuación en el Mach."),
                    zona="abajo", run_time=0.5)
        self.wait(1.2)

        formula = MathTex(r"M_2^2 = \frac{1 + \tfrac{\gamma-1}{2}M_1^2}"
                          r"{\gamma M_1^2 - \tfrac{\gamma-1}{2}}",
                          font_size=52, color=C_CALCULO)
        formula.move_to(UP * 0.85)
        self.play(Write(formula), run_time=1.4)
        self.wait(3.4)

        rot.mostrar(pie_curso("Tiene dos soluciones. Una es que no pase "
                              "nada: el aire sigue igual."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        trivial = MathTex(r"M_2 = M_1", font_size=40, color=C_TENUE)
        trivial.move_to(DOWN * 0.70)
        self.play(FadeIn(trivial, shift=0.12 * UP), run_time=0.6)
        rot.mostrar(pie_curso("Es una solución perfectamente válida. Y "
                              "perfectamente aburrida."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- momento: la otra solucion ------------------------------------
        # El numero sale de la libreria: la misma expresion que se acaba de
        # escribir, evaluada en el Mach de referencia del modulo.
        otra = MathTex(rf"M_1 = {M1_REF:g} \;\Rightarrow\; "
                       rf"M_2 = {SALTO['M2']:.4f}", font_size=40,
                       color=C_SUPER)
        otra.move_to(DOWN * 0.70)
        rot.mostrar(pie_curso("La otra es la interesante."), zona="abajo",
                    run_time=0.5)
        self.wait(1.0)
        self.play(TransformMatchingShapes(trivial, otra), run_time=1.0)
        self.wait(3.4)

        rot.mostrar(pie_curso("Entra supersónico y sale subsónico. Siempre, "
                              "sin excepción."), zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Un choque normal no puede dejar el flujo "
                              "supersónico. Lo frena por debajo de 1."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
