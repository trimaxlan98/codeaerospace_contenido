class Clip4(Scene):
    """7.3.4 - Contando multiplicaciones reales en los dos lados, la FFT
    gana a partir de M_CRUCE. Escala logaritmica, cierre de leccion.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("El cruce"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- las dos pistas, escala logaritmica -------------------------------
        log_dir = [math.log10(COSTE_DIR[m]) for m in MS_TABLA]
        log_fft = [math.log10(COSTE_FFT[m]) for m in MS_TABLA]
        lo = min(log_dir + log_fft) * 0.97
        hi = max(log_dir + log_fft) * 1.02

        bar_d = Barras(log_dir, ancho=8.4, alto=1.6, color=C_MUESTRA,
                       rango_y=(lo, hi))
        bar_d.move_to(UP * 1.55)
        bar_f = Barras(log_fft, ancho=8.4, alto=1.6, color=C_CALCULO,
                       rango_y=(lo, hi))
        bar_f.move_to(DOWN * 0.35)

        et_d = tag_hud("directo", font_size=18, color=C_MUESTRA)
        et_d.next_to(bar_d, LEFT, buff=0.32)
        et_f = tag_hud("fft", font_size=18, color=C_CALCULO)
        et_f.next_to(bar_f, LEFT, buff=0.32)
        et_log = tag_hud("escala log", font_size=15, color=C_TENUE)
        et_log.next_to(bar_d, UP, buff=0.22)

        etiquetas = VGroup()
        for i, m in enumerate(MS_TABLA):
            t = tag_hud(f"M={m}", font_size=16, color=C_TENUE)
            t.next_to(bar_f.barra(i), DOWN, buff=0.16)
            etiquetas.add(t)

        self.play(FadeIn(bar_d), FadeIn(et_d), FadeIn(bar_f), FadeIn(et_f),
                  FadeIn(et_log), FadeIn(etiquetas), run_time=1.3)
        self.wait(1.2)

        tops = VGroup()
        for i, m in enumerate(MS_TABLA):
            gana = "directo" if COSTE_DIR[m] < COSTE_FFT[m] else "fft"
            top_d = tag_hud(f"{COSTE_DIR[m] // 1000}k", font_size=16,
                            color=C_MUESTRA)
            top_d.next_to(bar_d.barra(i), UP, buff=0.08)
            top_f = tag_hud(f"{COSTE_FFT[m] // 1000}k", font_size=16,
                            color=C_CALCULO)
            top_f.next_to(bar_f.barra(i), UP, buff=0.08)
            tops.add(top_d, top_f)
            rot.mostrar(cifra_pie(f"M {m} gana {gana}"), zona="abajo",
                        run_time=0.4)
            self.play(FadeIn(top_d), FadeIn(top_f), run_time=0.6)
            self.wait(1.9)

        self.play(FadeOut(bar_d), FadeOut(bar_f), FadeOut(et_d),
                  FadeOut(et_f), FadeOut(et_log), FadeOut(etiquetas),
                  FadeOut(tops), run_time=0.6)

        # --- el cruce: M_CRUCE -------------------------------------------------
        panel = panel_cifras((f"M cruce = {M_CRUCE}", C_CALCULO),
                             (f"{COSTE_D_CRUCE:,} vs {COSTE_F_CRUCE:,}",
                              C_TENUE))
        self.play(FadeIn(panel), run_time=0.7)
        rot.mostrar(cifra_pie(f"en {M_CRUCE} se cruzan"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        rot.mostrar(formula_pie(r"\mathcal{O}(N\log N)"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        cierre_leccion(self, rot, "La FFT no siempre gana.",
                       "Hay que contar las multiplicaciones.", panel,
                       espera=5.4)
