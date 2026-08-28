class Clip2(Scene):
    """8.2.2 - El MISMO filtro repartido en M ramas: h[k], h[k+M],
    h[k+2M]... Cada rama calcula solo lo que hace falta. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("Las ramas polifase"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        COLS = [C_MUESTRA, C_SENAL, C_SALIDA, C_APREND]
        RANGO = (-0.27, 0.27)

        # --- los 61 coeficientes del mismo filtro -------------------------
        sec = Secuencia(H_P, 0, RANGO, ancho=11.4, alto=2.6,
                        color=C_TENUE, radio=0.036)
        sec.move_to(UP * 0.55)
        self.play(FadeIn(sec.ejes), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i))
                                for i in range(N_TAPS_P)], lag_ratio=0.012),
                  LaggedStart(*[FadeIn(sec.punto(i))
                                for i in range(N_TAPS_P)], lag_ratio=0.012),
                  run_time=2.0)
        rot.mostrar(cifra_pie(f"{N_TAPS_P} coeficientes"), zona="abajo",
                    run_time=0.5)
        self.wait(2.0)

        # --- se reparten por k % M ---------------------------------------
        for k in range(M_DIEZ):
            idx = list(range(k, N_TAPS_P, M_DIEZ))
            self.play(LaggedStart(
                *[sec.tallo(i).animate.set_color(COLS[k]) for i in idx],
                *[sec.punto(i).animate.set_color(COLS[k]) for i in idx],
                lag_ratio=0.03), run_time=0.8)
            rot.mostrar(cifra_pie(f"rama {k}: {TAPS_RAMA[k]} taps",
                                  color=COLS[k]), zona="abajo", run_time=0.45)
            self.wait(1.1)

        # --- y se separan: cuatro filtros cortos --------------------------
        filas = VGroup()
        etiquetas = VGroup()
        for k in range(M_DIEZ):
            r = Secuencia(RAMAS[k], 0, RANGO, ancho=6.6, alto=0.7,
                          color=COLS[k], radio=0.042, grosor=2.0,
                          eje_y=False)
            r.move_to(LEFT * 2.6 + UP * (1.35 - 1.0 * k))
            filas.add(r)
            et = tag_hud(f"h{k}: {TAPS_RAMA[k]} taps", font_size=19,
                         color=COLS[k])
            et.next_to(r, RIGHT, buff=0.34)
            etiquetas.add(et)

        self.play(FadeOut(sec.ejes), FadeOut(sec.tallos), FadeOut(sec.puntos),
                  run_time=0.7)
        self.play(LaggedStart(*[FadeIn(f) for f in filas], lag_ratio=0.18),
                  run_time=1.8)
        self.play(LaggedStart(*[FadeIn(e) for e in etiquetas],
                              lag_ratio=0.15), run_time=0.8)
        self.wait(2.0)

        # --- lo que cuesta ahora ------------------------------------------
        panel = panel_cifras(f"directo = {MACS_DIRECTO}",
                             f"polifase = {fmt(MACS_POLIFASE, 2)}",
                             (f"ahorro = {fmt(AHORRO, 1)}x", C_SALIDA))
        self.play(FadeIn(panel), run_time=0.7)
        rot.mostrar(cifra_pie(f"{MACS_DIRECTO} -> {fmt(MACS_POLIFASE, 2)}"
                              " macs"), zona="abajo", run_time=0.5)
        self.wait(3.0)

        rot.mostrar(cifra_pie(f"ahorro {fmt(AHORRO, 1)}x exacto",
                              color=C_SALIDA), zona="abajo", run_time=0.5)
        self.wait(3.0)

        rot.mostrar(formula_pie(r"h_k[n] = h[nM + k]"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)
