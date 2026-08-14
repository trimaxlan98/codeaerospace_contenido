class Clip2(Scene):
    """2.4.2 - Ecuacion diferencial area-velocidad.

    Juntando continuidad, cantidad de movimiento y la definicion del Mach
    sale una sola relacion diferencial, y en ella todo el asunto cuelga del
    signo de M^2 - 1. Es la ecuacion mas rentable del modulo: en una linea
    contiene los dos comportamientos opuestos del clip siguiente. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La ecuación área-velocidad")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        rot.mostrar(pie_curso("Continuidad, cantidad de movimiento y la "
                              "definición del Mach. Nada nuevo."),
                    zona="abajo", run_time=0.5)
        self.wait(1.2)

        # En partes y no en una sola cadena: el recuadro tiene que abrazar
        # el parentesis, y localizarlo por indices de glifo (formula[0][8:15])
        # acaba encerrando «-1) dV/V», que no es lo que se esta señalando.
        formula = MathTex(r"\frac{dA}{A}", r"=", r"\left(M^2 - 1\right)",
                          r"\frac{dV}{V}", font_size=58, color=C_CALCULO)
        formula.move_to(UP * 0.75)
        self.play(Write(formula), run_time=1.4)
        self.wait(3.6)

        rot.mostrar(pie_curso("Todo lo que va a pasar en este módulo está "
                              "aquí dentro."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: el parentesis manda ---------------------------------
        marco = SurroundingRectangle(formula[2], color=C_SUPER,
                                     stroke_width=2.6, buff=0.10)
        self.play(Create(marco), run_time=0.7)
        rot.mostrar(pie_curso("Y dentro de aquí, todo cuelga de un signo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        casos = VGroup(
            VGroup(Text("M < 1", font=FUENTE_HUD, font_size=24, color=C_SUB),
                   Text("el paréntesis es negativo", font_size=21,
                        color=C_SUB)).arrange(RIGHT, buff=0.40),
            VGroup(Text("M > 1", font=FUENTE_HUD, font_size=24,
                        color=C_SUPER),
                   Text("el paréntesis es positivo", font_size=21,
                        color=C_SUPER)).arrange(RIGHT, buff=0.40))
        casos.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        casos.move_to(DOWN * 1.55)

        for caso, pie in zip(casos, (
                "Por debajo de Mach 1, área y velocidad van al revés: "
                "estrechar acelera.",
                "Por encima, van a la par: estrechar frena.")):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(caso, shift=0.12 * UP), run_time=0.7)
            self.wait(4.6)

        rot.mostrar(pie_curso("Dos comportamientos opuestos, y el mismo tubo "
                              "los hace los dos."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
