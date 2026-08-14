class Clip1(Scene):
    """3.2.1 - Lectura e interpretacion del diagrama theta-beta-M.

    Un diagrama que se lee al reves de como se dedujo: la formula da theta a
    partir de beta, pero el ingeniero conoce la rampa y quiere la onda. El
    grafico resuelve esa inversion de un vistazo. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El mapa del choque oblicuo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        mapa = diagrama_theta_beta(machs=MACHS_DIAGRAMA, ancho=5.4, alto=2.9)
        mapa.move_to(LEFT * 0.25 + DOWN * 0.35)
        self.play(FadeIn(mapa.ejes), run_time=0.7)
        rot.mostrar(pie_curso("La fórmula da la deflexión a partir del "
                              "ángulo de onda. Pero tú conoces la rampa."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        self.play(LaggedStart(*[Create(mapa.curva(i))
                                for i in range(len(MACHS_DIAGRAMA))],
                              lag_ratio=0.3), run_time=2.2)
        self.play(FadeIn(mapa.etiquetas), run_time=0.6)
        rot.mostrar(pie_curso("Una curva por Mach. Entras por abajo con tu "
                              "deflexión y subes hasta cortarla."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: leer el diagrama -------------------------------------
        # El punto y la cifra salen de choque_oblicuo, no del trazo: si la
        # curva estuviese mal dibujada, el punto NO caeria encima.
        i = list(MACHS_DIAGRAMA).index(M_EJEMPLO)
        punto = Dot(mapa.punto_de(i, THETA_EJEMPLO), radius=0.075,
                    color=C_SUPER)
        guia = DashedLine(mapa._en(THETA_EJEMPLO, 0.0), punto.get_center(),
                          stroke_width=1.4, color=C_TENUE, dash_length=0.07)
        # Fuera de la caja, a la altura del punto: pegada a el cruza la
        # curva de Mach 1.5, que a esa deflexion pasa justo por ahi.
        cifra = MathTex(rf"\beta = {DEBIL['beta']:.1f}^\circ", font_size=30,
                        color=C_SUPER)
        cifra.move_to([mapa.ejes[1].get_left()[0] - 1.05,
                       punto.get_center()[1], 0])

        self.play(Create(guia), run_time=0.6)
        self.play(FadeIn(punto, scale=1.6), FadeIn(cifra), run_time=0.6)
        rot.mostrar(pie_curso(f"Mach {M_EJEMPLO:g}, rampa de "
                              f"{THETA_EJEMPLO:g} grados: la onda sale a "
                              f"{DEBIL['beta']:.1f}."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Sin resolver nada. Ese es el trabajo que hace "
                              "un diagrama."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Fíjate en que las curvas están cerradas por "
                              "arriba. Eso significa algo."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
