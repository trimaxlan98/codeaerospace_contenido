class Clip1(Scene):
    """5.1.1 - La rejilla tiempo-frecuencia: FDMA reparte por bandas fijas
    (filas), TDMA por turnos de tiempo (columnas); el recurso es UNA
    sabana finita. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Una sábana finita")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la rejilla vacia --------------------------------
        rot.mostrar(pie_curso("Mil terminales, un satélite: hay un "
                              "trozo de espectro y un tiempo. Eso es "
                              "TODO lo que hay para repartir."),
                    zona="abajo", run_time=0.5)
        rej = rejilla_acceso(nf=NF_REJ, nt=NT_REJ, ancho=7.4, alto=4.0)
        rej.move_to(DOWN * 0.15)
        self.play(FadeIn(rej), run_time=0.9)
        self.wait(4.2)

        # --- momento: FDMA, filas fijas --------------------------------
        rot.mostrar(pie_curso("FDMA: a cada usuario, una banda de "
                              "frecuencia FIJA, para siempre."),
                    zona="abajo", run_time=0.5)
        rej_fdma = rej.con_plan(PLAN_FDMA)
        etiquetas_f = VGroup(*[
            tag_junto(rej.ranura(f, NT_REJ - 1), f"usuario {f + 1}",
                      direccion=RIGHT, buff=0.16, font_size=16)
            for f in range(N_USUARIOS_REJ)])
        self.play(Transform(rej, rej_fdma), run_time=1.3)
        self.play(LaggedStart(*[FadeIn(e) for e in etiquetas_f],
                              lag_ratio=0.15), run_time=0.9)
        self.wait(4.4)

        # --- momento: TDMA, columnas fijas ------------------------------
        rot.mostrar(pie_curso("TDMA: a cada usuario, TODO el ancho, "
                              "por turnos."),
                    zona="abajo", run_time=0.5)
        rej_tdma = rej.con_plan(PLAN_TDMA)
        self.play(FadeOut(etiquetas_f), run_time=0.4)
        self.play(Transform(rej, rej_tdma), run_time=1.4)
        etiquetas_t = VGroup(*[
            tag_junto(rej.ranura(0, t), f"usuario {t // 2 + 1}",
                      direccion=UP, buff=0.16, font_size=15)
            for t in (0, 2, 4)])
        self.play(LaggedStart(*[FadeIn(e) for e in etiquetas_t],
                              lag_ratio=0.2), run_time=0.9)
        self.wait(4.4)

        # --- momento: la sabana es finita --------------------------------
        rot.mostrar(pie_curso("Frecuencia o tiempo: se reparte de un "
                              "modo o de otro, pero la sábana no crece."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(etiquetas_t), run_time=0.4)
        marco = SurroundingRectangle(rej, color=C_TENUE, buff=0.22,
                                     stroke_width=1.6)
        self.play(Create(marco), run_time=1.0)
        self.wait(5.0)
