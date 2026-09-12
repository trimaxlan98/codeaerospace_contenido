# 10 · HIPERBOLA — convierte productos en sumas.
#
# EL VERBO VISUAL: la franja de 1 a 2 se estira al doble a lo ancho y se
# encoge a la mitad a lo alto. Con esas dos cosas a la vez el area no
# cambia... y el trozo estirado cae EXACTAMENTE encima de la hiperbola
# otra vez, ahora entre 2 y 4. Por eso ir de 1 a 2, de 2 a 4 y de 4 a 8
# cuesta siempre lo mismo: multiplicar por dos suma siempre lo mismo.
#
# Eso es un logaritmo, y la pieza no necesita decir la palabra hasta el
# final: lo que se ve son tres franjas de la misma area.
#
# EL AREA SE MIDE CON TRAPECIOS, NO CON np.log. Si se calculara con el
# logaritmo, la pieza no estaria midiendo nada: el logaritmo es la
# CONCLUSION, no el metodo.
class Clip(Pieza):
    NOMBRE = "HIPERBOLA"
    TESIS = "convierte productos en sumas"

    TRAMOS = ((1.0, 2.0), (2.0, 4.0), (4.0, 8.0))
    RX = (0.80, 8.60)
    RY = (0.0, 1.28)
    ANCHO_CAJA = ANCHO - 0.60
    ALTO_CAJA = 3.90

    def franja(self, a, b, opacidad=0.20):
        x = np.linspace(a, b, 400)
        return cal.region(x, cal.hiperbola(x), self.P, color=AMBAR,
                          opacidad=opacidad)

    def pieza(self):
        L = self.L
        self.P = P = cal.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                               alto=self.ALTO_CAJA)
        xs = np.linspace(self.RX[0], self.RX[1], 1400)
        curva = cal.curva(xs, cal.hiperbola(xs), P, color=TINTA,
                          grosor=cal.TRAZO)
        cuadro = cal.recuadro(P)

        franjas = [self.franja(a, b) for a, b in self.TRAMOS]
        # La que se estira: nace igual que la primera y se morfea en la
        # segunda. Son dos objetos distintos a proposito — la primera se
        # queda donde esta, para que se puedan comparar.
        viajera = self.franja(*self.TRAMOS[0], opacidad=0.20)
        viajera.set_stroke(color=AMBAR, width=2.0, opacity=0.0)
        for m in franjas + [viajera]:
            m.set_fill(opacity=0.0)

        # Sin rotulos dentro del cuadro: la franja de 1 a 2 mide 0.72
        # unidades de ancho en pantalla y un "1 A 2" mide 1.4, asi que las
        # tres etiquetas se solapaban entre ellas. Lo que nombra cada
        # franja es la etiqueta de la cifra, que ya dice de cual habla.
        dibujo = lz.agrupar(cuadro, curva, *franjas, viajera)

        # --- 1. una franja bajo la hiperbola --------------------------
        L.escena(dibujo, t=1.2)
        self.leer(2.6)
        franjas[0].set_fill(opacity=0.20)
        L.morfeo(None,
                 dato=(f"{cal.area_hiperbola(*self.TRAMOS[0]):.4f}",
                       "el area de uno a dos"),
                 animaciones=[FadeIn(franjas[0])], t=1.0)
        self.leer(3.6)

        # --- 2. se estira al doble y se encoge a la mitad -------------
        viajera.set_fill(opacity=0.20).set_stroke(opacity=0.8)
        franjas[1].set_fill(opacity=0.20)
        self.play(FadeIn(viajera), run_time=0.5)
        L.morfeo(None,
                 dato=(f"{cal.area_hiperbola(*self.TRAMOS[1]):.4f}",
                       "y la de dos a cuatro"),
                 animaciones=[Transform(viajera, franjas[1])],
                 t=1.8, rate_func=smooth)
        self.leer(3.6)

        # --- 3. y otra vez ---------------------------------------------
        franjas[2].set_fill(opacity=0.20)
        L.morfeo(None,
                 dato=(f"{cal.area_hiperbola(*self.TRAMOS[2]):.4f}",
                       "y la de cuatro a ocho"),
                 animaciones=[FadeIn(franjas[2])], t=1.2)
        self.leer(3.6)

        # --- 4. tres franjas, la misma area ---------------------------
        # Y aqui se dice lo que significa: para llegar a ocho se ha
        # multiplicado por dos tres veces, y el area ha sumado tres veces
        # lo mismo. Multiplicar por fuera, sumar por dentro.
        total = cal.area_hiperbola(self.TRAMOS[0][0], self.TRAMOS[2][1])
        L.dato(f"{total:.4f}", "de uno a ocho: tres veces")
        self.leer(4.2)
