# 19 · Cierre — la espiral se recoge en el punto de la marca.
#
# El gesto lo pone la propia materia del curso, y por eso este cierre solo
# podia ser este: la espiral de Cornu de la pieza 04 da infinitas vueltas
# acercandose a un punto al que no llega nunca (0.5, 0.5). Ese limite es el
# punto ambar de CO.DE. La marca no se posa encima del contenido: es el
# sitio al que el contenido tiende.
#
# El punto no se dibuja aparte: es el mismo mobject que venia siendo la
# espiral, de modo que la continuidad es real y no una coincidencia de
# posiciones.
#
# La espiral la calcula `especiales.py`, la misma libreria que las 18
# piezas. Ni el cierre lleva curvas a mano.
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

        # --- 1. la espiral entera se dibuja ---------------------------
        LADO = 3.9
        P = esp.marco((-0.82, 0.82), (-0.82, 0.82), ancho=LADO, alto=LADO)
        s, xc, yc = esp.clotoide(4.8, 4400)
        espiral = esp.curva(xc, yc, P, color=AMBAR, grosor=2.2)
        espiral.move_to([0, 2.25, 0])
        lz.cabe(espiral, "espiral de cierre")

        self.wait(0.5)
        self.play(Create(espiral), run_time=2.2, rate_func=smooth)
        self.wait(1.3)

        # --- 2. y se recoge en su propio limite ------------------------
        # La espiral no "desaparece": se va a donde ella misma iba.
        self.play(Transform(espiral, punto.copy()), run_time=1.3,
                  rate_func=smooth)
        self.remove(espiral)
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
