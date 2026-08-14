class Clip7(Scene):
    """7 - El techo de Shannon. La curva limite con su region prohibida, tres
    MODCOD reales posados debajo y, a la izquierda, la constelacion que crece
    de QPSK a 16APSK. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))

        titulo = titulo_curso("El techo de Shannon")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la curva y lo que hay encima ------------------------
        sh = curva_shannon(snr_db=(-2.0, 20.0), ancho=4.8, alto=2.5)
        sh.move_to(RIGHT * 1.9 + DOWN * 0.15)

        self.play(FadeIn(sh.ejes), run_time=0.6)
        self.play(Create(sh.curva), run_time=1.6)
        self.wait(0.8)

        rot.mostrar(pie_curso("Ninguna antena, ningún código, ningún truco "
                              "pasa de esta curva."), zona="abajo",
                    run_time=0.5)
        self.play(sh.revelar_prohibida(), run_time=1.0)
        self.wait(4.8)

        rot.mostrar(formula_pie(r"C = B\log_2(1 + \text{SNR})"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: mas simbolos, mas bits ------------------------------
        rot.mostrar(pie_curso("Más símbolos caben más bits, pero se estorban "
                              "entre ellos."), zona="abajo", run_time=0.5)

        nube = nube_simbolos(orden=4, dispersion=0.045, escala=0.95)
        nube.move_to(LEFT * 3.6 + UP * 0.35)
        # buff generoso: la nube es redonda y sus puntos bajos llegan mas
        # abajo que el borde nominal del grupo.
        tag = tag_junto(nube, "QPSK", DOWN, buff=0.42, font_size=18,
                        color=C_SENAL)
        self.play(FadeIn(nube, scale=1.1), FadeIn(tag), run_time=0.9)
        self.wait(2.6)

        for orden, nombre in ((8, "8PSK"), (16, "16APSK")):
            nueva = nube.con_orden(orden)
            nuevo_tag = tag_junto(nueva, nombre, DOWN, buff=0.42,
                                  font_size=18, color=C_SENAL)
            self.play(Transform(nube, nueva), Transform(tag, nuevo_tag),
                      run_time=1.0)
            self.wait(2.0)

        # --- momento: donde viven los estandares reales -------------------
        # Cada MODCOD se posa en SUS coordenadas (SNR requerido, eficiencia),
        # tomadas de la tabla del style_block: la distancia al techo que se
        # ve es la distancia real.
        marcas = VGroup()
        for etiqueta, snr, bph in (MODCODS[0], MODCODS[2], MODCODS[3]):
            punto = Dot(sh.punto_modcod(snr, bph), radius=0.06,
                        color=C_SENAL)
            marcas.add(punto)

        rot.mostrar(pie_curso("Los estándares modernos operan a menos de un "
                              "decibelio del límite."), zona="abajo",
                    run_time=0.5)
        self.play(LaggedStart(*[FadeIn(m, scale=1.5) for m in marcas],
                              lag_ratio=0.4), run_time=1.4)
        self.wait(5.4)
