class Clip1(Scene):
    """3.3.1 - Dos tonos casi identicos: el que cae en un bin da una raya
    y el que cae entre bins derrama por todo el espectro. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("La fuga"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- el tono que cae JUSTO en el bin 100 --------------------------
        ed1 = EspectroDoble(F_EJE, DB_EN_BIN, piso_db=-60.0, ancho=9.0,
                            alto=1.9, color=C_BANDA)
        ed1.move_to(UP * 1.72 + LEFT * 0.75)
        et1 = tag_hud("bin 100", font_size=20, color=C_BANDA)
        et1.next_to(ed1, RIGHT, buff=0.30)
        self.play(FadeIn(ed1.ejes), run_time=0.5)
        self.play(Create(ed1.curva), FadeIn(ed1.area), FadeIn(et1),
                  run_time=1.6)
        rot.mostrar(cifra_pie(f"bin 100 = {fmt(F_EN_BIN, 1)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- el mismo tono medio bin mas arriba ---------------------------
        ed2 = EspectroDoble(F_EJE, DB_ENTRE_RECT, piso_db=-60.0, ancho=9.0,
                            alto=1.9, color=C_RUIDO)
        ed2.move_to(DOWN * 0.62 + LEFT * 0.75)
        et2 = tag_hud("bin 100.5", font_size=20, color=C_RUIDO)
        et2.next_to(ed2, RIGHT, buff=0.30)
        hz = tag_hud("Hz", font_size=17, color=C_TENUE)
        hz.next_to(ed2.en(F_EJE[-1], -60.0), DOWN, buff=0.18)
        self.play(FadeIn(ed2.ejes), FadeIn(hz), run_time=0.4)
        self.play(Create(ed2.curva), FadeIn(ed2.area), FadeIn(et2),
                  run_time=2.2)
        rot.mostrar(cifra_pie(f"bin 100.5 = {fmt(F_ENTRE_BINS, 1)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- cuanto derrama a 8 bins del tono ------------------------------
        f_lejos = F_ENTRE_BINS + 8 * RESOLUCION
        marca8 = ed2.marca_f(f_lejos, color=C_CALCULO)
        et8 = tag_hud("8 bins", font_size=18, color=C_CALCULO)
        et8.next_to(ed2.en(f_lejos, 0.0), UP, buff=0.10)
        nivel = DashedLine(ed2.en(F_EJE[0], FUGA["rect"]),
                           ed2.en(F_EJE[-1], FUGA["rect"]),
                           color=C_CALCULO, stroke_width=1.8,
                           dash_length=0.08)
        self.play(Create(marca8), FadeIn(et8), run_time=0.8)
        self.play(Create(nivel), run_time=1.0)
        rot.mostrar(cifra_pie(f"fuga = {fmt(FUGA['rect'], 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- la causa: donde la ventana rectangular corta el tono ----------
        espectros = VGroup(ed1, ed2, et1, et2, hz, marca8, et8, nivel)
        self.play(FadeOut(espectros), run_time=0.7)

        t_win = N_S / FS_V
        span = 3.0 / F_EN_BIN

        def _periodica(f):
            return lambda t: float(np.cos(2 * np.pi * f * (t % t_win)))

        gA = grafica(_periodica(F_EN_BIN), (t_win - span, t_win + span),
                     (-1.3, 1.3), ancho=5.2, alto=1.95, color=C_SENAL,
                     muestras=321)
        gA.move_to(LEFT * 3.4 + UP * 0.55)
        gB = grafica(_periodica(F_ENTRE_BINS), (t_win - span, t_win + span),
                     (-1.3, 1.3), ancho=5.2, alto=1.95, color=C_RUIDO,
                     muestras=321)
        gB.move_to(RIGHT * 3.4 + UP * 0.55)
        corteA = gA.vertical_en(t_win, color=C_CALCULO)
        corteB = gB.vertical_en(t_win, color=C_CALCULO)
        etA = tag_hud("ciclo entero", font_size=19, color=C_SENAL)
        etA.next_to(gA, DOWN, buff=0.30)
        etB = tag_hud("medio ciclo cortado", font_size=19, color=C_RUIDO)
        etB.next_to(gB, DOWN, buff=0.30)

        self.play(FadeIn(gA.ejes), FadeIn(gB.ejes), run_time=0.5)
        self.play(Create(gA.curva), Create(gB.curva), run_time=2.2)
        self.play(Create(corteA), Create(corteB), run_time=0.8)
        self.play(FadeIn(etA), FadeIn(etB), run_time=0.5)
        rot.mostrar(cifra_pie(f"{fmt(F_EN_BIN, 1)} Hz vs "
                              f"{fmt(F_ENTRE_BINS, 1)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- vuelta a la evidencia -----------------------------------------
        seam = VGroup(gA, gB, corteA, corteB, etA, etB)
        self.play(FadeOut(seam), run_time=0.6)
        self.play(FadeIn(espectros), run_time=0.8)
        rot.mostrar(cifra_pie(f"fuga = {fmt(FUGA['rect'], 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)
