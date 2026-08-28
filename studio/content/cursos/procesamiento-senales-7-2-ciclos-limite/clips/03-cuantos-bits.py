class Clip3(Scene):
    """7.2.3 - 6, 8 y 10 bits atrapan 0.125, 0.03125 y 0.0078: cada dos
    bits divide por cuatro, exactamente como el paso de cuantizacion. Es
    ruido de redondeo, no señal. (~33 s)"""

    N_DIB = 48       # muestras por carril (los tres se paran dentro)
    DEC = {6: 3, 8: 5, 10: 4}   # decimales justos de cada amplitud

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("Cuantos bits"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        n = self.N_DIB
        centros = (UP * 1.55, ORIGIN, DOWN * 1.55)
        carriles, izq, der = [], VGroup(), VGroup()
        for b, c in zip(BITS_CL, centros):
            s = Secuencia(Y_POS[b][0][:n], 0, (0.0, 0.5), ancho=8.6,
                          alto=1.25, color=C_SALIDA, radio=0.032)
            s.move_to(LEFT * 0.55 + c)
            e = tag_hud(f"{b} bits", font_size=18, color=C_TENUE)
            e.next_to(s, LEFT, buff=0.24)
            v = tag_hud(f"{fmt(ATRAPADA_POS[b], self.DEC[b])}", font_size=18,
                        color=C_CALCULO)
            v.next_to(s, RIGHT, buff=0.26)
            carriles.append(s)
            izq.add(e)
            der.add(v)

        for i, b in enumerate(BITS_CL):
            s = carriles[i]
            self.play(FadeIn(s.ejes), FadeIn(izq[i]), run_time=0.4)
            self.play(LaggedStart(*[FadeIn(s.tallo(k)) for k in range(n)],
                                  lag_ratio=0.025),
                      LaggedStart(*[FadeIn(s.punto(k)) for k in range(n)],
                                  lag_ratio=0.025), run_time=1.3)
            self.play(FadeIn(der[i]), run_time=0.35)
            rot.mostrar(cifra_pie(f"{b} bits: "
                                  f"{fmt(ATRAPADA_POS[b], self.DEC[b])}"),
                        zona="abajo", run_time=0.45)
            self.wait(1.7)

        # --- las tres amplitudes, en escala logaritmica ------------------
        self.play(*[FadeOut(s) for s in carriles], FadeOut(izq),
                  FadeOut(der), run_time=0.7)

        alturas = [float(np.log10(ATRAPADA_POS[b])) for b in BITS_CL]
        bar = barras(alturas, ancho=6.2, alto=2.5, color=C_CALCULO,
                     rango_y=(-2.6, -0.6))
        bar.move_to(LEFT * 0.45 + DOWN * 0.55)
        et_log = tag_hud("escala log", font_size=18, color=C_TENUE)
        et_log.next_to(bar, RIGHT, buff=0.55)
        pies = VGroup()
        for i, b in enumerate(BITS_CL):
            t = tag_hud(f"{b} bits", font_size=18, color=C_TENUE)
            t.next_to(bar.barra(i), DOWN, buff=0.16)
            pies.add(t)
        self.play(FadeIn(bar), FadeIn(et_log), FadeIn(pies), run_time=1.0)
        self.wait(1.6)

        cimas = VGroup()
        for i, b in enumerate(BITS_CL):
            t = tag_hud(f"{fmt(ATRAPADA_POS[b], self.DEC[b])}",
                        font_size=18, color=C_CALCULO)
            t.next_to(bar.barra(i), UP, buff=0.14)
            cimas.add(t)
            self.play(FadeIn(t), Indicate(bar.barra(i), color=C_CALCULO,
                                          scale_factor=1.04), run_time=0.6)
            self.wait(1.5)

        rot.mostrar(cifra_pie("cada 2 bits, entre 4"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        # --- la amplitud atrapada son 4 pasos de cuantizacion ------------
        panel = panel_cifras(*[(f"{b} bits: {fmt(BANDA[b][1] / BANDA[b][2], 0)}"
                                f" pasos", C_CALCULO) for b in BITS_CL])
        self.play(FadeIn(panel), run_time=0.7)
        rot.mostrar(cifra_pie("siempre 4 pasos"), zona="abajo", run_time=0.5)
        self.wait(3.0)
        rot.mostrar(formula_pie(r"A_{\mathrm{atrapada}} = 4\,\Delta"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)
