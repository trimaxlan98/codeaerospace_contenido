class Clip3(Scene):
    """3.1.3 - Uso de las relaciones de choque normal con Mn1 = M1 sen(beta).

    El pago de los dos clips anteriores: no hay tablas nuevas. Se calcula
    Mn1, se entra con el en la tabla de choque NORMAL de la leccion 2.2, y
    se sale con todo. La unica cuenta extra es deshacer la descomposicion al
    final. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El truco del seno")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        rot.mostrar(formula_pie(r"M_{n1} = M_1 \sin\beta"), zona="abajo",
                    run_time=0.5)
        self.wait(1.2)

        # Los cuatro pasos, colocados de una vez y encendidos por turnos: asi
        # ninguno se mueve cuando entra el siguiente. Cada cifra sale de la
        # libreria, no de la memoria.
        pasos = VGroup(
            VGroup(Text("1", font=FUENTE_HUD, font_size=22, color=C_TENUE),
                   MathTex(rf"M_{{n1}} = {M_RAMPA:g}\,"
                           rf"\sin {OBLICUO['beta']:.2f}^\circ = "
                           rf"{OBLICUO['Mn1']:.4f}", font_size=34,
                           color=C_SUPER)),
            VGroup(Text("2", font=FUENTE_HUD, font_size=22, color=C_TENUE),
                   MathTex(rf"\text{{tabla de choque normal}} \;\Rightarrow\; "
                           rf"M_{{n2}} = {OBLICUO['Mn2']:.4f}", font_size=34,
                           color=C_CALCULO)),
            VGroup(Text("3", font=FUENTE_HUD, font_size=22, color=C_TENUE),
                   MathTex(rf"\frac{{p_2}}{{p_1}} = "
                           rf"{OBLICUO['p2/p1']:.4f}\qquad "
                           rf"\frac{{T_2}}{{T_1}} = "
                           rf"{OBLICUO['T2/T1']:.4f}", font_size=34,
                           color=C_CALCULO)),
            VGroup(Text("4", font=FUENTE_HUD, font_size=22, color=C_TENUE),
                   MathTex(rf"M_2 = \frac{{M_{{n2}}}}"
                           rf"{{\sin(\beta - \theta)}} = "
                           rf"{OBLICUO['M2']:.4f}", font_size=34,
                           color=C_SUB)))
        for fila in pasos:
            fila.arrange(RIGHT, buff=0.42)
        pasos.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        pasos.move_to(UP * 0.35)

        pies = ("Primero, la componente que cruza la onda de frente.",
                "Con ella entras en la tabla del choque normal. La misma de "
                "la lección 2.2.",
                "Y de ahí salen la presión y la temperatura. Sin fórmulas "
                "nuevas.",
                "Solo queda deshacer la descomposición para recuperar el "
                "Mach de salida.")
        for fila, pie in zip(pasos, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(fila, shift=0.12 * UP), run_time=0.7)
            self.wait(4.4)

        rot.mostrar(pie_curso("Un choque oblicuo no tiene tablas propias. "
                              "Usa las del normal, entrando por el seno."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
