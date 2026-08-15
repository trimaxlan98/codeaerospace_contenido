class Clip2(Scene):
    """2 - La entropia: cuanto hay que decir. La sorpresa PROMEDIO de una
    fuente es su entropia H. La campana h(p) de la moneda: 1 bit justo en
    p = 0.5, 0.47 con la trucada al 90 % y cero si siempre cae cara.
    Luego una fuente real: los 27 simbolos de un texto de muestra en
    espanol (Quijote, cap. I), con sus frecuencias MEDIDAS -- H = 3.96
    bits por simbolo frente a los 4.75 de una fuente uniforme: el idioma
    es predecible y por eso pesa menos. Cierre: H es lo minimo que hay que
    decir, en promedio, por simbolo. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("La entropía: cuánto hay que decir"),
                    zona="arriba", run_time=0.6)

        def punto(coords):
            v = [float(c) for c in coords]
            return np.array(v + [0.0] * (3 - len(v)))

        def rotulo(texto, centro, color, fs=14):
            t = tag_hud(texto, font_size=fs, color=color)
            t.move_to(punto(centro))
            return t

        def guia(desde, hasta, color):
            g = DashedLine(punto(desde), punto(hasta), stroke_width=1.2,
                           color=color, dash_length=0.08)
            g.set_stroke(opacity=0.45)
            return g

        # --- momento 1: la entropia es la sorpresa promedio -------------
        # La campana vive a la izquierda (x = -2.7) y la formula a la
        # derecha (x = +2.6): la banda central queda partida en dos y nada
        # se toca. Despues la campana se va y entra el histograma.
        rot.mostrar(pie_curso("La sorpresa promedio de una fuente es su "
                              "entropía. Shannon la llamó H."), zona="abajo")
        campana = curva_entropia_binaria().scale(0.95)
        campana.move_to(np.array([-2.70, 0.40, 0.0]))
        self.play(Create(campana.ejes), FadeIn(campana.ticks),
                  FadeIn(campana.etiqueta_x), FadeIn(campana.etiqueta_y),
                  run_time=0.8)
        self.play(Create(campana.curva), run_time=1.1)

        ley = MathTex(r"H = -\sum p_i \log_2 p_i", font_size=30,
                      color=C_LIMITE)
        ley.move_to(np.array([2.60, 0.60, 0.0]))
        self.play(Write(ley), run_time=0.9)
        self.wait(2.9)

        # --- momento 2: los tres casos de la moneda ---------------------
        rot.mostrar(pie_curso(f"Una moneda justa: "
                              f"{entropia_binaria(0.5):.0f} bit por tirada. "
                              f"Trucada al {P_MONEDA_TRUCADA * 100:.0f} %: "
                              f"{H_MONEDA_TRUCADA:.2f}. Que siempre cae "
                              f"cara: {entropia_binaria(1.0):.0f}."),
                    zona="abajo")

        p_justa = campana.en(0.5)
        d_justa = Dot(p_justa, radius=0.075, color=C_LIMITE)
        t_justa = rotulo(f"{entropia_binaria(0.5):.0f} bit",
                         [p_justa[0], p_justa[1] + 0.30], C_LIMITE)
        self.play(FadeIn(d_justa, scale=0.6), FadeIn(t_justa, shift=0.08 * UP),
                  run_time=0.5)

        p_truc = campana.en(P_MONEDA_TRUCADA)
        d_truc = Dot(p_truc, radius=0.075, color=C_LIMITE)
        t_truc = rotulo(f"{H_MONEDA_TRUCADA:.2f} bits", [0.25, 0.30],
                        C_LIMITE)
        g_truc = guia(p_truc, t_truc.get_left() + LEFT * 0.05, C_LIMITE)
        self.play(FadeIn(d_truc, scale=0.6), Create(g_truc), FadeIn(t_truc),
                  run_time=0.5)

        p_cara = campana.en(1.0)
        d_cara = Dot(p_cara, radius=0.075, color=C_LIMITE)
        t_cara = rotulo(f"{entropia_binaria(1.0):.0f} bits", [0.40, -0.85],
                        C_LIMITE)
        g_cara = guia(p_cara, t_cara.get_left() + LEFT * 0.05, C_LIMITE)
        self.play(FadeIn(d_cara, scale=0.6), Create(g_cara), FadeIn(t_cara),
                  run_time=0.5)
        self.wait(3.9)

        # --- momento 3: una fuente real ---------------------------------
        rot.mostrar(pie_curso(f"Una fuente real: un texto en español. "
                              f"Contamos sus {len(SIMBOLOS)} símbolos."),
                    zona="abajo")
        # El histograma ocupa la banda central entera: la linea base baja a
        # y = -1.25 y las barras suben 2.1, asi que el pico (el espacio,
        # 18.8 %) queda en y = +0.85, por debajo de la caja y del rotulo
        # del texto de muestra.
        hist = histograma_simbolos(FREC_ES, C_FUENTE, alto=2.1)
        hist.move_to(np.array([0.15, -0.32, 0.0]))
        t_muestra = rotulo("texto de muestra: Quijote, cap. I",
                           [-0.80, 1.35], C_TENUE, fs=12)
        # La campana sale ENTERA antes de que entre el histograma: sus
        # ticks y las 27 etiquetas caen a alturas parecidas y en el cruce
        # se rozarian.
        self.play(FadeOut(ley),
                  FadeOut(VGroup(campana, d_justa, t_justa, d_truc, g_truc,
                                 t_truc, d_cara, g_cara, t_cara)),
                  run_time=0.45)
        self.play(FadeIn(hist.linea_base), FadeIn(hist.etiquetas),
                  LaggedStart(*[GrowFromEdge(b, DOWN) for b in hist.barras],
                              lag_ratio=0.035), run_time=1.7)
        self.play(FadeIn(t_muestra, shift=0.08 * UP), run_time=0.4)
        self.wait(3.1)

        # --- momento 4: H medida frente a la uniforme -------------------
        rot.mostrar(pie_curso(f"Sale H = {H_ES:.2f} bits por símbolo. Si "
                              f"todos fueran igual de probables, "
                              f"{H_UNIFORME_27:.2f}."), zona="abajo")
        uniforme = hist.linea_uniforme(C_LIMITE)
        t_uniforme = tag_hud(f"uniforme: {H_UNIFORME_27:.2f} bits",
                             font_size=13, color=C_LIMITE)
        t_uniforme.next_to(uniforme, RIGHT, buff=0.16)
        self.play(Create(uniforme), run_time=0.8)
        self.play(FadeIn(t_uniforme), run_time=0.4)

        caja = caja_numero("H medida", f"{H_ES:.2f} bits", C_LIMITE,
                           ancho=2.2)
        caja.move_to(np.array([4.55, 0.55, 0.0]))
        self.play(FadeIn(caja, shift=0.12 * UP), run_time=0.6)
        self.wait(3.6)

        # --- cierre ------------------------------------------------------
        rot.mostrar(pie_curso("H es lo mínimo que hay que decir, en "
                              "promedio, por símbolo. Ni un bit menos."),
                    zona="abajo")
        self.wait(5.0)
