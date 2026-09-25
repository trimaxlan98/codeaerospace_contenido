class Clip2(Scene):
    """7.3.2 - El codigo C/A del PRN 7: los primeros 64 chips como +-1, y su
    autocorrelacion circular: un pico de 1023 y todo lo demas en tres
    valores (63, -1, -65). Ganancia 10 log10(1023). (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El codigo C/A"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        c = 1 - 2 * CA
        N_CH = len(c)
        auto = np.array([np.dot(c, np.roll(c, k)) for k in range(N_CH)])
        PICO = int(auto[0])
        NIVELES = sorted(set(int(v) for v in auto[1:]))     # 3 valores

        # --- los chips ----------------------------------------------------
        N_V = 64
        X0, X1 = -5.4, 6.2
        Y_C, H_C = 2.05, 0.42           # centro y semialtura de la fila
        w = (X1 - X0) / N_V
        pts = []
        for k in range(N_V):
            y = Y_C + H_C * c[k]
            pts += [np.array([X0 + k * w, y, 0]),
                    np.array([X0 + (k + 1) * w, y, 0])]
        chips = VMobject(stroke_color=C_SENAL, stroke_width=3.0)
        chips.set_points_as_corners(pts)
        base = DashedLine([X0, Y_C, 0], [X1, Y_C, 0], color=C_EJE,
                          stroke_width=1.2, dash_length=0.06)
        mas = tag_hud("+1", font_size=19, color=C_TENUE)
        mas.move_to([X0 - 0.45, Y_C + H_C, 0])
        menos = tag_hud("-1", font_size=19, color=C_TENUE)
        menos.move_to([X0 - 0.45, Y_C - H_C, 0])
        t_ch = tag_junto(chips, f"{N_V} de {N_CH} chips", DOWN,
                         buff=0.16, font_size=22)
        t_ch.align_to(chips, RIGHT)

        self.play(Create(base), FadeIn(mas), FadeIn(menos), run_time=0.5)
        self.play(Create(chips), run_time=2.8, rate_func=linear)
        self.play(FadeIn(t_ch), run_time=0.4)
        rot.mostrar(dato_pie("1023 chips en 1 ms"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)
        rot.mostrar(dato_pie("PRN 7"), zona="abajo", run_time=0.5)
        self.wait(1.6)
        rot.limpiar(zona="abajo", run_time=0.3)

        # --- autocorrelacion: escala completa ------------------------------
        Y_B, Y_T = -2.35, 0.95          # marco vertical del panel
        LO_V, HI_V = -120.0, 1100.0
        AX0, AX1 = -5.4, 1.0
        lags = np.arange(-(N_CH // 2), N_CH // 2 + 1)
        vals = np.array([auto[k % N_CH] for k in lags])

        def pa(lag, v):
            fx = (lag - lags[0]) / (lags[-1] - lags[0])
            fy = (v - LO_V) / (HI_V - LO_V)
            return np.array([AX0 + fx * (AX1 - AX0),
                             Y_B + fy * (Y_T - Y_B), 0.0])

        eje0 = Line(pa(lags[0], 0), pa(lags[-1], 0), color=C_EJE,
                    stroke_width=1.6)
        curva = VMobject(stroke_color=C_SENAL, stroke_width=2.2)
        curva.set_points_as_corners([pa(l, v) for l, v in zip(lags, vals)])
        y0 = tag_hud("0", font_size=19, color=C_TENUE)
        y0.next_to(pa(lags[0], 0), LEFT, buff=0.14)
        t_pico = tag_hud(f"{PICO}", font_size=24)
        t_pico.next_to(pa(0, PICO), RIGHT, buff=0.14)
        t_lag = tag_junto(eje0, "retardo en chips", DOWN, buff=0.22,
                          font_size=22)
        t_lag.move_to([(AX0 + AX1) / 2, Y_B - 0.12, 0])

        self.play(Create(eje0), FadeIn(y0), run_time=0.5)
        self.play(Create(curva), run_time=2.4)
        self.play(FadeIn(t_pico), FadeIn(t_lag), run_time=0.5)
        rot.mostrar(cifra_pie(f"pico = {PICO}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- zoom: los tres valores -----------------------------------------
        Z0, Z1 = 2.2, 6.2
        ZLO, ZHI = -95.0, 95.0
        K_Z = 40                                   # retardos 1..40

        def pz(k, v):
            fx = (k - 0.5) / K_Z
            fy = (v - ZLO) / (ZHI - ZLO)
            return np.array([Z0 + fx * (Z1 - Z0),
                             Y_B + fy * (Y_T - Y_B), 0.0])

        marco = Rectangle(width=Z1 - Z0 + 0.2, height=Y_T - Y_B,
                          stroke_color=C_EJE, stroke_width=1.4)
        marco.move_to([(Z0 + Z1) / 2, (Y_T + Y_B) / 2, 0])
        # la franja del zoom sobre la escala completa
        franja = Rectangle(width=(AX1 - AX0) * K_Z / len(lags) + 0.06,
                           height=abs(pa(0, ZHI)[1] - pa(0, ZLO)[1]),
                           stroke_color=C_TENUE, stroke_width=1.4)
        franja.move_to((pa(1, ZHI) + pa(K_Z, ZLO)) / 2)
        niveles = VGroup()
        t_niv = VGroup()
        for v in NIVELES:
            niveles.add(DashedLine(pz(0.5, v), pz(K_Z + 0.5, v),
                                   color=C_CALCULO, stroke_width=1.2,
                                   dash_length=0.06).set_stroke(opacity=0.6))
            t = tag_hud(f"{v:+d}", font_size=20)
            t.next_to(pz(0.5, v), LEFT, buff=0.34)
            t_niv.add(t)
        tallos = VGroup()
        for k in range(1, K_Z + 1):
            v = int(auto[k])
            tallos.add(Line(pz(k, 0), pz(k, v), color=C_SENAL,
                            stroke_width=3.0))
        t_zoom = tag_junto(marco, f"retardos 1 a {K_Z}", DOWN, buff=0.1,
                           font_size=22)
        t_zoom.move_to([(Z0 + Z1) / 2, Y_B - 0.12, 0])

        self.play(Create(franja), run_time=0.5)
        self.play(TransformFromCopy(franja, marco), run_time=0.9)
        self.play(FadeIn(t_zoom), run_time=0.3)
        self.play(LaggedStart(*[Create(t) for t in tallos], lag_ratio=0.06),
                  run_time=2.4)
        self.play(*[Create(n) for n in niveles], FadeIn(t_niv), run_time=0.8)
        rot.mostrar(cifra_pie(f"el resto: solo {len(NIVELES)} valores"),
                    zona="abajo", run_time=0.5)
        self.wait(3.6)

        # --- la ganancia ------------------------------------------------------
        rot.mostrar(formula_pie(r"10\log_{10}(" + f"{N_CH}" + r") = "
                                + fmt(GANANCIA, 1) + r"\ \mathrm{dB}"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)
        rot.mostrar(cifra_pie(f"ganancia {fmt(GANANCIA, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(4.5)
