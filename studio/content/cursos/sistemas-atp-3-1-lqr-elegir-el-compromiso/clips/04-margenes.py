class Clip4(Scene):
    """3.1.4 - Los margenes del lazo LQR, MEDIDOS barriendo frecuencia:
    margen de fase 67.3 grados y de ganancia infinito, porque la fase
    nunca llega a -180. Un retardo de 50 ms se come 9.5 grados y aun
    sobra. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Los margenes del lazo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el barrido en frecuencia que ya trae la libreria ---------------
        w, mag, fase = MARG["w"], MARG["mag_db"], MARG["fase_deg"]
        sel = (w >= 0.1) & (w <= 10.0)
        lw = np.log10(w[sel])
        mag_v, fase_v = mag[sel], fase[sel]
        # un retardo puro no toca la magnitud: solo resta w*tau de fase
        fase_r = fase_v - np.degrees(w[sel] * RETARDO)
        lwc = float(np.log10(WC))

        # Los ejes se dibujan a mano y NO con `Axes`: manim cruza los ejes
        # por el origen, asi que un panel de 0 a 50 dB deja la vertical en
        # mitad del cuadro y uno de -190 a -85 grados deja la horizontal
        # PISANDO la curva. Aqui van al borde, como en `atp._ejes`.
        def panel(centro, x0, x1, y0, y1, ancho=5.6, alto=1.5):
            o = centro + np.array([-ancho / 2.0, -alto / 2.0, 0.0])

            def p(x, y):
                return o + np.array([(x - x0) / (x1 - x0) * ancho,
                                     (y - y0) / (y1 - y0) * alto, 0.0])

            marco = VGroup(
                Line(p(x0, y0), p(x1, y0), stroke_width=2.2, color=C_EJE),
                Line(p(x0, y0), p(x0, y1), stroke_width=2.2, color=C_EJE))
            return p, marco

        pm, ej_m = panel(np.array([-2.55, 1.20, 0.0]), -1.0, 1.0, -15.0, 50.0)
        pf, ej_f = panel(np.array([-2.55, -1.20, 0.0]), -1.0, 1.0,
                         -190.0, -85.0)

        t_m = tag_hud("|L| dB", font_size=17, color=C_TENUE)
        t_m.move_to(pm(-1.0, 50.0) + UP * 0.20 + RIGHT * 0.30)
        t_f = tag_hud("fase deg", font_size=17, color=C_TENUE)
        t_f.move_to(pf(-1.0, -85.0) + UP * 0.20 + RIGHT * 0.38)
        t_w = tag_hud("w (rad/s log)", font_size=17, color=C_TENUE)
        t_w.move_to(pf(1.0, -190.0) + DOWN * 0.28 + LEFT * 0.55)

        def traza(p, ys, color, grosor=3.4):
            c = VMobject(color=color, stroke_width=grosor)
            c.set_points_as_corners([p(a, b) for a, b in zip(lw, ys)])
            return c

        # --- la magnitud y su cruce por 0 dB --------------------------------
        cero = DashedVMobject(
            Line(pm(-1.0, 0.0), pm(1.0, 0.0), stroke_width=2.0,
                 color=C_TENUE), num_dashes=28)
        c_mag = traza(pm, mag_v, C_CALCULO)
        self.play(Create(ej_m), FadeIn(t_m), run_time=0.8)
        self.play(Create(cero), run_time=0.5)
        self.play(Create(c_mag), run_time=1.4)

        m_wc_m = DashedVMobject(
            Line(pm(lwc, -15.0), pm(lwc, 50.0), stroke_width=2.4,
                 color=C_SAT), num_dashes=12)
        d_wc = Dot(pm(lwc, 0.0), radius=0.075, color=C_SAT)
        self.play(Create(m_wc_m), FadeIn(d_wc, scale=1.6), run_time=0.8)
        rot.mostrar(cifra_pie(f"wc {fmt(WC, 2)} rad/s"), zona="abajo")
        self.wait(2.0)

        # --- la fase, y la linea que nunca se toca --------------------------
        menos180 = DashedVMobject(
            Line(pf(-1.0, -180.0), pf(1.0, -180.0), stroke_width=2.2,
                 color=C_PELIGRO), num_dashes=28)
        c_fase = traza(pf, fase_v, C_CALCULO)
        self.play(Create(ej_f), FadeIn(t_f), FadeIn(t_w), run_time=0.8)
        self.play(Create(menos180), run_time=0.5)
        self.play(Create(c_fase), run_time=1.4)

        m_wc_f = DashedVMobject(
            Line(pf(lwc, -190.0), pf(lwc, -85.0), stroke_width=2.4,
                 color=C_SAT), num_dashes=12)
        d_f = Dot(pf(lwc, -180.0 + MF), radius=0.075, color=C_OK)
        self.play(Create(m_wc_f), FadeIn(d_f, scale=1.6), run_time=0.8)
        self.wait(0.5)

        # --- el margen de fase, contra su objetivo, a la MISMA escala -------
        esc = float(np.linalg.norm(pf(0.0, -180.0) - pf(0.0, -179.0)))
        # Space Mono a 18 px anda por 0.148 unidades de ancho POR CARACTER:
        # "MF 67.3 deg" mide 1.6 y no 1.1, asi que las dos barras piden
        # 1.85 de separacion o los rotulos de abajo se pisan.
        base = np.array([1.85, -1.95, 0.0])
        base2 = base + RIGHT * 1.85
        b_mf = Line(base, base + UP * MF * esc, color=C_OK, stroke_width=8)
        b_obj = Line(base2, base2 + UP * MF_OBJETIVO * esc, color=C_DATO,
                     stroke_width=8)
        t_mf = tag_hud(f"MF {fmt(MF, 1)} deg", font_size=18, color=C_OK)
        t_mf.move_to(base + DOWN * 0.28)
        t_obj = tag_hud(f"obj {fmt(MF_OBJETIVO, 0)} deg", font_size=18,
                        color=C_DATO)
        t_obj.move_to(base2 + DOWN * 0.28)
        self.play(GrowFromEdge(b_mf, DOWN), FadeIn(t_mf), run_time=0.8)
        self.play(GrowFromEdge(b_obj, DOWN), FadeIn(t_obj), run_time=0.7)
        rot.mostrar(cifra_pie(f"MF {fmt(MF, 1)} deg"), zona="abajo")
        self.wait(2.2)

        # --- el margen de ganancia: la fase NO llega a -180 -----------------
        t_nunca = tag_hud("nunca cruza -180", font_size=18, color=C_OK)
        t_nunca.move_to(pf(-0.34, -180.0) + UP * 0.24)
        self.play(Indicate(menos180, color=C_PELIGRO, scale_factor=1.0),
                  FadeIn(t_nunca), run_time=1.0)
        rot.mostrar(formula_pie(r"\mathrm{MG} = \infty"), zona="abajo")
        self.wait(2.4)

        # --- lo que se come un lazo digital de 50 ms ------------------------
        c_ret = DashedVMobject(traza(pf, fase_r, C_PELIGRO, 3.0),
                               num_dashes=60)
        d_ret = Dot(pf(lwc, -180.0 + MF_RETARDO), radius=0.075,
                    color=C_PELIGRO)
        rot.mostrar(cifra_pie(f"retardo {fmt(RETARDO * 1000.0, 0)} ms"),
                    zona="abajo")
        self.play(Create(c_ret), run_time=1.4)
        self.play(FadeIn(d_ret, scale=1.6),
                  Transform(b_mf, Line(base, base + UP * MF_RETARDO * esc,
                                       color=C_OK, stroke_width=8)),
                  run_time=1.0)
        # Dos rotulos de igual longitud siguen sin ser gemelos de
        # estructura: se relevan por fundido, en dos play seguidos.
        self.play(FadeOut(t_mf), run_time=0.3)
        t_mf2 = tag_hud(f"MF {fmt(MF_RETARDO, 1)} deg", font_size=18,
                        color=C_OK)
        t_mf2.move_to(base + DOWN * 0.28)
        self.play(FadeIn(t_mf2), run_time=0.3)
        rot.mostrar(cifra_pie(f"pierde {fmt(MF - MF_RETARDO, 1)} deg"),
                    zona="abajo")
        self.wait(2.0)
        rot.mostrar(cifra_pie(f"MF {fmt(MF_RETARDO, 1)} deg"), zona="abajo")
        self.wait(2.0)

        # --- la advertencia que NO se mide aqui: es literatura --------------
        rot.mostrar(dato_pie("LQG no hereda garantias"), zona="abajo")
        self.wait(2.0)
        rot.mostrar(dato_pie("Doyle 1978"), zona="abajo")
        self.wait(1.8)

        panel_ur = panel_cifras((f"MF {fmt(MF, 1)} deg", C_OK),
                                ("MG infinito", C_OK),
                                f"wc {fmt(WC, 2)} rad/s",
                                (f"con retardo {fmt(MF_RETARDO, 1)}", C_SAT))
        self.play(FadeIn(panel_ur), run_time=0.7)
        self.wait(2.2)

        # --- el cierre literal de la leccion ---------------------------------
        todo = VGroup(ej_m, ej_f, cero, menos180, c_mag, c_fase, c_ret,
                      m_wc_m, m_wc_f, d_wc, d_f, d_ret, t_m, t_f, t_w,
                      t_nunca, b_mf, b_obj, t_mf2, t_obj, panel_ur)
        cierre_leccion(self, rot,
                       "Q y R no son ganancias",
                       "son una declaracion de prioridades.",
                       todo, espera=4.0)
