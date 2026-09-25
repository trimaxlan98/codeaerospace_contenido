class Clip3(Scene):
    """2.2.3 - La curva medida de SINAD frente a ganancia: el tramo de 48 a
    60 dB (centro 54) se queda a menos de 1 dB del maximo, 30.3 dB. Un
    punto recorre la curva y el medidor lo acompana hasta el recorte.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El punto dulce"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- cuadro propio (a mano, con Lines): ganancia vs SINAD ---------
        X_LO, X_HI = float(G.min()), float(G.max())
        Y_LO = 0.0
        Y_HI = float(np.ceil(SINAD.max())) + 3.0
        ANCHO, ALTO = 9.6, 3.8
        ORIGEN = LEFT * 1.2 + UP * 0.25

        def xy(g, s):
            fx = (g - X_LO) / (X_HI - X_LO)
            fy = (min(max(s, Y_LO), Y_HI) - Y_LO) / (Y_HI - Y_LO)
            return ORIGEN + np.array([(fx - 0.5) * ANCHO,
                                      (fy - 0.5) * ALTO, 0.0])

        esq = [xy(X_LO, Y_LO), xy(X_HI, Y_LO), xy(X_HI, Y_HI),
              xy(X_LO, Y_HI)]
        marco = VGroup(*[Line(esq[i], esq[(i + 1) % 4], color=S.C_EJE,
                              stroke_width=1.6) for i in range(4)])
        t_x = tag_junto(marco[0], "ganancia", DOWN, buff=0.22, font_size=19)
        t_y = tag_junto(marco[3], "SINAD", LEFT, buff=0.22, font_size=19)

        banda = Rectangle(width=abs(xy(G1, 0)[0] - xy(G0, 0)[0]), height=ALTO,
                          stroke_width=0, fill_color=C_OK, fill_opacity=0.16)
        banda.move_to((xy(G0, Y_LO) + xy(G1, Y_HI)) / 2)

        curva = VMobject(stroke_color=C_CALCULO, stroke_width=3.0)
        curva.set_points_as_corners([xy(g, s) for g, s in zip(G, SINAD)])

        self.play(Create(marco), FadeIn(t_x), FadeIn(t_y), run_time=0.9)
        self.wait(0.5)
        self.play(Create(curva), run_time=2.0)
        self.wait(0.8)
        self.play(FadeIn(banda), run_time=0.8)
        self.wait(1.0)

        rot.mostrar(cifra_pie(f"{fmt(G0, 0)} a {fmt(G1, 0)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)
        rot.mostrar(cifra_pie(f"SINAD max {fmt(SMAX, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        # --- el medidor acompana el recorrido ------------------------------
        med = S.Medidor(alto=ALTO, ancho=0.55, minimo=-80.0)
        med.move_to(ORIGEN + RIGHT * (ANCHO / 2 + 1.5))
        t_zona = tag_junto(med.zona, "techo", UP, buff=0.16, font_size=19,
                           color=C_RUIDO)
        self.play(FadeIn(med), FadeIn(t_zona), run_time=0.6)
        self.wait(0.4)

        vt = ValueTracker(X_LO)
        punto = Dot(radius=0.1, color=C_CALCULO)
        punto.move_to(xy(X_LO, float(np.interp(X_LO, G, SINAD))))
        barra = med.nivel(-60.0 + X_LO, color=C_SENAL)

        def actualizar_punto(m):
            g = vt.get_value()
            s = float(np.interp(g, G, SINAD))
            m.move_to(xy(g, s))

        def actualizar_barra(m):
            color = C_RUIDO if vt.get_value() >= G1 else C_SENAL
            m.become(med.nivel(-60.0 + vt.get_value(), color=color))

        punto.add_updater(actualizar_punto)
        barra.add_updater(actualizar_barra)
        self.add(barra, punto)
        self.play(FadeIn(punto), run_time=0.4)
        self.wait(0.3)
        self.play(vt.animate.set_value(X_HI), run_time=6.0, rate_func=linear)
        punto.clear_updaters()
        barra.clear_updaters()
        self.wait(6.5)
