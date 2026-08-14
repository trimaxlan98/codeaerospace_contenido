class Clip4(Scene):
    """4.4.4 - Winglets, carenados y consideraciones de crucero transonico.

    Las tres soluciones anteriores no se eligen: se suman, y cada una cuesta
    algo. Un avion de linea es el punto donde esas cuentas se equilibran, y
    por eso todos acaban pareciendose. Cierre de la leccion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Lo que se negocia en crucero")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Tres columnas: lo que gana cada solucion y lo que cuesta.
        soluciones = (("flecha", f"M⊥ {M_NORMAL:.2f}", "más peso, peor a baja "
                       "velocidad", C_SUB),
                      ("supercrítico", f"+{GANANCIA_WHITCOMB:.2f} de Mach",
                       "momento de picado, más carga", C_CALCULO),
                      ("regla del área", "menos arrastre de onda",
                       "fuselaje incómodo de fabricar", C_TRANS))
        columnas = VGroup()
        for nombre, gana, cuesta, color in soluciones:
            texto_cuesta = Text(cuesta, font_size=16, color=C_TENUE)
            if texto_cuesta.width > 3.1:
                texto_cuesta.scale_to_fit_width(3.1)
            columna = VGroup(
                Text(nombre, font_size=22, color=color),
                Text(gana, font=FUENTE_HUD, font_size=18, color=color),
                texto_cuesta).arrange(DOWN, buff=0.22)
            columnas.add(columna)
        columnas.arrange(RIGHT, buff=0.75).move_to(UP * 0.75)

        pies = ("La flecha es barata y se paga en peso y en velocidad de "
                "aproximación.",
                "El supercrítico regala Mach y se paga en momento de "
                "picado.",
                "Y la regla del área se paga en un fuselaje que nadie "
                "quiere fabricar.")
        for columna, pie in zip(columnas, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(columna, shift=0.12 * UP), run_time=0.8)
            self.wait(4.6)

        rot.mostrar(pie_curso("No se elige una. Se usan las tres, y se "
                              "negocia cuánto de cada una."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Por eso todos los aviones de línea acaban "
                              "pareciéndose tanto: resuelven el mismo "
                              "problema."), zona="abajo", run_time=0.5)
        self.wait(5.4)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(columnas), run_time=0.8)
        cierre = VGroup(
            titulo_marca("El transónico no se resuelve.", font_size=36,
                         color=C_TITULO),
            titulo_marca("Se negocia.", font_size=36,
                         color=C_TRANS)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)
