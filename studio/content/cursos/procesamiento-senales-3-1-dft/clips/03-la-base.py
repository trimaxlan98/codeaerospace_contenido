class Clip3(Scene):
    """3.1.3 - Las filas de W son una BASE: cada una mide una frecuencia y
    ninguna se mete en el terreno de otra. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Una base ortogonal"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- las cuatro primeras filas de W --------------------------------
        colores = (C_TENUE, C_MUESTRA, C_SALIDA, C_CALCULO)
        filas = VGroup()
        etiquetas = VGroup()
        for i, (k, fila) in enumerate(zip(BASE_KS, BASE)):
            s = Secuencia(fila, 0, (-1.3, 1.3), ancho=7.0, alto=0.95,
                          color=colores[i], radio=0.045, eje_y=False)
            s.move_to(UP * (1.55 - 1.05 * i))
            filas.add(s)
            e = tag_hud(f"k = {k}", font_size=19, color=colores[i])
            e.next_to(s, LEFT, buff=0.30)
            etiquetas.add(e)
        for s, e in zip(filas, etiquetas):
            self.play(FadeIn(s), FadeIn(e), run_time=0.55)
        self.wait(2.0)

        # --- dos distintas: el producto se cancela --------------------------
        marco_a = SurroundingRectangle(VGroup(filas[1], etiquetas[1]),
                                       color=C_MUESTRA, buff=0.12,
                                       stroke_width=1.8)
        marco_b = SurroundingRectangle(VGroup(filas[3], etiquetas[3]),
                                       color=C_CALCULO, buff=0.12,
                                       stroke_width=1.8)
        self.play(Create(marco_a), Create(marco_b), run_time=0.9)
        rot.mostrar(cifra_pie(f"producto = {ORTO_DISTINTAS:.1e}"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)

        # --- una consigo misma: no se cancela nada -------------------------
        marco_c = SurroundingRectangle(VGroup(filas[3], etiquetas[3]),
                                       color=C_CALCULO, buff=0.20,
                                       stroke_width=2.4)
        self.play(FadeOut(marco_a), Transform(marco_b, marco_c),
                  run_time=0.8)
        rot.mostrar(cifra_pie(f"consigo misma = {fmt(ORTO_MISMA, 0)}"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- por eso cada bin mide SOLO lo suyo ----------------------------
        self.play(FadeOut(marco_b), run_time=0.4)
        bar = barras(MAG, ancho=7.0, alto=1.9, rango_y=(0.0, 9.0))
        bar.move_to(DOWN * 2.15)
        et_bar = tag_hud("|X[k]|", font_size=19, color=C_CALCULO)
        et_bar.next_to(bar, LEFT, buff=0.30)
        self.play(*[FadeOut(m) for m in filas[:3]],
                  *[FadeOut(m) for m in etiquetas[:3]], run_time=0.7)
        self.play(FadeIn(bar), FadeIn(et_bar), run_time=0.9)
        self.wait(3.4)
        marca = bar.barra(K_BUENO).copy().set_fill(C_CALCULO, opacity=0.9)
        self.play(FadeIn(marca), run_time=0.5)
        rot.mostrar(cifra_pie(f"|X[{K_BUENO}]| = {fmt(PICO, 3)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)
        rot.mostrar(cifra_pie(f"el resto = {FUERA:.0e}"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
