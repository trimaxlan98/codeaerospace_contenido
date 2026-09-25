class Clip1(Scene):
    """2.2.1 - Con ganancia 0 dB la senal de -60 dBFS solo mueve el ADC
    entre 2 de 256 niveles: SINAD medida 6.3 dB. Zoom a la rejilla de
    niveles cercana a cero; el medidor muestra cuan lejos queda el techo.
    (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Poca ganancia"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- zoom a la rejilla de niveles cerca de cero -------------------
        PASO = 2.0 / 256
        ANCHO, ALTO = 8.0, 3.6
        V_LO, V_HI = -2.5 * PASO, 2.5 * PASO
        ORIGEN = LEFT * 1.4 + UP * 0.15
        N = 80

        def en(i, v):
            fx = i / (N - 1)
            fy = (min(max(v, V_LO), V_HI) - V_LO) / (V_HI - V_LO)
            return ORIGEN + np.array([(fx - 0.5) * ANCHO,
                                      (fy - 0.5) * ALTO, 0.0])

        eje_x = Line(en(0, 0.0), en(N - 1, 0.0), color=S.C_EJE,
                    stroke_width=1.4)
        rejilla = VGroup(*[
            Line(en(0, k * PASO), en(N - 1, k * PASO), color=S.C_EJE,
                stroke_width=1.2)
            for k in (-2, -1, 1, 2)])
        t_rejilla = tag_junto(eje_x, "rejilla de niveles", UP, font_size=18)
        t_rejilla.move_to(en(N - 14, 2.3 * PASO))

        g0 = 10 ** ((0.0 - 60.0) / 20.0)
        antes = (g0 * XG[:N]).real
        despues = S.adc(g0 * XG[:N]).real

        curva = VMobject(stroke_color=C_SENAL, stroke_width=2.2)
        curva.set_points_as_corners([en(i, antes[i]) for i in range(N)])

        pts = []
        for i in range(N):
            pts.append(en(i, despues[i]))
            if i + 1 < N:
                pts.append(en(i + 1, despues[i]))
        pasos = VMobject(stroke_color=C_TITULO, stroke_width=4.2)
        pasos.set_points_as_corners(pts)

        self.play(Create(eje_x), FadeIn(rejilla), FadeIn(t_rejilla),
                  run_time=0.9)
        self.wait(1.0)
        self.play(Create(curva), run_time=1.6)
        t_onda = tag_junto(curva, "la senal real", UP, buff=0.14,
                           font_size=19, color=C_SENAL)
        t_onda.move_to(en(6, -2.3 * PASO))
        self.play(FadeIn(t_onda), run_time=0.5)
        self.wait(1.4)
        self.play(Create(pasos), run_time=1.8)
        self.wait(2.2)

        # --- el medidor: cuan lejos queda el techo -------------------------
        med = S.Medidor(alto=ALTO, ancho=0.55, minimo=-80.0)
        med.move_to(ORIGEN + RIGHT * (ANCHO / 2 + 1.6))
        t_techo = tag_junto(med.zona, "techo", UP, buff=0.16, font_size=19,
                            color=C_RUIDO)
        barra = med.nivel(-60.0, color=C_SENAL)
        self.play(FadeIn(med), FadeIn(t_techo), run_time=0.7)
        self.wait(0.6)
        self.play(GrowFromEdge(barra, DOWN), run_time=1.0)
        d_niv = tag_dato("-60 dBFS", font_size=19)
        d_niv.next_to(barra, RIGHT, buff=0.22)
        self.play(FadeIn(d_niv), run_time=0.5)
        self.wait(1.8)

        d_snr = tag_dato("SNR entrada 30 dB", font_size=18)
        d_snr.next_to(med, DOWN, buff=0.5)
        self.play(FadeIn(d_snr), run_time=0.5)
        self.wait(1.6)

        rot.mostrar(cifra_pie(f"{NIV_POCA} de 256 niveles"), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)
        rot.mostrar(cifra_pie(f"SINAD {fmt(SINAD_POCA, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(6.2)
