class Clip2(Scene):
    """2.3.2 - La fundamental sube 1 a 1 y el producto de intermodulacion
    sube 3 a 1: las dos rectas ajustadas al tramo lineal se prolongan y se
    cruzan en el IIP3, la entrada donde el amplificador ya no serviria.
    Marco a mano (sin Axes): el rango no cruza por el origen. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La recta de 3 a 1"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        x0, x1 = -42.0, 14.0
        y0, y1 = -130.0, 36.0
        ancho, alto = 10.6, 5.0
        origen = UP * 0.1

        def punto(x, y):
            fx = (x - x0) / (x1 - x0)
            fy = (y - y0) / (y1 - y0)
            return origen + np.array([(fx - 0.5) * ancho,
                                      (fy - 0.5) * alto, 0.0])

        esquinas = [punto(x0, y0), punto(x1, y0), punto(x1, y1),
                   punto(x0, y1)]
        marco = VGroup(*[Line(esquinas[i], esquinas[(i + 1) % 4],
                              color=C_TENUE, stroke_width=1.8)
                         for i in range(4)])
        self.play(Create(marco), run_time=0.9)

        et_x = tag_junto(marco, "entrada dB", DOWN, buff=0.18, font_size=19)
        et_y = tag_junto(marco, "salida dB", LEFT, buff=0.18, font_size=19)
        self.play(FadeIn(et_x), FadeIn(et_y), run_time=0.5)
        self.wait(2.0)

        entrada = RIP3["entrada_db"]
        fund = RIP3["fund_db"]
        im3 = RIP3["im3_db"]
        pf = VGroup(*[Dot(punto(x, y), radius=0.055, color=C_SENAL)
                     for x, y in zip(entrada, fund)])
        pi = VGroup(*[Dot(punto(x, y), radius=0.055, color=C_RUIDO)
                     for x, y in zip(entrada, im3)])
        self.play(LaggedStart(*[FadeIn(d) for d in pf], lag_ratio=0.08),
                  run_time=1.6)
        self.wait(0.6)
        self.play(LaggedStart(*[FadeIn(d) for d in pi], lag_ratio=0.08),
                  run_time=1.6)
        self.wait(2.6)

        # --- rectas ajustadas: solidas donde se midio (hasta -20 dB),
        # punteadas donde se extrapolan hasta el IIP3 --------------------
        xm0, xm1 = float(entrada.min()), -20.0
        recta_f_s = Line(punto(xm0, np.polyval(RIP3["ajuste_1"], xm0)),
                         punto(xm1, np.polyval(RIP3["ajuste_1"], xm1)),
                         color=C_SENAL, stroke_width=2.8)
        recta_i_s = Line(punto(xm0, np.polyval(RIP3["ajuste_3"], xm0)),
                         punto(xm1, np.polyval(RIP3["ajuste_3"], xm1)),
                         color=C_RUIDO, stroke_width=2.8)
        self.play(Create(recta_f_s), Create(recta_i_s), run_time=1.4)
        self.wait(2.2)

        recta_f_d = DashedLine(
            punto(xm1, np.polyval(RIP3["ajuste_1"], xm1)),
            punto(IIP3, np.polyval(RIP3["ajuste_1"], IIP3)),
            color=C_SENAL, stroke_width=2.4, dash_length=0.1)
        recta_i_d = DashedLine(
            punto(xm1, np.polyval(RIP3["ajuste_3"], xm1)),
            punto(IIP3, np.polyval(RIP3["ajuste_3"], IIP3)),
            color=C_RUIDO, stroke_width=2.4, dash_length=0.1)
        self.play(Create(recta_f_d), Create(recta_i_d), run_time=1.6)
        self.wait(2.0)

        cruce = Dot(punto(IIP3, RIP3["oip3_db"]), radius=0.09,
                   color=C_CALCULO)
        guia_v = DashedLine(punto(IIP3, y0), punto(IIP3, RIP3["oip3_db"]),
                           color=C_CALCULO, stroke_width=1.6,
                           dash_length=0.08)
        guia_h = DashedLine(punto(x0, RIP3["oip3_db"]),
                           punto(IIP3, RIP3["oip3_db"]), color=C_CALCULO,
                           stroke_width=1.6, dash_length=0.08)
        self.play(Create(guia_v), Create(guia_h), run_time=0.9)
        self.play(FadeIn(cruce), run_time=0.5)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"pendiente {fmt(PEND1, 2)} y {fmt(PEND3, 2)}"),
                    zona="abajo", run_time=0.5)
        self.wait(3.6)
        rot.mostrar(cifra_pie(f"IIP3 = {fmt(IIP3, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(6.0)
