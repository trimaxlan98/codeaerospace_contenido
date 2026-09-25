class Clip2(Scene):
    """6.3.2 - Quitar el chirp: rx (simbolo 90, SF7) por el chirp base
    conjugado se vuelve un tono; su FFT de 128 bins da UN pico en el
    simbolo. Antes -> despues -> FFT. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Quitar el chirp"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        sf = 7
        n = 2 ** sf
        simbolo = 90
        t_simb = T_SIMB[sf]
        ancho, alto = 10.8, 4.6
        centro = DOWN * 0.15
        x0, x1 = 0.0, t_simb
        y0, y1 = -BW / 2.0, BW / 2.0

        def P(x, y):
            fx = (x - x0) / (x1 - x0)
            fy = (y - y0) / (y1 - y0)
            return centro + RIGHT * (fx - 0.5) * ancho + UP * (fy - 0.5) * alto

        eje_x = Line(P(x0, 0), P(x1, 0), color=C_EJE, stroke_width=1.8)
        eje_y = Line(P(0, y0), P(0, y1), color=C_EJE, stroke_width=1.8)
        self.play(Create(eje_x), Create(eje_y), run_time=0.5)

        etiqueta = tag_junto(eje_y, "antes", UP, buff=0.18, font_size=22,
                             color=C_TENUE)
        self.play(FadeIn(etiqueta), run_time=0.4)

        # --- "antes": la sierra del simbolo 90 (S.chirp_lora) --------------
        c = S.chirp_lora(sf, simbolo)
        base = S.chirp_lora(sf, 0)
        ang_c = np.unwrap(np.angle(c))
        finst_c = np.diff(ang_c) / (2 * np.pi) * BW
        tiempos = np.arange(len(finst_c)) / n * t_simb
        cortes = np.flatnonzero(np.abs(np.diff(finst_c)) > BW * 0.5)
        inicio = 0
        tramos = []
        for k in cortes:
            tramos.append((tiempos[inicio:k + 1], finst_c[inicio:k + 1]))
            inicio = k + 1
        tramos.append((tiempos[inicio:], finst_c[inicio:]))
        sierra = VGroup()
        for tp, fp in tramos:
            if len(tp) < 2:
                continue
            pts = [P(tt, ff) for tt, ff in zip(tp, fp)]
            seg = VMobject(stroke_color=C_SENAL, stroke_width=3.4)
            seg.set_points_as_corners(pts)
            sierra.add(seg)
        dot0 = Dot(P(tiempos[0], finst_c[0]), radius=0.07, color=C_CALCULO)
        lab0 = tag_hud(f"simbolo {simbolo}", font_size=20, color=C_CALCULO)
        lab0.next_to(dot0, DOWN, buff=0.18)

        self.play(LaggedStart(*[Create(m) for m in sierra], lag_ratio=0.15),
                  run_time=2.0)
        self.play(FadeIn(dot0), FadeIn(lab0), run_time=0.5)
        self.wait(3.5)

        # --- "despues": el tono (rx * conj(chirp base)) --------------------
        tono = c * np.conj(base)
        ang_t = np.unwrap(np.angle(tono))
        finst_t = np.diff(ang_t) / (2 * np.pi) * BW
        pts_t = [P(tt, ff) for tt, ff in zip(tiempos, finst_t)]
        recta = VMobject(stroke_color=C_SENAL, stroke_width=3.4)
        recta.set_points_as_corners(pts_t)

        etiqueta2 = tag_junto(eje_y, "despues", UP, buff=0.18, font_size=22,
                              color=C_TENUE)
        self.play(FadeOut(sierra), FadeOut(dot0), FadeOut(lab0),
                  FadeOut(etiqueta), run_time=0.6)
        self.play(FadeIn(etiqueta2), run_time=0.4)
        self.play(Create(recta), run_time=1.4)
        rot.mostrar(cifra_pie("frecuencia constante"), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)

        # --- la FFT: un pico en el simbolo -----------------------------
        rot.limpiar(zona="abajo", run_time=0.3)
        self.play(FadeOut(recta), FadeOut(etiqueta2), FadeOut(eje_x),
                  FadeOut(eje_y), run_time=0.6)

        espectro_x = np.fft.fft(tono)
        db = S.db10(np.abs(espectro_x) ** 2)
        db = db - db.max()
        bins = np.arange(n)
        esp = S.Espectro(bins, db, piso=-40.0, techo=2.0, ancho=10.8,
                         alto=3.7, color=C_SENAL)
        esp.move_to(DOWN * 0.1)
        ticks = esp.marcas([0, 32, 64, 90, 127],
                           ["0", "32", "64", "90", "127"])
        self.play(Create(esp.ejes), FadeIn(ticks), run_time=0.5)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=1.4)
        self.wait(2.0)

        hallado = S.lora_demodular(c, sf)
        marca = esp.marca_f(hallado, color=C_CALCULO)
        self.play(Create(marca), run_time=0.6)
        rot.mostrar(cifra_pie(f"simbolo {hallado}"), zona="abajo",
                    run_time=0.5)
        self.wait(9.0)
