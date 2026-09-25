class Clip4(Scene):
    """3.3.4 - Corregir: el NCO resta la deriva medida fila a fila; el
    waterfall mismo se endereza (no una raya dibujada al lado) y lo que
    queda es el residuo (2.4 Hz de rms, el error de la propia medida).
    Cierre de la leccion. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Corregir"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        ANCHO_WF, ALTO_WF = 10.4, 4.9
        FS_KHZ = 24.0
        T_MAX = float(T_WF[-1])
        F0_KHZ = -6.0
        FS_WF, COLUMNAS, SEMILLA_WF = 48e3, 256, 12

        img = S.waterfall(WF, ancho=ANCHO_WF, alto=ALTO_WF, piso=-40.0,
                          techo=0.0)
        img.move_to(UP * 0.02)

        def x_de(khz):
            return img.get_left()[0] + (khz + FS_KHZ) / (2 * FS_KHZ) * ANCHO_WF

        def y_de(minuto):
            return img.get_top()[1] - minuto / T_MAX * ALTO_WF

        marco = Rectangle(width=ANCHO_WF, height=ALTO_WF, stroke_color=C_EJE,
                          stroke_width=1.8, fill_opacity=0.0)
        marco.move_to(img.get_center())

        ticks_x = VGroup()
        for khz, txt in zip([-24, -12, 0, 12, 24],
                            ["-24", "-12", "0", "12", "24"]):
            xp = x_de(khz)
            yb = img.get_bottom()[1]
            t = Line(np.array([xp, yb, 0.0]), np.array([xp, yb - 0.1, 0.0]),
                     color=C_EJE, stroke_width=1.6)
            lbl = tag_hud(txt, font_size=16, color=C_TENUE)
            lbl.next_to(t, DOWN, buff=0.08)
            ticks_x.add(t, lbl)
        u_x = tag_junto(ticks_x[-1], "kHz", RIGHT, buff=0.14, font_size=18)

        ticks_y = VGroup()
        for m in [0, 5, 10]:
            yp = y_de(m)
            xl = img.get_left()[0]
            t = Line(np.array([xl - 0.1, yp, 0.0]), np.array([xl, yp, 0.0]),
                     color=C_EJE, stroke_width=1.6)
            lbl = tag_hud(str(m), font_size=16, color=C_TENUE)
            lbl.next_to(t, LEFT, buff=0.08)
            ticks_y.add(t, lbl)
        u_y = tag_junto(ticks_y[0], "min", UP, buff=0.14, font_size=18)

        # --- todo el mobiliario entra JUNTO: nunca el waterfall solo --------
        self.play(FadeIn(img), Create(marco), FadeIn(ticks_x), FadeIn(u_x),
                  FadeIn(ticks_y), FadeIn(u_y), run_time=1.0)
        self.wait(1.6)

        # --- la traza torcida, como quedo en la leccion anterior -----------
        pts_torcida = [np.array([x_de(F0_KHZ + DERIVA_MED[k] / 1e3),
                                 y_de(T_WF[k]), 0.0])
                      for k in range(len(T_WF))]
        traza = VMobject(stroke_color=C_CALCULO, stroke_width=2.4,
                         stroke_opacity=0.9)
        traza.set_points_smoothly(pts_torcida)
        punto = Dot(pts_torcida[-1], radius=0.07, color=C_CALCULO)
        self.play(Create(traza), FadeIn(punto), run_time=1.6)
        self.wait(1.0)

        # --- el NCO: lo que resta la deriva medida --------------------------
        nco = Circle(radius=0.22, color=C_LO, stroke_width=2.4)
        nco.move_to(np.array([x_de(F0_KHZ), img.get_top()[1] + 0.5, 0.0]))
        xs = np.linspace(-0.14, 0.14, 26)
        onda = VMobject(stroke_color=C_LO, stroke_width=2.0)
        onda.set_points_smoothly([nco.get_center() + np.array(
            [xk, 0.08 * math.sin(xk / 0.14 * 2 * math.pi), 0])
            for xk in xs])
        et_nco = tag_junto(nco, "NCO", RIGHT, buff=0.18, font_size=20,
                           color=C_LO)
        flecha_nco = Arrow(nco.get_bottom(), pts_torcida[0], color=C_LO,
                           buff=0.06, stroke_width=2.6)
        self.play(FadeIn(nco), Create(onda), FadeIn(et_nco), run_time=0.7)
        self.play(GrowArrow(flecha_nco), run_time=0.6)
        self.wait(1.4)

        # --- se resta DERIVA_MED fila a fila: el WATERFALL se endereza ------
        self.play(FadeOut(traza), FadeOut(punto), FadeOut(nco), FadeOut(onda),
                  FadeOut(et_nco), FadeOut(flecha_nco), run_time=0.6)

        def _waterfall_de(freqs_hz):
            r = np.random.default_rng(SEMILLA_WF)
            filas = []
            for fk in freqs_hz:
                x = S.tono(fk, FS_WF, COLUMNAS * 4) + S.ruido_complejo(
                    COLUMNAS * 4, 0.05, int(r.integers(1 << 30)))
                f, d = S.espectro_db(x, FS_WF, nfft=COLUMNAS, ref="abs")
                filas.append(d)
            filas = np.array(filas)
            filas -= filas.max()
            return filas

        residuo = DERIVA_MED - DERIVA
        rms = float(np.sqrt(np.mean(residuo ** 2)))
        freqs_corr = -6e3 + (DERIVA - DERIVA_MED)
        WF_CORR = _waterfall_de(freqs_corr)
        img_corr = S.waterfall(WF_CORR, ancho=ANCHO_WF, alto=ALTO_WF,
                               piso=-40.0, techo=0.0)
        img_corr.move_to(img.get_center())
        self.play(FadeOut(img), FadeIn(img_corr), run_time=1.3)
        self.wait(1.4)

        rot.mostrar(cifra_pie(f"residuo: {fmt(rms, 1)} Hz"), zona="abajo",
                   run_time=0.5)
        self.wait(9.0)

        cierre_leccion(self, rot, "El cristal miente un poco.",
                       "Una senal conocida lo delata.", img_corr, marco,
                       ticks_x, u_x, ticks_y, u_y)
