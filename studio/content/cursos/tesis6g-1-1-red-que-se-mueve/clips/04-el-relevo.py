class Clip4(Scene):
    """1.1.4 - Un tren de cuatro satelites que se relevan: con solape la
    estacion no se queda sola; si los pases solo se tocan, la rotacion de
    la Tierra ya abre un hueco. Cierre de la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El relevo"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        t_max = max(HO_SOLAPE["t_s"][-1], HO_TOCAN["t_s"][-1])
        X0, X1, Y0, Y1 = -5.0, 6.2, -2.3, 2.1
        e_max = 90.0
        xy = lambda t, e: np.array([X0 + (X1 - X0) * t / t_max,
                                    Y0 + (Y1 - Y0) * np.clip(e, 0, e_max) / e_max, 0.0])
        base = Line(xy(0, 0), xy(t_max, 0), stroke_color=C_TENUE, stroke_width=2)
        umbral = DashedLine(xy(0, EL_MIN), xy(t_max, EL_MIN), dash_length=0.1,
                            stroke_color=C_ENLACE, stroke_width=2)
        et_u = tag_hud(f"{fmt(EL_MIN, 0)} grados", font_size=17, color=C_ENLACE)
        et_u.next_to(umbral, LEFT, buff=0.15)
        et_t = tag_junto(base, "tiempo", DOWN, buff=0.16, font_size=20)
        et_t.align_to(base, RIGHT)
        self.play(Create(base), Create(umbral), FadeIn(et_u), FadeIn(et_t), run_time=1.0)
        self.wait(1.4)

        colores = [C_ADAPTA, C_PRIV, C_OK, C_ENLACE]

        def cascada(h):
            g = VGroup()
            for k in range(h["n_sats"]):
                fino = VMobject(stroke_color=colores[k], stroke_width=2, stroke_opacity=0.35)
                fino.set_points_as_corners([xy(t, e) for t, e in zip(h["t_s"], h["elev"][k])
                                            if e > -5])
                g.add(fino)
            servido = VGroup()
            for k in range(h["n_sats"]):
                m = h["servidor"] == k
                idx = np.nonzero(m)[0]
                if idx.size < 2:
                    continue
                grueso = VMobject(stroke_color=colores[k], stroke_width=6)
                grueso.set_points_as_corners([xy(h["t_s"][i], h["elev"][k][i]) for i in idx])
                servido.add(grueso)
            return g, servido

        finos, gruesos = cascada(HO_SOLAPE)
        self.play(LaggedStart(*[Create(f) for f in finos], lag_ratio=0.25), run_time=3.0)
        self.wait(1.0)
        self.play(LaggedStart(*[Create(s) for s in gruesos], lag_ratio=0.25), run_time=3.0)
        relevos = VGroup(*[DashedLine(xy(t, 0), xy(t, 88), dash_length=0.08,
                                      stroke_color=CODE_INK, stroke_width=1.5,
                                      stroke_opacity=0.7) for t in HO_SOLAPE["relevos_s"]])
        self.play(Create(relevos), run_time=0.8)
        self.wait(1.0)
        rot.mostrar(cifra_pie(f"relevos = {len(HO_SOLAPE['relevos_s'])}  cobertura = "
                              f"{fmt(100 * HO_SOLAPE['cobertura'], 0)} %"), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)

        # --- los pases solo se tocan: la Tierra gira y abre un hueco -------
        finos2, gruesos2 = cascada(HO_TOCAN)
        rot.limpiar("abajo", run_time=0.3)      # la cifra vieja sale ANTES del relevo
        self.play(FadeOut(relevos), FadeOut(gruesos), run_time=0.6)
        self.play(ReplacementTransform(finos, finos2), run_time=1.8)
        self.play(LaggedStart(*[Create(s) for s in gruesos2], lag_ratio=0.25), run_time=2.4)
        self.wait(1.0)
        rot.mostrar(cifra_pie(f"hueco = {fmt(HO_TOCAN['hueco_s'], 0)} s"), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)

        cierre_leccion(self, rot, "La red no esta siempre ahi.",
                       "Se gobierna, no se fija.",
                       finos2, gruesos2, base, umbral, et_u, et_t)
