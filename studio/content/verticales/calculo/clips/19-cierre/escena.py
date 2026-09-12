# 19 · Cierre — los anillos se recogen en el punto de la marca.
#
# El gesto lo pone la propia materia del curso, y por eso este cierre solo
# podia ser este: el circulo de la pieza 14 es una pila de anillos, y
# medirlo consiste en apretarlos hasta que cada uno es un punto. Aqui se
# aprietan del todo, y lo que queda es el punto ambar de CO.DE. La marca no
# se posa encima del contenido: es el sitio al que el contenido tiende.
#
# Los anillos no "desaparecen": se contraen hacia su centro, que es donde
# acaban todos los anillos de todos los circulos.
#
# Los calcula `calculo.py`, la misma libreria que las 18 piezas. Ni el
# cierre lleva curvas a mano.
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

        # --- 1. el circulo, anillo a anillo ---------------------------
        LADO = 3.8
        R = 5.0
        P = cal.marco_igual((-R - 0.3, R + 0.3), (-R - 0.3, R + 0.3),
                            ancho=LADO, alto=LADO)
        aros = lz.agrupar(*[cal.circulo_en(P, 0.0, 0.0, re, color=AMBAR,
                                           grosor=2.0)
                            for _ri, re, _rm, _g in cal.anillos_circulo(R, 9)])
        aros.move_to([0, 2.25, 0])
        lz.cabe(aros, "anillos de cierre")

        self.wait(0.5)
        self.play(LaggedStart(*[Create(a) for a in aros], lag_ratio=0.10),
                  run_time=2.0)
        self.wait(1.2)

        # --- 2. y se aprietan hasta el centro -------------------------
        self.play(Transform(aros, punto.copy()), run_time=1.4,
                  rate_func=smooth)
        self.remove(aros)
        self.add(punto)
        self.play(FadeIn(co, shift=RIGHT * 0.45),
                  FadeIn(de, shift=LEFT * 0.45), run_time=0.9,
                  rate_func=smooth)
        self.play(FadeIn(academy, lag_ratio=0.08, shift=UP * 0.12),
                  run_time=0.8)
        self.play(Create(raya), run_time=0.6)

        # --- 3. el punto parpadea como un cursor y se despide ----------
        self.wait(0.5)
        for _ in range(2):
            punto.set_opacity(0.0)
            self.wait(0.17)
            punto.set_opacity(1.0)
            self.wait(0.16)
        self.wait(1.8)
