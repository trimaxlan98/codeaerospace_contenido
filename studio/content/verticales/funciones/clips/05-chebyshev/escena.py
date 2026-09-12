# 05 · CHEBYSHEV — el error repartido por igual.
#
# Para aproximar una funcion por un polinomio, lo natural es repartir los
# puntos de apoyo por igual. Y es lo peor que se puede hacer: el polinomio
# se descontrola justo en los bordes, y —esto es lo que no se espera nadie—
# CUANTOS MAS PUNTOS, PEOR. Chebyshev encontro donde hay que ponerlos:
# apiñados en los bordes, que son las proyecciones de puntos repartidos por
# igual sobre una circunferencia. Con los mismos 21 puntos y el mismo
# grado, el error cae de 59.82 a 0.0177.
#
# El arco de la pieza es el de la sorpresa: primero nueve puntos, que van
# bien; luego veintiuno, que van mucho peor; y solo entonces los de
# Chebyshev. Empezar por el desastre habria hecho pensar que el problema es
# el grado alto.
#
# TRES CUIDADOS, y los tres son de honestidad:
#
#   - **Los tres polinomios van en el MISMO cuadro y con el MISMO rango.**
#     Si cada uno llevara su escala, el que estalla se veria igual de manso
#     que el que no.
#   - **El que estalla se CORTA, no se aplasta** (`esp.recortar`). Un
#     `np.clip` lo dejaria pegado al borde y se leeria como saturacion, que
#     es lo contrario de dispararse.
#   - **El que acierta va A TROZOS** sobre la curva objetivo. Dos trazos
#     opacos superpuestos se funden en un color que no es ninguno de los
#     dos; a trozos se ve el cian de abajo en cada hueco, y "coinciden" se
#     lee porque se ven DOS curvas.
class Clip(Pieza):
    NOMBRE = "CHEBYSHEV"
    TESIS = "el error repartido por igual"

    # PARAMETROS elegidos: los dos grados. 20 es el clasico del fenomeno de
    # Runge; 8 es el que todavia se porta bien.
    GRADO_BAJO = 8
    GRADO = 20
    RX = (-1.06, 1.06)
    RY = (-0.85, 1.30)
    ANCHO_CAJA = ANCHO - 0.55
    ALTO_CAJA = 5.00

    def _panel(self, nodos, a_trozos):
        """La curva objetivo, sus nodos y el polinomio que sale."""
        P = esp.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)
        xs = np.linspace(self.RX[0], self.RX[1], 1600)
        objetivo = esp.curva(xs, esp.runge(xs), P, color=CIAN,
                             grosor=esp.TRAZO)
        puntos = lz.agrupar(*[esp.marca_en(P, float(n), float(esp.runge(n)),
                                           radio=0.052)
                              for n in nodos])
        # El polinomio se dibuja SOLO en [-1, 1], que es donde interpola.
        # Con el cuadro sampleado entero (hasta 1.06), los 0.06 de fuera
        # son EXTRAPOLACION y cualquier polinomio de grado 20 se dispara
        # ahi: el de Chebyshev salia con dos rayas verticales en los
        # bordes, contradiciendo a su propia cifra de 0.0177. El margen
        # del cuadro esta para que los nodos de los extremos no queden
        # pegados al borde, no para dibujar en el.
        xp = np.linspace(-1.0, 1.0, 1600)
        y = esp.interpola(nodos, esp.runge(nodos), xp)
        tramos = esp.recortar(xp, y, self.RY)
        poli = lz.agrupar(*[esp.curva(a, b, P, color=AMBAR,
                                      grosor=esp.TRAZO,
                                      a_trozos=a_trozos)
                            for a, b in tramos])
        # El RECUADRO no es mobiliario decorativo en esta pieza: es el
        # sujeto. "Se sale del cuadro" no significa nada si no hay cuadro,
        # y ademas es lo que hace que lo pintado ocupe la franja entera —
        # sin el, la campana de Runge llenaba el 28 % y el guardian
        # abortaba el render.
        return P, lz.agrupar(esp.recuadro(P), esp.eje_x(P), objetivo,
                             poli, puntos), poli

    def pieza(self):
        L = self.L

        # --- 1. nueve puntos, y va bien -------------------------------
        n_bajo = esp.nodos_equiespaciados(self.GRADO_BAJO)
        _, panel_bajo, poli_bajo = self._panel(n_bajo, True)
        L.escena(panel_bajo, t=0.9)
        self.leer(3.6)
        L.dato(medido(esp.error_interpolacion(n_bajo), 3),
               "de error, con nueve")
        self.leer(3.6)

        # --- 2. veintiuno, y va MUCHO peor ----------------------------
        n_eq = esp.nodos_equiespaciados(self.GRADO)
        P, panel_eq, poli_eq = self._panel(n_eq, False)
        fuera = rot("SE SALE DEL CUADRO", color=AMBAR)
        # Arriba en el centro, que es el unico sitio donde el polinomio no
        # pasa: sus dos excursiones salen por x ~ +-0.9 y en el centro se
        # queda pegado a la campana. Colocado a la izquierda, la excursion
        # izquierda le cruzaba la palabra "SALE" por encima.
        fuera.move_to(P(0.0, 1.21))
        panel_eq = lz.agrupar(panel_eq, fuera)
        L.relevo(escena=panel_eq,
                 dato=(medido(esp.error_interpolacion(n_eq), 2),
                       "de error, con veintiuno"), t=0.9)
        self.leer(4.2)

        # --- 3. los mismos veintiuno, bien puestos --------------------
        n_ch = esp.nodos_chebyshev(self.GRADO)
        _, panel_ch, poli_ch = self._panel(n_ch, True)
        L.relevo(escena=panel_ch,
                 dato=(medido(esp.error_interpolacion(n_ch), 4),
                       "de error, bien puestos"), t=0.9)
        self.leer(4.2)

        # --- 4. y la unica diferencia es DONDE se mira ----------------
        # Los mismos veintiun puntos, en dos filas. Arriba repartidos por
        # igual; abajo, los de Chebyshev. No hay nada mas distinto entre
        # los dos casos.
        Q = esp.marco((-1.06, 1.06), (-1.0, 1.0), ancho=self.ANCHO_CAJA,
                      alto=3.6)
        filas = []
        for y0, nodos, color, texto in ((0.72, n_eq, CIAN, "REPARTIDOS"),
                                        (-0.72, n_ch, AMBAR, "DE CHEBYSHEV")):
            linea = esp.curva(np.array([-1.06, 1.06]),
                              np.array([y0, y0]), Q, color=LINEA,
                              grosor=esp.TRAZO_PELO)
            ptos = lz.agrupar(*[esp.marca_en(Q, float(n), y0, radio=0.055,
                                             color=color) for n in nodos])
            eti = rot(texto, color=color)
            eti.next_to(Q(0.0, y0), DOWN, buff=0.26)
            filas.append(lz.agrupar(linea, ptos, eti))
        razon = (esp.error_interpolacion(n_eq)
                 / esp.error_interpolacion(n_ch))
        L.relevo(escena=lz.agrupar(*filas),
                 dato=(medido(razon, 0), "veces menos error"), t=0.9)
        self.leer(4.2)
