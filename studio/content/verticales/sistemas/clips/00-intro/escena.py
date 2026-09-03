# 00 · Intro — la marca de la casa y el gesto del curso, sobre el lienzo.
#
# El wordmark va como manda la marca y como quedo corregido en el curso 31:
# "CO.DE" en MAYUSCULAS con un PUNTO TIPOGRAFICO, los tres alineados por el
# borde INFERIOR (mayusculas y punto comparten linea de base, asi que
# igualar los bordes de abajo ES alinearlos).
#
# Lo que NO viene es la reticula HUD ni las escuadras de esquina: son la
# identidad de CONSOLA y aqui contradirian el estilo.
#
# El gesto de este curso es la CAJA. Un golpe entra por la izquierda y por
# la derecha sale una forma que se apaga: eso es el curso entero. Ninguna
# palabra dice que es un sistema; se ve entrar una cosa y salir otra.
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
        # "SENALES" sin eñe: la regla de la casa es que el texto
        # RENDERIZADO no lleva acentos ni eñe, porque Rajdhani las
        # trae mal. Aqui salio con la tilde despegada de la N, que es
        # peor que no ponerla. La eñe vive en `curso.json`, que no se
        # renderiza.
        titulo = lz.titulo_display("SENALES", font_size=56)
        titulo2 = lz.titulo_display("Y SISTEMAS", font_size=56)
        titulo2.next_to(titulo, DOWN, buff=0.18)
        bloque_titulo = VGroup(titulo, titulo2)
        bajada = lz.espaciado("que le hace a la senal", font_size=26,
                              color=AMBAR, tracking=0.30)
        bloque_titulo.move_to([0, 0.45, 0])
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
        self.wait(1.1)

        # --- 5. el gesto: un golpe entra en la caja y sale una forma ---
        # La respuesta la calcula la libreria, igual que en las 18 piezas
        # de contenido: ni siquiera el logotipo lleva numeros a mano.
        h = sis.h_amortiguada(N=36, tau=7.0, f=0.13)
        golpe = sis.tallos(sis.impulso(N=8), ancho=1.05, alto=1.35,
                           color=CIAN, grosor=2.8, punta=0.045)
        salida = sis.tallos(h, ancho=1.85, alto=1.35, color=AMBAR,
                            grosor=2.0, punta=0.034,
                            rango_y=(-0.75, 1.0))
        sistema = sis.caja("h", ancho=1.35, alto=1.05)

        fila = VGroup(golpe, sistema, salida).arrange(RIGHT, buff=0.48)
        fila.move_to([0, -2.55, 0])
        f1 = sis.flecha(golpe.get_right() + RIGHT * 0.06,
                        sistema.get_left() + LEFT * 0.06)
        f2 = sis.flecha(sistema.get_right() + RIGHT * 0.06,
                        salida.get_left() + LEFT * 0.06)
        gesto = VGroup(fila, f1, f2)
        lz.cabe(gesto, "el gesto de la caja")

        self.play(FadeIn(golpe, shift=RIGHT * 0.3), run_time=0.6)
        self.play(Create(sistema), run_time=0.6)
        self.play(GrowArrow(f1), run_time=0.35)
        self.play(GrowArrow(f2), run_time=0.35)
        self.play(FadeIn(salida, lag_ratio=0.05, shift=RIGHT * 0.2),
                  run_time=0.9)
        self.wait(1.4)
