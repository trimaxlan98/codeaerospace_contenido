# 13 · CAUCHY — la campana sin media.
#
# La campana de Cauchy se parece muchisimo a la de Gauss: una joroba
# simetrica con su maximo en el centro. Pero no tiene media. No es que sea
# dificil de calcular: es que no existe, y se nota promediando — por muchas
# muestras que se tomen, el promedio nunca se asienta, porque siempre queda
# por llegar una muestra lo bastante grande para moverlo entero.
#
# El verbo visual son las dos medias corriendo sobre el mismo cuadro. La de
# Gauss se pega al cero a las pocas cientos de muestras. La de Cauchy da
# saltos hasta la ultima.
#
# UNA DEMO QUE SOLO FUNCIONA CON TU SEMILLA NO ES UNA DEMO, asi que el
# ultimo plano dibuja VEINTE semillas distintas. Ninguna se asienta. La
# sonda lo comprueba ademas con la cifra: en las veinte, el salto final de
# Cauchy es al menos tres veces el de la gaussiana.
class Clip(Pieza):
    NOMBRE = "CAUCHY"
    TESIS = "la campana sin media"

    # PARAMETROS elegidos: cuantas muestras y cuantas semillas.
    N = 20000
    SEMILLAS = 20
    RY = (-3.2, 3.2)
    ANCHO_CAJA = ANCHO - 0.55
    ALTO_CAJA = 4.30

    def _cuadro(self):
        return esp.marco((0.0, float(self.N)), self.RY,
                         ancho=self.ANCHO_CAJA, alto=self.ALTO_CAJA)

    def pieza(self):
        L = self.L
        P = self._cuadro()
        n = np.arange(1, self.N + 1, dtype=float)
        mg = esp.media_corrida(esp.muestras_gauss(self.N))
        mc = esp.media_corrida(esp.muestras_cauchy(self.N))

        # --- 1. la media de la gaussiana se asienta -------------------
        gauss = esp.curva(n, mg, P, color=CIAN, grosor=esp.TRAZO_FINO)
        gauss.set_stroke(opacity=0.0)
        eti_g = rot("GAUSS", color=CIAN)
        # Los dos rotulos van DEBAJO del eje: por encima, el unico sitio
        # libre para la etiqueta de Gauss estaba justo donde la media de
        # Cauchy cruza una y otra vez, y el trazo ambar pasaba por encima
        # de la palabra.
        eti_g.move_to(P(self.N * 0.30, -0.62))
        eti_g.set_opacity(0.0)
        # La de Cauchy se sale del cuadro: se CORTA en tramos, que es lo
        # que de verdad hace. Aplastarla contra el borde se leeria como
        # que el promedio se estanca, o sea lo contrario.
        tramos = esp.recortar(n, mc, self.RY)
        cauchy = lz.agrupar(*[esp.curva(a, b, P, color=AMBAR,
                                        grosor=esp.TRAZO)
                              for a, b in tramos])
        cauchy.set_stroke(opacity=0.0)
        eti_c = rot("CAUCHY", color=AMBAR)
        eti_c.move_to(P(self.N * 0.76, -1.95))
        eti_c.set_opacity(0.0)

        dibujo = lz.agrupar(esp.recuadro(P), esp.eje_x(P), gauss, cauchy,
                            eti_g, eti_c)
        L.escena(dibujo, t=0.9)
        gauss.set_stroke(opacity=1.0)
        self.play(Create(gauss, introducer=False),
                  eti_g.animate.set_opacity(1.0), run_time=2.2,
                  rate_func=linear)
        self.leer(2.4)
        L.dato(medido(esp.salto_maximo(mg), 5), "lo que salta al final")
        self.leer(3.2)

        # --- 2. la de Cauchy no ---------------------------------------
        cauchy.set_stroke(opacity=1.0)
        self.play(Create(cauchy, introducer=False),
                  eti_c.animate.set_opacity(1.0), run_time=2.6,
                  rate_func=linear)
        self.leer(2.4)
        L.dato(medido(esp.salto_maximo(mc), 3), "lo que salta al final")
        self.leer(3.4)

        # --- 3. y no es cosa de esta semilla --------------------------
        filas = esp.barrido_semillas(self.SEMILLAS, self.N)
        Q = self._cuadro()
        haz = VGroup()
        for i in range(self.SEMILLAS):
            m = esp.media_corrida(esp.muestras_cauchy(self.N,
                                                      esp.SEMILLA + i))
            for a, b in esp.recortar(n, m, self.RY):
                haz.add(esp.curva(a, b, Q, color=AMBAR, grosor=1.2))
        eti_h = rot(f"{self.SEMILLAS} SEMILLAS", color=AMBAR)
        eti_h.move_to(Q(self.N * 0.74, 2.5))
        peor = min(c / g for _, g, c in filas)

        L.relevo(escena=lz.agrupar(esp.recuadro(Q), esp.eje_x(Q), haz,
                                   eti_h),
                 dato=(medido(peor, 0), "veces mas, la peor"), t=0.9)
        self.leer(4.8)
