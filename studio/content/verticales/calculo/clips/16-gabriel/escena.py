# 16 · GABRIEL — se llena, no se pinta.
#
# EL VERBO VISUAL: la trompeta de 1/x se va llenando de pintura y la
# pintura se PARA. Por mucho que se alargue la trompeta, el volumen no
# pasa de pi. Y sin embargo la pared no se acaba nunca: la superficie
# crece como el logaritmo, y al ir mil veces mas lejos se DUPLICA.
#
# Se llena con pi de pintura y con esa pintura no se puede pintar por
# dentro. La paradoja no es una trampa: es que el volumen suma radios al
# CUADRADO (que se hacen pequeños deprisa) y la superficie los suma a
# secas.
#
# LA SUPERFICIE SE INTEGRA EN ESCALA LOGARITMICA (u = ln x). Con malla
# lineal en x, llegar a 10^6 con trapecios pediria mil millones de puntos
# para que la cifra significara algo; con el cambio, el integrando es
# suave y acotado y 200 000 puntos bastan. La sonda lo comprueba con dos
# mallas.
class Clip(Pieza):
    NOMBRE = "GABRIEL"
    TESIS = "se llena, no se pinta"

    CORTES = (3.0, 12.0)
    RX = (0.80, 12.60)
    RY = (-1.32, 1.32)
    ANCHO_CAJA = ANCHO - 0.55
    ALTO_CAJA = 3.70

    def pieza(self):
        L = self.L
        P = cal.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)
        xs = np.linspace(1.0, self.RX[1], 1200)
        ys = cal.hiperbola(xs)

        perfil = VGroup(cal.curva(xs, ys, P, color=AMBAR, grosor=cal.TRAZO),
                        cal.curva(xs, -ys, P, color=AMBAR, grosor=cal.TRAZO))
        boca = cal.segmento(P, 1.0, -1.0, 1.0, 1.0, color=AMBAR,
                            grosor=cal.TRAZO)
        eje = cal.eje_x(P)

        pinturas = []
        for c in self.CORTES:
            x = np.linspace(1.0, c, 600)
            y = cal.hiperbola(x)
            pinturas.append(lz.agrupar(
                cal.region(x, y, P, color=CIAN, opacidad=0.30),
                cal.region(x, -y, P, color=CIAN, opacidad=0.30)))
        for m in pinturas:
            m.set_fill(opacity=0.0)

        dibujo = lz.agrupar(caja(P), eje, boca, perfil, *pinturas)

        # --- 1. una trompeta que no se acaba --------------------------
        L.escena(dibujo, t=1.2)
        self.leer(2.8)

        # --- 2, 3. se llena de pintura --------------------------------
        for i, c in enumerate(self.CORTES):
            pinturas[i].set_fill(opacity=0.30)
            animaciones = [FadeIn(pinturas[i])]
            if i:
                animaciones.append(FadeOut(pinturas[i - 1]))
            L.morfeo(None,
                     dato=(f"{cal.volumen_trompeta(c):.4f}",
                           "de pintura, hasta aqui"),
                     animaciones=animaciones, t=1.3)
            self.leer(3.0)

        # --- 4. y por mucho que se alargue, no pasa de ahi ------------
        L.dato(f"{cal.volumen_trompeta(1e9):.4f}", "y hasta el final, esto")
        self.leer(3.4)

        # --- 5. pero la pared no se acaba -----------------------------
        s6 = cal.superficie_trompeta(1e6)
        L.dato(f"{s6:.2f}", "de pared, al llegar al millon")
        self.leer(3.2)

        # --- 6. y mil veces mas lejos, el doble -----------------------
        # Es la cifra de la pieza: no que sea grande, sino que NO PARA.
        # El volumen ya no se mueve en el decimal doce y la superficie se
        # duplica cada vez que el limite se eleva al cuadrado.
        L.dato(f"{cal.superficie_trompeta(1e12):.2f}", "el doble, y sin parar")
        self.leer(3.8)
