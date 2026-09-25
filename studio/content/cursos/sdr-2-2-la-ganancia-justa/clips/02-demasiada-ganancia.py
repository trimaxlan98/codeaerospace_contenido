class Clip2(Scene):
    """2.2.2 - Con ganancia 66 dB el ADC recorta contra el techo +-1: el
    espurio mas alto del espectro queda a -12.9 dBc del tono, y el medidor
    entra en la zona roja. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Demasiada ganancia"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- la onda recortada contra el techo, unidades de ADC ----------
        ANCHO, ALTO = 8.0, 3.6
        V_LO, V_HI = -2.1, 2.1
        ORIGEN = LEFT * 1.4 + UP * 0.15
        N = 80

        def en(i, v):
            fx = i / (N - 1)
            fy = (min(max(v, V_LO), V_HI) - V_LO) / (V_HI - V_LO)
            return ORIGEN + np.array([(fx - 0.5) * ANCHO,
                                      (fy - 0.5) * ALTO, 0.0])

        eje_x = Line(en(0, 0.0), en(N - 1, 0.0), color=S.C_EJE,
                    stroke_width=1.4)
        techo_hi = DashedLine(en(0, 1.0), en(N - 1, 1.0), color=C_RUIDO,
                              stroke_width=2.2, dash_length=0.1)
        techo_lo = DashedLine(en(0, -1.0), en(N - 1, -1.0), color=C_RUIDO,
                              stroke_width=2.2, dash_length=0.1)
        t_techo = tag_junto(techo_hi, "techo", UP, buff=0.14, font_size=19,
                            color=C_RUIDO)

        g66 = 10 ** ((66.0 - 60.0) / 20.0)
        antes = (g66 * XG[:N]).real
        despues = S.adc(g66 * XG[:N]).real

        curva = VMobject(stroke_color=C_SENAL, stroke_width=2.2)
        curva.set_points_as_corners([en(i, antes[i]) for i in range(N)])

        pts = []
        for i in range(N):
            pts.append(en(i, despues[i]))
            if i + 1 < N:
                pts.append(en(i + 1, despues[i]))
        pasos = VMobject(stroke_color=C_TITULO, stroke_width=3.4)
        pasos.set_points_as_corners(pts)

        med = S.Medidor(alto=ALTO, ancho=0.55, minimo=-80.0)
        med.move_to(ORIGEN + RIGHT * (ANCHO / 2 + 1.6))
        t_zona = tag_junto(med.zona, "techo", UP, buff=0.16, font_size=19,
                           color=C_RUIDO)
        barra = med.nivel(6.0, color=C_RUIDO)

        self.play(Create(eje_x), Create(techo_hi), Create(techo_lo),
                  FadeIn(t_techo), FadeIn(med), FadeIn(t_zona), run_time=1.0)
        self.wait(0.6)
        self.play(Create(curva), run_time=1.6)
        t_onda = tag_junto(curva, "la senal real", UP, buff=0.16,
                           font_size=19, color=C_SENAL)
        t_onda.move_to(en(2, 2.0))
        self.play(FadeIn(t_onda), run_time=0.5)
        self.wait(1.2)
        self.play(Create(pasos), run_time=1.6)
        self.wait(0.8)
        self.play(GrowFromEdge(barra, DOWN), run_time=1.0)
        self.wait(3.4)

        grupo_onda = VGroup(eje_x, techo_hi, techo_lo, t_techo, curva,
                            t_onda, pasos, med, t_zona, barra)
        self.play(FadeOut(grupo_onda), run_time=0.7)

        # --- el espectro: el espurio mas alto ------------------------------
        n = 1 << 14
        x = np.exp(2j * np.pi * 611 * np.arange(n) / n)
        y = S.adc(g66 * x)
        f, db = S.espectro_db(y, 1.0, nfft=n)
        k_tono = int(np.argmax(db))
        mask = np.ones_like(db, bool)
        mask[max(0, k_tono - 3):k_tono + 4] = False
        k_esp = int(np.flatnonzero(mask)[np.argmax(db[mask])])
        f_tono, f_esp = float(f[k_tono]), float(f[k_esp])
        fr, dbr = S.para_dibujar(f, db, puntos=900)

        esp = S.Espectro(fr, dbr, piso=-70.0, techo=5.0, ancho=10.8,
                         alto=4.0, color=C_SENAL)
        esp.move_to(UP * 0.15)
        marca_t = esp.marca_f(f_tono, color=C_SENAL)
        etiq_t = tag_junto(marca_t, "tono", UP, buff=0.16, font_size=19,
                           color=C_SENAL)
        marca_e = esp.marca_f(f_esp, color=C_RUIDO)
        etiq_e = tag_junto(marca_e, "espurio", UP, buff=0.16, font_size=19,
                           color=C_RUIDO)

        self.play(Create(esp.ejes), run_time=0.5)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=1.8)
        self.wait(0.6)
        self.play(Create(marca_t), FadeIn(etiq_t), run_time=0.6)
        self.wait(0.8)
        self.play(Create(marca_e), FadeIn(etiq_e), run_time=0.6)
        self.wait(1.6)

        rot.mostrar(cifra_pie(f"espurio {fmt(ESP_MUCHA, 1)} dBc"),
                    zona="abajo", run_time=0.5)
        self.wait(9.5)
