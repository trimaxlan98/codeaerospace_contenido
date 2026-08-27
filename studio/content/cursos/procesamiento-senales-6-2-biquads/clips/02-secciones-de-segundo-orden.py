class Clip2(Scene):
    """6.2.2 - El mismo filtro partido en 5 biquads: cada seccion solo
    tiene que representar DOS polos. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("Secciones de segundo orden"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        colores = [C_SENAL, C_SALIDA, C_BANDA, C_APREND, C_IDEAL]
        # El par de polos de cada seccion y su radio, medidos sobre SOS.
        pares = [np.roots([1.0, fila[4], fila[5]]) for fila in SOS]
        radios = [float(abs(par[0])) for par in pares]

        # --- de donde se viene: un solo polinomio de grado 10 -------------
        caja0 = bloque(f"orden {ORDEN}", ancho=2.9, alto=1.0, color=C_DATO,
                       color_texto=C_DATO, tamano=26)
        caja0.move_to(LEFT * 4.75)
        et0 = tag_hud(f"{len(A)} coeficientes", font_size=19, color=C_DATO)
        et0.next_to(caja0, DOWN, buff=0.22)
        self.play(FadeIn(caja0), run_time=0.7)
        self.play(FadeIn(et0), run_time=0.4)
        rot.mostrar(cifra_pie(f"un polinomio de grado {ORDEN}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.0)

        # --- la cadena de 5 biquads ---------------------------------------
        cajas = VGroup()
        for i in range(N_BIQUADS):
            c = bloque(f"biquad {i + 1}", ancho=2.2, alto=0.60,
                       color=C_DATO, color_texto=C_DATO, tamano=22)
            c.move_to(LEFT * 4.75 + UP * (2.1 - 1.05 * i))
            cajas.add(c)
        flechas = VGroup(*[conectar(cajas[i], cajas[i + 1], color=C_DATO,
                                    grosor=2.2, margen=0.06)
                           for i in range(N_BIQUADS - 1)])
        for f in flechas:                 # la punta de una flecha de 0.3 de
            f.tip.scale(2.0)              # largo sale de 4 px: se agranda
        self.play(FadeOut(caja0), FadeOut(et0),
                  LaggedStart(*[FadeIn(c) for c in cajas], lag_ratio=0.16),
                  run_time=1.6)
        self.play(LaggedStart(*[Create(f) for f in flechas],
                              lag_ratio=0.20), run_time=0.9)
        et_x = tag_hud("x[n]", font_size=19, color=C_MUESTRA)
        et_x.next_to(cajas[0], UP, buff=0.16)
        et_y = tag_hud("y[n]", font_size=19, color=C_SALIDA)
        et_y.next_to(cajas[-1], DOWN, buff=0.16)
        self.play(FadeIn(et_x), FadeIn(et_y), run_time=0.5)
        rot.mostrar(cifra_pie(f"{N_BIQUADS} biquads / 2 polos"),
                    zona="abajo", run_time=0.5)
        self.wait(1.6)

        # --- los mismos 10 polos, de cerca --------------------------------
        pz = PlanoZ([], POLOS_EXACTOS, unidad=5.00, alcance=1.10,
                    color_polo=C_DATO)
        pz.shift(np.array([-1.875, -0.15, 0.0]) - pz.en(0))
        arco = pz.arco(-0.52, 0.52, color=C_DATO, grosor=2.2)
        et_circ = tag_hud("|z| = 1", font_size=19, color=C_DATO)
        et_circ.next_to(pz.en(1.05), RIGHT, buff=0.15)
        self.play(Create(arco), run_time=0.9)
        self.play(FadeIn(et_circ), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(m) for m in pz.polos],
                              lag_ratio=0.07), run_time=1.4)
        rot.mostrar(cifra_pie(f"{ORDEN} polos exactos"), zona="abajo",
                    run_time=0.5)
        self.wait(1.5)

        # --- cada seccion se lleva SU par ---------------------------------
        for i in range(N_BIQUADS):
            idx = [int(np.argmin(np.abs(POLOS_EXACTOS - z)))
                   for z in pares[i]]
            self.play(cajas[i].animate.set_color(colores[i]),
                      pz.polos[idx[0]].animate.set_color(colores[i]),
                      pz.polos[idx[1]].animate.set_color(colores[i]),
                      run_time=0.55)
            rot.mostrar(cifra_pie(f"biquad {i + 1}: r = {radios[i]:.4f}"),
                        zona="abajo", run_time=0.5)
            self.wait(1.1)

        panel = panel_cifras((f"{N_BIQUADS} secciones", C_CALCULO),
                             ("2 polos cada una", C_CALCULO),
                             (f"grado {ORDEN} -> grado 2", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.6)

        rot.mostrar(formula_pie(r"H_k(z) = \frac{b_0 + b_1 z^{-1} + "
                                r"b_2 z^{-2}}{1 + a_1 z^{-1} + a_2 z^{-2}}",
                                font_size=30), zona="abajo", run_time=0.5)
        self.wait(4.0)
