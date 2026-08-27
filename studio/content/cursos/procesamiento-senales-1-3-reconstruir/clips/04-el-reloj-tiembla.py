class Clip4(Scene):
    """1.3.4 - El reloj tiembla: los instantes de muestreo no caen donde
    deben y la SNR cae 20 dB por decada, tal cual predice la formula.
    Cierre de la leccion. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El reloj tiembla"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- momento visual: los instantes tiemblan --------------------------
        sec = Secuencia(XK, 0, (-1.18, 1.18), ancho=10.0, alto=2.3,
                        color=C_MUESTRA)
        sec.move_to(UP * 1.05)
        self.play(FadeIn(sec), run_time=0.9)
        self.wait(1.0)

        rng = np.random.default_rng(4)
        offsets = rng.normal(0.0, 1.0, N_MUESTRAS)
        offsets = offsets / float(np.max(np.abs(offsets))) * 0.16

        jitter_tallos = VGroup()
        jitter_puntos = VGroup()
        for i in range(N_MUESTRAS):
            dx = float(offsets[i])
            base = sec.tallo(i).get_start()
            top = sec.tallo(i).get_end()
            jitter_tallos.add(Line(base + RIGHT * dx, top + RIGHT * dx,
                                   color=C_RUIDO, stroke_width=2.0))
            jitter_puntos.add(Dot(top + RIGHT * dx, radius=0.045,
                                  color=C_RUIDO))

        self.play(sec.tallos.animate.set_stroke(opacity=0.30),
                  sec.puntos.animate.set_opacity(0.30), run_time=0.5)
        self.play(LaggedStart(*[Create(t) for t in jitter_tallos],
                              lag_ratio=0.015),
                  LaggedStart(*[FadeIn(p) for p in jitter_puntos],
                              lag_ratio=0.015), run_time=1.8)
        et_jit = tag_junto(jitter_puntos, "jitter", UP, buff=0.16,
                           font_size=20, color=C_RUIDO)
        self.play(FadeIn(et_jit), run_time=0.6)
        self.wait(2.2)

        self.play(FadeOut(sec), FadeOut(jitter_tallos), FadeOut(jitter_puntos),
                  FadeOut(et_jit), run_time=0.8)
        self.wait(0.4)

        # --- las cifras: la SNR cae con la frecuencia -------------------------
        def _fmt_hz(f):
            if f >= 1e6:
                return f"{fmt(f / 1e6, 0)}M"
            if f >= 1e3:
                return f"{fmt(f / 1e3, 0)}k"
            return fmt(f, 0)

        bars = barras(SNR_JITTER, ancho=9.2, alto=2.9, color=C_CALCULO,
                     rango_y=(0.0, max(SNR_JITTER) * 1.18))
        bars.move_to(DOWN * 0.30)
        self.play(FadeIn(bars.ejes), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(b, shift=0.1 * UP) for b in
                                bars.barras], lag_ratio=0.15), run_time=1.6)
        self.wait(0.6)

        etiquetas_f = VGroup()
        etiquetas_v = VGroup()
        for i, (f, v) in enumerate(zip(F_JITTER, SNR_JITTER)):
            ef = tag_hud(_fmt_hz(f), font_size=16, color=C_TENUE)
            ef.next_to(bars.barra(i), DOWN, buff=0.10)
            ev = tag_hud(fmt(v, 1), font_size=16, color=C_CALCULO)
            ev.next_to(bars.cima(i), UP, buff=0.08)
            etiquetas_f.add(ef)
            etiquetas_v.add(ev)
        self.play(FadeIn(etiquetas_f), FadeIn(etiquetas_v), run_time=0.8)
        self.wait(1.2)

        rot.mostrar(cifra_pie(f"sigma = {fmt(SIGMA_JITTER * 1e12, 0)} ps"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- coincide con la teoria: se confirma la formula -------------------
        ticks = VGroup()
        for i, (v, t) in enumerate(zip(SNR_JITTER, SNR_TEORICA)):
            dy = (t - v) / (bars.y1 - bars.y0) * bars.alto
            p = bars.cima(i) + np.array([0.0, dy, 0.0])
            ticks.add(Line(p + LEFT * 0.14, p + RIGHT * 0.14, color=C_IDEAL,
                          stroke_width=3.0))
        et_teo = tag_junto(ticks, "teorica", RIGHT, buff=0.16, font_size=18,
                          color=C_IDEAL)
        self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.15),
                  FadeIn(et_teo), run_time=1.6)
        self.wait(2.0)

        rot.mostrar(formula_pie(r"\mathrm{SNR} = -20\log_{10}"
                                r"(2\pi f \sigma_t)"), zona="abajo",
                    run_time=0.6)
        self.wait(2.8)

        rot.mostrar(cifra_pie("cae 20 dB/decada"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        cierre_leccion(self, rot, "La secuencia no vale nada",
                       "sin el reloj que la sostiene.", bars, ticks,
                       etiquetas_f, etiquetas_v, et_teo)
