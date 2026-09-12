# 17 · ZETA — los primos tienen musica.
#
# Empieza como una suma inocente: uno mas un cuarto mas un noveno... Euler
# demostro que da pi cuadrado partido por seis, y de paso que esa suma se
# puede escribir como un producto sobre TODOS los numeros primos. Desde
# entonces, saber donde se anula zeta es saber como se reparten los primos.
#
# El verbo visual es el paso por el origen. La curva que dibuja zeta sobre
# la recta critica —el conjunto de los numeros con parte real un medio— se
# enrosca sobre el plano y, en un instante muy concreto, pasa EXACTAMENTE
# por el cero. Ese instante es 14.1347.
#
# La cifra no se busca como el minimo de |zeta| sobre una malla: eso daria
# el punto mas bajo de la malla, que no es un cero. Se busca por cambio de
# signo de la funcion Z de Hardy, que es real sobre esta recta y tiene
# exactamente los mismos ceros.
class Clip(Pieza):
    NOMBRE = "ZETA"
    TESIS = "los primos tienen musica"

    T_MAX = 32.0
    ANCHO_CAJA = ANCHO - 0.55

    def pieza(self):
        L = self.L

        # --- 1. la suma de Basilea -----------------------------------
        n = np.arange(1, 61, dtype=float)
        sumas = np.cumsum(1.0 / n ** 2)
        z2 = float(esp.zeta(2.0).real)
        P = esp.marco((0.0, 61.0), (0.90, 1.75), ancho=self.ANCHO_CAJA,
                      alto=4.10)
        parcial = esp.curva(n, sumas, P, color=AMBAR, grosor=esp.TRAZO)
        techo = esp.curva(np.array([0.0, 61.0]), np.array([z2, z2]), P,
                          color=CIAN, grosor=esp.TRAZO_PELO)
        eti = rot("UNO MAS UN CUARTO MAS", color=APAGADO)
        eti.move_to(P(30.0, 1.03))
        dibujo = lz.agrupar(esp.recuadro(P), techo, parcial, eti)

        L.escena(dibujo, t=0.9)
        self.leer(3.0)
        L.dato(medido(z2, 4), "a lo que suma")
        self.leer(3.2)

        # --- 2. la curva sobre la recta critica ----------------------
        t, z = esp.zeta_en_recta(0.0, self.T_MAX, 2000)
        re, im = np.real(z), np.imag(z)
        m = 0.14 * max(float(re.max() - re.min()), float(im.max() - im.min()))
        Q = esp.marco((float(re.min()) - m, float(re.max()) + m),
                      (float(im.min()) - m, float(im.max()) + m),
                      ancho=self.ANCHO_CAJA, alto=4.30)
        curva = esp.curva(re, im, Q, color=AMBAR, grosor=2.0)
        curva.set_stroke(opacity=0.0)
        origen = Dot(Q(0.0, 0.0), radius=0.075, color=TINTA)
        origen.set_opacity(0.0)
        panel = lz.agrupar(esp.recuadro(Q), esp.eje_x(Q), esp.eje_y(Q),
                           curva, origen)

        L.relevo(escena=panel, dato=None, t=0.8)
        curva.set_stroke(opacity=1.0)
        self.play(Create(curva, introducer=False), run_time=3.2,
                  rate_func=linear)
        self.leer(2.4)

        # --- 3. y el instante en que pasa por el cero ----------------
        t0 = esp.primer_cero_zeta()
        L.morfeo(None, dato=(medido(t0, 4), "donde zeta se anula"),
                 animaciones=[origen.animate.set_opacity(1.0)], t=0.8)
        self.leer(3.4)

        # --- 4. y no es el unico -------------------------------------
        ceros = esp.ceros_zeta(0.5, self.T_MAX)
        L.dato(medido(len(ceros), 0), "ceros hasta el treinta")
        self.leer(4.8)
