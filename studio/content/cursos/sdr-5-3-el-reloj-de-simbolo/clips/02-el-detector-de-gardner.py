class Clip2(Scene):
    """5.3.2 - El detector de Gardner: sobre una transicion, tres muestras
    (antes, medio, despues); a tiempo la del medio cae en cero y el error
    tambien; tarde, no. Luego la curva S medida (sin ruido): cero en el
    centro, signo del desfase, ceros inestables en +-1/2. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El detector de Gardner"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        # --- la traza: diez simbolos de una BPSK con coseno alzado --------
        SPS = 8
        N = 40
        sim = S.simbolos_bpsk(N, 7)
        rx, ret = S.senal_con_pulsos(sim, sps=SPS)
        K0, K1 = 2, 12
        KT = 7                     # transicion de +1 (k-1 = 6) a -1 (k = 7)
        ANCHO, ALTO, RANGO = 11.6, 3.6, 1.6
        centro = np.array([0.0, 0.3, 0.0])

        def en(t, v):
            fx = (t - K0) / (K1 - K0)
            return centro + np.array([(fx - 0.5) * ANCHO,
                                      float(np.clip(v / RANGO, -1, 1)) *
                                      ALTO / 2.0, 0.0])

        seg = np.real(rx[ret + K0 * SPS:ret + K1 * SPS + 1])
        pts = [en(K0 + i / SPS, v) for i, v in enumerate(seg)]
        traza = VMobject(stroke_color=C_SENAL, stroke_width=2.8)
        traza.set_points_smoothly(pts)
        cero = DashedLine(en(K0, 0), en(K1, 0), color=C_EJE,
                          stroke_width=1.3, dash_length=0.08)
        base_y = centro[1] - ALTO / 2.0 - 0.12

        def reloj(tau):
            """Ticks del reloj del receptor (fucsia) y las tres muestras."""
            y = np.real(S.muestrear_en(rx, ret, SPS, tau, N))
            ym = np.real(S.muestrear_en(rx, ret, SPS, tau - 0.5, N))
            ticks = VGroup()
            for k in range(K0, K1 + 1):
                x = en(k + tau, 0)[0]
                ticks.add(Line([x, base_y, 0], [x, base_y - 0.22, 0],
                               color=C_LO, stroke_width=2.6))
            d_a = Dot(en(KT - 1 + tau, y[KT - 1]), radius=0.1, color=C_LO)
            d_m = Dot(en(KT - 0.5 + tau, ym[KT]), radius=0.1, color=C_LO)
            d_b = Dot(en(KT + tau, y[KT]), radius=0.1, color=C_LO)
            e = (y[KT] - y[KT - 1]) * ym[KT]
            return VGroup(ticks, d_a, d_m, d_b), e

        def etiquetas(g):
            _, d_a, d_m, d_b = g
            l_a = MathTex(r"y_{k-1}", font_size=34, color=C_TITULO)
            l_a.next_to(d_a, UP, buff=0.5)
            l_m = MathTex(r"y_{k-1/2}", font_size=34, color=C_TITULO)
            l_m.next_to(d_m, RIGHT, buff=0.16)
            l_b = MathTex(r"y_{k}", font_size=34, color=C_TITULO)
            l_b.next_to(d_b, DOWN, buff=0.14)
            return VGroup(l_a, l_m, l_b)

        self.play(FadeIn(cero), Create(traza), run_time=2.2)
        self.wait(1.0)

        g0, e0 = reloj(0.0)
        self.play(LaggedStart(*[Create(t) for t in g0[0]], lag_ratio=0.08),
                  run_time=1.2)
        self.wait(1.0)
        lab0 = etiquetas(g0)
        self.play(FadeIn(g0[1], scale=1.4), FadeIn(lab0[0]), run_time=0.5)
        self.play(FadeIn(g0[3], scale=1.4), FadeIn(lab0[2]), run_time=0.5)
        self.play(FadeIn(g0[2], scale=1.4), FadeIn(lab0[1]), run_time=0.5)
        self.wait(0.8)
        rot.mostrar(formula_pie(r"e = (y_k - y_{k-1})\, y_{k-1/2}"),
                    zona="abajo", run_time=0.6)
        self.wait(1.2)

        t_e = tag_hud(f"e = {fmt(e0, 2)}", font_size=26)
        t_e.move_to([4.6, -2.05, 0])
        self.play(FadeIn(t_e), run_time=0.5)
        self.wait(3.0)

        # --- el reloj llega tarde: 0.2 de simbolo -------------------------
        TAU_T = float(TAUS[2])
        g1, e1 = reloj(TAU_T)
        lab1 = etiquetas(g1)
        t_tarde = tag_dato(f"retraso {fmt(TAU_T, 1)} simbolo", font_size=21)
        t_tarde.move_to([-4.3, -2.05, 0])
        self.play(FadeOut(t_e), run_time=0.3)
        self.play(Transform(g0, g1), Transform(lab0, lab1), FadeIn(t_tarde),
                  run_time=1.6)
        t_e1 = tag_hud(f"e = {fmt(e1, 2)}", font_size=26)
        t_e1.move_to(t_e)
        self.play(FadeIn(t_e1), run_time=0.5)
        self.wait(3.6)

        # --- la curva S: el error medio para cada desfase ------------------
        self.play(FadeOut(VGroup(traza, cero, g0, lab0, t_tarde, t_e1)),
                  run_time=0.7)
        W, H, EMAX = 10.4, 4.1, 0.2
        c2 = np.array([0.0, 0.1, 0.0])

        def en_s(t, e):
            return c2 + np.array([t / 1.0 * W, e / EMAX * H / 2.0, 0.0])

        eje_x = Line(en_s(-0.5, 0), en_s(0.5, 0), color=C_EJE,
                     stroke_width=1.8)
        eje_y = DashedLine(en_s(0, -EMAX), en_s(0, EMAX), color=C_EJE,
                           stroke_width=1.3, dash_length=0.08)
        marcas = VGroup()
        for t, txt in ((-0.5, "-0.5"), (-0.25, "-0.25"), (0.25, "0.25"),
                       (0.5, "0.5")):
            p = en_s(t, -EMAX)
            marcas.add(Line(en_s(t, -0.008), en_s(t, 0.008), color=C_EJE,
                            stroke_width=1.6))
            lb = tag_hud(txt, font_size=17, color=C_TENUE)
            lb.move_to(p + DOWN * 0.22)
            marcas.add(lb)
        l0 = tag_hud("0", font_size=17, color=C_TENUE)
        l0.move_to(en_s(0, -EMAX) + DOWN * 0.22)
        marcas.add(l0)
        u_x = tag_junto(marcas[-2], "desfase", RIGHT, buff=0.2, font_size=18)
        u_x.align_to(marcas[-2], DOWN)
        t_eje = MathTex(r"e", font_size=34, color=C_TENUE)
        t_eje.next_to(en_s(0, EMAX), LEFT, buff=0.18)
        self.play(Create(eje_x), FadeIn(eje_y), FadeIn(marcas), FadeIn(u_x),
                  FadeIn(t_eje), run_time=0.9)

        puntos = VGroup(*[Dot(en_s(t, e), radius=0.05, color=C_CALCULO)
                          for t, e in zip(TT, CURVA_S)])
        curva = VMobject(stroke_color=C_CALCULO, stroke_width=3.0)
        curva.set_points_smoothly([en_s(t, e) for t, e in zip(TT, CURVA_S)])
        self.play(LaggedStart(*[FadeIn(p, scale=1.5) for p in puntos],
                              lag_ratio=0.12), run_time=2.4)
        self.play(Create(curva), run_time=1.6)
        self.wait(2.0)

        # --- el signo dice hacia donde; el cero del centro es el bueno -----
        s_neg = MathTex(r"e < 0", font_size=34, color=C_TENUE)
        s_neg.move_to(en_s(-0.25, -0.07))
        s_pos = MathTex(r"e > 0", font_size=34, color=C_TENUE)
        s_pos.move_to(en_s(0.25, 0.07))
        f_izq = Arrow(en_s(-0.36, 0) + UP * 0.35, en_s(-0.08, 0) + UP * 0.35,
                      color=C_LO, stroke_width=4, buff=0,
                      max_tip_length_to_length_ratio=0.12)
        f_der = Arrow(en_s(0.36, 0) + DOWN * 0.35, en_s(0.08, 0) + DOWN * 0.35,
                      color=C_LO, stroke_width=4, buff=0,
                      max_tip_length_to_length_ratio=0.12)
        self.play(FadeIn(s_neg), FadeIn(s_pos), run_time=0.6)
        self.wait(1.2)
        self.play(GrowArrow(f_izq), GrowArrow(f_der), run_time=0.8)
        estable = Dot(en_s(0, 0), radius=0.12, color=C_OK)
        self.play(FadeIn(estable, scale=1.6), run_time=0.5)
        self.wait(1.6)

        i_a = Dot(en_s(-0.5, 0), radius=0.12, color=C_RUIDO)
        i_b = Dot(en_s(0.5, 0), radius=0.12, color=C_RUIDO)
        t_ia = tag_junto(i_a, "inestable", UP, buff=0.2, font_size=20,
                         color=C_RUIDO)
        t_ib = tag_junto(i_b, "inestable", DOWN, buff=0.2, font_size=20,
                         color=C_RUIDO)
        self.play(FadeIn(i_a, scale=1.6), FadeIn(i_b, scale=1.6),
                  FadeIn(t_ia), FadeIn(t_ib), run_time=0.7)
        self.wait(5.0)
