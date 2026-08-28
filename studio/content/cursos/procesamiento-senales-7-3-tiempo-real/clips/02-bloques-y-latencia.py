class Clip2(Scene):
    """7.3.2 - Procesar por bloques no cuesta cuentas, cuesta espera: hay
    que tener el bloque entero antes de empezar. L / fs. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("Bloques y latencia"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        vals = [LATENCIA[L] for L in BLOQUES]
        bar = Barras(vals, ancho=8.6, alto=3.2, color=C_MUESTRA,
                     rango_y=(0.0, max(vals) * 1.25))
        bar.move_to(DOWN * 0.35)
        etiquetas = VGroup()
        for i, L in enumerate(BLOQUES):
            t = tag_hud(f"L={L}", font_size=18, color=C_TENUE)
            t.next_to(bar.barra(i), DOWN, buff=0.16)
            etiquetas.add(t)
        self.play(FadeIn(bar.ejes), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(b) for b in bar.barras],
                              lag_ratio=0.15),
                  FadeIn(etiquetas), run_time=1.8)
        self.wait(0.8)

        tops = VGroup()
        for i, L in enumerate(BLOQUES):
            top = tag_hud(f"{fmt(LATENCIA[L], 2)} ms", font_size=18,
                         color=C_CALCULO)
            top.next_to(bar.barra(i), UP, buff=0.10)
            tops.add(top)
            rot.mostrar(cifra_pie(f"L {L} {fmt(LATENCIA[L], 2)} ms"),
                        zona="abajo", run_time=0.42)
            self.play(FadeIn(top), run_time=0.55)
            self.wait(2.6)

        # --- donde empieza a notarse: los dos bloques mas grandes ------------
        marca = DashedLine(bar.barra(1).get_right() + RIGHT * 0.10,
                           bar.barra(1).get_right() + RIGHT * 0.10
                           + UP * bar.alto,
                           color=C_RUIDO, stroke_width=2.0)
        et_marca = tag_hud("se nota", font_size=18, color=C_RUIDO)
        et_marca.next_to(marca, UP, buff=0.16)
        self.play(Create(marca), FadeIn(et_marca), run_time=0.8)
        self.wait(2.6)

        rot.mostrar(formula_pie(r"t = \frac{L}{f_s}"), zona="abajo",
                    run_time=0.5)
        self.wait(6.8)
