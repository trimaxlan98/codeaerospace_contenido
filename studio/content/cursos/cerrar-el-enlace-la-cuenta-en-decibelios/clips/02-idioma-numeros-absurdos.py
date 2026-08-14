class Clip2(Scene):
    """2 - Un idioma para numeros absurdos. La regla de decibelios con tres
    pares resaltados (x2/+3, x10/+10, x1000000/+60) y, al final, la cifra
    imposible del clip 1 convertida en un numero de cuatro cifras. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Un idioma para números absurdos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        rot.mostrar(pie_curso("Cada vez que la señal se divide o se "
                              "multiplica, la cuenta se vuelve "
                              "impronunciable."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: la regla, dos escalas sobre un mismo eje ------------
        regla = regla_db(ancho=6.6, alto=0.95)
        regla.move_to(UP * 0.55)
        self.play(FadeIn(regla, shift=0.15 * UP), run_time=1.1)
        self.wait(0.7)

        rot.mostrar(pie_curso("El decibelio cambia multiplicar por sumar."),
                    zona="abajo", run_time=0.5)
        self.wait(2.0)

        # Los tres pares que cuentan la historia: doblar, un orden de
        # magnitud, y un millon. El indice es el del escalon en la regla.
        for i in (1, 2, 5):
            self.play(Indicate(regla.par(i), color=C_MARGEN,
                               scale_factor=1.22), run_time=1.0)
            self.wait(0.7)
        self.wait(2.4)

        # --- momento: la cifra imposible se vuelve manejable --------------
        rot.mostrar(pie_curso("Aquel número de once ceros cabe ahora en "
                              "cuatro cifras."), zona="abajo", run_time=0.5)

        antes = MathTex(r"4.3 \times 10^{-12}\ \text{W}", font_size=40,
                        color=C_SENAL)
        antes.move_to(DOWN * 1.35)
        self.play(FadeIn(antes, shift=0.16 * UP), run_time=0.8)
        self.wait(3.4)

        # El valor sale del style_block: es exactamente la potencia que el
        # clip 1 mostro en vatios, ahora dicha en el idioma del curso.
        despues = MathTex(rf"{C_RX_DBW:.1f}\ \text{{dBW}}", font_size=46,
                          color=C_MARGEN)
        despues.move_to(antes.get_center())
        self.play(Transform(antes, despues), run_time=1.1)
        self.wait(4.6)

        rot.mostrar(pie_curso("Con este idioma, el enlace entero cabe en una "
                              "sola fila de sumas."), zona="abajo",
                    run_time=0.5)
        self.wait(5.4)
