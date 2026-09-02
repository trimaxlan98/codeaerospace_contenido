# 19 · Cierre — el espectro se recoge en el punto de la marca.
#
# El gesto inverso al de la intro: alli una onda se volvia su espectro; aqui
# el espectro se contrae hasta quedar en UN solo tallo, ese tallo se
# convierte en el punto ambar, y el punto es el de CO.DE. La marca no se
# posa encima del contenido: SALE de el.
#
# El wordmark se construye igual que en la intro (mayusculas y punto
# tipografico alineados por el borde inferior), y el punto no se dibuja
# aparte: es el mismo mobject que venia siendo el tallo, de modo que la
# continuidad es real y no una coincidencia de posiciones.
class Clip(Pieza):
    ES_MARCA = True
    SALIDA = 1.1

    def pieza(self):
        Y_MARCA = 0.95

        # --- el destino: donde tiene que acabar el punto ---------------
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
        raya = Line(marca.get_corner(DL), marca.get_corner(DR),
                    stroke_width=4.0, color=AMBAR)
        raya.shift(DOWN * 0.26)

        # --- 1. un espectro ancho --------------------------------------
        n = np.arange(256)
        onda = (np.cos(2 * np.pi * 7 * n / 256)
                + 0.7 * np.cos(2 * np.pi * 19 * n / 256)
                + 0.45 * np.cos(2 * np.pi * 34 * n / 256))
        ancho = tf.tallos(np.abs(np.fft.rfft(onda))[:44], ancho=4.6,
                          alto=1.9, color=AMBAR, grosor=2.2, punta=0.038)
        ancho.move_to([0, 2.3, 0])
        self.wait(0.5)
        self.play(FadeIn(ancho, lag_ratio=0.02, run_time=1.2))
        self.wait(1.4)

        # --- 2. se recoge en uno solo ----------------------------------
        uno = np.zeros(44)
        uno[22] = 1.0
        solo = tf.tallos(uno, ancho=4.6, alto=1.9, color=AMBAR, grosor=2.2,
                         punta=0.038)
        solo.move_to([0, 2.3, 0])
        self.play(Transform(ancho, solo), run_time=1.3, rate_func=smooth)
        self.wait(1.0)

        # --- 3. y el tallo se vuelve EL punto de la marca --------------
        self.play(Transform(ancho, punto.copy()), run_time=1.0,
                  rate_func=smooth)
        self.remove(ancho)
        self.add(punto)
        self.play(FadeIn(co, shift=RIGHT * 0.45),
                  FadeIn(de, shift=LEFT * 0.45), run_time=0.9,
                  rate_func=smooth)
        self.play(FadeIn(academy, lag_ratio=0.08, shift=UP * 0.12),
                  run_time=0.8)
        self.play(Create(raya), run_time=0.6)

        # --- 4. el punto parpadea como un cursor y se despide ----------
        self.wait(0.5)
        for _ in range(2):
            punto.set_opacity(0.0)
            self.wait(0.17)
            punto.set_opacity(1.0)
            self.wait(0.16)
        self.wait(1.8)
