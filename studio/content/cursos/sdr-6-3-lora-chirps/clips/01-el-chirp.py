class Clip1(Scene):
    """6.3.1 - El chirp LoRa: frecuencia instantanea en diente de sierra;
    4 simbolos de SF7 seguidos, cada uno empieza donde dice su valor.
    (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El chirp"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        sf = 7
        n = 2 ** sf
        simbolos = [0, 40, 90, 17]
        t_simb = T_SIMB[sf]
        ancho, alto = 11.6, 4.4
        centro = DOWN * 0.15
        x0, x1 = 0.0, len(simbolos) * t_simb
        y0, y1 = -BW / 2.0, BW / 2.0

        def P(x, y):
            fx = (x - x0) / (x1 - x0)
            fy = (y - y0) / (y1 - y0)
            return centro + RIGHT * (fx - 0.5) * ancho + UP * (fy - 0.5) * alto

        eje_x = Line(P(x0, 0), P(x1, 0), color=C_EJE, stroke_width=1.8)
        eje_y = Line(P(0, y0), P(0, y1), color=C_EJE, stroke_width=1.8)
        self.play(Create(eje_x), Create(eje_y), run_time=0.6)

        t_ms = tag_junto(eje_x, "ms", RIGHT, buff=0.16, font_size=19,
                         color=C_TENUE)
        t_hz = tag_hud(f"+{fmt(BW / 2e3, 1)} kHz", font_size=17,
                       color=C_TENUE)
        t_hz.next_to(P(0, y1), UP, buff=0.14)
        t_hz2 = tag_hud(f"-{fmt(BW / 2e3, 1)} kHz", font_size=17,
                        color=C_TENUE)
        t_hz2.next_to(P(0, y0), DOWN, buff=0.14)
        self.play(FadeIn(t_ms), FadeIn(t_hz), FadeIn(t_hz2), run_time=0.5)
        self.wait(0.4)

        # --- las 4 sierras (calculadas con S.chirp_lora) -------------------
        segmentos = VGroup()
        marcas = VGroup()
        for i, s in enumerate(simbolos):
            c = S.chirp_lora(sf, s)
            ang = np.unwrap(np.angle(c))
            finst = np.diff(ang) / (2 * np.pi) * BW
            tiempos = i * t_simb + np.arange(len(finst)) / n * t_simb
            cortes = np.flatnonzero(np.abs(np.diff(finst)) > BW * 0.5)
            inicio = 0
            tramos = []
            for k in cortes:
                tramos.append((tiempos[inicio:k + 1], finst[inicio:k + 1]))
                inicio = k + 1
            tramos.append((tiempos[inicio:], finst[inicio:]))
            for tp, fp in tramos:
                if len(tp) < 2:
                    continue
                pts = [P(tt, ff) for tt, ff in zip(tp, fp)]
                seg = VMobject(stroke_color=C_SENAL, stroke_width=3.4)
                seg.set_points_as_corners(pts)
                segmentos.add(seg)
            p0 = P(tiempos[0], finst[0])
            arriba = finst[0] > 0
            dot = Dot(p0, radius=0.065, color=C_CALCULO)
            lab = tag_hud(str(s), font_size=20, color=C_CALCULO)
            lab.next_to(p0, UP if not arriba else DOWN, buff=0.16)
            marcas.add(dot, lab)

        self.play(LaggedStart(*[Create(m) for m in segmentos], lag_ratio=0.12),
                  run_time=3.2)
        self.wait(1.0)
        self.play(LaggedStart(*[FadeIn(m) for m in marcas], lag_ratio=0.18),
                  run_time=1.8)
        self.wait(3.0)

        rot.mostrar(dato_pie(f"BW {fmt(BW / 1e3, 0)} kHz"), zona="abajo",
                    run_time=0.5)
        self.wait(7.0)
        rot.mostrar(cifra_pie(f"T simbolo {fmt(t_simb, 2)} ms"), zona="abajo",
                    run_time=0.5)
        self.wait(12.0)
