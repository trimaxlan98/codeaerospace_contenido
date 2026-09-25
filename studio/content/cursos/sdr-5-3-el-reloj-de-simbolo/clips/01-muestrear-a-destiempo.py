class Clip1(Scene):
    """5.3.1 - Muestrear a destiempo: el diagrama de ojo de una BPSK con
    coseno alzado y el instante de muestreo (fucsia) que se corre de 0 a
    0.4 de simbolo; a cada paso, la BER MEDIDA a 7 dB. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Muestrear a destiempo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        SPS = 8
        N = 64
        sim = S.simbolos_bpsk(N, 11)
        rx, ret = S.senal_con_pulsos(sim, sps=SPS)
        ks = list(range(4, 52))

        # --- el marco del ojo -------------------------------------------
        ANCHO, ALTO, RANGO = 8.4, 4.5, 1.9
        centro = np.array([-2.0, 0.05, 0.0])

        def en(t, v):
            return centro + np.array([t / 2.0 * ANCHO,
                                      float(np.clip(v / RANGO, -1, 1)) *
                                      ALTO / 2.0, 0.0])

        marco = Rectangle(width=ANCHO, height=ALTO, stroke_color=C_EJE,
                          stroke_width=1.6).move_to(centro)
        cero = DashedLine(en(-1, 0), en(1, 0), color=C_EJE, stroke_width=1.2,
                          dash_length=0.07)
        ticks = VGroup()
        for t, txt in ((-1, "-1"), (-0.5, "-0.5"), (0, "0"), (0.5, "0.5"),
                       (1, "1")):
            p = en(t, -RANGO)
            ticks.add(Line(p, p + DOWN * 0.1, color=C_EJE, stroke_width=1.6))
            lb = tag_hud(txt, font_size=17, color=C_TENUE)
            lb.next_to(p, DOWN, buff=0.14)
            ticks.add(lb)
        u_t = tag_junto(ticks[-1], "simbolos", RIGHT, buff=0.14,
                        font_size=18)
        for v, txt in ((1, "+1"), (-1, "-1")):
            p = en(-1, v)
            ticks.add(Line(p, p + LEFT * 0.1, color=C_EJE, stroke_width=1.6))
            lb = tag_hud(txt, font_size=17, color=C_TENUE)
            lb.next_to(p, LEFT, buff=0.12)
            ticks.add(lb)

        trazas = VGroup()
        for k in ks:
            i0 = ret + (k - 1) * SPS
            seg = np.real(rx[i0:i0 + 2 * SPS + 1])
            pts = [en(-1 + i / SPS, v) for i, v in enumerate(seg)]
            tr = VMobject(stroke_color=C_SENAL, stroke_width=1.5)
            tr.set_points_smoothly(pts)
            tr.set_stroke(opacity=0.55)
            trazas.add(tr)

        self.play(Create(marco), FadeIn(cero), FadeIn(ticks), FadeIn(u_t),
                  run_time=0.9)
        self.play(LaggedStart(*[Create(t) for t in trazas], lag_ratio=0.04),
                  run_time=3.0)
        self.wait(2.0)

        # --- el instante de muestreo y las muestras que toma --------------
        def linea_en(tau):
            return Line(en(tau, -RANGO), en(tau, RANGO), color=C_LO,
                        stroke_width=3.2)

        def muestras_en(tau):
            y = np.real(S.muestrear_en(rx, ret, SPS, tau, N))
            g = VGroup()
            for k in ks:
                d = Dot(en(tau, y[k]), radius=0.055, color=C_LO)
                g.add(d)
            return g

        TAU_TXT = [fmt(t, 1) for t in TAUS]
        linea = linea_en(TAUS[0])
        puntos = muestras_en(TAUS[0])
        t_linea = tag_junto(linea, "muestreo", UP, buff=0.12, font_size=20,
                            color=C_LO)
        self.play(Create(linea), FadeIn(t_linea), run_time=0.8)
        self.play(FadeIn(puntos, scale=1.3), run_time=0.7)
        self.wait(1.2)

        # --- la tabla: desfase (parametro) y BER medida -------------------
        X_TAU, X_BER = 3.35, 6.3
        cab_t = tag_hud("desfase", font_size=19, color=C_TENUE)
        cab_t.move_to([X_TAU, 1.95, 0])
        cab_b = tag_hud("BER", font_size=19, color=C_TENUE)
        cab_b.move_to([X_BER, 1.95, 0], aligned_edge=RIGHT)
        raya = Line([2.85, 1.68, 0], [6.4, 1.68, 0], color=C_EJE,
                    stroke_width=1.4)
        filas = []
        for i, tau in enumerate(TAUS):
            y = 1.25 - 0.68 * i
            a = tag_dato(TAU_TXT[i], font_size=24).move_to([X_TAU, y, 0])
            b = tag_hud(f"{fmt(100 * BER[i], 2)} %", font_size=26)
            b.move_to([X_BER, y, 0], aligned_edge=RIGHT)
            filas.append(VGroup(a, b))
        beta = MathTex(r"\beta = 0.35", font_size=30, color=C_DATO)
        snr = tag_dato("SNR 7 dB", font_size=20)
        VGroup(beta, snr).arrange(RIGHT, buff=0.5).move_to([5.05, -2.2, 0])
        marca = Triangle(color=C_LO, fill_opacity=1.0, stroke_width=0)
        marca.scale(0.09).rotate(-PI / 2)
        marca.next_to(filas[0], LEFT, buff=0.22)

        self.play(FadeIn(cab_t), FadeIn(cab_b), Create(raya), FadeIn(beta),
                  FadeIn(snr), run_time=0.7)
        self.play(FadeIn(filas[0], shift=LEFT * 0.1), FadeIn(marca),
                  run_time=0.5)
        self.wait(3.0)

        for i in range(1, len(TAUS)):
            nueva = linea_en(TAUS[i])
            nuevos = muestras_en(TAUS[i])
            self.play(filas[i - 1].animate.set_opacity(0.4),
                      FadeOut(marca), run_time=0.3)
            self.play(Transform(linea, nueva), Transform(puntos, nuevos),
                      t_linea.animate.next_to(nueva, UP, buff=0.12),
                      run_time=1.3)
            marca.next_to(filas[i], LEFT, buff=0.22)
            self.play(FadeIn(filas[i], shift=LEFT * 0.1), FadeIn(marca),
                      run_time=0.5)
            self.wait(2.6)

        # --- vuelta a 0.3: la fila que se compara con el centro -----------
        self.play(filas[4].animate.set_opacity(0.4),
                  filas[3].animate.set_opacity(1.0),
                  filas[0].animate.set_opacity(1.0),
                  FadeOut(marca), run_time=0.4)
        self.play(Transform(linea, linea_en(TAUS[3])),
                  Transform(puntos, muestras_en(TAUS[3])),
                  t_linea.animate.next_to(linea_en(TAUS[3]), UP, buff=0.12),
                  run_time=1.0)
        marca.next_to(filas[3], LEFT, buff=0.22)
        self.play(FadeIn(marca), run_time=0.3)
        self.wait(0.6)
        rot.mostrar(cifra_pie(f"x{fmt(BER[3] / BER[0], 0)} errores a "
                              f"{TAU_TXT[3]} simbolo"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)
