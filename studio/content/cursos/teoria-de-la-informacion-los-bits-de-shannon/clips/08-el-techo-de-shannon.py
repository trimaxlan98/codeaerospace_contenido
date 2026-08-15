class Clip8(Scene):
    """8 - El techo de Shannon. En el plano SNR (dB) contra eficiencia
    espectral, log2(1 + SNR) es una frontera: por encima no hay nada. Los
    cuatro MODCOD publicados de DVB-S2 (cita ETSI) caen debajo, y su
    distancia al techo se CALCULA con `snr_para_eficiencia`: entre 1.1 y
    2.9 dB. La linea de tiempo cuenta los cincuenta anios que costo
    rozarla -- Hamming, turbo codigos, LDPC, 5G -- y la fila de
    miniaturas recoge todo el curso. Cierre a pantalla limpia: la
    informacion no se adivina, se mide. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("El techo de Shannon"), zona="arriba",
                    run_time=0.6)

        # eta_max=6.5 (y no el 5 de fabrica): a 18 dB la curva vale 6.0
        # b/s/Hz, asi que con el techo por defecto se recortaria en una
        # MESETA falsa a partir de los 15 dB. Con 6.5 la curva sube hasta
        # el borde derecho, que es lo que dice el teorema.
        plano = plano_shannon(db_min=-2, db_max=18, eta_max=6.5).scale(0.95)
        plano.move_to(np.array([-1.6, -0.15, 0.0]))

        # --- momento 1: nada por encima de la curva --------------------
        rot.mostrar(pie_curso("En el plano señal a ruido contra bits por "
                              "segundo y hercio: nada por encima."),
                    zona="abajo")
        self.play(Create(plano.ejes), FadeIn(plano.ticks),
                  FadeIn(plano.etiqueta_x), FadeIn(plano.etiqueta_y),
                  run_time=0.8)
        self.play(Create(plano.curva), run_time=1.4)
        formula = MathTex(r"\eta = \log_2(1 + \mathrm{SNR})", font_size=28,
                          color=C_LIMITE)
        formula.move_to(np.array([2.8, 1.50, 0.0]))
        self.play(FadeIn(plano.prohibido), FadeIn(formula, shift=0.10 * UP),
                  run_time=0.8)
        self.wait(3.2)

        # --- momento 2: los modems reales se acercan -------------------
        rot.mostrar(pie_curso("Los módems de satélite DVB-S2 se acercan: a "
                              "uno, dos o tres decibelios del techo."),
                    zona="abajo")
        # Los nombres alternan derecha / abajo: 8PSK y 16APSK caen a menos
        # de un cuarto de unidad uno de otro y de otro modo se pisarian.
        lados = (RIGHT, DOWN, RIGHT, RIGHT)
        marcas, nombres = VGroup(), VGroup()
        for (nombre, eta, db, _gap), lado in zip(GAPS_DVBS2, lados):
            d = plano.marca(db, eta, C_CODIGO)
            t = tag_hud(nombre, font_size=11, color=C_CODIGO)
            t.next_to(d, lado, buff=0.14 if lado is DOWN else 0.12)
            marcas.add(d)
            nombres.add(t)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(d, scale=0.5),
                                               FadeIn(t))
                                for d, t in zip(marcas, nombres)],
                              lag_ratio=0.35), run_time=1.5)

        # La distancia al techo del ultimo MODCOD, en horizontal: cuantos
        # dB de mas pide frente a lo que permite Shannon a esa eficiencia.
        nombre_u, eta_u, db_u, gap_u = GAPS_DVBS2[-1]
        p_modcod = plano.punto(db_u, eta_u)
        p_techo = plano.punto(snr_para_eficiencia(eta_u), eta_u)
        guia = DashedLine(p_techo, p_modcod, stroke_width=1.8, color=C_RUIDO,
                          dash_length=0.07)
        tag_gap = tag_hud(f"{gap_u:.1f} dB", font_size=11, color=C_RUIDO)
        tag_gap.move_to((p_techo + p_modcod) / 2.0 + DOWN * 0.22)
        tag_cita = tag_hud("DVB-S2 (ETSI, cita)", font_size=11,
                           color=C_TENUE)
        tag_cita.move_to(plano.punto(11.0, 0.62))
        self.play(Create(guia), FadeIn(tag_gap), FadeIn(tag_cita),
                  run_time=0.9)
        self.wait(3.6)

        # --- momento 3: cincuenta anios para rozarlo -------------------
        rot.mostrar(pie_curso("Tardamos cincuenta años en rozarlo: turbo "
                              "códigos, LDPC… hoy en cada satélite y en "
                              "5G."), zona="abajo")
        self.play(FadeOut(nombres), FadeOut(guia), FadeOut(tag_gap),
                  FadeOut(tag_cita), FadeOut(formula), run_time=0.5)
        grupo_plano = VGroup(plano, marcas)
        self.play(grupo_plano.animate.scale(0.72 / 0.95).move_to(
            np.array([-2.30, 0.95, 0.0])), run_time=1.1)

        tiempo = linea_tiempo(HITOS, ancho=8.6)
        tiempo.move_to(np.array([0.0, -1.60, 0.0]))
        self.play(FadeIn(tiempo.linea), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(tiempo.hito(k), shift=0.10 * UP)
                                for k in range(len(HITOS))], lag_ratio=0.4),
                  run_time=1.4)
        self.wait(3.2)

        # --- momento 4: todo lo que vimos ------------------------------
        rot.mostrar(pie_curso("Cada bit que baja del cielo lo mide esta "
                              "curva. Y todo lo que vimos:"), zona="abajo")
        self.play(FadeOut(tiempo.linea), FadeOut(tiempo.hitos), run_time=0.4)

        piezas = (curva_sorpresa(), curva_entropia_binaria(),
                  arbol_huffman(FREC_HUFFMAN), esquema_bsc(P_BSC),
                  curva_shannon_hartley(), venn_hamming(PALABRA_HAMMING))
        rotulos_mini = ("sorpresa", "entropia", "Huffman", "canal", "techo",
                        "Hamming")
        fila = VGroup(*[p.scale(0.35) for p in piezas])
        fila.arrange(RIGHT, buff=0.35)
        if fila.width > 11.2:
            fila.scale_to_fit_width(11.2)
        fila.move_to(np.array([0.0, -1.45, 0.0]))
        y_tag = fila.get_bottom()[1] - 0.22
        tags_mini = VGroup()
        for pieza, texto in zip(fila, rotulos_mini):
            t = tag_hud(texto, font_size=11, color=C_TENUE)
            t.move_to(np.array([pieza.get_center()[0], y_tag, 0.0]))
            tags_mini.add(t)
        self.play(LaggedStart(*[FadeIn(p, scale=0.85) for p in fila],
                              lag_ratio=0.28), run_time=1.8)
        self.play(FadeIn(tags_mini), run_time=0.5)
        self.wait(3.2)

        # --- cierre: pantalla limpia -----------------------------------
        rot.limpiar(run_time=0.45)
        self.play(FadeOut(grupo_plano), FadeOut(fila), FadeOut(tags_mini),
                  run_time=0.7)
        frase_1 = Text("La información no se adivina.", font_size=44,
                       color=C_TITULO)
        frase_1.move_to(np.array([0.0, 0.55, 0.0]))
        frase_2 = Text("Se mide.", font_size=52, color=C_LIMITE)
        frase_2.next_to(frase_1, DOWN, buff=0.55)
        self.play(Write(frase_1), run_time=1.1)
        self.play(FadeIn(frase_2, shift=0.12 * UP), run_time=0.8)
        self.wait(5.2)
