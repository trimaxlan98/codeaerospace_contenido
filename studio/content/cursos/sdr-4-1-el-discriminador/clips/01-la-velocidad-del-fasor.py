class Clip1(Scene):
    """4.1.1 - La velocidad del fasor: la FM en banda base es un fasor de
    modulo 1 cuya velocidad angular es proporcional al mensaje instantaneo;
    tono lento y desviacion reducida (escala ilustrativa) para que el giro
    se vea. Debajo, el mensaje con un punto sincronizado. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La velocidad del fasor"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        # --- senal ilustrativa: tono lento, desviacion reducida ----------
        N = 200
        t = np.linspace(0.0, 1.0, N)
        m = np.sin(np.pi * t)
        FS_IL = float(N)
        DESV_IL = 2.5
        X = S.fm_modular(m, FS_IL, DESV_IL)

        # --- plano IQ a la izquierda, curva del mensaje a la derecha:
        # dos figuras separadas que juntas llenan el cuadro ----------------
        plano = S.PlanoIQ(unidad=1.75, alcance=1.15)
        plano.move_to(LEFT * 3.5)
        msg = S.Espectro(t, m, piso=0.0, techo=1.05, ancho=6.0, alto=3.6,
                         color=C_SENAL)
        msg.move_to(RIGHT * 2.5)
        et_msg = tag_junto(msg, "mensaje", UP, buff=0.18, font_size=20,
                           color=C_SENAL)

        self.play(Create(plano.ejes), Create(plano.unidad_circulo),
                  run_time=0.7)
        self.play(Create(msg.ejes), FadeIn(et_msg), run_time=0.6)
        self.play(Create(msg.curva), FadeIn(msg.area), run_time=1.7)
        self.wait(0.6)

        rot.mostrar(dato_pie("escala ilustrativa"), zona="abajo",
                    run_time=0.5)

        idx = ValueTracker(0.0)

        def _k():
            return min(int(idx.get_value()), N - 1)

        origen = plano.p(0)
        flecha = always_redraw(lambda: Arrow(
            origen, plano.p(X[_k()]), buff=0, color=C_SENAL,
            stroke_width=5, max_tip_length_to_length_ratio=0.22))
        traza = TracedPath(flecha.get_end, stroke_color=C_SENAL,
                           stroke_width=2.2, stroke_opacity=0.45)
        punto = always_redraw(lambda: Dot(msg.en(t[_k()], m[_k()]),
                                          radius=0.075, color=C_SENAL))

        self.add(traza, flecha, punto)
        self.wait(0.4)
        # el indice avanza LINEAL en tiempo real: la velocidad angular que
        # se ve es la del fasor (proporcional al mensaje), no un artificio
        self.play(idx.animate.set_value(N - 1), run_time=13.0,
                  rate_func=linear)
        self.wait(2.2)
        self.play(idx.animate.set_value(0.0), run_time=7.0,
                  rate_func=linear)
        self.wait(4.0)
