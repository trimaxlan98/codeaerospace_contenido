# 19 · Cierre — la salida se recoge en el punto de la marca.
#
# El gesto inverso al de la intro: alli un golpe entraba en la caja y salia
# una forma que se apagaba; aqui esa forma se apaga del todo hasta quedar
# en UN solo tallo, ese tallo se convierte en el punto ambar, y el punto es
# el de CO.DE. La marca no se posa encima del contenido: SALE de el.
#
# El punto no se dibuja aparte: es el mismo mobject que venia siendo el
# tallo, de modo que la continuidad es real y no una coincidencia de
# posiciones.
#
# La respuesta que se apaga la calcula `sis.h_amortiguada`, la misma
# funcion que usan las piezas de contenido. Ni el cierre lleva numeros a
# mano.
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

        # --- 1. una respuesta que todavia suena ------------------------
        h = sis.h_amortiguada(N=44, tau=13.0, f=0.10)
        RANGO = (-0.85, 1.0)
        viva = sis.tallos(h, ancho=4.6, alto=2.5, color=AMBAR, grosor=2.2,
                          punta=0.038, rango_y=RANGO)
        viva.move_to([0, 2.3, 0])
        self.wait(0.5)
        self.play(FadeIn(viva, lag_ratio=0.02, run_time=1.2))
        self.wait(1.4)

        # --- 2. se apaga hasta quedar el golpe solo --------------------
        # Mismo rango que la anterior: si cada una se normaliza por su
        # cuenta, apagarse no se ve, porque el maximo siempre llena el
        # cuadro (medido en el curso 32, pieza de Wigner).
        solo = sis.tallos(sis.impulso(N=44), ancho=4.6, alto=2.5,
                          color=AMBAR, grosor=2.2, punta=0.038,
                          rango_y=RANGO)
        solo.move_to([0, 2.3, 0])
        self.play(Transform(viva, solo), run_time=1.3, rate_func=smooth)
        self.wait(1.0)

        # --- 3. y el tallo se vuelve EL punto de la marca --------------
        self.play(Transform(viva, punto.copy()), run_time=1.0,
                  rate_func=smooth)
        self.remove(viva)
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
