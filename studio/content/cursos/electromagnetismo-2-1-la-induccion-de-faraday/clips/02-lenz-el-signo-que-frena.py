class Clip2(Scene):
    """2.1.2 - Lenz: la corriente inducida crea su PROPIO campo, y ese
    campo se opone al cambio que lo creo. Al meter el iman, la bobina lo
    repele; al sacarlo, lo retiene. El signo menos de la formula es
    conservacion de la energia. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Lenz: el signo que frena")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: retomamos el experimento ------------------------------
        eim = espira_iman()
        self.play(FadeIn(eim), run_time=0.7)
        rot.mostrar(pie_curso("La aguja se movió. Pero esa corriente "
                              "también crea su propio campo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: al entrar, la bobina repele -----------------------------
        rot.mostrar(pie_curso("Al meter el imán, ese campo lo EMPUJA "
                              "hacia afuera: la bobina lo repele."),
                    zona="abajo", run_time=0.5)
        aguja_1 = eim.aguja_a(0.85)
        self.play(eim.iman.animate.move_to(ORIGIN),
                  ReplacementTransform(eim.aguja, aguja_1), run_time=1.8)
        eim.aguja = aguja_1
        self.wait(4.4)

        # --- momento: al salir, la bobina retiene ------------------------------
        rot.mostrar(pie_curso("Al sacarlo, pasa lo contrario: la bobina "
                              "lo RETIENE, no quiere que se vaya."),
                    zona="abajo", run_time=0.5)
        aguja_2 = eim.aguja_a(-0.85)
        self.play(eim.iman.animate.move_to(LEFT * 2.6),
                  ReplacementTransform(eim.aguja, aguja_2), run_time=1.8)
        eim.aguja = aguja_2
        self.wait(4.4)

        rot.mostrar(pie_curso("Siempre en CONTRA del cambio. Así frena "
                              "de verdad el imán que cae por un tubo de "
                              "cobre."), zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- momento: la formula con el signo recuadrado ------------------------
        self.play(FadeOut(eim), run_time=0.6)
        formula = MathTex(r"\mathcal{E}", r"=", r"-", r"\frac{d\Phi}{dt}",
                          font_size=40, color=C_CALCULO)
        if formula.width > config.frame_width - 3.0:
            formula.scale_to_fit_width(config.frame_width - 3.0)
        formula.move_to(ORIGIN)
        rot.mostrar(pie_curso("Esa oposición vive en un solo signo: el "
                              "menos de la ley de Faraday-Lenz."),
                    zona="abajo", run_time=0.5)
        self.play(Write(formula), run_time=1.2)
        self.wait(3.2)

        recuadro = SurroundingRectangle(formula[2], color=C_ACENTO_2,
                                        stroke_width=3.0, buff=0.09)
        rot.mostrar(pie_curso("Ese signo menos es CONSERVACIÓN DE LA "
                              "ENERGÍA: si ayudara en vez de frenar, "
                              "sería energía gratis."), zona="abajo",
                    run_time=0.5)
        self.play(Create(recuadro), run_time=0.8)
        self.wait(4.8)
