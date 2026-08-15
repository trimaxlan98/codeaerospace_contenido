class Clip6(Scene):
    """6 - Shannon-Hartley: el techo del enlace. C = B log2(1 + S/N)
    sobre un transpondedor Ku de 36 MHz: 10 dB de C/N dan 124.5 Mb/s y 20
    dB -- diez veces la potencia -- solo 239.7, ni el doble; la curva es
    logaritmica. Doblar el ancho de banda si dobla la capacidad (la curva
    verde de 72 MHz, recortada al techo de los ejes) y tres decibelios
    mas suman un bit por segundo y hercio (3.46 -> 4.39). Con B infinito
    queda el muro: Eb/N0 >= -1.59 dB. Puente con «Cerrar el enlace»:
    C/N0 = C/N + 10 log B = 85.6 dBHz. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 06")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Shannon–Hartley: el techo del enlace"),
                    zona="arriba", run_time=0.6)

        # Geometria: la curva (5.13 x 3.58 con ejes y etiquetas, escalada
        # 0.9) ocupa la mitad izquierda de la banda central; la columna
        # derecha (x = 3.25) lleva la formula arriba (y = +1.75), la caja
        # de la eficiencia (y = +0.35) y los dos tags de los limites
        # (y = -0.85 y y = -1.75). Los rotulos de los puntos van DENTRO
        # del plano, en las zonas que la curva deja vacias.
        formula = MathTex(r"C = B\,\log_2\!\left(1 + \tfrac{S}{N}\right)",
                          font_size=40, color=C_LIMITE)
        formula.move_to(np.array([0.0, 0.20, 0.0]))

        # --- momento 1: el techo tiene formula -------------------------------
        rot.mostrar(pie_curso("Un canal real tiene ancho de banda B y señal "
                              "a ruido. El techo de Shannon y Hartley:"),
                    zona="abajo")
        self.play(Write(formula), run_time=1.4)
        self.wait(2.4)
        self.play(formula.animate.scale(0.7).move_to(
            np.array([3.25, 1.75, 0.0])), run_time=0.9)

        # --- momento 2: el transpondedor de 36 MHz ---------------------------
        rot.mostrar(pie_curso(f"Un transpondedor de "
                              f"{B_TRANSPONDEDOR_HZ / 1e6:.0f} MHz con "
                              f"{CN_DB_1} dB de señal a ruido: "
                              f"{C_ENLACE_1 / 1e6:.1f} megabits por "
                              f"segundo."), zona="abajo")
        curva = curva_shannon_hartley(B_TRANSPONDEDOR_HZ).scale(0.9)
        curva.move_to(np.array([-2.40, -0.45, 0.0]))
        leyenda_b = tag_hud(f"B = {B_TRANSPONDEDOR_HZ / 1e6:.0f} MHz",
                            font_size=13, color=C_LIMITE)
        leyenda_b.move_to(curva.punto(4.5, 268))
        self.play(Create(curva.ejes), FadeIn(curva.ticks),
                  FadeIn(curva.etiqueta_x), FadeIn(curva.etiqueta_y),
                  run_time=0.8)
        self.play(Create(curva.curva), FadeIn(leyenda_b), run_time=1.3)

        p_1 = curva.en(CN_DB_1)
        dot_1 = Dot(p_1, radius=0.075, color=C_BIT)
        tag_1 = tag_hud(f"{CN_DB_1} dB -> {C_ENLACE_1 / 1e6:.1f} Mb/s",
                        font_size=14, color=C_BIT)
        tag_1.move_to(curva.punto(11.0, 40))
        guia_1 = DashedLine(p_1, tag_1.get_top() + UP * 0.04,
                            stroke_width=1.2, color=C_BIT, dash_length=0.07)
        guia_1.set_stroke(opacity=0.45)
        self.play(FadeIn(dot_1, scale=0.5), Create(guia_1), FadeIn(tag_1),
                  run_time=0.8)
        self.wait(2.6)

        # --- momento 3: diez veces la potencia -------------------------------
        rot.mostrar(pie_curso(f"Diez veces más potencia, {CN_DB_2} dB: "
                              f"{C_ENLACE_2 / 1e6:.1f} megabits. Ni el "
                              f"doble."), zona="abajo")
        p_2 = curva.en(CN_DB_2)
        dot_2 = Dot(p_2, radius=0.075, color=C_BIT)
        tag_2 = tag_hud(f"{CN_DB_2} dB -> {C_ENLACE_2 / 1e6:.1f} Mb/s",
                        font_size=14, color=C_BIT)
        # Bajo la curva y a la derecha del rotulo de 10 dB: arriba manda la
        # curva de 72 MHz, que se pega al techo de los ejes.
        tag_2.move_to(curva.punto(19.0, 140))
        guia_2 = DashedLine(p_2, tag_2.get_top() + UP * 0.05,
                            stroke_width=1.2, color=C_BIT, dash_length=0.07)
        guia_2.set_stroke(opacity=0.45)
        self.play(FadeIn(dot_2, scale=0.5), Create(guia_2), FadeIn(tag_2),
                  run_time=0.8)
        self.wait(4.0)

        # --- momento 4: las dos perillas -------------------------------------
        rot.mostrar(pie_curso("Doblar B dobla la capacidad; tres decibelios "
                              "más suman un bit por segundo y hercio."),
                    zona="abajo")
        # La curva de 72 MHz se RECORTA al techo de estos ejes (300 Mb/s):
        # se ve pegada arriba a partir de los 12 dB, y eso es exactamente
        # lo que dice el momento.
        curva_2b = curva.con_ancho(2 * B_TRANSPONDEDOR_HZ, color=C_CODIGO)
        leyenda_2b = tag_hud(f"2B = {2 * B_TRANSPONDEDOR_HZ / 1e6:.0f} MHz",
                             font_size=13, color=C_CODIGO)
        leyenda_2b.next_to(leyenda_b, DOWN, buff=0.14, aligned_edge=LEFT)
        caja_eta = caja_numero("+3 dB (b/s/Hz)",
                               f"{ETA_10:.2f} -> {ETA_13:.2f}", C_BIT,
                               ancho=2.9)
        caja_eta.move_to(np.array([3.25, 0.35, 0.0]))
        self.play(Create(curva_2b), run_time=1.3)
        self.play(FadeIn(leyenda_2b), run_time=0.4)
        self.play(FadeIn(caja_eta, shift=0.12 * UP), run_time=0.6)
        self.wait(2.8)

        # --- momento 5: el muro de Eb/N0 -------------------------------------
        rot.mostrar(pie_curso(f"Con ancho de banda infinito hay un muro: "
                              f"Eb/N0 no baja de {EBN0_MIN:.2f} dB. El "
                              f"límite de Shannon."), zona="abajo")
        tag_limite = tag_hud(f"limite: Eb/N0 >= {EBN0_MIN:.2f} dB",
                             font_size=15, color=C_LIMITE)
        tag_limite.move_to(np.array([3.25, -0.85, 0.0]))
        self.play(FadeIn(tag_limite, shift=0.1 * UP), run_time=0.5)
        self.wait(4.0)

        # --- momento 6: el puente con «Cerrar el enlace» ---------------------
        rot.mostrar(pie_curso(f"C/N0 = C/N + 10 log B: aquí, "
                              f"{CN0_ENLACE_1:.1f} dB·Hz — la cuenta de "
                              f"«Cerrar el enlace»."), zona="abajo")
        tag_cn0 = tag_hud(f"C/N0 = {CN0_ENLACE_1:.1f} dBHz", font_size=15,
                          color=C_FUENTE)
        tag_cn0.move_to(np.array([3.25, -1.75, 0.0]))
        self.play(FadeIn(tag_cn0, shift=0.1 * UP), run_time=0.5)
        self.wait(4.0)

        # --- cierre ----------------------------------------------------------
        rot.mostrar(pie_curso("El enlace tiene techo. Y sale de una fórmula "
                              "de 1948."), zona="abajo")
        self.wait(5.0)
