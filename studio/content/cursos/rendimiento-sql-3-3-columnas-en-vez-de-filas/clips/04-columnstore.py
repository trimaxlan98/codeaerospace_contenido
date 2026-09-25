class Clip4(Scene):
    """3.3.4 - El almacen por columnas tambien cuenta las lecturas distinto:
    16,468 contra 6,512 con un solo hilo (escala LINEAL: las dos cifras son
    comparables). Con 8 hilos el motor cuenta de otra forma. Cierre de la
    leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Leer menos columnas"), zona="arriba",
                    run_time=0.6)
        self.wait(1.0)

        largo, alto = 7.2, 0.62
        maximo = CS_FILAS
        base_x = LEFT * 3.9
        bar_top = S.barra_lecturas(CS_FILAS, maximo, largo=largo, alto=alto,
                                   color=C_MALO, log=False)
        bar_top.shift(base_x + UP * 0.9)
        bar_bot = S.barra_lecturas(CS_1HILO, maximo, largo=largo, alto=alto,
                                   color=C_BUENO, log=False)
        bar_bot.shift(base_x + DOWN * 0.9)

        base = Line(base_x + UP * 1.7, base_x + DOWN * 1.7,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        self.wait(0.8)

        lab_top = tag_junto(bar_top, "por filas", LEFT, buff=0.3)
        self.play(GrowFromEdge(bar_top, LEFT), FadeIn(lab_top), run_time=0.9)
        tag_top = tag_motor(lecturas(CS_FILAS))
        tag_top.next_to(bar_top, RIGHT, buff=0.2)
        self.play(FadeIn(tag_top), run_time=0.4)
        self.wait(1.8)

        lab_bot = tag_junto(bar_bot, "por columnas", LEFT, buff=0.3)
        self.play(GrowFromEdge(bar_bot, LEFT), FadeIn(lab_bot), run_time=0.9)
        tag_bot = tag_motor(lecturas(CS_1HILO))
        tag_bot.next_to(bar_bot, RIGHT, buff=0.2)
        self.play(FadeIn(tag_bot), run_time=0.4)
        self.wait(1.4)

        et_hilo = tag_junto(tag_bot, "un hilo", DOWN, buff=0.24, color=C_MOTOR)
        self.play(FadeIn(et_hilo), run_time=0.4)
        self.wait(2.0)

        et_8h = tag_junto(et_hilo, "8 hilos cuentan distinto", DOWN, buff=0.32,
                          color=C_DATO)
        self.play(FadeIn(et_8h), run_time=0.5)
        self.wait(3.0)

        rot.mostrar(cifra_pie(f"{RAZON_CS:.1f}x menos lecturas"), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(bar_top, color=C_MOTOR, scale_factor=1.02),
                  Indicate(bar_bot, color=C_MOTOR, scale_factor=1.05),
                  run_time=1.0)
        self.wait(4.6)

        cierre_leccion(self, rot, "Para sumar millones:",
                       "guarda columnas, no filas.",
                       base, bar_top, bar_bot, lab_top, lab_bot, tag_top,
                       tag_bot, et_hilo, et_8h, espera=6.0)
