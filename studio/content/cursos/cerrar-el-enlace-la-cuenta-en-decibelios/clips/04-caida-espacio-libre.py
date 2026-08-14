class Clip4(Scene):
    """4 - La caida del espacio libre. Primero el frente esferico que crece y
    diluye la misma energia; despues la curva de FSPL con tres bandas y el
    punto del enlace del curso rotulado con su valor real. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La caída del espacio libre")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        # --- momento: la misma energia en una esfera que crece ------------
        frente = frente_esferico(radios=(0.55, 1.15, 1.75, 2.35),
                                 color=C_SENAL, puntos=40)
        frente.move_to(LEFT * 1.1 + DOWN * 0.15)
        emisor = Dot(frente.origen(), radius=0.06, color=C_SENAL)

        self.play(FadeIn(emisor), run_time=0.4)
        self.play(LaggedStart(*[Create(frente.anillo(i)) for i in range(4)],
                              lag_ratio=0.45), run_time=2.6)

        rot.mostrar(pie_curso("Nada se pierde en el vacío: la misma energía "
                              "se reparte en una esfera que no para de "
                              "crecer."), zona="abajo", run_time=0.5)
        self.wait(5.4)

        # El receptor se cuelga del anillo exterior con el localizador, no a
        # ojo: si el frente se mueve, el cuadrito lo sigue.
        receptor = Square(side_length=0.26, stroke_width=2.4, color=C_MARGEN)
        receptor.move_to(frente.en(3, 18.0))
        self.play(FadeIn(receptor, scale=1.4), run_time=0.6)

        rot.mostrar(pie_curso("Tu antena solo recoge el trocito de esfera "
                              "que alcanza a tapar."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        # --- momento: cuanto cuesta, en numeros ---------------------------
        self.play(FadeOut(VGroup(frente, emisor, receptor)), run_time=0.7)

        curva = curva_fspl(f_ghz=(2.0, 12.0, 30.0), ancho=6.0, alto=2.6)
        curva.move_to(LEFT * 0.35 + DOWN * 0.15)
        self.play(FadeIn(curva.ejes), run_time=0.6)
        self.play(LaggedStart(*[Create(c) for c in curva.curvas],
                              lag_ratio=0.35), run_time=2.0)
        self.play(FadeIn(curva.etiquetas), run_time=0.6)
        self.wait(1.4)

        rot.mostrar(formula_pie(r"\text{FSPL} = 20\log_{10} d + "
                                r"20\log_{10} f + 92.45"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- momento: el punto de ESTE enlace -----------------------------
        # El rotulo lo calcula la libreria: la curva dibujada y el numero
        # escrito no pueden discrepar.
        punto = Dot(curva.punto_de(D_KM, F_GHZ), radius=0.07, color=C_MARGEN)
        # El rotulo baja al hueco libre bajo las tres curvas y se ata al punto
        # con una guia vertical: en el codo derecho del grafico las curvas y
        # sus etiquetas de banda dejan menos de un renglon de aire, y
        # cualquier posicion pegada al punto se encima con alguna de ellas.
        etiqueta = Text(f"{curva.db(D_KM, F_GHZ):.0f} dB", font=FUENTE_HUD,
                        font_size=20, color=C_MARGEN)
        etiqueta.move_to([punto.get_center()[0],
                          curva.ejes[0].get_center()[1] + 0.42, 0])
        guia = DashedLine(punto.get_center() + DOWN * 0.10,
                          etiqueta.get_top() + UP * 0.06, stroke_width=1.3,
                          color=C_EJE, dash_length=0.07)

        self.play(FadeIn(punto, scale=1.6), run_time=0.5)
        self.play(Create(guia), FadeIn(etiqueta, shift=0.1 * UP),
                  run_time=0.6)

        rot.mostrar(pie_curso("Doscientos cinco decibelios: el término que "
                              "manda en toda la cuenta."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Doblar la distancia cuesta seis decibelios. "
                              "Doblar la frecuencia, otros seis."),
                    zona="abajo", run_time=0.5)
        self.wait(5.6)
