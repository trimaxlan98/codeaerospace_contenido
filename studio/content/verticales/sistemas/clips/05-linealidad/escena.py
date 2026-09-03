# 05 · LINEALIDAD — dos entradas no se estorban.
#
# LA TRAMPA DE ESTA PIEZA, y por eso son DOS actos y no uno: ensenar que
# la superposicion se cumple no demuestra nada. Una salida que cae justo
# encima de la suma de las otras dos parece un truco de dibujo mientras no
# se vea la MISMA prueba fallando en otra caja. Asi que el protocolo es
# identico en los dos actos, la cifra es la misma medida, el dibujo esta a
# la misma escala, y lo UNICO que cambia entre ellos es la caja.
#
# El protocolo, en cuatro planos:
#   1. entra x1 sola          -> sale su respuesta
#   2. entra x2 sola          -> sale la suya
#   3. entran LAS DOS JUNTAS  -> la salida cae exactamente sobre la suma
#                                de las dos anteriores.   0 por ciento.
#   4. la misma prueba en una caja que SATURA -> ya no.   41.67 por ciento.
#
# La gramatica de los dos paneles no se explica con palabras porque el
# color ya lo hace: CIAN es la ENTRADA y AMBAR la SALIDA en las dieciocho
# piezas del curso. Y dentro de cada panel, APAGADO = la REFERENCIA (las
# dos senales por separado, y la suma de sus dos salidas) y color =
# lo que esta pasando AHORA. Por eso los planos 3 y 4 se leen sin leer:
# la linea de color aterriza dentro de la banda gris, o no aterriza.
#
# TRES DECISIONES QUE VALE LA PENA DEJAR ESCRITAS:
#
#   - **El marco invisible.** Los tres cuadros son grupos distintos y
#     `encajar` apoya cada uno por su BORDE INFERIOR: con contenidos de
#     distinta altura, la caja del medio saltaba de sitio en cada corte.
#     Cada grupo lleva un rectangulo de opacidad 0 con la caja exacta del
#     cuadro, asi que los tres se encajan igual y nada se mueve. El
#     guardian de la fraccion mide lo que se PINTA, asi que ese marco no
#     lo engaña: no cuenta para el 45 %.
#   - **El umbral se elige para que NINGUNA de las dos entradas sature
#     por separado** (0.65 y 0.55 contra un umbral de 0.70). Es lo que
#     hace honrado el contraejemplo: la caja que satura no maltrata a
#     ninguna de las dos senales; solo deja de ser la suma cuando entran
#     juntas. Ahi, la suma de las dos salidas sueltas es identica a la
#     entrada dibujada arriba —porque sola, ninguna se recorta— y la
#     salida de verdad se queda plana en el umbral. Las dos discontinuas
#     dicen donde corta la caja.
#   - **La cifra del acto lineal es 0 y no "3.6e-14".** El error de
#     superposicion de una convolucion es el redondeo del coma flotante.
#     Escribirlo en notacion cientifica en un movil no informa a nadie;
#     rotularlo "POR CIENTO DE ERROR" y ensenar el cero redondeado a dos
#     decimales dice exactamente lo que hay que entender, y ademas es la
#     misma medida y el mismo rotulo que el 41.67 del acto siguiente, que
#     es donde esta la ensenanza.
class Clip(Pieza):
    NOMBRE = "LINEALIDAD"
    TESIS = "dos entradas no se estorban"

    # --- parametros ELEGIDOS (no son medidas) --------------------------
    N = 64                       # muestras de la ventana
    F1 = 2.0 / 64                # el tono lento: 2 vueltas en la ventana
    F2 = 6.0 / 64                # el tono rapido: 6 vueltas
    A1 = 0.65                    # amplitudes: las DOS por debajo del umbral
    A2 = 0.55
    UMBRAL = 0.70                # donde recorta la caja del acto 2
    FC = 0.11                    # el paso bajo del acto 1: el tono lento
    M = 15                       # pasa entero y del rapido se lleva un
                                 # tercio (medido: 0.96 y 0.64 de ganancia)

    # --- geometria del cuadro (la misma en los tres) -------------------
    # `RANGO` es el mismo en los dos paneles y en los dos actos: aqui se
    # comparan alturas de curva a ojo, asi que nada puede estar dibujado a
    # una escala distinta de lo que tiene al lado o encima.
    ANCHO_CAJA = ANCHO - 0.5
    ALTO_P = 1.62                # alto de cada panel
    RANGO = (-1.35, 1.35)
    ANCHO_GLIFO = 4.0            # la caja del sistema, entre los paneles
    ALTO_GLIFO = 0.78
    Y_E = ALTO_GLIFO / 2 + 0.30 + ALTO_P / 2      # centro del panel de
    Y_S = -Y_E                                    # entrada y del de salida
    GRUESO = 9.0                 # la banda gris de la referencia
    Y_ETI = -2.80                # el borde INFERIOR del rotulo de abajo
    MARCO = (-2.84, 2.30)        # la caja fija de todos los cuadros

    # --- piezas del cuadro ---------------------------------------------
    def _marco(self):
        """El rectangulo invisible que fija la caja del cuadro.

        Sin trazo ni relleno: entra en el `bounding box` que usa `encajar`
        y NO cuenta en el guardian del 45 %, que mide lo pintado."""
        r = Rectangle(width=self.ANCHO_CAJA,
                      height=self.MARCO[1] - self.MARCO[0],
                      stroke_opacity=0.0, fill_opacity=0.0)
        r.move_to([0, (self.MARCO[0] + self.MARCO[1]) / 2, 0])
        return r

    def _trazo(self, valores, y, color, grosor, opacidad=1.0):
        """Una senal dentro de su panel. Devuelve (curva, punto).

        Apagar o atenuar se hace SIEMPRE con `set_stroke`: `set_opacity`
        encenderia el relleno y convertiria la polilinea en una mancha."""
        curva, punto = sis.traza(np.arange(self.N), valores,
                                 ancho=self.ANCHO_CAJA, alto=self.ALTO_P,
                                 color=color, grosor=grosor,
                                 rango_x=(0, self.N - 1),
                                 rango_y=self.RANGO, escalones=True)
        if opacidad != 1.0:
            curva.set_stroke(opacity=opacidad)
        curva.shift(UP * y)
        return curva, punto

    def _ejes(self):
        return VGroup(*[sis.cero(ancho=self.ANCHO_CAJA, y=0.0,
                                 color=LINEA).shift(UP * y)
                        for y in (self.Y_E, self.Y_S)])

    def _glifo(self, nombre):
        """La caja del sistema, entre los dos paneles. Es lo unico que
        cambia entre los dos actos, y por eso lleva su nombre dentro."""
        return sis.caja(texto=nombre, ancho=self.ANCHO_GLIFO,
                        alto=self.ALTO_GLIFO, color=AMBAR)

    def _eti(self, texto):
        """El rotulo de abajo, apoyado por su BORDE INFERIOR en Y_ETI: asi
        el cuadro mide lo mismo diga lo que diga el rotulo."""
        e = rot(texto)
        e.move_to([0, 0, 0])
        e.align_to(np.array([0.0, self.Y_ETI, 0.0]), DOWN)
        return e

    def pieza(self):
        L = self.L

        # --- la materia -------------------------------------------------
        # Las dos entradas salen de la MISMA funcion: `dos_tonos` con la
        # amplitud de la otra puesta a cero. Asi x1 + x2 es exactamente
        # `dos_tonos(F1, F2, N, A1, A2)` y no hay ninguna aritmetica de
        # dibujo por medio.
        x1 = sis.dos_tonos(self.F1, self.F2, self.N, a1=self.A1, a2=0.0)
        x2 = sis.dos_tonos(self.F1, self.F2, self.N, a1=0.0, a2=self.A2)
        xs = x1 + x2
        h = sis.paso_bajo(self.FC, self.M)

        # La ventana dibujada son las N primeras muestras de la
        # convolucion (lo que sigue es la cola, ya sin entrada). Las dos
        # curvas del plano 3 se cortan igual, asi que la comparacion es la
        # misma que mide `error_superposicion` sobre el array entero.
        y1 = sis.convolucion(x1, h)[:self.N]
        y2 = sis.convolucion(x2, h)[:self.N]
        y_sueltas = y1 + y2
        y_juntas = sis.convolucion(xs, h)[:self.N]

        s_sueltas = (sis.saturar(x1, self.UMBRAL)
                     + sis.saturar(x2, self.UMBRAL))
        s_juntas = sis.saturar(xs, self.UMBRAL)

        # Las dos cifras se miden ya, juntas, por una razon de
        # composicion: es LA MISMA medida en dos cajas distintas, y el
        # lienzo elige el cuerpo de la cifra por el ancho de la cadena. Un
        # "0" a cuerpo entero al lado de un "41.67" a la mitad las haria
        # parecer de distinto rango. `cuerpo_cifra` devuelve el cuerpo
        # comun, el del estado mas ancho.
        err = sis.error_superposicion(h, x1, x2)
        err_sat = sis.error_superposicion_saturado(self.UMBRAL, x1, x2)
        cuerpo = lz.cuerpo_cifra([medido(err, 2), medido(err_sat, 2)])

        # --- cuadro A: una por una, en la caja lineal --------------------
        cur_x1, _ = self._trazo(x1, self.Y_E, CIAN, sis.TRAZO)
        cur_x2, _ = self._trazo(x2, self.Y_E, CIAN, sis.TRAZO, opacidad=0.0)
        cur_y1, _ = self._trazo(y1, self.Y_S, AMBAR, sis.TRAZO)
        cur_y2, _ = self._trazo(y2, self.Y_S, AMBAR, sis.TRAZO, opacidad=0.0)
        cuadro_a = VGroup(self._marco(), self._ejes(),
                          self._glifo("CAJA LINEAL"), self._eti("UNA POR UNA"),
                          cur_x1, cur_x2, cur_y1, cur_y2)

        L.escena(cuadro_a, t=1.0)
        self.leer(2.6)

        # La segunda entrada RELEVA a la primera en el mismo panel: las dos
        # trazas tienen la misma estructura (mismo numero de muestras y de
        # esquinas), que es la condicion para que Transform no invente
        # nada por el camino.
        cur_x2.set_stroke(opacity=1.0)
        cur_y2.set_stroke(opacity=1.0)
        self.play(Transform(cur_x1, cur_x2), Transform(cur_y1, cur_y2),
                  run_time=1.3, rate_func=smooth)
        cur_x2.set_stroke(opacity=0.0)
        cur_y2.set_stroke(opacity=0.0)
        self.leer(2.8)

        # --- cuadro B: las dos juntas, en la MISMA caja lineal -----------
        # Arriba, las dos entradas en gris y su suma en cian. Abajo, en
        # gris y gruesa, la suma de las dos salidas de antes —lo que la
        # superposicion PREDICE— y encima, en ambar fino, lo que sale de
        # verdad al meterlas juntas. Gris opaco y no ambar traslucido: el
        # ambar al 32 % sobre este azul da verde oliva (medido en el
        # curso 31, y confirmado en la primera vuelta de esta pieza).
        b_x1, _ = self._trazo(x1, self.Y_E, APAGADO, sis.TRAZO_FINO)
        b_x2, _ = self._trazo(x2, self.Y_E, APAGADO, sis.TRAZO_FINO)
        b_xs, _ = self._trazo(xs, self.Y_E, CIAN, sis.TRAZO)
        b_fondo, _ = self._trazo(y_sueltas, self.Y_S, APAGADO, self.GRUESO)
        b_encima, _ = self._trazo(y_juntas, self.Y_S, AMBAR, sis.TRAZO,
                                  opacidad=0.0)
        cuadro_b = VGroup(self._marco(), self._ejes(),
                          self._glifo("CAJA LINEAL"),
                          self._eti("LAS DOS JUNTAS"),
                          b_x1, b_x2, b_xs, b_fondo, b_encima)

        L.relevo(escena=cuadro_b, t=0.9)
        self.leer(2.2)

        self.play(b_encima.animate.set_stroke(opacity=1.0), run_time=0.8)
        self.leer(2.6)

        L.dato(medido(err, 2), "por ciento de error", medido=True, t=0.5,
               font_size=cuerpo)
        self.leer(2.8)

        # --- cuadro C: la misma prueba en una caja que SATURA ------------
        # Misma entrada, misma escala, mismo rotulo, misma cifra: lo unico
        # distinto es la caja. La cifra vieja se vacia en el mismo
        # movimiento que entra el cuadro nuevo — un 0 debajo de este
        # dibujo seria mentira.
        c_x1, _ = self._trazo(x1, self.Y_E, APAGADO, sis.TRAZO_FINO)
        c_x2, _ = self._trazo(x2, self.Y_E, APAGADO, sis.TRAZO_FINO)
        c_xs, _ = self._trazo(xs, self.Y_E, CIAN, sis.TRAZO)
        c_fondo, punto = self._trazo(s_sueltas, self.Y_S, APAGADO,
                                     self.GRUESO)
        c_encima, _ = self._trazo(s_juntas, self.Y_S, AMBAR, sis.TRAZO,
                                  opacidad=0.0)
        # `punto` es la escala del panel de abajo SIN el desplazamiento,
        # asi que la banda se construye con el y se baja despues, igual
        # que la curva.
        recorte = sis.banda(0.0, self.UMBRAL, punto, ancho=self.ANCHO_CAJA,
                            color=AMBAR)
        recorte.shift(UP * self.Y_S)
        cuadro_c = VGroup(self._marco(), self._ejes(),
                          self._glifo("CAJA QUE SATURA"),
                          self._eti("LAS DOS JUNTAS"),
                          c_x1, c_x2, c_xs, recorte, c_fondo, c_encima)

        L.relevo(escena=cuadro_c, dato=None, t=0.9)
        self.leer(2.4)

        self.play(c_encima.animate.set_stroke(opacity=1.0), run_time=0.8)
        self.leer(2.6)

        L.dato(medido(err_sat, 2), "por ciento de error", medido=True,
               t=0.5, font_size=cuerpo)
        self.leer(3.0)
        self.leer(2.4)
