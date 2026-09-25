class Clip3(Scene):
    """6.3.3 - El factor de dispersion: SF7 y SF12 en la MISMA escala de
    tiempo. 32 simbolos de SF7 caben en el tiempo de un solo simbolo de
    SF12. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El factor de dispersion"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        sf_corto, sf_largo = 7, 12
        t_corto, t_largo = T_SIMB[sf_corto], T_SIMB[sf_largo]
        factor = 2 ** (sf_largo - sf_corto)

        ancho = 9.0
        x_off = LEFT * 1.75
        x0, x1 = 0.0, t_largo
        alto_lane = 1.55
        y_corto, y_largo = UP * 1.55, DOWN * 1.55

        def carril(centro, escala_y=1.0):
            def P(x, y):
                fx = (x - x0) / (x1 - x0)
                return centro + x_off + RIGHT * (fx - 0.5) * ancho \
                    + UP * (y / (BW / 2.0)) * (alto_lane / 2.0) * escala_y
            return P

        P7 = carril(y_corto)
        P12 = carril(y_largo)

        eje7 = Line(P7(x0, 0), P7(x1, 0), color=C_EJE, stroke_width=1.8)
        eje12 = Line(P12(x0, 0), P12(x1, 0), color=C_EJE, stroke_width=1.8)
        self.play(Create(eje7), Create(eje12), run_time=0.6)

        t7 = tag_junto(eje7, "SF7", LEFT, buff=0.22, font_size=22)
        t12 = tag_junto(eje12, "SF12", LEFT, buff=0.22, font_size=22)
        self.play(FadeIn(t7), FadeIn(t12), run_time=0.4)
        self.wait(0.3)

        # --- SF7: 32 dientes iguales (S.chirp_lora repetido) ---------------
        c7 = S.chirp_lora(sf_corto, 0)
        n7 = 2 ** sf_corto
        ang7 = np.unwrap(np.angle(c7))
        finst7 = np.diff(ang7) / (2 * np.pi) * BW
        t_local7 = np.arange(len(finst7)) / n7 * t_corto
        dientes = VGroup()
        for rep in range(factor):
            pts = [P7(rep * t_corto + tt, ff)
                  for tt, ff in zip(t_local7, finst7)]
            seg = VMobject(stroke_color=C_SENAL, stroke_width=2.2)
            seg.set_points_as_corners(pts)
            dientes.add(seg)
        self.play(LaggedStart(*[Create(m) for m in dientes], lag_ratio=0.03),
                  run_time=2.4)
        self.wait(2.0)

        # --- SF12: un solo diente gigante (S.chirp_lora), submuestreado ----
        c12 = S.chirp_lora(sf_largo, 0)
        n12 = 2 ** sf_largo
        ang12 = np.unwrap(np.angle(c12))
        finst12 = np.diff(ang12) / (2 * np.pi) * BW
        t_local12 = np.arange(len(finst12)) / n12 * t_largo
        idx = np.linspace(0, len(finst12) - 1, 380).astype(int)
        pts12 = [P12(t_local12[i], finst12[i]) for i in idx]
        diente_largo = VMobject(stroke_color=C_SENAL, stroke_width=3.4)
        diente_largo.set_points_as_corners(pts12)
        self.play(Create(diente_largo), run_time=2.4)
        self.wait(2.5)

        fx = tag_hud(f"{factor}x", font_size=26, color=C_CALCULO)
        fx.move_to(x_off)
        self.play(FadeIn(fx, scale=0.7), run_time=0.6)
        self.wait(2.0)

        # --- panel: a la DERECHA de los carriles (zona libre, sin lineas) ---
        panel = panel_cifras(f"SF7  {fmt(t_corto, 2)} ms",
                             f"SF9  {fmt(T_SIMB[9], 2)} ms",
                             f"SF12 {fmt(t_largo, 1)} ms")
        panel.move_to(RIGHT * 4.7)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(4.0)

        rot.mostrar(cifra_pie(f"{factor}x mas largo"), zona="abajo",
                    run_time=0.5)
        self.wait(10.5)
