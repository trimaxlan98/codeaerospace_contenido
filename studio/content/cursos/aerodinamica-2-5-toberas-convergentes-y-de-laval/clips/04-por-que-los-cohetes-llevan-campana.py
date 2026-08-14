class Clip4(Scene):
    """2.5.4 - Aplicacion a motores cohete y toberas de turbina.

    La relacion de areas de una tobera es una decision de altitud: campana
    corta para el nivel del mar, campana larga para el vacio. Es la razon de
    que la primera etapa y la segunda de un mismo lanzador no lleven la
    misma tobera. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Por qué los cohetes llevan campana")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        rot.mostrar(pie_curso("La relación de áreas no es un capricho de "
                              "diseño: es una decisión de altitud."),
                    zona="abajo", run_time=0.5)
        self.wait(1.2)

        # Dos toberas con relacion de areas distinta. Los Mach de salida los
        # invierte la libreria a partir de la geometria de cada una.
        casos = ((0.62, "primera etapa", C_TRANS, LEFT * 3.3),
                 (AREA_GARGANTA, "etapa superior", C_CALCULO, RIGHT * 3.3))
        grupos = VGroup()
        for garganta, nombre, color, sitio in casos:
            tubo = conducto("delaval", area_garganta=garganta, largo=3.6,
                            alto=1.9, color=C_TENUE)
            m_salida = mach_de_area(1.0 / garganta, "super")
            etiqueta = Text(nombre, font_size=21, color=color)
            cifras = VGroup(
                Text(f"Ae/At = {1 / garganta:.2f}", font=FUENTE_HUD,
                     font_size=17, color=color),
                Text(f"M salida = {m_salida:.2f}", font=FUENTE_HUD,
                     font_size=17, color=color)).arrange(DOWN, buff=0.12)
            grupo = VGroup(tubo, etiqueta, cifras)
            tubo.move_to(sitio + UP * 0.75)
            etiqueta.next_to(tubo, UP, buff=0.28)
            cifras.next_to(tubo, DOWN, buff=0.28)
            grupos.add(grupo)

        self.play(FadeIn(grupos[0], shift=0.12 * UP), run_time=0.9)
        rot.mostrar(pie_curso("Campana corta. Se abre poco, así que el aire "
                              "sale a bastante presión."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        self.play(FadeIn(grupos[1], shift=0.12 * UP), run_time=0.9)
        rot.mostrar(pie_curso("Campana larga. Expande mucho más y sale más "
                              "rápido, pero a muy poca presión."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Al nivel del mar, la larga estaría "
                              "sobreexpandida: la atmósfera le aplastaría el "
                              "chorro."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("En el vacío, la corta desperdiciaría "
                              "expansión que podría haber sido empuje."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Por eso un lanzador no lleva la misma tobera "
                              "abajo que arriba."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
