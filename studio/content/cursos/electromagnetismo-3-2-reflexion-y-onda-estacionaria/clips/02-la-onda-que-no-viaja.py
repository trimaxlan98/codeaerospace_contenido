class Clip2(Scene):
    """3.2.2 - La onda que no viaja. La incidente y la reflejada ocupan la
    misma linea: la suma hierve, pero la envolvente se queda clavada. Su
    razon maximo/minimo es el SWR que mide el instalador. (~37 s)"""

    POS = LEFT * 1.5 + DOWN * 0.35
    ANCHO = 7.0
    ALTO = 2.8

    def _onda(self, gamma, fase=0.0):
        """La onda total en su sitio, con la envolvente propia apagada
        (la envolvente se enciende aparte, cuando el guion la pide)."""
        o = onda_estacionaria(gamma=gamma, fase=fase, ancho=self.ANCHO,
                              alto=self.ALTO)
        o.envolventes.set_stroke(opacity=0.0)
        o.move_to(self.POS)
        return o

    def _envolvente(self, gamma):
        e = onda_estacionaria(gamma=gamma, ancho=self.ANCHO,
                              alto=self.ALTO).envolventes.copy()
        e.set_stroke(opacity=1.0)
        e.move_to(self.POS)
        return e

    def _fase(self, oes, fase, run_time=0.95):
        """Un instante mas tarde: la onda hierve, el marco no se mueve."""
        nueva = oes.con_fase(fase)
        nueva.envolventes.set_stroke(opacity=0.0)
        self.play(ReplacementTransform(oes, nueva), run_time=run_time)
        return nueva

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La onda que no viaja")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: incidente + reflejada en la misma linea --------------
        oes = self._onda(GAMMA_SALTO)
        env = self._envolvente(GAMMA_SALTO)
        rot.mostrar(pie_curso("La que va y la que vuelve comparten cable. "
                              "Lo que se ve es la SUMA."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(oes.ejes), Create(oes.onda), Create(env),
                  run_time=1.1)
        self.wait(4.4)

        # --- momento: el hervor --------------------------------------------
        rot.mostrar(pie_curso("Corre el tiempo. La onda de dentro hierve "
                              "arriba y abajo, pero no avanza."),
                    zona="abajo", run_time=0.5)
        for f in (1.1, 2.2, 3.3):
            oes = self._fase(oes, f)
        self.wait(1.8)

        rot.mostrar(pie_curso("Los bordes cian no se han movido ni un "
                              "pelo. Eso ES la onda estacionaria."),
                    zona="abajo", run_time=0.5)
        oes = self._fase(oes, 4.4)
        self.wait(3.7)

        # --- momento: como seria con la linea adaptada ---------------------
        oes_plana = self._onda(GAMMA_ADAPTADO)
        env_plana = self._envolvente(GAMMA_ADAPTADO)
        swr_plano = tag_hud(f"SWR = {swr_de(GAMMA_ADAPTADO):.2f}",
                            font_size=26)
        swr_plano.move_to(np.array([4.6, 0.55, 0.0]))
        rot.mostrar(pie_curso("Con la carga adaptada la envolvente se "
                              "aplana: ni un bulto, y el SWR vale uno."),
                    zona="abajo", run_time=0.5)
        self.play(ReplacementTransform(oes, oes_plana),
                  ReplacementTransform(env, env_plana),
                  FadeIn(swr_plano), run_time=1.1)
        oes, env = oes_plana, env_plana
        self.wait(4.4)

        # --- momento: vuelve el 75, y con el maximo y minimo ---------------
        oes = self._onda(GAMMA_SALTO)
        env_real = self._envolvente(GAMMA_SALTO)
        # Los dos localizadores de la pieza; las lineas guia son mobiliario
        # puesto a la ALTURA que ellos devuelven, nunca a ojo.
        p_max = oes.punto_maximo()
        p_min = oes.punto_minimo()
        x_ini = self.POS[0] - self.ANCHO / 2
        x_fin = self.POS[0] + self.ANCHO / 2 + 0.1
        nivel_max = DashedLine(np.array([x_ini, p_max[1], 0.0]),
                               np.array([x_fin, p_max[1], 0.0]),
                               color=C_EJE, stroke_width=1.8,
                               dash_length=0.10)
        nivel_min = DashedLine(np.array([x_ini, p_min[1], 0.0]),
                               np.array([x_fin, p_min[1], 0.0]),
                               color=C_EJE, stroke_width=1.8,
                               dash_length=0.10)
        d_max = Dot(p_max, radius=0.065, color=C_CALCULO)
        d_min = Dot(p_min, radius=0.065, color=C_CALCULO)
        t_max = tag_hud("max", font_size=17)
        t_max.move_to(np.array([x_fin + 0.18, p_max[1], 0.0]),
                      aligned_edge=LEFT)
        t_min = tag_hud("min", font_size=17)
        t_min.move_to(np.array([x_fin + 0.18, p_min[1], 0.0]),
                      aligned_edge=LEFT)
        marcas = VGroup(nivel_max, nivel_min, d_max, d_min, t_max, t_min)

        rot.mostrar(pie_curso("Vuelve el 75 y vuelven los bultos: aquí "
                              "siempre llega al tope, aquí nunca sube."),
                    zona="abajo", run_time=0.5)
        self.play(ReplacementTransform(oes_plana, oes),
                  ReplacementTransform(env, env_real),
                  FadeOut(swr_plano), run_time=1.0)
        env = env_real
        self.play(Create(nivel_max), Create(nivel_min), FadeIn(d_max),
                  FadeIn(d_min), FadeIn(t_max), FadeIn(t_min),
                  run_time=0.8)
        self.wait(4.4)

        # --- momento: el SWR ------------------------------------------------
        swr = MathTex(r"\mathrm{SWR} = \frac{V_{max}}{V_{min}}"
                      rf" = {SWR_SALTO:.2f}", font_size=32,
                      color=C_CALCULO)
        swr.move_to(np.array([4.6, 0.15, 0.0]))
        rot.mostrar(pie_curso("La razón entre esos dos es el SWR: con "
                              "gamma 0.2, uno y medio. Eso mide el "
                              "medidor."), zona="abajo", run_time=0.5)
        self.play(FadeIn(swr, shift=0.14 * UP), run_time=0.6)
        self.wait(4.8)
