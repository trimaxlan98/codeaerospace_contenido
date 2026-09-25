class Clip4(Scene):
    """6.3.4 - Bajo el ruido: un simbolo de SF12 enterrado a -20 dB no se
    ve en el tiempo, pero su FFT (tras quitar el chirp) tiene un pico
    claro en el simbolo correcto. Cierre de la leccion. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Bajo el ruido"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        sf = 12
        n = 2 ** sf
        simbolo = 555
        semilla = 2
        rx = S.chirp_lora(sf, simbolo) + S.ruido_complejo(
            n, 10 ** (20 / 10), semilla)

        # --- la traza en el tiempo: puro ruido a la vista -------------------
        idx = np.linspace(0, n - 1, 380).astype(int)
        muestra = rx.real[idx]
        ymax = float(np.max(np.abs(muestra))) * 1.08
        ancho, alto = 10.6, 3.0
        centro = UP * 0.85
        x0, x1 = 0.0, T_SIMB[sf]
        t_ms = idx / n * T_SIMB[sf]

        def P(x, y):
            fx = (x - x0) / (x1 - x0)
            fy = (y + ymax) / (2 * ymax)
            return centro + RIGHT * (fx - 0.5) * ancho \
                + UP * (fy - 0.5) * alto

        eje_x = Line(P(x0, 0), P(x1, 0), color=C_EJE, stroke_width=1.6)
        traza = VMobject(stroke_color=C_RUIDO, stroke_width=1.8)
        traza.set_points_as_corners([P(tt, yy) for tt, yy in
                                     zip(t_ms, muestra)])
        et_traza = tag_junto(eje_x, "amplitud", UP, buff=1.55,
                             font_size=20, color=C_TENUE)
        self.play(Create(eje_x), run_time=0.4)
        self.play(Create(traza), FadeIn(et_traza), run_time=1.8)
        self.wait(0.8)
        rot.mostrar(dato_pie("-20 dB enterrado"), zona="abajo", run_time=0.5)
        self.wait(4.0)

        # --- quitar el chirp y mirar la FFT ---------------------------------
        rot.limpiar(zona="abajo", run_time=0.3)
        self.play(FadeOut(traza), FadeOut(eje_x), FadeOut(et_traza),
                  run_time=0.6)

        base = S.chirp_lora(sf, 0)
        tono = rx * np.conj(base)
        espectro_x = np.fft.fft(tono)
        db = S.db10(np.abs(espectro_x) ** 2)
        db = db - db.max()
        bins = np.arange(n)
        f_r, db_r = S.para_dibujar(bins, db, puntos=820)
        esp = S.Espectro(f_r, db_r, piso=-30.0, techo=2.0, ancho=11.0,
                         alto=3.7, color=C_OK)
        esp.move_to(DOWN * 0.15)
        ticks = esp.marcas([0, 1024, 2048, 3072, 4095],
                           ["0", "1024", "2048", "3072", "4095"])
        self.play(Create(esp.ejes), FadeIn(ticks), run_time=0.5)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=1.6)
        self.wait(1.6)

        hallado = S.lora_demodular(rx, sf)
        marca = esp.marca_f(hallado, color=C_CALCULO)
        self.play(Create(marca), run_time=0.6)
        rot.mostrar(cifra_pie(f"simbolo {hallado}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        # --- los tres umbrales, en cian -------------------------------------
        panel = panel_cifras(f"SF7  {fmt(UMBRAL[7], 1)}",
                             f"SF9  {fmt(UMBRAL[9], 1)}",
                             f"SF12 {fmt(UMBRAL[12], 1)}")
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(4.4)

        cierre_leccion(self, rot, "Mas lento, mas lejos.",
                       "Por debajo del ruido.", esp, ticks, marca, panel,
                       espera=6.5)
