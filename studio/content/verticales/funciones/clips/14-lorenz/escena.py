# 14 · LORENZ — nunca pasa dos veces.
#
# Lorenz escribio tres ecuaciones para una rodaja de atmosfera calentada
# por abajo. La trayectoria que sale no se repite nunca, no se corta nunca
# a si misma, y no se va a ninguna parte: se queda para siempre dando
# vueltas sobre una figura que cabe en una caja.
#
# QUE NO CUENTA ESTA PIEZA, y es una decision del curso: no cuenta caos.
# El curso 12 conto el efecto mariposa y el 26 midio la dimension de esta
# misma traza. Aqui la mariposa es un OBJETO —una curva de un solo trazo
# que nunca se cruza— y la cifra es de las que se pueden contar: cuantas
# veces cambia de ala, y cuanto tarda en notarse una diferencia de una
# milmillonesima.
#
# Las dos trayectorias del segundo plano se comparan en el TIEMPO, no en
# el espacio: dibujadas las dos sobre el atractor, se superponen y luego
# lo llenan las dos, y no se distingue nada. En x(t) se ve exactamente el
# instante en que dejan de ser la misma.
class Clip(Pieza):
    NOMBRE = "LORENZ"
    TESIS = "nunca pasa dos veces"

    # PARAMETROS elegidos: el paso de integracion, cuanto se integra y la
    # diferencia inicial entre las dos trayectorias.
    DT = 0.004
    PASOS = 12000
    EPS = 1e-9
    ANCHO_CAJA = ANCHO - 0.55

    def pieza(self):
        L = self.L
        a, b = esp.par_lorenz(self.EPS, n=self.PASOS, dt=self.DT)

        # --- 1. la mariposa, de un solo trazo -------------------------
        P = esp.marco((-20.0, 20.0), (0.0, 48.0), ancho=self.ANCHO_CAJA,
                      alto=4.60)
        alas = esp.curva(a[:, 0], a[:, 2], P, color=AMBAR, grosor=1.3)
        alas.set_stroke(opacity=0.0)
        dibujo = lz.agrupar(esp.recuadro(P), alas)

        L.escena(dibujo, t=0.7)
        alas.set_stroke(opacity=1.0)
        self.play(Create(alas, introducer=False), run_time=4.0,
                  rate_func=linear)
        self.leer(2.6)

        # --- 2. cuantas veces cambia de ala --------------------------
        L.dato(medido(esp.vueltas(a), 0), "veces que cambia de ala")
        self.leer(3.2)
        L.dato(medido(self.PASOS * self.DT, 0), "segundos de vuelo", False)
        self.leer(2.8)

        # --- 3. dos que empiezan casi iguales ------------------------
        t = np.arange(self.PASOS) * self.DT
        Q = esp.marco((0.0, float(t[-1])), (-21.0, 21.0),
                      ancho=self.ANCHO_CAJA, alto=4.20)
        uno = esp.curva(t, a[:, 0], Q, color=AMBAR, grosor=1.4)
        # La segunda va A TROZOS por encima: durante los primeros veinte
        # segundos las dos son la MISMA curva, y dos trazos opacos
        # superpuestos se funden en un color que no es ninguno de los dos.
        # A trozos se ve el ambar en cada hueco, y "coinciden" se lee
        # porque se ven dos.
        dos = esp.curva(t, b[:, 0], Q, color=CIAN, grosor=1.4,
                        a_trozos=True)
        corte = esp.tiempo_hasta(a, b, 1.0, self.DT)
        raya = esp.vertical(Q, corte, color=TINTA)
        panel = lz.agrupar(esp.recuadro(Q), esp.eje_x(Q), uno, dos, raya)

        L.relevo(escena=panel,
                 dato=(medido(self.EPS, 9), "de diferencia al empezar",
                       False), t=0.9)
        self.leer(3.4)

        # --- 4. y cuanto tardan en dejar de ser la misma -------------
        L.dato(medido(corte, 2), "segundos hasta notarse")
        self.leer(4.6)
