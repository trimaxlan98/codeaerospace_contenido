class Clip7(Scene):
    """7 - Corregir sin volver a preguntar: Hamming(7,4). Repetir cada bit
    tres veces corrige un error pero gasta el triple; Hamming mete tres
    bits de paridad entre cuatro de datos y deja los tres circulos del
    diagrama de Venn con un numero PAR de unos. Un rayo voltea el bit 5:
    dos circulos quedan impares y su interseccion delata al culpable --
    el sindrome ES la posicion, calculado por la libreria. Tasas 1/3
    frente a 4/7, y las BER MEDIDAS por simulacion sembrada en un canal
    con 5 % de error. Cierre: la comparacion justa es por energia por
    bit. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Corregir sin volver a preguntar"),
                    zona="arriba", run_time=0.6)

        # Geometria: dos columnas. La fila de tiras vive arriba (y = 1.75,
        # bien por debajo del titulo); el Venn ocupa la columna izquierda
        # de la banda central (su borde inferior queda en -2.2, encima del
        # pie) y la columna derecha guarda las tasas y la tabla de BER.
        Y_FILA, X_IZQ, X_DER = 1.75, -2.75, 2.35

        # --- momento 1: repetir gasta el triple ------------------------
        rot.mostrar(pie_curso("Repetir cada bit tres veces corrige un "
                              "error… pero gasta el triple."), zona="abajo")
        tira_datos = tira_bits(DATOS_HAMMING, C_BIT, celda=0.34)
        tira_datos.move_to(np.array([X_IZQ, Y_FILA, 0.0]))
        tag_datos = tag_hud("datos", font_size=14, color=C_TENUE)
        tag_datos.next_to(tira_datos, DOWN, buff=0.18)

        bits_rep = repeticion_codificar(DATOS_HAMMING, 3)
        tira_rep = tira_bits(bits_rep, C_CODIGO, celda=0.26)
        tira_rep.move_to(np.array([X_DER, Y_FILA, 0.0]))
        tag_rep = tag_hud(f"x3 -> {len(bits_rep)} bits", font_size=14,
                          color=C_TENUE)
        tag_rep.next_to(tira_rep, DOWN, buff=0.18)

        self.play(FadeIn(tira_datos, shift=0.12 * UP), FadeIn(tag_datos),
                  run_time=0.6)
        self.play(LaggedStart(*[FadeIn(c, scale=0.7)
                                for c in tira_rep.celdas], lag_ratio=0.06),
                  run_time=1.1)
        self.play(FadeIn(tag_rep), run_time=0.35)
        self.wait(3.0)

        # --- momento 2: los tres circulos suman par --------------------
        rot.mostrar(pie_curso("Hamming, 1950: cuatro bits de datos, tres de "
                              "paridad, y cada círculo suma par."),
                    zona="abajo")
        self.play(FadeOut(tira_rep), FadeOut(tag_rep), run_time=0.45)

        venn = venn_hamming(PALABRA_HAMMING).scale(0.9)
        venn.move_to(np.array([X_IZQ, -0.40, 0.0]))
        tira7 = tira_bits(PALABRA_HAMMING, C_CODIGO, celda=0.30)
        tira7.move_to(np.array([X_DER, Y_FILA, 0.0]))
        tag7 = tag_hud(f"{len(PALABRA_HAMMING)} bits: p1 p2 d1 p3 d2 d3 d4",
                       font_size=11, color=C_TENUE)
        tag7.next_to(tira7, DOWN, buff=0.18)
        self.play(FadeIn(venn, shift=0.12 * UP),
                  LaggedStart(*[FadeIn(c, scale=0.7) for c in tira7.celdas],
                              lag_ratio=0.07),
                  FadeIn(tag7), run_time=1.3)
        # `colorear_paridad` MUTA: se aplica sobre la gemela y se transforma
        # para que el verde entre animado, no de golpe.
        venn_par = venn.con_bits(PALABRA_HAMMING)
        venn_par.colorear_paridad()
        self.play(Transform(venn, venn_par), run_time=0.8)
        self.wait(3.2)

        # --- momento 3: un rayo voltea el bit 5 ------------------------
        rot.mostrar(pie_curso(f"Un rayo voltea el bit {POS_ERROR_HAMMING}. "
                              f"Dos círculos quedan impares."), zona="abajo")
        venn_err = venn.con_bits(PALABRA_CON_ERROR)
        venn_err.colorear_paridad()
        tira_err = tira7.con_bits(PALABRA_CON_ERROR)
        n_volteado = tira_err.marcar_distintos(PALABRA_HAMMING, C_RUIDO)
        tag_volteado = tag_hud(f"{n_volteado} bit volteado", font_size=12,
                               color=C_RUIDO)
        tag_volteado.next_to(tira7, UP, buff=0.16)
        self.play(Transform(venn, venn_err), Transform(tira7, tira_err),
                  run_time=1.4)
        self.play(Flash(venn.region(POS_ERROR_HAMMING), color=C_RUIDO,
                        line_length=0.16, num_lines=14, flash_radius=0.40),
                  FadeIn(tag_volteado, shift=0.10 * DOWN), run_time=0.7)
        self.wait(3.0)

        # --- momento 4: el sindrome ES la posicion ---------------------
        rot.mostrar(pie_curso(f"La intersección de los impares delata al "
                              f"culpable: síndrome {SINDROME}. Se corrige."),
                    zona="abajo")
        tag_sind = tag_hud(f"sindrome = {SINDROME} -> bit {POS_CORREGIDA}",
                           font_size=14, color=C_CODIGO)
        tag_sind.next_to(venn, DOWN, buff=0.16)
        venn_ok = venn.con_bits(PALABRA_CORREGIDA)
        venn_ok.colorear_paridad()
        tira_ok = tira7.con_bits(PALABRA_CORREGIDA)
        self.play(FadeIn(tag_sind, shift=0.10 * UP), run_time=0.5)
        self.play(Transform(venn, venn_ok), Transform(tira7, tira_ok),
                  run_time=1.2)
        self.wait(3.2)

        # --- momento 5: lo que cuesta cada tasa ------------------------
        rot.mostrar(pie_curso("Repetir manda un tercio de datos útiles; "
                              "Hamming, cuatro séptimos."), zona="abajo")
        self.play(FadeOut(tira_datos), FadeOut(tag_datos),
                  FadeOut(tag_volteado), run_time=0.5)
        tag_tasas = tag_hud(f"tasa: rep x3 = {TASA_REP3:.2f}   "
                            f"Hamming = {TASA_HAMMING:.2f}", font_size=13,
                            color=C_TENUE)
        tag_tasas.move_to(np.array([X_DER, 0.55, 0.0]))
        self.play(FadeIn(tag_tasas, shift=0.10 * UP), run_time=0.5)
        self.wait(3.6)

        # --- momento 6: las BER medidas --------------------------------
        rot.mostrar(pie_curso(f"En un canal con {P_CODIGOS * 100:.0f} % de "
                              f"error, medido: sin código "
                              f"{BER['sin'] * 100:.1f} %, repetición "
                              f"{BER['rep3'] * 100:.1f} %, Hamming "
                              f"{BER['hamming'] * 100:.1f} %."), zona="abajo")
        filas = VGroup(
            tag_hud(f"sin codigo  BER {BER['sin']:.3f}  tasa 1",
                    font_size=12, color=C_RUIDO),
            tag_hud(f"rep x3      BER {BER['rep3']:.3f}  "
                    f"tasa {TASA_REP3:.2f}", font_size=12, color=C_CODIGO),
            tag_hud(f"Hamming     BER {BER['hamming']:.3f}  "
                    f"tasa {TASA_HAMMING:.2f}", font_size=12,
                    color=C_CODIGO),
        ).arrange(DOWN, buff=0.20, aligned_edge=LEFT)
        filas.move_to(np.array([X_DER, -0.75, 0.0]))
        tag_bloques = tag_hud(f"{miles(N_BLOQUES)} bloques, semilla",
                              font_size=11, color=C_TENUE)
        tag_bloques.next_to(filas, DOWN, buff=0.22)
        self.play(LaggedStart(*[FadeIn(f, shift=0.10 * UP) for f in filas],
                              lag_ratio=0.35), run_time=1.1)
        self.play(FadeIn(tag_bloques), run_time=0.4)
        self.wait(3.2)

        # --- cierre ----------------------------------------------------
        rot.mostrar(pie_curso("La comparación justa es por energía por bit. "
                              "Y ahí Shannon puso el techo."), zona="abajo")
        self.wait(5.0)
