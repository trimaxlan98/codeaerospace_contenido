class Clip4(Scene):
    """1.4.4 - Concepto de volumen de control aplicado a un conducto.

    Se juntan las dos piezas del modulo: la caja del clip 1 se pega al
    conducto del clip 2 y sale la continuidad en la forma con la que se
    trabaja el resto del curso. Cierre de la leccion y del modulo 1.
    (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La caja, sobre el conducto")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        tubo = conducto("delaval", area_garganta=AREA_GARGANTA, largo=6.6,
                        alto=2.4, color=C_TENUE)
        tubo.move_to(UP * 0.45)
        self.play(Create(tubo.paredes), FadeIn(tubo.eje), run_time=1.2)

        # --- momento: las dos secciones ------------------------------------
        # Ambas cuelgan del localizador del conducto: la altura de cada corte
        # es la del area en esa estacion, no un numero copiado a mano.
        # Los tres rotulos (1, 2 y garganta) comparten linea base, por
        # debajo del punto MAS BAJO del conducto: colgados de su propia
        # seccion, el de la garganta caeria dentro del tubo, encima de la
        # pared, porque justo ahi el conducto es estrecho.
        y_tags = tubo.punto_de(0.0, -1.0)[1] - 0.34

        estaciones = VGroup()
        for x, nombre, color in ((0.10, "1", C_SUB), (0.90, "2", C_TRANS)):
            corte = Line(tubo.punto_de(x, -1.0), tubo.punto_de(x, 1.0),
                         stroke_width=2.6, color=color)
            tag = Text(nombre, font=FUENTE_HUD, font_size=20, color=color)
            tag.move_to([corte.get_center()[0], y_tags, 0])
            estaciones.add(VGroup(corte, tag))

        self.play(LaggedStart(*[Create(e[0]) for e in estaciones],
                              lag_ratio=0.4), run_time=1.0)
        self.play(FadeIn(VGroup(*[e[1] for e in estaciones])), run_time=0.5)
        rot.mostrar(pie_curso("Dos secciones. El trozo de tubo entre ellas "
                              "es el volumen de control."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: la continuidad --------------------------------------
        rot.mostrar(formula_pie(r"\rho_1 A_1 V_1 = \rho_2 A_2 V_2 = \dot m"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Por las dos secciones pasa el mismo gasto. "
                              "Aunque el área no se parezca en nada."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: la garganta ------------------------------------------
        garganta = Line(tubo.punto_de(0.5, -1.0), tubo.punto_de(0.5, 1.0),
                        stroke_width=2.6, color=C_SUPER)
        tag_g = Text("garganta", font_size=20, color=C_SUPER)
        tag_g.move_to([garganta.get_center()[0], y_tags, 0])
        self.play(Create(garganta), FadeIn(tag_g), run_time=0.8)
        rot.mostrar(pie_curso("Y si el gasto es fijo, apretar el área obliga "
                              "a algo a cambiar."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Qué cambia exactamente, y por qué depende del "
                              "régimen, es el módulo 2."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- cierre de la leccion y del modulo ------------------------------
        self.play(FadeOut(VGroup(tubo, estaciones, garganta, tag_g)),
                  run_time=0.8)
        cierre = VGroup(
            titulo_marca("Ya tienes el idioma.", font_size=38,
                         color=C_TITULO),
            titulo_marca("Ahora toca romper el aire.", font_size=38,
                         color=C_SUPER)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)
