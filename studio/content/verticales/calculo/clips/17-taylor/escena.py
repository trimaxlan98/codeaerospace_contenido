# 17 · TAYLOR — un polinomio que se pega.
#
# EL VERBO VISUAL: polinomios que abrazan al seno cada vez mas lejos. El de
# grado 1 lo suelta enseguida; el de grado 11 aguanta hasta x = 4. Lo que
# se mide no es "el error", que no se ve, sino HASTA DONDE aguanta, que es
# lo unico que se ve.
#
# CADA POLINOMIO SE DIBUJA SOLO DONDE CABE. Un polinomio de grado 11 fuera
# de su alcance se dispara a miles en dos decimas, y si se dibujara entero
# el cuadro tendria dos rayas verticales al lado de un rotulo que dice
# "acierta hasta 4". Es la misma trampa que en el curso 34 salio con
# Chebyshev: un polinomio dibujado fuera de donde interpola contradice a su
# propia cifra.
#
# LA TOLERANCIA (0.01) ES UN PARAMETRO ELEGIDO y va en gris dentro del
# dibujo: el alcance no significa nada sin decir con que error se mide.
class Clip(Pieza):
    NOMBRE = "TAYLOR"
    TESIS = "un polinomio que se pega"

    GRADOS = (1, 3, 7, 11)
    RX = (0.0, 5.20)
    RY = (-1.55, 1.55)
    ANCHO_CAJA = ANCHO - 0.60
    ALTO_CAJA = 3.60

    def polinomio(self, P, grado):
        """El polinomio, dibujado solo mientras cabe en el cuadro."""
        xs = np.linspace(self.RX[0], self.RX[1], 1600)
        ys = cal.taylor_seno(xs, grado)
        dentro = np.abs(ys) <= self.RY[1] - 0.03
        corte = np.argmax(~dentro) if (~dentro).any() else len(xs)
        return cal.curva(xs[:corte], ys[:corte], P, color=CIAN,
                         grosor=cal.TRAZO_FINO)

    def pieza(self):
        L = self.L
        P = cal.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)
        xs = np.linspace(self.RX[0], self.RX[1], 900)
        seno = cal.curva(xs, np.sin(xs), P, color=AMBAR, grosor=cal.TRAZO)
        eje = cal.eje_x(P)

        polis = [self.polinomio(P, g) for g in self.GRADOS]
        # Las marcas de alcance van SOLO por debajo del eje: de cuadro
        # entero cruzaban el rotulo del tope de error, que vive arriba a
        # la derecha porque es el unico hueco que deja el seno.
        topes = [cal.segmento(P, cal.alcance(g), self.RY[0] + 0.06,
                              cal.alcance(g), 0.0, color=TINTA, grosor=1.2,
                              a_trozos=True)
                 for g in self.GRADOS]
        for m in polis + topes:
            m.set_stroke(opacity=0.0)
        aviso = rot("tope de error: 0.01", color=APAGADO)
        aviso.move_to(P(3.62, 1.30))

        dibujo = lz.agrupar(caja(P), eje, seno, aviso, *polis, *topes)

        # --- 1. el seno -------------------------------------------------
        L.escena(dibujo, t=1.2)
        self.leer(3.2)

        # --- 2..5. grado a grado --------------------------------------
        for i, g in enumerate(self.GRADOS):
            polis[i].set_stroke(opacity=1.0)
            topes[i].set_stroke(opacity=1.0)
            animaciones = [Create(polis[i], introducer=False),
                           FadeIn(topes[i])]
            if i:
                animaciones += [FadeOut(polis[i - 1]), FadeOut(topes[i - 1])]
            L.morfeo(None,
                     dato=(f"{cal.alcance(g):.2f}",
                           f"hasta aqui, con grado {g}"),
                     animaciones=animaciones, t=1.4)
            self.leer(3.0 if i < len(self.GRADOS) - 1 else 4.2)
