class Clip5(Scene):
    """2.5.5 - Difusores y el tunel de viento supersonico.

    Un tunel supersonico es una tobera seguida de su espejo. La primera
    acelera y la segunda tendria que frenar sin perdidas... salvo que en el
    arranque hay un choque paseandose por el circuito, y por eso la garganta
    de aguas abajo NO puede ser igual que la de aguas arriba. Cierre de la
    leccion y del modulo 2. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))

        titulo = titulo_curso("El túnel que va al revés")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        tobera = conducto("delaval", area_garganta=AREA_GARGANTA, largo=3.4,
                          alto=2.0, color=C_TENUE)
        tobera.move_to(LEFT * 2.6 + UP * 0.55)
        difusor = conducto("delaval", area_garganta=0.52, largo=3.4,
                           alto=2.0, color=C_TENUE)
        difusor.move_to(RIGHT * 2.6 + UP * 0.55)
        ensayo = DashedVMobject(
            Rectangle(width=1.4, height=1.5, stroke_width=1.8, color=C_CALCULO)
            .move_to(UP * 0.55), num_dashes=28)
        tag_ensayo = Text("modelo", font_size=18, color=C_CALCULO)
        tag_ensayo.next_to(ensayo, UP, buff=0.14)

        self.play(Create(tobera.paredes), FadeIn(tobera.eje), run_time=0.9)
        rot.mostrar(pie_curso("Un túnel supersónico es una tobera que "
                              "acelera el aire hasta el Mach de ensayo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        self.play(FadeIn(ensayo), FadeIn(tag_ensayo), run_time=0.6)
        self.play(Create(difusor.paredes), FadeIn(difusor.eje), run_time=0.9)
        rot.mostrar(pie_curso("Y detrás del modelo, la misma tobera del "
                              "revés: un difusor que lo vuelve a frenar."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Frenar así, sin choques, apenas cuesta "
                              "energía. En el papel."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- momento: el arranque -------------------------------------------
        choque = Line(difusor.punto_de(0.30, -1.0),
                      difusor.punto_de(0.30, 1.0), stroke_width=3.4,
                      color=C_SUPER)
        tag_choque = Text("choque de arranque", font_size=18, color=C_SUPER)
        tag_choque.next_to(difusor, DOWN, buff=0.30)
        self.play(Create(choque), FadeIn(tag_choque), run_time=0.8)
        rot.mostrar(pie_curso("En el papel. Al arrancar, un choque recorre "
                              "el circuito y hay que dejarlo pasar."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Y un choque se lleva presión de "
                              "estancamiento, así que detrás hace falta más "
                              "área para el mismo gasto."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Por eso la segunda garganta nunca es igual "
                              "que la primera. Es más ancha."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- cierre de la leccion y del modulo ------------------------------
        self.play(FadeOut(VGroup(tobera, difusor, ensayo, tag_ensayo, choque,
                                 tag_choque)), run_time=0.8)
        cierre = VGroup(
            titulo_marca("Ya sabes romper el aire de frente.", font_size=35,
                         color=C_TITULO),
            titulo_marca("Ahora, de lado.", font_size=35,
                         color=C_SUPER)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)
