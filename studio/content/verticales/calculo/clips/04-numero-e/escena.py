# 04 · NUMERO E — su pendiente es su altura.
#
# EL VERBO VISUAL: cuatro tangentes en cuatro sitios distintos de la misma
# curva, y las cuatro cortan el eje EXACTAMENTE una unidad antes del punto
# del que salen. Esa base que siempre mide 1 es la propiedad que define al
# numero, dibujada: si la altura es y y la base es 1, la pendiente es y.
#
# POR QUE LA BASE Y NO LA FORMULA: "la derivada de e^x es e^x" no se puede
# enseñar, solo se puede escribir. La subtangente si: es un segmento, se
# mide con la vista y sale igual cuatro veces seguidas.
#
# LOS CUATRO PUNTOS ESTAN ELEGIDOS para que su corte con el eje caiga
# dentro del cuadro (x0 - 1 >= -1.35): con x0 = -0.5 el corte se iria a
# -1.5, fuera, y la base —que es LO QUE HAY QUE VER— se saldria del
# dibujo.
class Clip(Pieza):
    NOMBRE = "NUMERO E"
    TESIS = "su pendiente es su altura"

    PUNTOS = (0.7, 0.0, 1.4, 2.0)     # el primero es el que abre
    RX = (-1.35, 2.30)
    RY = (-1.55, 10.40)
    ANCHO_CAJA = ANCHO - 0.55
    ALTO_CAJA = 4.85
    PROFUNDIDAD = (-0.30, -0.60, -0.90, -1.20)

    def tangente_de(self, P, x0, prof):
        """(recta, plomada, base, punto) de la tangente en x0.

        La base NO va sobre el eje. La primera version las dibujaba las
        cuatro encima del eje y, como van de x0-1 a x0 con x0 distinto en
        cada una, se soldaban en UNA barra ambar continua de tres
        unidades: la pieza afirmaba que las cuatro miden lo mismo y lo que
        se veia era una raya larga. Cada una a su profundidad, con sus dos
        topes, se leen como cuatro medidas iguales."""
        y0 = float(np.exp(x0))
        corte = cal.corte_de_tangente(x0)
        xs = np.array([corte, min(self.RX[1], x0 + 0.45)])
        recta = cal.curva(xs, cal.tangente_exp(x0, xs), P, color=CIAN,
                          grosor=cal.TRAZO_FINO)
        plomo = cal.plomada(P, x0, y0, color=APAGADO, trozos=8)
        barra = cal.segmento(P, corte, prof, x0, prof, color=AMBAR,
                             grosor=4.2)
        topes = VGroup(*[cal.segmento(P, x, prof - 0.11, x, prof + 0.11,
                                      color=AMBAR, grosor=2.0)
                         for x in (corte, x0)])
        guia = cal.segmento(P, corte, 0.0, corte, prof, color=LINEA,
                            grosor=1.0)
        base = VGroup(barra, topes, guia)
        punto = cal.marca_en(P, x0, y0, radio=0.055)
        return recta, plomo, base, punto

    def pieza(self):
        L = self.L
        P = cal.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)

        eje = cal.eje_x(P)
        marco_fijo = caja(P)
        xs = np.linspace(self.RX[0], self.RX[1], 900)
        curva = cal.curva(xs, cal.exp_(xs), P, color=AMBAR, grosor=cal.TRAZO)

        grupos = [self.tangente_de(P, x0, prof)
                  for x0, prof in zip(self.PUNTOS, self.PROFUNDIDAD)]
        for recta, plomo, base, punto in grupos:
            recta.set_stroke(opacity=0.0)
            plomo.set_stroke(opacity=0.0)
            base.set_stroke(opacity=0.0)
            punto.set_opacity(0.0)

        # El remate: el punto donde la altura vale e.
        e = cal.numero_e()
        marca_e = cal.marca_en(P, 1.0, e)
        plomo_e = cal.plomada(P, 1.0, e, color=TINTA, trozos=8)
        marca_e.set_opacity(0.0)
        plomo_e.set_stroke(opacity=0.0)

        dibujo = lz.agrupar(marco_fijo, eje, curva, marca_e, plomo_e,
                            *[m for g in grupos for m in g])

        # --- 1. la curva ------------------------------------------------
        L.escena(dibujo, t=1.2)
        self.leer(3.2)

        # --- 2. un punto y su tangente ---------------------------------
        r0, p0, b0, pt0 = grupos[0]
        r0.set_stroke(opacity=1.0)
        self.play(pt0.animate.set_opacity(1.0),
                  p0.animate.set_stroke(opacity=1.0), run_time=0.6)
        self.play(Create(r0, introducer=False), run_time=1.1)
        self.leer(2.8)

        # --- 3. y la base que deja en el eje ---------------------------
        b0.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{cal.subtangente(self.PUNTOS[0]):.4f}",
                       "lo que mide esa base"),
                 animaciones=[Create(b0, introducer=False)], t=0.9)
        self.leer(3.2)

        # --- 4. las otras tres, y la base vuelve a medir uno -----------
        # Misma cifra con otra etiqueta, y es el unico sitio del curso
        # donde eso se permite: el numero no ha cambiado porque de eso va
        # la pieza, y la etiqueta lo dice.
        animaciones = []
        for recta, plomo, base, punto in grupos[1:]:
            for m in (recta, plomo, base):
                m.set_stroke(opacity=1.0)
            punto.set_opacity(1.0)
            animaciones += [FadeIn(punto), FadeIn(plomo),
                            Create(recta, introducer=False),
                            Create(base, introducer=False)]
        L.morfeo(None,
                 dato=(f"{cal.subtangente(self.PUNTOS[1]):.4f}",
                       "en las cuatro, lo mismo"),
                 animaciones=animaciones, t=1.6)
        self.leer(3.6)

        # --- 5. y por eso hay un sitio donde la pendiente vale uno -----
        marca_e.set_opacity(1.0)
        plomo_e.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{e:.4f}", "la altura donde vale uno"),
                 animaciones=[FadeIn(marca_e), FadeIn(plomo_e)], t=0.9)
        self.leer(4.2)
