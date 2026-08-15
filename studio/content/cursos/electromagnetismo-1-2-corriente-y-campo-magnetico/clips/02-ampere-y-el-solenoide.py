class Clip2(Scene):
    """1.2.2 - Ampere y el solenoide: apilar espiras suma sus circulos de
    campo. Dentro queda un campo denso y uniforme; fuera, casi nada. Asi
    se fabrica un campo de laboratorio con un carrete de alambre. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Ampère y el solenoide")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el carrete cortado a lo largo ------------------------
        sol = solenoide_corte(n_espiras=9)
        sol.move_to(DOWN * 0.3)
        rot.mostrar(pie_curso("Un círculo de campo es poca cosa. Ampère "
                              "enrolla el hilo y los APILA."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(sol.tubo),
                  FadeIn(sol.espiras_arriba, lag_ratio=0.08),
                  FadeIn(sol.espiras_abajo, lag_ratio=0.08), run_time=1.4)
        self.wait(4.4)

        # --- momento: leer el corte ----------------------------------------
        rot.mostrar(pie_curso("Es un corte del carrete: cruz, la "
                              "corriente entra; punto, sale hacia ti."),
                    zona="abajo", run_time=0.5)
        tag_entra = tag_junto(sol.espiras_arriba[0], "entra", UP,
                              buff=0.34, color=C_CARGA)
        tag_sale = tag_junto(sol.espiras_abajo[0], "sale", DOWN,
                             buff=0.34, color=C_CARGA)
        self.play(FadeIn(tag_entra, shift=0.1 * UP),
                  FadeIn(tag_sale, shift=0.1 * DOWN), run_time=0.6)
        self.wait(4.4)

        # --- momento: dentro, uniforme -------------------------------------
        rot.mostrar(pie_curso("Dentro, todas las espiras empujan igual: "
                              "el campo sale denso y uniforme."),
                    zona="abajo", run_time=0.5)
        self.play(LaggedStart(*[GrowArrow(f) for f in sol.flechas],
                              lag_ratio=0.08), run_time=1.6)
        self.wait(4.4)

        # --- momento: fuera, nada ------------------------------------------
        rot.mostrar(pie_curso("Fuera, las vueltas se cancelan entre sí: "
                              "ahí fuera casi no queda campo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        rot.mostrar(formula_pie(r"B = \mu_0\, n\, I"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: la cifra ---------------------------------------------
        rot.mostrar(pie_curso("Mil espiras por metro y diez amperios: "
                              "doce militeslas, encima de tu mesa."),
                    zona="abajo", run_time=0.5)
        cifra = tag_hud(f"{B_SOL * 1e3:.1f} mT con {N_SOL:.0f} esp/m "
                        f"y {I_SOL:.0f} A", font_size=16)
        cifra.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(cifra, shift=0.1 * DOWN), run_time=0.5)
        self.wait(4.4)

        rot.mostrar(pie_curso("Así se fabrica un campo de laboratorio: "
                              "un carrete de alambre y una fuente."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
