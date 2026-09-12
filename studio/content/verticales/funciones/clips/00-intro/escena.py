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
# El gesto de este curso es el REPARTO: tres siluetas, una detras de otra,
# en el mismo sitio. Ninguna palabra dice que son funciones con nombre; se
# ve que son tres dibujos que ninguna formula de bachillerato produce. Y
# las tres las calcula `especiales.py`, la misma libreria que las 18 piezas:
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
        # TRES lineas, no dos: "CON NOMBRE PROPIO" a cuerpo 56 mide 6.53 y
        # la zona segura son 5.76 — el guardian aborto el render. Se parte
        # el titulo antes que bajar el cuerpo: la tipografia no decide el
        # temario (leccion del curso 33).
        titulo = lz.titulo_display("FUNCIONES", font_size=54)
        titulo2 = lz.titulo_display("CON NOMBRE", font_size=54)
        titulo3 = lz.titulo_display("PROPIO", font_size=54)
        titulo2.next_to(titulo, DOWN, buff=0.14)
        titulo3.next_to(titulo2, DOWN, buff=0.14)
        bloque_titulo = VGroup(titulo, titulo2, titulo3)
        bajada = lz.espaciado("las que hubo que inventar", font_size=26,
                              color=AMBAR, tracking=0.30)
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

        # --- 5. el reparto: tres siluetas en el mismo sitio ------------
        LADO = 2.05
        centro = [0, -2.60, 0]

        s, xc, yc = esp.clotoide(4.2, 2600)
        clotoide = esp.curva(xc, yc, esp.marco((-0.80, 0.80), (-0.80, 0.80),
                                               ancho=LADO, alto=LADO),
                             color=AMBAR, grosor=2.4)

        pts = esp.lorenz(n=7000, dt=0.005)
        mariposa = esp.curva(pts[:, 0], pts[:, 2],
                             esp.marco((-19.0, 19.0), (2.0, 47.0),
                                       ancho=LADO, alto=LADO),
                             color=AMBAR, grosor=1.5)

        phi, r = esp.superformula(**esp.FORMAS["diatomea"])
        flor = esp.polar(phi, r, radio=LADO / 2, color=AMBAR, grosor=2.4)

        for silueta in (clotoide, mariposa, flor):
            silueta.move_to(centro)
            lz.cabe(silueta, "silueta del reparto")

        self.play(Create(clotoide), run_time=1.3, rate_func=smooth)
        self.wait(0.55)
        self.play(FadeOut(clotoide), FadeIn(mariposa), run_time=0.65)
        self.wait(0.55)
        self.play(FadeOut(mariposa), FadeIn(flor), run_time=0.65)
        self.wait(1.25)
