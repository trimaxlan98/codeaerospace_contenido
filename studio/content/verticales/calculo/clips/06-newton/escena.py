# 06 · NEWTON — los decimales se duplican.
#
# EL VERBO VISUAL: el zigzag. Desde un punto cualquiera de la curva se baja
# por la TANGENTE hasta el eje, se sube a la curva y se vuelve a bajar. En
# tres pasos ya no se ve el movimiento, y esa es exactamente la cifra: los
# decimales correctos pasan de 1 a 3, a 6 y a 13.
#
# LA ECUACION ES LA DE NEWTON: x^3 - 2x - 5 = 0 es el ejemplo con el que el
# propio Newton presento el metodo en 1669. La raiz no es redonda
# (2.0945514815...), que es justo lo que hace falta para que se vea ganar
# decimales.
#
# NO ES EL FRACTAL DE NEWTON. Las cuencas en el plano complejo son del
# curso 26 y alli estan bien contadas. Aqui el metodo es una tangente y una
# cuenta de decimales.
#
# EL PUNTO DE PARTIDA NO ES 2.0 AUNQUE LA LIBRERIA LO TENGA POR DEFECTO:
# desde 2.0 el primer salto vale 0.1 y el segundo 0.005, o sea que el
# zigzag no se ve. Desde 2.35 los dos primeros triangulos se ven enteros y
# la sucesion de decimales sigue duplicandose igual.
class Clip(Pieza):
    NOMBRE = "NEWTON"
    TESIS = "los decimales se duplican"

    PARTIDA = 2.35
    RX = (2.03, 2.42)
    RY = (-0.75, 3.45)
    ANCHO_CAJA = ANCHO - 0.60
    ALTO_CAJA = 4.55

    def pieza(self):
        L = self.L
        P = cal.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)
        raiz = cal.raiz_de_newton()
        pasos = cal.newton_pasos(self.PARTIDA, 4)

        xs = np.linspace(self.RX[0], self.RX[1], 700)
        curva = cal.curva(xs, cal.f_newton(xs), P, color=AMBAR,
                          grosor=cal.TRAZO)
        eje = cal.eje_x(P)
        cero = cal.marca_en(P, raiz, 0.0, color=TINTA, radio=0.058)

        # --- el zigzag, tramo a tramo ---------------------------------
        # Se dibuja por pasos y no de un tiron: cada bajada es una
        # tangente distinta, y lo que la pieza enseña es que cada una
        # deja el error al cuadrado de la anterior.
        bajadas, subidas, puntos = [], [], []
        for i in range(3):
            x, xn = pasos[i], pasos[i + 1]
            y = float(cal.f_newton(x))
            bajadas.append(cal.segmento(P, x, y, xn, 0.0, color=CIAN,
                                        grosor=cal.TRAZO_FINO))
            subidas.append(cal.segmento(P, xn, 0.0, xn,
                                        float(cal.f_newton(xn)),
                                        color=APAGADO, grosor=1.2,
                                        a_trozos=True))
            puntos.append(cal.marca_en(P, x, y, color=CIAN, radio=0.050))
        puntos.append(cal.marca_en(P, pasos[3], float(cal.f_newton(pasos[3])),
                                   color=CIAN, radio=0.050))

        for m in bajadas + subidas:
            m.set_stroke(opacity=0.0)
        for m in puntos:
            m.set_opacity(0.0)
        cero.set_opacity(0.0)

        dibujo = lz.agrupar(caja(P), eje, curva, cero, *bajadas, *subidas,
                            *puntos)

        # --- 1. una curva que cruza el cero en un sitio feo ------------
        L.escena(dibujo, t=1.2)
        cero.set_opacity(1.0)
        self.play(FadeIn(cero), run_time=0.5)
        self.leer(2.8)

        # --- 2. se empieza por un punto cualquiera --------------------
        puntos[0].set_opacity(1.0)
        L.morfeo(None,
                 dato=(f"{self.PARTIDA:.2f}", "una suposicion, sin mas"),
                 animaciones=[FadeIn(puntos[0])], t=0.8)
        self.leer(2.6)

        # --- 3, 4, 5. y se baja por la tangente -----------------------
        for i in range(3):
            bajadas[i].set_stroke(opacity=1.0)
            subidas[i].set_stroke(opacity=1.0)
            puntos[i + 1].set_opacity(1.0)
            d = cal.digitos_correctos(pasos[i + 1], raiz)
            L.morfeo(None,
                     dato=(f"{pasos[i + 1]:.6f}",
                           f"{d} decimales correctos" if d != 1
                           else "1 decimal correcto"),
                     animaciones=[Create(bajadas[i], introducer=False),
                                  Create(subidas[i], introducer=False),
                                  FadeIn(puntos[i + 1])],
                     t=1.2)
            self.leer(2.6)

        # --- 6. el cuarto paso ya no se ve, y es el mejor -------------
        # No hay animacion: el dibujo NO cambia, y que no cambie es la
        # afirmacion. Lo que cambia es cuantos decimales son ciertos.
        # Y la cifra cambia de papel: hasta ahora era la aproximacion y la
        # etiqueta contaba los decimales; aqui el numero ES la cuenta. La
        # aproximacion con trece decimales no cabe en el carril (la cifra
        # aguanta once caracteres a cuerpo minimo) y ademas no es lo que
        # hay que recordar.
        d = cal.digitos_correctos(pasos[4], raiz)
        L.dato(f"{d}", "decimales, en cuatro pasos")
        self.leer(3.6)
