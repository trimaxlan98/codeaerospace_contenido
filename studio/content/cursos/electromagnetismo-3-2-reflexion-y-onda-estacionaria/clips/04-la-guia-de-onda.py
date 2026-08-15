class Clip4(Scene):
    """3.2.4 - La guia de onda: el pasillo con paredes. El zigzag rebota al
    angulo REAL (sen theta = fc/f); cerca del corte se empina hasta no
    avanzar. Cierra la leccion. (~39 s)"""

    POS = DOWN * 0.35

    def _guia(self, f_hz):
        g = guia_te10(a_metros=A_WR90, f_hz=f_hz, largo=7.4, alto=1.9)
        g.move_to(self.POS)
        return g

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La guía de onda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el pasillo con paredes -------------------------------
        gui = self._guia(F_GUIA_LEJOS)
        t_guia = tag_hud(f"WR-90    a = {A_WR90 * 1000:.2f} mm",
                         font_size=19, color=C_TENUE)
        t_guia.next_to(gui, UP, buff=0.34)
        rot.mostrar(pie_curso("Arriba de los gigahercios el cable estorba. "
                              "Basta un tubo hueco de metal."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(gui.paredes), FadeIn(t_guia), run_time=0.8)
        self.wait(4.6)

        # --- momento: el zigzag --------------------------------------------
        t_f = tag_hud(f"f = {F_GUIA_LEJOS / 1e9:.0f} GHz", font_size=20)
        t_f.next_to(gui, DOWN, buff=0.30)
        rot.mostrar(pie_curso("Dentro no va recta: rebota de pared a "
                              "pared, y el ángulo lo fija la frecuencia."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(gui.patron), run_time=0.6)
        self.play(Create(gui.zigzag), FadeIn(t_f), run_time=1.2)
        self.wait(4.4)

        rot.mostrar(formula_pie(r"\sin\theta = f_c / f"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- momento: acercarse al corte -----------------------------------
        gui_nueva = self._guia(F_GUIA_CERCA)
        t_f_nuevo = tag_hud(f"f = {F_GUIA_CERCA / 1e9:.0f} GHz",
                            font_size=20)
        t_f_nuevo.move_to(t_f)
        rot.mostrar(pie_curso("Baja a 7 gigahercios, cerca del corte: el "
                              "rebote se empina y casi no avanza."),
                    zona="abajo", run_time=0.5)
        self.play(ReplacementTransform(gui, gui_nueva),
                  ReplacementTransform(t_f, t_f_nuevo), run_time=1.2)
        gui, t_f = gui_nueva, t_f_nuevo
        self.wait(4.4)

        # --- momento: la frecuencia de corte -------------------------------
        # La cifra sale de la propia guia dibujada, no de una cuenta aparte.
        t_fc = tag_hud(f"corte    fc = {gui.fc_hz() / 1e9:.3f} GHz",
                       font_size=20)
        t_fc.next_to(t_f, DOWN, buff=0.22)
        rot.mostrar(pie_curso("Por debajo del corte el modo no cabe: la "
                              "guía deja de transportar. No atenúa: NO "
                              "pasa."), zona="abajo", run_time=0.5)
        self.play(FadeIn(t_fc, shift=0.14 * UP), run_time=0.6)
        self.wait(4.6)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(gui), FadeOut(t_guia), FadeOut(t_f),
                  FadeOut(t_fc), run_time=0.8)
        rot.limpiar("arriba", run_time=0.4)
        linea1 = Text("Guiar ya sabes.", font_size=40, color=C_TITULO)
        linea2 = Text("Falta soltar.", font_size=40, color=C_CALCULO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        rot.mostrar(pie_curso("Los alimentadores de las antenas de "
                              "satélite son guías: sin dieléctrico que "
                              "perder, aguantan kilovatios."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.7)
        self.wait(4.6)
