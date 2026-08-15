class Clip3(Scene):
    """3 - Hasta donde sirve la regla. Ningun laser es una onda infinita:
    el LED emite un tren corto (Lc 20 um) y el HeNe uno casi de medio
    metro (0.40 m): la coherencia dice hasta donde sirve la regla.
    (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Hasta dónde sirve la regla"),
                    zona="arriba", run_time=0.6)

        led = tren_coherencia(lc_rel=0.14, ancho=5.6, n_periodos=9,
                              amplitud=0.55, color=C_ONDA)
        led.shift(UP * 1.4)
        led_tag = tag_junto(led, "LED (20 nm de ancho)", DOWN, buff=0.22,
                            font_size=17, color=C_TENUE)

        # --- momento 1: el tren corto ------------------------------------------
        rot.mostrar(pie_curso("Ninguna fuente es una onda infinita: "
                              "emite trenes de ondas."), zona="abajo")
        self.play(Create(led.eje), run_time=0.4)
        self.play(FadeIn(led.envolvente), Create(led.curva), run_time=1.2)
        self.play(FadeIn(led_tag), run_time=0.4)
        self.wait(4.5)

        # --- momento 2: la longitud de coherencia ----------------------------------
        rot.mostrar(pie_curso("La longitud de coherencia es lo que dura "
                              "el tren: lambda al cuadrado sobre el "
                              "ancho espectral."), zona="abajo")
        formula = MathTex(r"L_c = \lambda^2/\Delta\lambda", font_size=32,
                          color=C_ACENTO)
        lc_led_tag = tag_hud(f"LED: {LC_LED_UM:.0f} um", font_size=17)
        grupo_formula = VGroup(formula, lc_led_tag).arrange(DOWN, buff=0.18)
        grupo_formula.move_to(DOWN * 0.35)
        self.play(FadeIn(grupo_formula, shift=0.10 * UP), run_time=0.6)
        self.wait(7.5)

        # --- momento 3: el tren largo del HeNe --------------------------------------
        rot.mostrar(pie_curso("Un láser estabilizado emite trenes de "
                              "casi medio metro."), zona="abajo")
        self.play(FadeOut(grupo_formula), run_time=0.4)
        hene = tren_coherencia(lc_rel=1.3, ancho=5.6, n_periodos=9,
                               amplitud=0.55, color=C_ONDA)
        hene.shift(DOWN * 1.55)
        hene_tag = tag_hud(f"HeNe: {LC_HENE_M:.2f} m", font_size=17)
        hene_tag.next_to(hene, DOWN, buff=0.22)
        self.play(Create(hene.eje), run_time=0.4)
        self.play(FadeIn(hene.envolvente), Create(hene.curva), run_time=1.2)
        self.play(FadeIn(hene_tag), run_time=0.4)
        self.wait(4.5)

        # --- cierre -----------------------------------------------------------------
        rot.mostrar(pie_curso("La regla sirve mientras las dos ondas "
                              "sigan siendo del mismo tren."), zona="abajo")
        self.wait(7.0)
