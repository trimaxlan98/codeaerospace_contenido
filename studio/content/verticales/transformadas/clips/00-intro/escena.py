# 00 · Intro — la marca de la casa y el gesto del curso, sobre el lienzo.
#
# El wordmark va como manda la marca y como quedo corregido en el curso 31:
# "CO.DE" en MAYUSCULAS con un PUNTO TIPOGRAFICO, los tres alineados por el
# borde INFERIOR (mayusculas y punto comparten linea de base, asi que
# igualar los bordes de abajo ES alinearlos). La version con minusculas y un
# `Dot` redondo a media altura se leia "co·de" y salia chueca.
#
# Lo que NO viene es la reticula HUD ni las escuadras de esquina: son la
# identidad de CONSOLA y aqui contradirian el estilo.
#
# El gesto propio de este curso va al final y es el curso entero en dos
# segundos: una onda se convierte en su espectro. Ninguna palabra explica
# que es una transformada; se ve.
class Clip(Pieza):
    ES_MARCA = True
    SALIDA = 1.0

    def pieza(self):
        Y_MARCA = 1.85

        # --- el wordmark, construido como manda la marca ---------------
        co = Text("CO", font=lz.FUENTE_DISPLAY, weight="SEMIBOLD",
                  font_size=104, color=TINTA)
        punto = Text(".", font=lz.FUENTE_DISPLAY, weight="BOLD",
                     font_size=104, color=AMBAR)
        de = Text("DE", font=lz.FUENTE_DISPLAY, weight="SEMIBOLD",
                  font_size=104, color=TINTA)
        marca = VGroup(co, punto, de).arrange(buff=0.10, aligned_edge=DOWN)
        marca.move_to([0, Y_MARCA, 0])
        lz.cabe(marca, "wordmark")

        academy = Text("A C A D E M Y", font=lz.FUENTE_DISPLAY,
                       weight="MEDIUM", font_size=34, color=APAGADO)
        academy.next_to(marca, DOWN, buff=0.42)
        lz.cabe(academy, "academy")

        raya = Line(marca.get_corner(DL), marca.get_corner(DR),
                    stroke_width=4.0, color=AMBAR)
        raya.shift(DOWN * 0.26)

        # --- el titulo del curso ---------------------------------------
        titulo = lz.titulo_display("TRANSFORMADAS", font_size=56)
        bajada = lz.espaciado("cambiar de dominio", font_size=28,
                              color=AMBAR, tracking=0.34)
        titulo.move_to([0, 0.30, 0])
        bajada.next_to(titulo, DOWN, buff=0.40)

        # --- 1. CO y DE se ensamblan -----------------------------------
        self.wait(0.6)
        self.play(FadeIn(co, shift=RIGHT * 0.60),
                  FadeIn(de, shift=LEFT * 0.60),
                  run_time=1.1, rate_func=smooth)

        # --- 2. el punto llega el ultimo, y parpadea como un cursor ----
        self.play(FadeIn(punto, shift=DOWN * 0.40), run_time=0.5,
                  rate_func=rate_functions.ease_out_cubic)
        for _ in range(2):
            punto.set_opacity(0.0)
            self.wait(0.17)
            punto.set_opacity(1.0)
            self.wait(0.16)
        self.wait(0.2)

        # --- 3. ACADEMY y el subrayado ---------------------------------
        self.play(FadeIn(academy, lag_ratio=0.08, shift=UP * 0.12),
                  run_time=0.9)
        self.play(Create(raya), run_time=0.6)
        self.wait(0.7)

        # --- 4. la marca se aparta y entra el titulo -------------------
        bloque = VGroup(marca, academy, raya)
        self.play(bloque.animate.scale(0.46).move_to([0, 4.35, 0]),
                  run_time=1.0, rate_func=smooth)
        self.play(FadeIn(titulo, shift=UP * 0.22), run_time=0.9)
        self.play(FadeIn(bajada, lag_ratio=0.06), run_time=0.7)
        self.wait(1.1)

        # --- 5. el gesto: una onda se vuelve su espectro ---------------
        n = np.arange(256)
        onda = np.cos(2 * np.pi * 9 * n / 256) + \
            0.55 * np.cos(2 * np.pi * 23 * n / 256)
        curva, _ = tf.traza(n, onda, ancho=4.6, alto=1.5, color=TINTA,
                            grosor=2.6)
        curva.move_to([0, -2.35, 0])
        espectro = tf.tallos(np.abs(np.fft.rfft(onda))[:40], ancho=4.6,
                             alto=1.5, color=AMBAR, grosor=2.2, punta=0.036)
        espectro.move_to([0, -2.35, 0])

        self.play(Create(curva), run_time=1.1)
        self.wait(0.6)
        self.play(Transform(curva, espectro), run_time=1.0,
                  rate_func=smooth)
        self.wait(1.5)
