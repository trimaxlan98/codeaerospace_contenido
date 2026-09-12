# 03 · RECTA ESCONDIDA — de cerca todo es recta.
#
# EL VERBO VISUAL: cuatro ventanas sobre el MISMO punto, cada una la mitad
# de ancha que la anterior. La curva se va enderezando hasta que no se
# distingue de su tangente. Es el unico zoom del curso: el 34 gasto ese
# gesto cuatro veces sobre Weierstrass para enseñar la excepcion; aqui se
# usa una vez, para enseñar la regla.
#
# EL ZOOM TIENE QUE SER ISOTROPO, Y ES LA TRAMPA DE LA PIEZA. Si en cada
# ventana se reajusta el rango vertical al recorrido de la curva, la curva
# sale IGUAL DE CURVADA en las cuatro y la pieza demuestra lo contrario de
# lo que dice. El alto de la ventana se divide entre dos a la vez que el
# ancho: `RY` se calcula de `RX` con la proporcion de la caja.
#
# POR ESO HAY CUATRO MARCOS Y NO UNO, que es la excepcion a la regla del
# curso: un zoom ES cambiar de marco. Lo que no cambia es la CAJA —el
# recuadro mide lo mismo en los cuatro—, asi que los estados se encajan
# igual y el morfeo no da saltos.
#
# LA CIFRA: el huequito blanco del borde derecho es lo que se separan
# curva y tangente, y es lo que se mide. Cae 0.2999 → 0.0721 → 0.0175 →
# 0.0043: se divide entre CUATRO cada vez que la ventana se parte por dos,
# porque lo primero que le sobra a la recta es un termino en h^2.
class Clip(Pieza):
    NOMBRE = "RECTA ESCONDIDA"
    TESIS = "de cerca todo es recta"

    X0 = 1.0
    ANCHOS = (0.8, 0.4, 0.2, 0.1)
    ANCHO_CAJA = ANCHO - 0.70
    ALTO_CAJA = 4.30

    def ventana(self, a):
        """El marco de una ventana de semiancho a, a escala isotropa."""
        y0 = float(cal.f_zoom(self.X0))
        k = a * self.ALTO_CAJA / self.ANCHO_CAJA
        return cal.marco((self.X0 - a, self.X0 + a), (y0 - k, y0 + k),
                         ancho=self.ANCHO_CAJA, alto=self.ALTO_CAJA)

    def estado(self, a):
        """(cuadro, curva, tangente, punto, hueco) de una ventana."""
        P = self.ventana(a)
        xs = np.linspace(self.X0 - a, self.X0 + a, 600)
        y0 = float(cal.f_zoom(self.X0))
        m = float(cal.df_zoom(self.X0))
        curva = cal.curva(xs, cal.f_zoom(xs), P, color=AMBAR,
                          grosor=cal.TRAZO)
        recta = cal.curva(xs, y0 + m * (xs - self.X0), P, color=CIAN,
                          grosor=cal.TRAZO_FINO)
        punto = cal.marca_en(P, self.X0, y0, radio=0.055)
        borde = self.X0 + a
        hueco = cal.segmento(P, borde, y0 + m * a, borde,
                             float(cal.f_zoom(borde)), color=TINTA,
                             grosor=3.2)
        return cal.recuadro(P), curva, recta, punto, hueco

    def pieza(self):
        L = self.L
        estados = [self.estado(a) for a in self.ANCHOS]
        cuadro, curva, recta, punto, hueco = estados[0]
        futuros = []
        for e in estados[1:]:
            futuros.extend(e)

        for c, cu, re, pt, hu in estados:
            re.set_stroke(opacity=0.0)
            hu.set_stroke(opacity=0.0)
        for e in estados[1:]:
            e[0].set_stroke(opacity=0.0)
            e[1].set_stroke(opacity=0.0)
            e[3].set_opacity(0.0)

        dibujo = lz.agrupar(cuadro, curva, punto, recta, hueco, *futuros)

        # --- 1. una curva, y un punto de ella --------------------------
        L.escena(dibujo, t=1.2)
        soltar(dibujo, *futuros)
        for e in estados[1:]:
            e[0].set_stroke(opacity=1.0)
            e[1].set_stroke(opacity=1.0)
            e[2].set_stroke(opacity=1.0)
            e[3].set_opacity(1.0)
            e[4].set_stroke(opacity=1.0)
        self.leer(2.4)

        # --- 2. y la recta que pasa por el con su pendiente ------------
        recta.set_stroke(opacity=1.0)
        self.play(Create(recta, introducer=False), run_time=1.2)
        hueco.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{cal.despegue(self.ANCHOS[0]):.4f}",
                       "lo que se separan"),
                 animaciones=[FadeIn(hueco)], t=0.8)
        self.leer(3.0)

        # --- 3, 4, 5. la ventana se parte por dos ----------------------
        for i in range(1, len(self.ANCHOS)):
            nuevo = estados[i]
            L.morfeo(None,
                     dato=(f"{cal.despegue(self.ANCHOS[i]):.4f}",
                           "lo que se separan"),
                     animaciones=[Transform(curva, nuevo[1]),
                                  Transform(recta, nuevo[2]),
                                  Transform(hueco, nuevo[4])],
                     t=1.5)
            self.leer(2.8 if i < len(self.ANCHOS) - 1 else 3.2)

        # --- 6. y el hueco no se achica de cualquier manera ------------
        # La razon entre dos huecos seguidos es la cifra de la pieza: 4.07
        # es la ULTIMA medida, la de las dos ventanas que se acaban de
        # ver. Las anteriores dan 4.16 y 4.12 — la razon TIENDE a cuatro,
        # y rotular un 4 pelado seria rotular el limite, no la medida.
        razon = cal.razon_de_despegue(self.X0, self.ANCHOS)[-1]
        L.dato(f"{razon:.2f}", "veces menos a cada zoom")
        self.leer(3.4)
