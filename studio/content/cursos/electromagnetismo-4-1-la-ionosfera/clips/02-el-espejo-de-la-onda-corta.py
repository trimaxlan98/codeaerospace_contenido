class Clip2(Scene):
    """4.1.2 - El espejo de la onda corta: por debajo de la frecuencia
    de plasma, la capa F refleja como un espejo. Con la Tierra curva,
    varios saltos techo-suelo-techo cruzan un océano entero sin cables
    ni satélites. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El espejo de la onda corta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la frecuencia que manda -------------------------------
        rot.mostrar(pie_curso("Ese plasma tiene una frecuencia propia: "
                              "por debajo de ella, refleja como un "
                              "espejo."), zona="abajo", run_time=0.5)
        formula = MathTex(r"f_p \approx 8.98\sqrt{N_e}", font_size=36,
                          color=C_CALCULO)
        formula.move_to(UP * 0.6)
        self.play(Write(formula), run_time=1.0)
        self.wait(3.2)

        cifra_fp = tag_hud(f"fp = {FP_PICO / 1e6:.1f} MHz (pico F, dia)",
                           font_size=18)
        cifra_fp.next_to(ORIGIN, DOWN, buff=0.4)
        rot.mostrar(pie_curso("Con el pico diurno de la capa F: unos "
                              "nueve megahercios."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(cifra_fp, shift=0.1 * DOWN), run_time=0.6)
        self.wait(4.4)

        self.play(FadeOut(formula), FadeOut(cifra_fp), run_time=0.6)

        # --- momento: la Tierra curva y los saltos ----------------------------
        reb = rebote_hf(n_saltos=3)
        reb.move_to(DOWN * 0.4)
        rot.mostrar(pie_curso("La Tierra es curva: un salto techo-suelo "
                              "no basta para llegar lejos."),
                    zona="abajo", run_time=0.5)
        self.play(Create(reb.tierra), Create(reb.iono), run_time=1.2)
        self.wait(3.6)

        rot.mostrar(pie_curso("Pero la onda vuelve a subir, rebota otra "
                              "vez y otra: salto, salto, salto."),
                    zona="abajo", run_time=0.5)
        self.play(Create(reb.saltos, lag_ratio=0.45), run_time=2.4)
        self.wait(3.6)

        cifra_km = tag_hud(f"{reb.alcance_km(2):.0f} km en 3 saltos",
                           font_size=18)
        cifra_km.next_to(reb.tierra, DOWN, buff=0.35)
        rot.mostrar(pie_curso("Tres saltos así cruzan siete mil "
                              "trescientos kilómetros: un océano "
                              "entero."), zona="abajo", run_time=0.5)
        self.play(FadeIn(cifra_km, shift=0.1 * UP), run_time=0.6)
        self.wait(4.6)

        rot.mostrar(pie_curso("Así una emisora de onda corta cruzaba un "
                              "océano sin cables ni satélites: la "
                              "primera red global fue esta."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Pero solo por debajo de esa frecuencia. "
                              "¿Y si subimos más?"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)
