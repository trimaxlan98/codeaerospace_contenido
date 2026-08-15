class Clip3(Scene):
    """3 - Huffman: decir lo justo. Con "ABRACADABRA" (A5 B2 R2 C1 D1) se
    construye el arbol de Huffman EN VIVO (fusion a fusion, `.paso(k)`) y
    cada letra recibe su codigo (`.codigo(s)`): la frecuente, corto; la
    rara, largo. El mensaje codificado como tira de segmentos pesa 23 bits
    frente a 33 con 3 bits fijos; la longitud media (2.09) casi toca la
    entropia (2.04). Salto al espanol: longitud media medida frente a H,
    5 fijos y 8 ASCII. Cierre: un buen codigo gasta casi exactamente la
    entropia, nunca menos. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Huffman: decir lo justo"), zona="arriba",
                    run_time=0.6)

        COLORES = {"A": C_BIT, "B": C_FUENTE, "R": C_CODIGO, "C": C_LIMITE,
                  "D": C_TENUE}
        ORDEN = ["A", "B", "R", "C", "D"]
        pesos = {s: int(round(f * len(MENSAJE_HUFFMAN)))
                 for s, f in FREC_HUFFMAN.items()}

        # --- momento 1: el mensaje y sus frecuencias -----------------------
        rot.mostrar(pie_curso("Un mensaje: ABRACADABRA. Cinco letras, pero "
                              "no igual de frecuentes."), zona="abajo")
        mensaje = Text(MENSAJE_HUFFMAN, font_size=34)
        for i, ch in enumerate(MENSAJE_HUFFMAN):
            mensaje[i].set_color(COLORES[ch])
        mensaje.move_to(np.array([0.0, 1.55, 0.0]))
        self.play(FadeIn(mensaje, shift=0.12 * UP), run_time=0.8)

        fila_conteo = VGroup(*[
            tag_hud(f"{s} x{pesos[s]}", font_size=17, color=COLORES[s])
            for s in ORDEN])
        fila_conteo.arrange(RIGHT, buff=0.45)
        fila_conteo.move_to(np.array([0.0, 0.95, 0.0]))
        self.play(LaggedStart(*[FadeIn(t, shift=0.08 * UP)
                                for t in fila_conteo], lag_ratio=0.15),
                  run_time=1.0)
        self.wait(2.3)

        # --- momento 2: el arbol se construye fusion a fusion ---------------
        rot.mostrar(pie_curso("Huffman (1952): se funden los dos pesos "
                              "menores, una y otra vez, hasta la raíz."),
                    zona="abajo")
        self.play(FadeOut(mensaje), FadeOut(fila_conteo), run_time=0.5)

        arbol = arbol_huffman(FREC_HUFFMAN, colores=COLORES, pesos=pesos,
                              ancho=5.5, alto=3.2)
        arbol.scale(0.98)
        arbol.move_to(np.array([-2.4, 0.05, 0.0]))
        self.play(FadeIn(arbol.hojas, shift=0.1 * UP), run_time=0.8)
        for k in range(arbol.n_fusiones):
            self.play(FadeIn(arbol.paso(k)), run_time=0.8)
        self.wait(1.0)

        # --- momento 3: cada letra recibe su camino --------------------------
        rot.mostrar(pie_curso("Cada letra recibe su camino: la frecuente, "
                              "corto; la rara, largo."), zona="abajo")
        col = VGroup(*[
            tag_hud(f"{s} = {CODIGO_HUFFMAN[s]}", font_size=16,
                    color=COLORES[s]) for s in ORDEN])
        col.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        col.move_to(np.array([2.5, 0.0, 0.0]))
        for s in ORDEN:
            self.play(FadeIn(col[ORDEN.index(s)], shift=0.1 * RIGHT),
                      run_time=0.45)
            self.play(Indicate(arbol.codigo(s), color=COLORES[s],
                               scale_factor=1.2), run_time=0.5)
        self.wait(0.8)

        # --- momento 4: la tira codificada frente a bits fijos ---------------
        rot.mostrar(pie_curso(f"El mensaje pesa {BITS_HUFFMAN} bits, frente "
                              f"a {BITS_FIJOS_HUFFMAN} con "
                              f"{bits_fijos(len(FREC_HUFFMAN))} bits fijos "
                              f"por letra."), zona="abajo")
        tira = tira_codigo(MENSAJE_HUFFMAN, CODIGO_HUFFMAN, COLORES,
                           ancho=5.6, alto=0.42)
        tira.move_to(np.array([-0.8, -2.2, 0.0]))
        self.play(LaggedStart(*[FadeIn(seg, shift=0.06 * UP)
                                for seg in tira.segmentos], lag_ratio=0.06),
                  run_time=1.4)
        tag_bits = tag_hud(f"{BITS_HUFFMAN} bits", font_size=18,
                           color=C_CODIGO)
        tag_bits.next_to(tira, RIGHT, buff=0.28)
        tag_fijo = tag_hud(f"fijo: {BITS_FIJOS_HUFFMAN} bits", font_size=14,
                           color=C_TENUE)
        tag_fijo.next_to(tag_bits, DOWN, buff=0.14, aligned_edge=LEFT)
        self.play(FadeIn(tag_bits, shift=0.1 * RIGHT), run_time=0.4)
        self.play(FadeIn(tag_fijo, shift=0.1 * RIGHT), run_time=0.4)
        self.wait(2.5)

        # --- momento 5: longitud media casi toca la entropia -----------------
        rot.mostrar(pie_curso(f"Longitud media {L_HUFFMAN:.2f} bits por "
                              f"letra; la entropía es {H_HUFFMAN:.2f}. Casi "
                              f"el mínimo."), zona="abajo")
        caja_media = caja_numero("media", f"{L_HUFFMAN:.2f}", C_CODIGO,
                                 ancho=1.55)
        caja_h = caja_numero("H", f"{H_HUFFMAN:.2f}", C_LIMITE, ancho=1.55)
        cajas = VGroup(caja_media, caja_h).arrange(RIGHT, buff=0.28)
        cajas.move_to(np.array([5.1, 2.1, 0.0]))
        self.play(FadeIn(caja_media, shift=0.15 * UP), run_time=0.5)
        self.play(FadeIn(caja_h, shift=0.15 * UP), run_time=0.5)
        self.wait(3.2)

        # --- momento 6: cierre, el español pasa igual -------------------------
        rot.mostrar(pie_curso(f"Con el español pasa igual: {L_ES:.2f} bits "
                              f"de media frente a H = {H_ES:.2f}, en vez de "
                              f"{BITS_FIJOS_27} fijos u 8 de ASCII."),
                    zona="abajo")
        tag_texto = tag_hud(
            f"texto: {miles(BITS_TEXTO_ASCII)} -> {miles(BITS_TEXTO_FIJOS)} "
            f"-> {miles(BITS_TEXTO_HUFFMAN)} bits", font_size=13,
            color=C_TENUE)
        tag_texto.next_to(cajas, DOWN, buff=0.30)
        self.play(FadeIn(tag_texto, shift=0.08 * UP), run_time=0.5)
        self.wait(5.0)

        # --- cierre --------------------------------------------------------
        rot.mostrar(pie_curso("Un buen código gasta casi exactamente la "
                              "entropía. Nunca menos."), zona="abajo")
        self.wait(5.0)
