class Clip1(Scene):
    """7.2.1 - El filtro mas simple que existe, y[n] = Q(a y[n-1]) con
    a = 0.9 y sin entrada: sin cuantizar se apaga, con 8 bits se queda
    clavado en 0.03125 y ya no baja mas. (~34 s)"""

    N_DIB = 40          # muestras del carril ancho
    N_ZOOM = (20, 60)   # tramo de la cola, ampliado

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("La banda muerta"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        n = self.N_DIB
        y_q = Y_POS[BITS_DEMO][0]

        # --- el ideal: se apaga ------------------------------------------
        ideal = Secuencia(Y_IDEAL[:n], 0, (0.0, 0.5), ancho=8.8, alto=1.7,
                          color=C_IDEAL, radio=0.038)
        ideal.move_to(LEFT * 0.7 + UP * 1.20)
        et_ideal = tag_hud("ideal", font_size=18, color=C_IDEAL)
        et_ideal.next_to(ideal, LEFT, buff=0.22)
        self.play(FadeIn(ideal.ejes), FadeIn(et_ideal), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(ideal.tallo(i)) for i in range(n)],
                              lag_ratio=0.035),
                  LaggedStart(*[FadeIn(ideal.punto(i)) for i in range(n)],
                              lag_ratio=0.035), run_time=1.8)
        rot.mostrar(cifra_pie(f"cola ideal {COLA_IDEAL:.1e}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        # --- el mismo filtro con 8 bits: se para -------------------------
        quant = Secuencia(y_q[:n], 0, (0.0, 0.5), ancho=8.8, alto=1.7,
                          color=C_SALIDA, radio=0.038)
        quant.move_to(LEFT * 0.7 + DOWN * 0.95)
        et_quant = tag_hud(f"{BITS_DEMO} bits", font_size=18, color=C_SALIDA)
        et_quant.next_to(quant, LEFT, buff=0.22)
        self.play(FadeIn(quant.ejes), FadeIn(et_quant), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(quant.tallo(i)) for i in range(n)],
                              lag_ratio=0.035),
                  LaggedStart(*[FadeIn(quant.punto(i)) for i in range(n)],
                              lag_ratio=0.035), run_time=1.8)
        self.wait(0.9)

        cola = quant.ventana(24, n - 1, color=C_RUIDO, opacidad=0.12)
        self.play(FadeIn(cola), run_time=0.6)
        rot.mostrar(cifra_pie(f"se para en {fmt(ATRAPADA_BM, 5)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- la cola, ampliada: uno llega a cero y el otro no ------------
        a, b = self.N_ZOOM
        self.play(FadeOut(ideal), FadeOut(et_ideal), FadeOut(quant),
                  FadeOut(et_quant), FadeOut(cola), run_time=0.7)

        zoom = Secuencia(y_q[a:b], a, (0.0, 0.06), ancho=9.2, alto=2.5,
                         color=C_SALIDA, radio=0.038)
        zoom.move_to(LEFT * 0.55 + DOWN * 0.35)
        curva = zoom.curva_de(np.arange(a, b), Y_IDEAL[a:b], color=C_IDEAL,
                              grosor=2.6)
        et_z = tag_hud(f"{BITS_DEMO} bits", font_size=18, color=C_SALIDA)
        et_z.next_to(zoom, LEFT, buff=0.22)
        self.play(FadeIn(zoom.ejes), FadeIn(et_z), run_time=0.5)
        self.play(Create(curva), run_time=1.3)
        self.play(LaggedStart(*[FadeIn(zoom.tallo(i)) for i in range(b - a)],
                              lag_ratio=0.03),
                  LaggedStart(*[FadeIn(zoom.punto(i)) for i in range(b - a)],
                              lag_ratio=0.03), run_time=1.6)
        self.wait(1.4)

        # --- la cota teorica (dato) y el suelo medido (cian) -------------
        lin_cota = zoom.horizontal_en(TEORICA_BM, color=C_DATO)
        et_cota = tag_hud(f"cota {fmt(TEORICA_BM, 4)}", font_size=18,
                          color=C_DATO)
        et_cota.next_to(zoom.en(b - 1, TEORICA_BM), RIGHT, buff=0.26)
        self.play(Create(lin_cota), FadeIn(et_cota), run_time=0.8)
        rot.mostrar(dato_pie(f"cota {fmt(TEORICA_BM, 4)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        lin_atr = zoom.horizontal_en(ATRAPADA_BM, color=C_CALCULO)
        et_atr = tag_hud(f"{fmt(ATRAPADA_BM, 5)}", font_size=18,
                         color=C_CALCULO)
        et_atr.next_to(zoom.en(b - 1, ATRAPADA_BM), RIGHT, buff=0.26)
        self.play(Create(lin_atr), FadeIn(et_atr), run_time=0.8)
        rot.mostrar(cifra_pie(f"atrapada en {fmt(ATRAPADA_BM, 5)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        panel = panel_cifras((f"paso = {fmt(PASO_BM, 4)}", C_TENUE),
                             (f"atrapada = {fmt(ATRAPADA_BM, 5)}", C_CALCULO),
                             (f"pasos = {fmt(PASOS_ATRAPADOS, 0)}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)
        rot.mostrar(formula_pie(r"y[n] = Q\!\left(a\, y[n-1]\right)"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
