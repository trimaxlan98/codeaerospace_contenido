class Clip3(Scene):
    """3 - Fotones por bit. La cuenta ideal: 30 dBm (1 W), dos telescopios
    de 10 cm que regalan 106.1 dBi cada uno, 272.2 dB de perdida de
    espacio libre a 5000 km: quedan -30 dBm, un microvatio. A 1550 nm eso
    son unos 780 fotones por bit a 10 Gbps. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Fotones por bit"), zona="arriba",
                    run_time=0.6)

        # --- momento 1: la cascada, paso a paso ----------------------------
        rot.mostrar(pie_curso("Hagamos la cuenta ideal: un vatio, dos "
                              "telescopios de 10 centímetros, cinco mil "
                              "kilómetros."), zona="abajo")
        barra = barra_enlace(Pt_dbm=PT_DBM, Gt=G_OPT_DBI, Gr=G_OPT_DBI,
                             fspl=FSPL_ISL_DB).scale(0.85)
        barra.move_to(DOWN * 0.30)
        self.play(FadeIn(barra.eje_cero), run_time=0.4)
        self.play(FadeIn(barra.paso(0), shift=0.10 * UP), run_time=0.6)
        self.play(FadeIn(barra.paso(1), shift=0.10 * UP), run_time=0.6)
        self.play(FadeIn(barra.paso(2), shift=0.10 * UP), run_time=0.6)
        self.play(FadeIn(barra.paso(3), shift=0.10 * UP), run_time=0.6)
        self.wait(5.5)

        # --- momento 2: el resultado ------------------------------------------
        rot.mostrar(pie_curso("Se pierden 272 decibelios por el camino y "
                              "quedan menos 30 dBm: un microvatio."),
                    zona="abajo")
        self.play(FadeIn(barra.paso(4), shift=0.10 * UP), run_time=0.6)
        self.play(FadeIn(barra.nota), run_time=0.4)
        tag_pr = tag_hud(f"Pr = {PR_DBM:.0f} dBm = 1 uW", font_size=18,
                         color=C_MEDIDA)
        tag_pr.move_to(RIGHT * 4.35 + UP * 0.55)
        self.play(FadeIn(tag_pr, shift=0.10 * UP), run_time=0.5)
        self.wait(4.5)

        # --- momento 3: fotones por bit -----------------------------------------
        rot.mostrar(formula_pie(r"E = \frac{hc}{\lambda}"), zona="abajo")
        cifra_fot = f"{FOTONES_BIT:.0f}"
        tag_fot = tag_hud(f"{cifra_fot} fotones/bit", font_size=20,
                          color=C_MEDIDA)
        tag_fot.move_to(RIGHT * 4.35 + DOWN * 0.30)
        self.play(FadeIn(tag_fot, shift=0.10 * UP), run_time=0.6)
        self.wait(5.5)

        # --- cierre -----------------------------------------------------------
        rot.mostrar(pie_curso("Bastan cientos de fotones para leer un "
                              "bit. Si llegan."), zona="abajo")
        self.wait(6.5)
