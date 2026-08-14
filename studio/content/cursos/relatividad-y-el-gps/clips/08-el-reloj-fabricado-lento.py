class Clip8(Scene):
    """8 - El reloj fabricado lento. El mismo reloj late distinto en
    orbita, asi que se desafina ANTES de lanzarlo: 10.23 MHz ->
    10.22999999544 MHz. Recapitulacion del curso y cierre. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El reloj fabricado lento")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: dos relojes identicos -------------------------------
        rot.mostrar(pie_curso("Dos relojes atómicos idénticos: uno se queda "
                              "en la fábrica, el otro sube a la órbita."),
                    zona="abajo", run_time=0.5)

        fila_fab = fila_pulsos(n=16, color=C_LUZ)
        fila_fab.move_to(RIGHT * 1.1 + UP * 1.5)
        fila_orb = fila_pulsos(n=16, color=C_SATELITE)
        fila_orb.move_to(RIGHT * 1.1 + UP * 0.4)
        tag_fab = tag_junto(fila_fab, "reloj en fábrica", LEFT, buff=0.35,
                            font_size=18, color=C_LUZ)
        tag_orb = tag_junto(fila_orb, "el mismo reloj, en órbita", LEFT,
                            buff=0.35, font_size=18, color=C_SATELITE)

        self.play(FadeIn(fila_fab, shift=0.20 * DOWN), FadeIn(tag_fab),
                  run_time=0.9)
        self.play(FadeIn(fila_orb, shift=0.20 * UP), FadeIn(tag_orb),
                  run_time=0.9)
        self.wait(3.2)

        # --- momento: en orbita late distinto -----------------------------
        rot.mostrar(pie_curso("En órbita el tic dura otra cosa: cada día se "
                              "va adelantando. El dibujo lo exagera."),
                    zona="abajo", run_time=0.5)

        guias = VGroup(*[
            DashedLine([fila_fab.en(k)[0], 1.78, 0.0],
                       [fila_fab.en(k)[0], 0.14, 0.0],
                       dash_length=0.07, stroke_width=1.4, color=C_EJE)
            for k in (2, 8, 14)])
        guias.set_stroke(opacity=0.75)

        desfasada = fila_orb.con_desfase(0.45)
        alineada = fila_orb.con_desfase(0.0)

        deriva = VGroup(
            Text("desfase real", font_size=16, color=C_TENUE),
            tag_hud(f"{DERIVA_NETA:+.1f} µs/día", font_size=20,
                    color=C_ERROR),
        ).arrange(RIGHT, buff=0.26)
        deriva.next_to(fila_orb, DOWN, buff=0.38)

        self.play(Transform(fila_orb, desfasada), FadeIn(guias),
                  FadeIn(deriva, shift=0.12 * UP), run_time=1.2)
        self.wait(3.8)

        # --- momento: se desafina de fabrica ------------------------------
        rot.mostrar(pie_curso("La solución es de ingeniería: se desafina el "
                              "reloj antes de lanzarlo."),
                    zona="abajo", run_time=0.5)

        cifra_mhz = tag_hud(f"{FREQ_GPS / 1e6:.2f} MHz → "
                            f"{F_FABRICA / 1e6:.11f} MHz",
                            font_size=20, color=C_SATELITE)
        cifra_mhz.move_to(DOWN * 1.30)
        tag_mhz = tag_junto(cifra_mhz, "así late exacto allá arriba", DOWN,
                            buff=0.20, font_size=17)
        self.play(FadeIn(cifra_mhz, shift=0.14 * UP), FadeIn(tag_mhz),
                  FadeOut(deriva), run_time=0.9)
        self.wait(1.1)
        self.play(Transform(fila_orb, alineada), run_time=1.3)
        self.wait(1.7)

        # --- momento: la recapitulacion -----------------------------------
        rot.mostrar(pie_curso("Especial y general, las dos a la vez, en tu "
                              "bolsillo."), zona="abajo", run_time=0.5)
        self.play(FadeOut(fila_fab), FadeOut(fila_orb), FadeOut(tag_fab),
                  FadeOut(tag_orb), FadeOut(guias), FadeOut(cifra_mhz),
                  FadeOut(tag_mhz), run_time=0.8)

        minis = VGroup(
            reloj_luz(beta=BETA_RELOJ, tics=3).scale_to_fit_height(1.2),
            trilateracion().scale_to_fit_height(1.4),
            pozo_potencial().scale_to_fit_height(1.3),
            orbita_gps().scale_to_fit_height(1.4),
        )
        minis.arrange(RIGHT, buff=0.8).move_to(UP * 0.35)
        self.play(LaggedStart(*[FadeIn(m, shift=0.18 * UP) for m in minis],
                              lag_ratio=0.22), run_time=1.8)
        self.wait(2.4)

        # --- momento: cierre del curso ------------------------------------
        rot.limpiar("arriba", run_time=0.3)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeOut(minis), run_time=0.5)
        cierre = VGroup(
            titulo_marca("El tiempo no es el mismo para todos.",
                         font_size=38),
            Text("Tu teléfono lo corrige a cada segundo.", font_size=26,
                 color=C_SATELITE),
        ).arrange(DOWN, buff=0.4)
        cierre.move_to(UP * 0.2)
        self.play(Write(cierre[0]), run_time=1.1)
        self.play(FadeIn(cierre[1], shift=0.18 * UP), run_time=0.8)
        self.wait(5.5)
