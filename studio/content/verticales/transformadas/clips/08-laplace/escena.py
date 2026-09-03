# 08 · Laplace — de derivadas a algebra.
#
# El verbo visual: una ecuacion diferencial se convierte en DOS PUNTOS de un
# plano, y esos dos puntos dicen cuanto se va a pasar la respuesta ANTES de
# resolverla. La curva se dibuja sola (Create, de izquierda a derecha: es
# tiempo, y el tiempo se lee asi), se releva a las dos aspas, y de las aspas
# sale un numero. Despues vuelve la curva con las dos rayas de referencia y
# el numero NO CAMBIA: solo cambia la etiqueta, de "predicho" a "medido".
# Ese es el remate y por eso las dos cifras tienen que ser la misma —
# `_igualdad()` aborta el render si algun dia dejaran de serlo.
#
# Aqui NO hay circulo unidad (`con_circulo=False`). El circulo es de la Z:
# en Laplace lo que separa lo estable de lo inestable es el eje imaginario,
# y dibujar una circunferencia contaria otra pelicula.
#
# El cierre es el panel partido de la casa (`lz.dos_dominios`): la respuesta
# arriba, sus polos abajo y una sola cifra para los dos. Es la frase entera
# de la pieza en una imagen, y es la unica razon de que existan las medidas
# pequeñas ANCHO_P/ALTO_P/RADIO_P — los dos paneles juntos no caben a la
# escala del plano suelto.
#
# Honestidad: `wn = 1.0` y `z = 0.5` son parametros ELEGIDOS y por eso no
# aparecen en pantalla como cifra (un parametro no es una medida, y la
# unica cifra grande de esta pieza tiene que ser ambar de verdad). Lo que
# si se enseña — 16.3, tres veces — lo calcula `transformadas.py` en este
# render por dos caminos independientes: `sobreimpulso_desde_polos` es
# formula cerrada sobre los polos y `sobreimpulso_medido` es el maximo de
# una respuesta integrada con Runge-Kutta. Ambar las tres veces.
#
# Encuadre: la ventana de tiempo es 14 s (la respuesta ya esta asentada en
# 1.000 mucho antes) y `rango_y` va de 0.0 a 1.30, asi que la curva entera
# cae dentro y `tf.traza` no se sale del cuadro. El 0.0 de abajo coincide
# a proposito con el suelo de `tf.eje_ele`: asi el eje horizontal ES la
# linea del cero y no hay dos rayas casi pegadas.
class Clip(Pieza):
    NOMBRE = "LAPLACE"
    TESIS = "de derivadas a algebra"

    WN = 1.0                 # parametro ELEGIDO, no una medida
    Z = 0.5                  # parametro ELEGIDO, no una medida
    VENTANA_T = 14.0
    RANGO_Y = (0.0, 1.30)

    ANCHO_C, ALTO_C = 5.2, 3.8       # la curva cuando va sola
    RADIO = 1.55                     # el plano cuando va solo
    ANCHO_P, ALTO_P = 4.6, 1.7       # la curva dentro del panel partido
    RADIO_P = 0.90                   # el plano dentro del panel partido

    # --- las dos caras del mismo sistema -------------------------------
    def _respuesta(self, ancho, alto):
        """La respuesta al escalon, integrada, dentro de su cuadro."""
        t, y = tf.escalon_segundo_orden(wn=self.WN, z=self.Z)
        dentro = t <= self.VENTANA_T
        t, y = t[dentro], y[dentro]
        curva, punto = tf.traza(t, y, ancho=ancho, alto=alto, color=AMBAR,
                                grosor=tf.TRAZO, rango_y=self.RANGO_Y,
                                rango_x=(0.0, self.VENTANA_T))
        return t, y, curva, punto, tf.eje_ele(ancho=ancho, alto=alto)

    def _marcas(self, t, y, punto, ancho):
        """Las dos referencias: el valor final y el pico.

        El valor final va en APAGADO (es la altura del escalon, un dado) y
        el pico en AMBAR (sale de mirar la curva integrada). El punto sobre
        la cresta ata el numero de abajo a un sitio concreto del dibujo:
        sin el, las dos rayas podrian estar hablando de otra cosa."""
        i = int(np.argmax(y))
        return VGroup(
            tf.nivel(1.0, punto, ancho=ancho, color=APAGADO),
            tf.nivel(float(y[i]), punto, ancho=ancho, color=AMBAR),
            Dot(punto(t[i], y[i]), radius=0.06, color=AMBAR))

    def _polos(self, radio):
        """Los dos polos, en aspa, sobre los ejes SIN circulo unidad."""
        aspas = VGroup(*[tf.aspa(p, radio=radio, escala=1.0, color=AMBAR)
                         for p in tf.polos_segundo_orden(self.WN, self.Z)])
        return tf.plano_z(radio, con_circulo=False), aspas

    def _igualdad(self):
        """Las dos cifras de la pieza, con la comprobacion que las une.

        La pieza AFIRMA que el numero que sale de los polos y el que sale
        de integrar la ecuacion son el mismo, y lo afirma enseñando la
        misma cifra dos veces con etiquetas distintas. Si algun dia dejaran
        de coincidir a la resolucion que se publica, eso seria una mentira
        en pantalla que ningun frame delataria: mejor que el render pare."""
        pred = tf.sobreimpulso_desde_polos(self.Z)
        med = tf.sobreimpulso_medido(self.WN, self.Z)
        if medido(pred, 2) != medido(med, 2):
            raise lz.FueraDelLienzo(
                f"la pieza enseña la prediccion y la medida como el mismo "
                f"numero y ya no lo son: {medido(pred, 2)} frente a "
                f"{medido(med, 2)}")
        return pred, med

    # --- la pieza -------------------------------------------------------
    def pieza(self):
        L = self.L
        pred, med = self._igualdad()

        # --- 1. el sistema: sube, se pasa, oscila y se asienta ----------
        # Se DIBUJA en vez de aparecer de golpe: el eje horizontal es
        # tiempo, y una respuesta al escalon que se pinta de izquierda a
        # derecha se entiende sin una sola palabra.
        t, y, curva, _, ejes = self._respuesta(self.ANCHO_C, self.ALTO_C)
        r_resp = rot("la respuesta", color=APAGADO)
        r_resp.next_to(VGroup(ejes, curva), UP, buff=0.28)
        L.escena(VGroup(ejes, curva, r_resp),
                 animacion=AnimationGroup(FadeIn(ejes, run_time=0.6),
                                          Create(curva, run_time=2.1),
                                          FadeIn(r_resp, run_time=0.6),
                                          lag_ratio=0.5))
        self.leer(4.2)

        # --- 2. la misma ecuacion, dos puntos --------------------------
        # Las aspas y su rotulo se construyen ANTES de que `encajar` toque
        # el grupo (si nacieran despues vendrian sin su escala ni su sitio)
        # y entran apagados, para que el relevo tenga DOS tiempos: primero
        # llega el plano vacio, y despues caen los dos polos. Ese segundo
        # tiempo es el momento de la pieza.
        plano, aspas = self._polos(self.RADIO)
        r_polos = rot("dos polos", color=APAGADO)
        r_polos.next_to(VGroup(plano, aspas), UP, buff=0.28)
        aspas.set_stroke(opacity=0.0)       # en una linea se toca el TRAZO
        r_polos.set_opacity(0.0)
        L.relevo(escena=VGroup(plano, aspas, r_polos), t=0.85, salida=0.45)
        self.wait(0.7)
        self.play(aspas.animate.set_stroke(opacity=1.0),
                  r_polos.animate.set_opacity(1.0), run_time=0.8)
        self.leer(4.0)

        # --- 3. lo que predicen sin resolver nada ----------------------
        L.dato(medido(pred, 2), "por ciento predicho", t=0.7)
        self.leer(4.6)

        # --- 4. y lo que hace la curva ---------------------------------
        # La cifra vale lo mismo que en el paso anterior A PROPOSITO: lo
        # que cambia es de donde sale. Por eso el relevo cambia dibujo y
        # etiqueta a la vez y el numero se queda quieto en 16.3.
        t2, y2, curva2, punto2, ejes2 = self._respuesta(self.ANCHO_C,
                                                        self.ALTO_C)
        marcas = self._marcas(t2, y2, punto2, self.ANCHO_C)
        r_pico = rot("cuanto se pasa", color=AMBAR)
        r_pico.next_to(VGroup(ejes2, curva2, marcas), UP, buff=0.28)
        L.relevo(escena=VGroup(ejes2, curva2, marcas, r_pico),
                 dato=(medido(med, 2), "por ciento medido"),
                 t=0.85, salida=0.45)
        self.leer(5.4)

        # --- 5. las dos caras y un solo numero -------------------------
        t3, y3, curva3, punto3, ejes3 = self._respuesta(self.ANCHO_P,
                                                        self.ALTO_P)
        plano3, aspas3 = self._polos(self.RADIO_P)
        panel = lz.dos_dominios(
            VGroup(ejes3, curva3, self._marcas(t3, y3, punto3, self.ANCHO_P)),
            VGroup(plano3, aspas3), "la respuesta", "sus polos", hueco=0.5)
        L.relevo(escena=panel, dato=(medido(med, 2), "por ciento de mas"),
                 t=0.85, salida=0.45)
        self.leer(5.0)
