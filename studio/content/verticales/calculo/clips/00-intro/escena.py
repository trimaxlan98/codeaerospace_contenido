# 00 · Intro — la marca de la casa y el reparto del curso, sobre el lienzo.
#
# El wordmark va como manda la marca y como quedo corregido en el curso 31:
# "CO.DE" en MAYUSCULAS con un PUNTO TIPOGRAFICO, los tres alineados por el
# borde INFERIOR (mayusculas y punto comparten linea de base, asi que
# igualar los bordes de abajo ES alinearlos).
#
# Lo que NO viene es la reticula HUD ni las escuadras de esquina: son la
# identidad de CONSOLA y aqui contradirian el estilo.
#
# El gesto de este curso es el REPARTO: tres dibujos, uno detras de otro,
# en el mismo sitio. Ninguna palabra dice de que van; se ve que son tres
# demostraciones —una escalera pegada a una circunferencia, un circulo
# desenrollado en un triangulo, una campana— y que ninguna es una formula.
# Las tres las calcula `calculo.py`, la misma libreria que las 18 piezas:
# ni la cabecera lleva una curva dibujada a mano.
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
        titulo = lz.titulo_display("CALCULO", font_size=62)
        titulo2 = lz.titulo_display("VISIBLE", font_size=62)
        titulo2.next_to(titulo, DOWN, buff=0.16)
        bloque_titulo = VGroup(titulo, titulo2)
        bajada = lz.espaciado("lo que se demuestra mirando", font_size=26,
                              color=AMBAR, tracking=0.28)
        bloque_titulo.move_to([0, 0.55, 0])
        bajada.next_to(bloque_titulo, DOWN, buff=0.42)
        lz.cabe(bloque_titulo, "titulo del curso")
        lz.cabe(bajada, "bajada del curso")

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
        self.play(FadeIn(bloque_titulo, shift=UP * 0.22), run_time=0.9)
        self.play(FadeIn(bajada, lag_ratio=0.06), run_time=0.7)
        self.wait(1.0)

        # --- 5. el reparto: tres demostraciones en el mismo sitio ------
        LADO = 2.05
        centro = [0, -2.60, 0]

        P = cal.marco_igual((-0.62, 0.62), (-0.62, 0.62), ancho=LADO,
                            alto=LADO)
        pts = cal.escalera_circulo(6)
        escalera = lz.agrupar(
            cal.circulo_en(P, 0.0, 0.0, cal.RADIO, color=AMBAR, grosor=2.4),
            cal.curva(pts[:, 0], pts[:, 1], P, color=AMBAR, grosor=1.6))

        Q = cal.marco((-np.pi * 5 * 1.03, np.pi * 5 * 1.03), (5.2, 0.0),
                      ancho=LADO * 1.35, alto=LADO * 0.62)
        triangulo = cal.tiras(cal.anillos_circulo(5.0, 7), Q, color=AMBAR,
                              opacidad=0.22)

        R = cal.marco((-2.6, 2.6), (0.0, 1.12), ancho=LADO * 1.35,
                      alto=LADO * 0.72)
        xs = np.linspace(-2.6, 2.6, 700)
        campana = lz.agrupar(
            cal.region(xs, cal.campana(xs), R, color=AMBAR, opacidad=0.20),
            cal.curva(xs, cal.campana(xs), R, color=AMBAR, grosor=2.4))

        for silueta in (escalera, triangulo, campana):
            silueta.move_to(centro)
            lz.cabe(silueta, "silueta del reparto")

        self.play(Create(escalera), run_time=1.3, rate_func=smooth)
        self.wait(0.55)
        self.play(FadeOut(escalera), FadeIn(triangulo), run_time=0.65)
        self.wait(0.55)
        self.play(FadeOut(triangulo), FadeIn(campana), run_time=0.65)
        self.wait(1.25)
