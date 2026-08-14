class Clip4(Scene):
    """4 - La prueba que cae del cielo. Los muones nacen a 15 km y viven
    2.2 us: clasicamente ninguno tocaria el suelo. La curva roja muere en
    nada; con gamma = 10 la cian llega con ~10 %. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La prueba que cae del cielo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        cm = curvas_muones()
        cm.shift(UP * 0.25)
        cima = cm.en(1.0, ALTURA_MUON)
        tag_cima = tag_junto(cima, f"{ALTURA_MUON / 1000:.0f} km", UP,
                             buff=0.14, font_size=17)
        tag_suelo = tag_junto(cm.suelo, "suelo", DOWN, buff=0.16,
                              font_size=17)
        etiq_y = tag_junto(cm.ejes[0], "altura", UP, buff=0.10, font_size=13)
        etiq_x = tag_junto(cm.suelo, "fracción viva", DOWN, buff=0.18,
                           font_size=13)
        etiq_x.align_to(cm.suelo, RIGHT)

        # --- momento: nacen arriba y viven un suspiro ----------------------
        rot.mostrar(pie_curso(
            f"Los muones nacen a {ALTURA_MUON / 1000:.0f} km de altura y "
            f"viven {TAU_MUON * 1e6:.1f} µs."), zona="abajo", run_time=0.5)
        self.play(Create(cm.suelo), FadeIn(cm.ejes), FadeIn(tag_cima),
                  FadeIn(tag_suelo), FadeIn(etiq_y), FadeIn(etiq_x),
                  run_time=1.5)

        lluvia = VGroup(*[
            Dot(cima + LEFT * (0.35 + 0.58 * k), radius=0.055, color=C_LUZ)
            for k in range(7)])
        caidas = (0.55, 1.35, 0.35, 2.05, 0.75, 2.55, 1.05)
        self.play(FadeIn(lluvia, shift=0.18 * DOWN), run_time=0.7)
        self.play(*[d.animate.shift(DOWN * h)
                    for d, h in zip(lluvia, caidas)],
                  run_time=1.6, rate_func=rush_into)
        self.play(LaggedStart(*[FadeOut(d) for d in lluvia], lag_ratio=0.16),
                  run_time=1.0)
        self.wait(1.6)

        # --- momento: clasicamente ninguno llega ---------------------------
        rot.mostrar(pie_curso(
            f"Clásicamente ninguno llegaría: les alcanza para "
            f"{BETA_MUON * C * TAU_MUON:.0f} m de caída."),
            zona="abajo", run_time=0.5)
        self.play(Create(cm.clasica), run_time=2.4, rate_func=linear)
        self.wait(2.6)

        # --- momento: pero sus relojes van lentos --------------------------
        rot.mostrar(pie_curso(
            f"Pero sus relojes van lentos: viven {GAMMA_MUON:.0f} veces "
            "más de lo que dice la tabla."), zona="abajo", run_time=0.5)
        g_tag = tag_hud(f"γ = {GAMMA_MUON:.0f}", font_size=21)
        g_tag.move_to(LEFT * 4.85 + UP * 1.85)
        b_tag = tag_hud(f"(β = {BETA_MUON})", font_size=14, color=C_TENUE)
        b_tag.next_to(g_tag, DOWN, buff=0.18)
        self.play(FadeIn(g_tag, shift=0.12 * UP), FadeIn(b_tag), run_time=0.7)
        self.play(Create(cm.relativista), run_time=3.0, rate_func=linear)
        self.wait(2.0)

        # --- momento: la cifra estrella ------------------------------------
        rot.mostrar(pie_curso(
            f"Cerca del {FRAC_RELATIVISTA * 100:.0f} % toca el suelo, y los "
            "detectores los cuentan de verdad."), zona="abajo", run_time=0.5)
        llegada = cm.en(FRAC_RELATIVISTA, 0.0)
        punto_llegada = Dot(llegada, radius=0.07, color=C_SATELITE)
        pct_tag = tag_hud(f"~{FRAC_RELATIVISTA * 100:.0f} % llegan",
                          font_size=19)
        pct_tag.move_to(llegada + RIGHT * 1.45 + UP * 0.34)
        self.play(FadeIn(punto_llegada, scale=0.4),
                  FadeIn(pct_tag, shift=0.12 * RIGHT), run_time=0.8)
        self.wait(4.4)

        # --- momento: el cierre --------------------------------------------
        rot.mostrar(pie_curso(
            "«Cada muón que llega al suelo es un reloj que llegó tarde.»"),
            zona="abajo", run_time=0.5)
        self.wait(5.2)
