class Clip4(Scene):
    """6.3.4 - Goertzel: cuando solo interesa un bin, un biquad de dos
    memorias lo saca con 128 multiplicaciones en vez de 448 de una FFT,
    y con el mismo resultado exacto que la DFT. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("Goertzel"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- el biquad de dos memorias --------------------------------
        s1 = RoundedRectangle(corner_radius=0.08, width=1.0, height=0.6,
                              stroke_color=C_MUESTRA, stroke_width=2.2,
                              fill_color=CODE_BG, fill_opacity=1.0)
        s1.move_to(LEFT * 1.1 + UP * 1.3)
        s1_lbl = tag_hud("s1", font_size=20, color=C_MUESTRA)
        s1_lbl.move_to(s1)
        s2 = s1.copy()
        s2.move_to(RIGHT * 1.1 + UP * 1.3)
        s2_lbl = tag_hud("s2", font_size=20, color=C_MUESTRA)
        s2_lbl.move_to(s2)
        avance = Arrow(s1.get_right(), s2.get_left(), buff=0.08,
                      color=C_EJE, stroke_width=2.2)
        realim = CurvedArrow(s2.get_bottom(), s1.get_bottom(),
                             color=C_CALCULO, angle=-TAU / 5.5,
                             stroke_width=2.2)
        et_re = tag_hud("2 cos(w)", font_size=17, color=C_CALCULO)
        et_re.next_to(realim, DOWN, buff=0.14)
        biquad = VGroup(s1, s1_lbl, avance, s2, s2_lbl, realim, et_re)
        biquad.move_to(UP * 1.2)

        self.play(FadeIn(s1), FadeIn(s1_lbl), run_time=0.5)
        self.play(GrowArrow(avance), FadeIn(s2), FadeIn(s2_lbl), run_time=0.7)
        self.play(Create(realim), FadeIn(et_re), run_time=0.7)
        rot.mostrar(formula_pie(
            r"s[m] = x[m] + 2\cos(\omega)\,s_1 - s_2"), zona="abajo",
            run_time=0.5)
        self.wait(3.8)

        self.play(FadeOut(biquad), run_time=0.6)

        # --- el costo: 128 contra 448 ------------------------------------
        bar = Barras([MACS_G, MACS_FFT], ancho=5.0, alto=3.0,
                     color=C_CALCULO)
        bar.move_to(DOWN * 0.55)
        bar.barra(1).set_color(C_BANDA)
        et_g = tag_junto(bar.barra(0), "goertzel", DOWN, font_size=18,
                         color=C_MUESTRA)
        et_f = tag_junto(bar.barra(1), "fft", DOWN, font_size=18,
                         color=C_MUESTRA)
        val_g = tag_hud(f"{MACS_G}", font_size=19, color=C_CALCULO)
        val_g.next_to(bar.barra(0), UP, buff=0.14)
        val_f = tag_hud(f"{MACS_FFT}", font_size=19, color=C_BANDA)
        val_f.next_to(bar.barra(1), UP, buff=0.14)
        self.play(FadeIn(bar.ejes), run_time=0.4)
        self.play(FadeIn(bar.barra(0), shift=0.12 * UP), FadeIn(et_g),
                  FadeIn(val_g), run_time=0.8)
        self.play(FadeIn(bar.barra(1), shift=0.12 * UP), FadeIn(et_f),
                  FadeIn(val_f), run_time=0.8)
        rot.mostrar(cifra_pie("128 vs 448 macs"), zona="abajo", run_time=0.5)
        self.wait(3.6)

        grupo_bar = VGroup(bar, et_g, et_f, val_g, val_f)
        self.play(FadeOut(grupo_bar), run_time=0.6)

        # --- el mismo resultado exacto ------------------------------------
        panel = panel_cifras((f"goertzel {fmt(POR_GOERTZEL, 1)}", C_CALCULO),
                             (f"dft {fmt(POR_DFT, 1)}", C_CALCULO),
                             (f"diferencia {fmt(DIF_G, 1)}", C_SALIDA))
        panel.move_to(UP * 0.7)
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.8)

        cierre_leccion(
            self, rot,
            "No siempre hace falta el espectro entero.",
            "A veces basta una nota.",
            panel, espera=6.5)
