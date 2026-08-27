class Clip4(Scene):
    """3.2.4 - Partir en pares e impares dos veces deja las entradas en el
    orden de los bits al reves; y la cuenta sale igual. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("El orden bit-reverso"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        Y0, Y1, Y2 = 1.95, 0.50, -1.00
        digitos = [tag_hud(str(i), font_size=27, color=C_TENUE)
                   for i in range(N_FFT)]
        for i, d in enumerate(digitos):
            d.move_to(np.array([-3.5 + i * 1.0, Y0, 0.0]))
        self.play(LaggedStart(*[FadeIn(d, scale=0.6) for d in digitos],
                              lag_ratio=0.07), run_time=1.3)
        self.wait(1.1)

        # El orden de partida se queda de fantasma arriba: es contra el que
        # se compara el orden barajado al final del clip.
        fantasma = VGroup(*[d.copy() for d in digitos])
        fantasma.set_opacity(0.40)
        et_nat = tag_hud("orden natural", font_size=18, color=C_TENUE)
        et_nat.move_to(np.array([-5.05, Y0, 0.0])).set_opacity(0.75)

        # --- primer corte: pares e impares ------------------------------------
        pares_i = list(range(0, N_FFT, 2))
        impares_i = list(range(1, N_FFT, 2))
        rot.mostrar(cifra_pie("corte 1: pares e impares"), zona="abajo",
                    run_time=0.5)
        self.play(*[digitos[i].animate.set_color(C_MUESTRA)
                    for i in pares_i],
                  *[digitos[i].animate.set_color(C_SALIDA)
                    for i in impares_i], run_time=0.8)
        destinos = {}
        for j, i in enumerate(pares_i):
            destinos[i] = np.array([-2.7 + (j - 1.5) * 0.9, Y1, 0.0])
        for j, i in enumerate(impares_i):
            destinos[i] = np.array([2.7 + (j - 1.5) * 0.9, Y1, 0.0])
        self.play(FadeIn(fantasma), FadeIn(et_nat),
                  *[digitos[i].animate.move_to(destinos[i])
                    for i in range(N_FFT)], run_time=1.4)
        caja_p = SurroundingRectangle(VGroup(*[digitos[i] for i in pares_i]),
                                      color=C_MUESTRA, buff=0.22,
                                      stroke_width=1.8)
        caja_i = SurroundingRectangle(VGroup(*[digitos[i] for i in impares_i]),
                                      color=C_SALIDA, buff=0.22,
                                      stroke_width=1.8)
        self.play(Create(caja_p), Create(caja_i), run_time=0.8)
        self.wait(1.9)

        # --- segundo corte: lo mismo dentro de cada mitad ----------------------
        grupos = [pares_i[0::2], pares_i[1::2],
                  impares_i[0::2], impares_i[1::2]]
        centros = [-4.5, -1.8, 1.8, 4.5]
        for g, cx in zip(grupos, centros):
            for j, i in enumerate(g):
                destinos[i] = np.array([cx + (j - 0.5) * 0.9, Y2, 0.0])
        rot.mostrar(cifra_pie("corte 2: otra vez"), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(caja_p), FadeOut(caja_i), run_time=0.35)
        self.play(*[digitos[i].animate.move_to(destinos[i])
                    for i in range(N_FFT)], run_time=1.4)
        cajas2 = VGroup(*[
            SurroundingRectangle(VGroup(*[digitos[i] for i in g]),
                                 color=(C_MUESTRA if k < 2 else C_SALIDA),
                                 buff=0.20, stroke_width=1.6)
            for k, g in enumerate(grupos)])
        self.play(LaggedStart(*[Create(c) for c in cajas2], lag_ratio=0.14),
                  run_time=1.0)
        self.wait(2.1)

        marca = llave(VGroup(*[digitos[i] for i in ORDEN]), "orden de entrada",
                      direccion=DOWN, color=C_CALCULO, font_size=20)
        self.play(FadeIn(marca), run_time=0.7)
        self.wait(2.3)

        # --- lo que queda es el indice con los bits al reves --------------------
        bits = int(math.log2(N_FFT))
        fila_orden = VGroup(*[digitos[i] for i in ORDEN])
        et_ord = tag_hud("bit-reverso", font_size=18, color=C_CALCULO)
        et_ord.move_to(np.array([-5.05, Y0, 0.0]))
        rot.mostrar(cifra_pie("orden = bits al reves"), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(marca), FadeOut(cajas2), FadeOut(fantasma),
                  FadeOut(et_nat), run_time=0.5)
        self.play(*[fila_orden[j].animate.move_to(
                        np.array([-3.5 + j * 1.0, Y0, 0.0]))
                    .set_color(C_CALCULO)
                    for j in range(N_FFT)],
                  FadeIn(et_ord), run_time=1.3)

        filas = VGroup(tag_hud("n    bits   rev    orden", font_size=20,
                               color=C_TENUE))
        for i in range(N_FFT):
            b = format(i, f"0{bits}b")
            filas.add(tag_hud(f"{i}    {b}    {b[::-1]}    {ORDEN[i]}",
                              font_size=20, color=C_CALCULO))
        filas.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        filas.move_to(DOWN * 0.45)
        self.play(FadeIn(filas[0]), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(f) for f in filas[1:]],
                              lag_ratio=0.09), run_time=1.8)
        self.wait(2.4)

        rot.mostrar(cifra_pie(f"FFT vs DFT: {ERROR_FFT:.1e}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        cierre_leccion(self, rot, "La FFT no es otra transformada.",
                       "Es la misma cuenta sin repetirla.",
                       filas, fila_orden, et_ord)
