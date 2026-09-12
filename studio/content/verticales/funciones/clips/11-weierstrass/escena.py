# 11 · WEIERSTRASS — continua y sin pendiente.
#
# En 1872 Weierstrass publico una funcion continua en todas partes y sin
# derivada en ninguna. No salio de un problema fisico: salio de demostrar
# que la intuicion miente. Hasta entonces se daba por hecho que una curva
# continua tiene tangente salvo en unos pocos sitios raros; esta no la
# tiene en NINGUNO.
#
# El verbo visual es el zoom. Se amplia una y otra vez sobre el mismo
# punto: una curva normal acabaria pareciendo una recta —eso ES tener
# derivada—, y esta sigue igual de quebrada a cualquier aumento.
#
# LA TRAMPA QUE TIENE ESTA PIEZA, y es de las que no avisan: por encima de
# cierto zoom hacen falta tantos terminos que el argumento del coseno
# (b^k·pi·x) pasa de 1e13 y un float64 se queda sin cifras para la FASE.
# El termino sale con desfase aleatorio y, como su amplitud es pequeña, el
# resultado no es ruido: es que la curva PIERDE el detalle fino y sale
# SUAVE. La pieza habria demostrado lo contrario de lo que dice. Por eso
# `ventana_zoom` aborta por encima de trece terminos, y por eso aqui solo
# se amplia tres veces.
class Clip(Pieza):
    NOMBRE = "WEIERSTRASS"
    TESIS = "continua y sin pendiente"

    # PARAMETROS elegidos: el punto que se amplia y cuantas veces.
    X0 = 0.30
    ZOOMS = 3
    ANCHO_CAJA = ANCHO - 0.55
    ALTO_CAJA = 4.10

    def _ventana(self, k):
        """El trozo de W a un aumento de b^k, con su rotulo."""
        ancho = 1.0 / (esp.W_B ** k)
        x, y = esp.ventana_zoom(self.X0, ancho, 3000)
        margen = 0.06 * (float(y.max()) - float(y.min()))
        P = esp.marco((float(x.min()), float(x.max())),
                      (float(y.min()) - margen, float(y.max()) + margen),
                      ancho=self.ANCHO_CAJA, alto=self.ALTO_CAJA)
        curva = esp.curva(x, y, P, color=AMBAR, grosor=2.2)
        texto = "SIN AMPLIAR" if k == 0 else f"AMPLIADO X{esp.W_B ** k}"
        eti = rot(texto, color=APAGADO)
        eti.next_to(P(self.X0, float(y.min()) - margen), DOWN, buff=0.24)
        return lz.agrupar(esp.recuadro(P), curva, eti)

    def pieza(self):
        L = self.L

        # --- 1. la curva entera ---------------------------------------
        L.escena(self._ventana(0), t=0.9)
        self.leer(3.2)
        L.dato(medido(esp.cociente_incremental(self.X0, 1.0 / esp.W_B), 0),
               "la pendiente que pide")
        self.leer(3.4)

        # --- 2, 3, 4. se amplia, y no se alisa ------------------------
        # La cifra va ENTERA: la cola de terminos que se deja fuera mueve
        # el valor un 0.25 %, asi que los decimales serian de la
        # truncatura y no de la funcion.
        for k in range(1, self.ZOOMS + 1):
            pendiente = esp.cociente_incremental(
                self.X0, 1.0 / (esp.W_B ** (k + 1)))
            L.relevo(escena=self._ventana(k),
                     dato=(medido(pendiente, 0), "la pendiente que pide"),
                     t=0.9)
            self.leer(3.4)

        # --- 5. y la sucesion no se para ------------------------------
        # En una curva con derivada, esta lista se queda quieta en un
        # valor. Esa es la definicion de tener derivada, y esta no la
        # cumple en ningun punto.
        ultima = esp.pendientes_que_se_disparan(self.X0, 5)[-1]
        L.dato(medido(ultima, 0), "y sigue sin pararse")
        self.leer(3.6)
