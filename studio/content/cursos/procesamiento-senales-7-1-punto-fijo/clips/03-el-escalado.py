class Clip3(Scene):
    """7.1.3 - Bajar la señal da margen y cuesta ruido, dB por dB: el
    escalado no crea cabecera, la compra. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("El escalado"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        bar_m = barras([MARGEN_ESC[e] for e in ESCALAS], ancho=4.0, alto=2.3,
                       color=C_SALIDA, rango_y=(0.0, 14.0))
        bar_m.move_to(LEFT * 3.3 + DOWN * 0.3)
        et_m = tag_hud("margen dB", font_size=19, color=C_SALIDA)
        et_m.next_to(bar_m, UP, buff=0.28)
        bar_s = barras([SNR_ESC[e] for e in ESCALAS], ancho=4.0, alto=2.3,
                       color=C_CALCULO, rango_y=(75.0, 96.0))
        bar_s.move_to(RIGHT * 3.3 + DOWN * 0.3)
        et_s = tag_hud("SNR dB", font_size=19, color=C_CALCULO)
        et_s.next_to(bar_s, UP, buff=0.28)
        etiquetas = VGroup()
        for i, e in enumerate(ESCALAS):
            for bar in (bar_m, bar_s):
                t = tag_hud(f"x{fmt(e, 2)}", font_size=17, color=C_TENUE)
                t.next_to(bar.barra(i), DOWN, buff=0.14)
                etiquetas.add(t)
        self.play(FadeIn(bar_m), FadeIn(et_m), FadeIn(bar_s), FadeIn(et_s),
                  FadeIn(etiquetas), run_time=1.2)
        self.wait(1.8)

        for i, e in enumerate(ESCALAS):
            m_top = tag_hud(f"{fmt(MARGEN_ESC[e], 2)}", font_size=18,
                            color=C_SALIDA)
            m_top.next_to(bar_m.barra(i), UP, buff=0.10)
            s_top = tag_hud(f"{fmt(SNR_ESC[e], 1)}", font_size=18,
                            color=C_CALCULO)
            s_top.next_to(bar_s.barra(i), UP, buff=0.10)
            rot.mostrar(cifra_pie(f"x{fmt(e, 2)}: margen "
                                  f"{fmt(MARGEN_ESC[e], 2)} dB"),
                        zona="abajo", run_time=0.45)
            self.play(FadeIn(m_top), FadeIn(s_top), run_time=0.6)
            self.wait(3.2)

        rot.mostrar(cifra_pie(f"gana {fmt(MARGEN_ESC[0.25] - MARGEN_ESC[1.0], 1)}"
                              f" pierde {fmt(SNR_ESC[1.0] - SNR_ESC[0.25], 1)}"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)
        rot.mostrar(formula_pie(r"6\ \mathrm{dB}\ \to\ 6\ \mathrm{dB}"),
                    zona="abajo", run_time=0.5)
        self.wait(6.6)
