class Clip3(Scene):
    """3.3.3 - Nadie regala nada: la ventana ensancha el filtro de cada
    bin (ENBW) y pierde nivel con el tono entre bins. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Lo que cuesta la ventana"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        col = {"rect": C_RUIDO, "hann": C_CALCULO,
               "hamming": C_MUESTRA, "blackman": C_IDEAL}
        nom = {"rect": "rect", "hann": "hann",
               "hamming": "hamm", "blackman": "black"}

        # --- el scalloping: el tono se aleja del centro del bin ------------
        bins_s = np.arange(95, 106)

        def _mag(d):
            f = f_de_bin(100 + d, FS_V, N_S)
            x = np.cos(2 * np.pi * f * T_V)
            _, db = espectro(x, FS_V, ventana="hann", norm=False)
            return 10.0 ** (db[bins_s] / 20.0)

        ref = float(_mag(0.0).max())
        pasos = (0.0, 0.17, 0.33, 0.5)
        vals = {d: _mag(d) / ref for d in pasos}

        bar = barras(vals[0.0], ancho=6.6, alto=2.2, color=C_MUESTRA,
                     rango_y=(0.0, 1.15))
        bar.move_to(UP * 0.15)
        et_v = tag_hud("hann", font_size=19, color=C_CALCULO)
        et_v.next_to(bar, LEFT, buff=0.34)
        et_d = tag_hud(f"tono en bin {fmt(100.0, 2)}", font_size=20,
                       color=C_MUESTRA)
        et_d.next_to(bar, UP, buff=0.42)
        self.play(FadeIn(bar), FadeIn(et_v), run_time=0.8)
        self.play(FadeIn(et_d), run_time=0.4)

        alto_ref = bar.cima(5)[1]
        linea_ref = DashedLine(np.array([bar.get_left()[0], alto_ref, 0.0]),
                               np.array([bar.get_right()[0], alto_ref, 0.0]),
                               color=C_IDEAL, stroke_width=1.8,
                               dash_length=0.08)
        self.play(Create(linea_ref), run_time=0.7)
        self.wait(1.6)

        for d in pasos[1:]:
            gem = bar.con_valores(vals[d])
            nuevo = tag_hud(f"tono en bin {fmt(100 + d, 2)}", font_size=20,
                            color=C_MUESTRA)
            nuevo.move_to(et_d)
            self.play(Transform(bar, gem), Transform(et_d, nuevo),
                      run_time=1.2)
            self.wait(0.9)

        rot.mostrar(cifra_pie(f"perdida = {fmt(SCALLOP['hann'], 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- las cuatro, en las dos cuentas que cuestan --------------------
        self.play(FadeOut(VGroup(bar, et_v, et_d, linea_ref)), run_time=0.7)

        b_e = barras([ENBW[v] for v in VENTANAS], ancho=4.2, alto=2.1,
                     color=C_MUESTRA, rango_y=(0.0, 2.0))
        b_e.move_to(LEFT * 3.3 + UP * 0.05)
        b_s = barras([abs(SCALLOP[v]) for v in VENTANAS], ancho=4.2,
                     alto=2.1, color=C_BANDA, rango_y=(0.0, 4.6))
        b_s.move_to(RIGHT * 3.3 + UP * 0.05)

        def _nombres(chart):
            g = VGroup()
            for i, v in enumerate(VENTANAS):
                t = tag_hud(nom[v], font_size=17, color=C_TENUE)
                t.next_to(chart.barra(i), DOWN, buff=0.16)
                g.add(t)
            return g

        def _valores(chart, textos):
            g = VGroup()
            for i, v in enumerate(VENTANAS):
                t = tag_hud(textos[i], font_size=17, color=col[v])
                t.next_to(chart.barra(i), UP, buff=0.14)
                g.add(t)
            return g

        cab_e = tag_hud("ruido: ENBW bins", font_size=19, color=C_MUESTRA)
        cab_e.next_to(b_e, UP, buff=0.62)
        cab_s = tag_hud("perdida entre bins", font_size=19, color=C_BANDA)
        cab_s.next_to(b_s, UP, buff=0.62)
        nom_e, nom_s = _nombres(b_e), _nombres(b_s)
        val_e = _valores(b_e, [fmt(ENBW[v], 3) for v in VENTANAS])
        val_s = _valores(b_s, [fmt(SCALLOP[v], 2) for v in VENTANAS])

        self.play(FadeIn(b_e), FadeIn(nom_e), FadeIn(cab_e), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(t) for t in val_e], lag_ratio=0.18),
                  run_time=1.1)
        rot.mostrar(cifra_pie(f"ENBW hann = {fmt(ENBW['hann'], 3)} bins"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        self.play(FadeIn(b_s), FadeIn(nom_s), FadeIn(cab_s), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(t) for t in val_s], lag_ratio=0.18),
                  run_time=1.1)
        rot.mostrar(cifra_pie(f"peor caso: {fmt(SCALLOP['rect'], 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- hann, el compromiso habitual ----------------------------------
        self.play(b_e.barra(1).animate.set_fill(C_CALCULO, opacity=0.85)
                  .set_stroke(C_CALCULO),
                  b_s.barra(1).animate.set_fill(C_CALCULO, opacity=0.85)
                  .set_stroke(C_CALCULO),
                  nom_e[1].animate.set_color(C_CALCULO),
                  nom_s[1].animate.set_color(C_CALCULO), run_time=0.9)
        rot.mostrar(cifra_pie(f"hann: {fmt(ENBW['hann'], 3)} bins, "
                              f"{fmt(SCALLOP['hann'], 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
