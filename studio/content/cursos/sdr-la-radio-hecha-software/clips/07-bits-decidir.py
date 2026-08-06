class Clip7(Scene):
    """7 - Bits en el aire: decidir. Una constelacion BPSK limpia se vuelve
    ruidosa: los puntos que cruzan la frontera son bits que mueren. La
    curva del acantilado muestra por que un par de decibelios cambian
    todo el enlace. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ------------------------------------------------
        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Bits en el aire: decidir")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(1.2)

        # --- momento: la constelacion limpia, dos nubes enfrentadas -------
        plano = plano_iq(radio=1.55)
        plano.move_to(np.array([-2.9, -0.1, 0.0]))
        limpia = constelacion_bpsk(plano, ruido=0.05)
        tag_uno = tag_junto(limpia.nube_uno, "1", direccion=UP, buff=0.18,
                            color=C_I)
        tag_cero = tag_junto(limpia.nube_cero, "0", direccion=UP, buff=0.18,
                             color=C_Q)

        self.play(FadeIn(plano), run_time=0.6)
        self.play(FadeIn(limpia), FadeIn(tag_uno), FadeIn(tag_cero),
                  run_time=0.7)
        rot.mostrar(pie_curso("Digital no es reproducir una onda: es "
                              "decidir. ¿Cero o uno?"), zona="abajo",
                    run_time=0.5)
        self.wait(5.3)

        # --- momento: la frontera de decision ------------------------------
        frontera = DashedLine(plano.punto(PI / 2, 1.15),
                              plano.punto(-PI / 2, 1.15),
                              stroke_width=2.6, color=C_ACENTO)
        frontera.set_stroke(opacity=0.6)
        self.play(Create(frontera), run_time=0.7)
        rot.mostrar(pie_curso("Dos puntos enfrentados — BPSK — y una "
                              "frontera en medio."), zona="abajo",
                    run_time=0.5)
        self.wait(5.4)

        # --- momento: el ruido vuelve nubes los puntos ---------------------
        ruidosa = constelacion_bpsk(plano, ruido=0.28, semilla=3)
        self.play(ReplacementTransform(limpia, ruidosa), run_time=1.0)
        self.play(*[Indicate(d, color=C_RUIDO, scale_factor=1.6)
                    for d in ruidosa.errados], run_time=0.8)
        for d in ruidosa.errados:
            d.set_color(C_RUIDO)
        rot.mostrar(pie_curso("El ruido vuelve nubes los puntos. Cuando "
                              "una muestra cruza la frontera, ese bit "
                              "muere."), zona="abajo", run_time=0.5)
        self.wait(5.4)

        # --- momento: el efecto acantilado -----------------------------------
        curva = curva_acantilado(ancho=3.2, alto=2.2)
        curva.move_to(np.array([3.1, -0.1, 0.0]))
        self.play(Create(curva), run_time=0.9)

        vt_x = ValueTracker(0.9)
        punto = punto_brillante(curva.punto_en(vt_x.get_value()),
                                color=C_SENAL, radio=0.075)
        punto.add_updater(lambda m: m.move_to(curva.punto_en(vt_x.get_value())))
        self.play(FadeIn(punto), run_time=0.3)

        rot.mostrar(pie_curso("Sobre el umbral, casi perfecto. Debajo, "
                              "colapso: el efecto acantilado."),
                    zona="abajo", run_time=0.5)
        self.play(vt_x.animate.set_value(0.25), run_time=2.5)
        self.wait(2.6)
        punto.clear_updaters()

        # --- momento: cierre ------------------------------------------------
        rot.mostrar(pie_curso("Por eso el operador pelea por dos "
                              "decibelios más, no por un waterfall "
                              "bonito."), zona="abajo", run_time=0.5)
        self.wait(5.6)
