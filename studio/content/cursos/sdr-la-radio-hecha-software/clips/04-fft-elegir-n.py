class Clip4(Scene):
    """4 - La FFT: elegir N. El flujo continuo se corta en bloques de N
    muestras, cada uno una FFT; comparar N chico contra N grande muestra el
    compromiso: bins mas finos en frecuencia a costa de que cada bloque
    abarque mas tiempo (lo rapido se emborrona)."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: titulo y HUD del modulo ------------------------------
        titulo = titulo_curso("La FFT: elegir N")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.wait(0.8)

        # --- momento: el flujo cortado en 5 bloques con la llave "N muestras"
        flujo5 = flujo_en_bloques(ancho=6.6, alto=0.65, bloques=5, ciclos=11.0)
        flujo5.move_to(np.array([0.0, 1.5, 0.0]))
        x0 = flujo5.cortes[0].get_center()[0]
        x1 = flujo5.cortes[1].get_center()[0]
        y_ref = float(flujo5.get_bottom()[1])
        segmento = Line(np.array([x0, y_ref, 0.0]), np.array([x1, y_ref, 0.0]))
        segmento.set_stroke(opacity=0.0)
        llave_n = llave(segmento, "N muestras", direccion=DOWN)

        self.play(Create(flujo5.onda), run_time=0.9)
        self.play(FadeIn(flujo5.cortes, lag_ratio=0.1), run_time=0.6)
        self.play(FadeIn(llave_n, shift=0.12 * DOWN), run_time=0.5)
        rot.mostrar(pie_curso("El flujo se corta en bloques de N muestras; "
                              "cada bloque, una FFT."), zona="abajo",
                   run_time=0.5)
        self.wait(5.6)

        # --- momento: la formula del bin de frecuencia -----------------------
        rot.mostrar(formula_pie("\\Delta f = f_s / N"), zona="abajo",
                   run_time=0.45)
        self.wait(5.2)

        # --- momento: la llave se retira antes de tocar el flujo -------------
        self.play(FadeOut(llave_n), run_time=0.4)

        # --- momento: dos espectros de barras, N chico vs N grande -----------
        xs5 = np.linspace(-1.0, 1.0, 5)
        alturas5 = np.clip(0.55 * np.exp(-14.0 * (xs5 + 0.15) ** 2)
                           + 0.85 * np.exp(-14.0 * (xs5 - 0.15) ** 2) + 0.05,
                           0.0, 1.0)
        xs20 = np.linspace(-1.0, 1.0, 20)
        alturas20 = np.clip(0.55 * np.exp(-14.0 * (xs20 + 0.15) ** 2)
                            + 0.85 * np.exp(-14.0 * (xs20 - 0.15) ** 2) + 0.05,
                            0.0, 1.0)
        barras_chico = barras_espectro(alturas5, ancho=2.9, alto=1.8,
                                       color=C_SENAL)
        barras_chico.move_to(np.array([-2.9, -1.2, 0.0]))
        barras_grande = barras_espectro(alturas20, ancho=2.9, alto=1.8,
                                        color=C_SENAL)
        barras_grande.move_to(np.array([2.9, -1.2, 0.0]))
        tag_chico = tag_junto(barras_chico, "N pequeño", direccion=DOWN)
        tag_grande = tag_junto(barras_grande, "N grande", direccion=DOWN)

        self.play(FadeIn(barras_chico, shift=0.15 * UP),
                  FadeIn(barras_grande, shift=0.15 * UP), run_time=0.9)
        self.play(FadeIn(tag_chico), FadeIn(tag_grande), run_time=0.5)
        rot.mostrar(pie_curso("N grande: bins más finos. Se distingue "
                              "mejor en frecuencia..."), zona="abajo",
                   run_time=0.5)
        self.wait(5.2)

        # --- momento: bajo el flujo, el compromiso temporal (5 -> 2 bloques)
        flujo2 = flujo_en_bloques(ancho=6.6, alto=0.65, bloques=2, ciclos=11.0)
        flujo2.move_to(np.array([0.0, 1.5, 0.0]))
        rot.mostrar(pie_curso("...pero cada bloque abarca más tiempo: lo "
                              "rápido se emborrona."), zona="abajo",
                   run_time=0.5)
        self.play(ReplacementTransform(flujo5, flujo2), run_time=1.6)
        self.wait(3.4)

        # --- momento: el numero concreto junto a las barras finas ------------
        hud_n = etiqueta_hud("N=2048 → Δf ≈ 1.2 kHz")
        hud_n.next_to(barras_grande, UP, buff=0.28)
        self.play(FadeIn(hud_n, shift=0.1 * UP), run_time=0.5)
        rot.mostrar(pie_curso("Ni grande ni pequeño es mejor: N se elige "
                              "según lo que quieras ver."), zona="abajo",
                   run_time=0.5)
        self.wait(5.6)
