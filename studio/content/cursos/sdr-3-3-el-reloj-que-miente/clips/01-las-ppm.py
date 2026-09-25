class Clip1(Scene):
    """3.3.1 - Las ppm: el error de un cristal barato (25 ppm) crece con
    la frecuencia (2.5/10.9/27.2 kHz a 100/437/1090 MHz -- fmt() redondea
    27.25 a 27.2, mitad exacta a par); con un TCXO de 1 ppm los mismos
    tres se encogen a 0.1/0.4/1.1 kHz, en la MISMA escala vertical. (~29 s)
    """

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Las ppm"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- escala unica, en kHz -------------------------------------
        Y0 = -2.05
        Y_TOP = 2.35
        MAX_KHZ = max(ERR25) / 1e3
        ESCALA = MAX_KHZ * 1.10          # margen para el rotulo de arriba
        XS = [-3.9, 0.0, 3.9]
        BAR_W = 1.9
        ETQ_F = ["100 MHz", "437 MHz", "1090 MHz"]

        def alto(khz):
            return (Y_TOP - Y0) * khz / ESCALA

        eje = Line(np.array([-5.3, Y0, 0.0]), np.array([5.3, Y0, 0.0]),
                  color=C_EJE, stroke_width=2.0)
        u = tag_junto(eje, "kHz de error", UP, buff=0.14, font_size=19)
        u.move_to(np.array([-4.5, Y_TOP + 0.12, 0.0]))
        self.play(Create(eje), FadeIn(u), run_time=0.7)
        self.wait(0.3)

        khz25 = [e / 1e3 for e in ERR25]
        barras, etqs = VGroup(), VGroup()
        for x, khz, fetq in zip(XS, khz25, ETQ_F):
            h = max(alto(khz), 0.02)
            b = Rectangle(width=BAR_W, height=h, stroke_color=C_CALCULO,
                         fill_color=C_CALCULO, fill_opacity=0.30,
                         stroke_width=2.4)
            b.move_to(np.array([x, Y0 + h / 2, 0.0]))
            e = tag_junto(b, fetq, DOWN, buff=0.18, font_size=20)
            barras.add(b)
            etqs.add(e)

        dato_ppm = tag_dato("cristal: 25 ppm", font_size=19)
        dato_ppm.next_to(u, DOWN, buff=0.55).align_to(u, LEFT)

        self.play(FadeIn(dato_ppm, shift=DOWN * 0.1), run_time=0.5)
        self.wait(0.4)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in barras],
                              lag_ratio=0.28),
                  LaggedStart(*[FadeIn(e) for e in etqs], lag_ratio=0.28),
                  run_time=1.7)
        self.wait(0.3)
        cifras = VGroup()
        for b, khz in zip(barras, khz25):
            c = tag_hud(f"{fmt(khz, 1)} kHz", font_size=21)
            c.next_to(b, UP, buff=0.15)
            cifras.add(c)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.08) for c in cifras],
                              lag_ratio=0.25), run_time=1.0)
        self.wait(6.5)

        # --- gemela: el mismo cristal, ahora un TCXO de 1 ppm -----------
        self.play(FadeOut(cifras), run_time=0.4)
        dato_tcxo = tag_dato("TCXO: 1 ppm", font_size=19)
        dato_tcxo.move_to(dato_ppm)
        self.play(Transform(dato_ppm, dato_tcxo), run_time=0.5)
        self.wait(0.7)

        khz1 = [e / 1e3 for e in ERR1]
        barras2 = VGroup()
        for x, khz in zip(XS, khz1):
            h = max(alto(khz), 0.02)
            b2 = Rectangle(width=BAR_W, height=h, stroke_color=C_CALCULO,
                          fill_color=C_CALCULO, fill_opacity=0.30,
                          stroke_width=2.4)
            b2.move_to(np.array([x, Y0 + h / 2, 0.0]))
            barras2.add(b2)
        self.play(*[Transform(b, b2) for b, b2 in zip(barras, barras2)],
                  run_time=1.6)
        self.wait(0.3)

        cifras2 = VGroup()
        for b, khz in zip(barras, khz1):
            c2 = tag_hud(f"{fmt(khz, 1)} kHz", font_size=21)
            c2.next_to(b, UP, buff=0.15)
            cifras2.add(c2)
        self.play(LaggedStart(*[FadeIn(c2, shift=UP * 0.08) for c2 in cifras2],
                              lag_ratio=0.25), run_time=1.0)
        self.wait(12.0)
