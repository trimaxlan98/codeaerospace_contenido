class Clip5(Scene):
    """5 - El efecto mariposa, medido. Dos atmosferas a una millonesima;
    abajo, su separacion en escala log es una RECTA y la pendiente es el
    exponente de Lyapunov, medido en pantalla. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 05")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El efecto mariposa, medido")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: dos atmosferas a una millonesima --------------------
        rot.mostrar(pie_curso("Dos atmósferas separadas una millonésima. "
                              "Míralas separarse."), zona="abajo",
                    run_time=0.5)
        pts_a, pts_b, d = par_lorenz(EPS_LORENZ, n=9000)
        traza_a = curva_lorenz(pts_a, alto=3.1, color=C_SISTEMA,
                               grosor=1.7)
        traza_b = curva_lorenz(pts_b, alto=3.1, color=C_GEMELO, grosor=1.7,
                               como=traza_a)
        for t in (traza_a, traza_b):
            t.shift(UP * 1.15)
            t.set_stroke(opacity=0.85)
        eps_tag = tag_hud(f"d0 = {EPS_LORENZ:.0e}", font_size=15)
        eps_tag.move_to(LEFT * 5.0 + UP * 2.5)
        rot.mostrar(eps_tag, zona="eps", run_time=0.4)
        self.play(Create(traza_a), Create(traza_b), run_time=4.6,
                  rate_func=linear)
        self.wait(1.6)

        # --- momento: en log, una recta -----------------------------------
        rot.mostrar(pie_curso("En escala logarítmica la separación es una "
                              "recta: el error crece exponencialmente."),
                    zona="abajo", run_time=0.5)
        sep = curva_separacion(d, ancho=6.4, alto=2.1)
        sep.move_to(DOWN * 1.75)
        etiq_x = tag_hud("tiempo", font_size=14, color=C_TENUE)
        etiq_x.next_to(sep.ejes[0], RIGHT, buff=0.14)
        etiq_y = tag_hud("log d", font_size=14, color=C_TENUE)
        etiq_y.next_to(sep.ejes[1], UP, buff=0.10)
        self.play(FadeIn(sep.ejes), FadeIn(etiq_x), FadeIn(etiq_y),
                  run_time=0.7)
        self.play(Create(sep.traza), run_time=2.6, rate_func=linear)
        self.wait(2.2)

        # --- momento: la pendiente tiene nombre ---------------------------
        formula = formula_pie(r"d(t) \approx d_0\, e^{\lambda t}",
                              color=C_GEMELO)
        rot.mostrar(formula, zona="abajo", run_time=0.5)
        recta = sep.recta_ajuste()
        lam_tag = tag_hud(f"λ = {sep.lyapunov():.2f}", font_size=19)
        lam_tag.move_to(RIGHT * 4.6 + DOWN * 1.1)
        self.play(Create(recta), run_time=1.0)
        self.play(FadeIn(lam_tag, shift=0.15 * UP), run_time=0.6)
        self.wait(4.8)

        # --- momento: la precision no compra futuro -----------------------
        rot.mostrar(pie_curso("Diez veces más precisión no compra diez "
                              "veces más futuro: compra un suspiro."),
                    zona="abajo", run_time=0.5)
        self.wait(6.6)
