class Clip3(Scene):
    """1.5.3 - Condiciones criticas (M = 1): T*, p*, rho*, a*.

    Un corte vertical en M = 1 sobre las mismas curvas del clip anterior.
    Los tres numeros que salen no dependen del avion, ni de la altitud, ni
    de la tobera: solo de gamma. Por eso sirven de referencia universal, y
    por eso el modulo 2 se escribe entero con asteriscos. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Justo en Mach 1")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        curvas = curvas_isentropicas(m_max=3.0, ancho=5.4, alto=2.7)
        curvas.move_to(DOWN * 0.35)
        self.play(FadeIn(curvas.ejes), run_time=0.5)
        self.play(*[Create(c) for c in curvas.curvas], run_time=1.4)
        self.play(FadeIn(curvas.etiquetas), run_time=0.5)

        rot.mostrar(pie_curso("Las mismas tres curvas. Ahora córtalas por "
                              "Mach 1."), zona="abajo", run_time=0.5)
        self.wait(1.2)

        # La vertical la construye la pieza: las coordenadas de la caja son
        # suyas, y asi el corte cae exactamente en M = 1 aunque el grafico se
        # haya movido.
        corte = curvas.vertical_en(1.0, color=C_TENUE)
        self.play(Create(corte), run_time=0.7)
        self.wait(3.2)

        # --- momento: los tres numeros ------------------------------------
        # Cada cifra sale de la curva que la dibuja; el orden vertical de las
        # etiquetas es el de los propios valores, asi que no pueden cruzarse.
        # Las cifras van FUERA de la caja de ejes, a la izquierda, cada una
        # a la altura exacta de su punto. Pegadas al punto se encimaban con
        # las propias curvas: en Mach 1 las tres estan en plena caida y no
        # hay hueco limpio a ningun lado dentro del grafico. A la misma
        # altura y del mismo color, la lectura sigue siendo inequivoca sin
        # necesidad de guias (que tambien cruzarian curvas).
        x_cifras = curvas.ejes[1].get_left()[0] - 0.58
        marcas = VGroup()
        for i in range(3):
            punto = Dot(curvas.punto_de(i, 1.0), radius=0.07,
                        color=curvas.color_de(i))
            cifra = Text(f"{curvas.valor(i, 1.0):.4f}", font=FUENTE_HUD,
                         font_size=18, color=curvas.color_de(i))
            cifra.move_to([x_cifras, punto.get_center()[1], 0])
            marcas.add(VGroup(punto, cifra))

        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in marcas],
                              lag_ratio=0.4), run_time=1.4)
        rot.mostrar(pie_curso("Cero coma ochenta y tres, cero coma sesenta y "
                              "tres, cero coma cincuenta y tres."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Estos tres números no dependen del avión, ni "
                              "de la altitud. Solo de gamma."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: el asterisco ----------------------------------------
        rot.mostrar(formula_pie(rf"\frac{{T^*}}{{T_0}} = \frac{{2}}"
                                rf"{{\gamma+1}} = "
                                rf"{CRITICAS['T*/T0']:.4f}"
                                rf"\qquad \frac{{a^*}}{{a_0}} = "
                                rf"{CRITICAS['a*/a0']:.4f}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Se llaman condiciones críticas y se marcan con "
                              "un asterisco."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("En la garganta de una tobera bloqueada, el "
                              "aire está exactamente ahí."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)
