# 16 · LISSAJOUS — dos senos en angulo recto.
#
# Un tono en el eje horizontal y otro en el vertical, y lo que sale es una
# figura. Su forma depende SOLO de la razon entre las dos frecuencias, y la
# razon se puede LEER sin medir ninguna frecuencia: se cuentan los toques
# con un lado y con el techo. Asi se calibraban los osciloscopios antes de
# que existieran los contadores digitales.
#
# El remate es lo que pasa cuando la razon no es una fraccion: la figura no
# se cierra nunca y acaba llenando el cuadrado. Que una curva se cierre o
# no es la diferencia entre un numero racional y uno que no lo es, dibujada
# en una pantalla.
#
# Los toques van MARCADOS con un punto cada uno. Sin ellos, la cifra "3" es
# algo que el espectador tiene que creerse; con ellos, algo que cuenta.
class Clip(Pieza):
    NOMBRE = "LISSAJOUS"
    TESIS = "dos senos en angulo recto"

    LADO = 4.20
    VUELTAS_IRRACIONAL = 26

    def _figura(self, a, b, marcas=None, irracional=False, vueltas_=None):
        P = esp.marco((-1.08, 1.08), (-1.08, 1.08), ancho=self.LADO,
                      alto=self.LADO)
        if irracional:
            x, y = esp.lissajous(a, b, N=40000, vueltas_=vueltas_)
        else:
            x, y = esp.lissajous(a, b, N=6000,
                                 vueltas_=esp.cierra_en(a, b) / (2 * np.pi))
        curva = esp.curva(x, y, P, color=AMBAR,
                          grosor=2.4 if not irracional else 1.0)
        caja = Square(side_length=self.LADO * (2.0 / 2.16),
                      stroke_color=LINEA, stroke_width=esp.TRAZO_PELO,
                      fill_opacity=0.0)
        piezas = [caja, curva]
        for pts in (marcas or ()):
            for px, py in pts:
                piezas.append(Dot(P(px, py), radius=0.070, color=TINTA))
        return lz.agrupar(*piezas), curva

    def pieza(self):
        L = self.L

        # --- 1. la figura de tres contra dos -------------------------
        dibujo, curva = self._figura(3, 2)
        curva.set_stroke(opacity=0.0)
        L.escena(dibujo, t=0.9)
        curva.set_stroke(opacity=1.0)
        self.play(Create(curva, introducer=False), run_time=2.6,
                  rate_func=linear)
        self.leer(2.6)

        # --- 2. los toques con el lado -------------------------------
        lado, techo = esp.puntos_de_toque(3, 2)
        n_lado, n_techo = esp.toques(3, 2)
        dib2, _ = self._figura(3, 2, marcas=(lado,))
        L.relevo(escena=dib2,
                 dato=(medido(n_lado, 0), "toques con el lado"), t=0.8)
        self.leer(3.0)

        # --- 3. y con el techo ---------------------------------------
        dib3, _ = self._figura(3, 2, marcas=(lado, techo))
        L.relevo(escena=dib3,
                 dato=(medido(n_techo, 0), "toques con el techo"), t=0.8)
        self.leer(3.2)

        # --- 4. otra razon, otra figura ------------------------------
        lado5, techo5 = esp.puntos_de_toque(5, 4)
        dib4, _ = self._figura(5, 4, marcas=(lado5, techo5))
        L.relevo(escena=dib4,
                 dato=(medido(esp.toques(5, 4)[0], 0),
                       "toques con el lado"), t=0.9)
        self.leer(3.2)

        # --- 5. y una razon que no es una fraccion -------------------
        # Raiz de dos. La curva no se cierra: cada vuelta pasa por un
        # sitio nuevo, y con suficientes vueltas llena el cuadrado.
        dib5, curva5 = self._figura(3.0, 2.0 * np.sqrt(2.0),
                                    irracional=True,
                                    vueltas_=self.VUELTAS_IRRACIONAL)
        L.relevo(escena=dib5,
                 dato=(medido(self.VUELTAS_IRRACIONAL, 0),
                       "vueltas sin cerrarse", False), t=1.0)
        self.leer(3.8)
