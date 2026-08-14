class Clip2(Scene):
    """1.4.2 - Hipotesis de flujo adiabatico, permanente y unidimensional.

    Las tres cuentas del clip anterior son exactas y por eso mismo
    inservibles: hay que podarlas. Las tres hipotesis del curso entran una a
    una sobre el conducto, y cada una se gana el derecho a estar. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Las tres hipótesis")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Gris CLARO y no el de mobiliario: el conducto no es un eje de
        # fondo, es el objeto del que habla el clip.
        tubo = conducto("delaval", area_garganta=AREA_GARGANTA, largo=6.4,
                        alto=2.3, color=C_TENUE)
        tubo.move_to(UP * 0.55)
        self.play(Create(tubo.paredes), FadeIn(tubo.eje), run_time=1.3)
        rot.mostrar(pie_curso("Este es el conducto de todo el módulo 2. "
                              "Antes hay que decidir qué se desprecia."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: las tres hipotesis, una a una -----------------------
        # Se colocan las tres de golpe (y ocultas) para que ninguna se mueva
        # cuando aparece la siguiente.
        etiquetas = VGroup(
            Text("permanente", font_size=24, color=C_SUB),
            Text("adiabático", font_size=24, color=C_TRANS),
            Text("unidimensional", font_size=24, color=C_CALCULO))
        etiquetas.arrange(RIGHT, buff=0.85).move_to(DOWN * 1.75)

        pies = ("Permanente: en cada punto del tubo las cosas no cambian con "
                "el tiempo.",
                "Adiabático: el aire pasa tan rápido que no da tiempo a que "
                "entre calor.",
                "Unidimensional: en cada sección, un solo valor de todo.")
        for etiqueta, pie in zip(etiquetas, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(etiqueta, shift=0.14 * UP), run_time=0.7)
            self.wait(4.4)

        # --- momento: lo que la tercera cuesta ----------------------------
        # La marca cae en la garganta usando el localizador del conducto: si
        # el tubo se mueve o cambia de perfil, la seccion sigue en su sitio.
        seccion = Line(tubo.punto_de(0.5, -1.0), tubo.punto_de(0.5, 1.0),
                       stroke_width=2.4, color=C_CALCULO)
        self.play(Create(seccion), run_time=0.6)
        rot.mostrar(pie_curso("Un solo Mach, una sola presión, una sola "
                              "temperatura por sección."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Es mentira cerca de la pared. Y aun así "
                              "acierta el empuje de un cohete."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)
