class Clip1(Scene):
    """1 - Por que laser. Dos satelites pueden hablarse por radio o por
    luz; la ganancia de una apertura crece con su tamano en longitudes
    de onda (G = (pi D/lambda)^2). Una antena de 1 m a 30 GHz da 50 dBi;
    un telescopio de 10 cm a 1550 nm da 106.1 dBi: 56 dB de regalo, unas
    400 000 veces mas ganancia. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Por qué láser"), zona="arriba", run_time=0.6)

        # --- momento 1: dos columnas ----------------------------------
        rot.mostrar(pie_curso("Dos satélites quieren hablarse. Pueden usar "
                              "radio... o luz."), zona="abajo")
        comp = comparador_rf_optico().scale(0.80)
        comp.move_to(DOWN * 0.10)
        self.play(FadeIn(comp.columna_rf, shift=0.15 * UP), run_time=0.6)
        self.play(FadeIn(comp.columna_optica, shift=0.15 * UP), run_time=0.6)
        self.play(FadeIn(comp.marco), FadeIn(comp.fila("apertura")),
                  run_time=0.6)
        self.wait(4.0)

        # --- momento 2: la formula de la ganancia ----------------------
        rot.mostrar(formula_pie(r"G = \left(\frac{\pi D}{\lambda}\right)^2"),
                    zona="abajo")
        self.play(FadeIn(comp.fila("lambda")), run_time=0.6)
        self.wait(6.0)

        # --- momento 3: las dos cifras -----------------------------------
        rot.mostrar(pie_curso("Una antena de un metro a 30 gigahercios: 50 "
                              "decibelios. Un telescopio de 10 centímetros "
                              "a 1550 nanómetros: 106."), zona="abajo")
        self.play(FadeIn(comp.fila("ganancia")), run_time=0.6)
        g_rf = tag_hud(f"G = {G_RF_DBI:.1f} dBi", font_size=17)
        g_rf.next_to(comp.columna_rf, UP, buff=0.30)
        g_opt = tag_hud(f"G = {G_OPT_DBI:.1f} dBi", font_size=17)
        g_opt.next_to(comp.columna_optica, UP, buff=0.30)
        self.play(FadeIn(g_rf, shift=0.10 * UP), FadeIn(g_opt, shift=0.10 * UP),
                  run_time=0.5)
        self.play(Flash(comp.columna_optica, color=C_MEDIDA, line_length=0.22,
                        num_lines=14, flash_radius=2.1), run_time=0.7)
        self.wait(5.5)

        # --- cierre: el regalo -------------------------------------------
        factor = 10 ** ((G_OPT_DBI - G_RF_DBI) / 10)
        cifra = f"{factor:,.0f}".replace(",", " ")
        rot.mostrar(pie_curso("Cincuenta y seis decibelios de regalo: "
                              f"unas {cifra} veces más ganancia."),
                    zona="abajo")
        regalo = tag_hud(f"x {cifra}", font_size=22, color=C_MEDIDA)
        regalo.next_to(comp, DOWN, buff=0.28)
        self.play(FadeIn(regalo, shift=0.10 * UP), run_time=0.6)
        self.wait(6.0)
