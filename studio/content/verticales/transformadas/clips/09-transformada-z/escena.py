# 09 · Transformada Z — el mundo a saltos.
#
# El verbo visual: un polo CRUZA el circulo unidad y la respuesta que se
# apagaba pasa a dispararse. Arriba, el plano complejo con el circulo
# unidad y el aspa del polo; abajo, la respuesta al impulso como
# `tf.tallos` (una secuencia DISCRETA: unirla con una curva sugeriria que
# hay algo entre las muestras, y no lo hay). Los dos a la vez con
# `lz.dos_dominios`, para que se vea la correspondencia entre donde esta
# el polo y como se comporta la respuesta.
#
# Tres estados de a = 0.90 -> 0.98 -> 1.05, cada uno con `L.relevo` para
# que el aspa, la respuesta y la cifra cambien juntos. La cifra de los
# tres primeros es el RADIO del polo (0.9 / 0.98 / 1.05): un parametro
# ELEGIDO, asi que va en gris (`medido=False`). El remate no cambia el
# dibujo — sigue en pantalla el estado ya disparado — y releva solo la
# cifra al CRECIMIENTO medido por `tf.crecimiento`, en ambar: esa es la
# unica cifra que termina la pieza, porque es la unica que este render
# calcula de verdad.
#
# Trampa de encuadre (la que avisa el contrato): con a=1.05 la respuesta
# llega a 17.8 veces su arranque; con a=0.90 se queda en 0.002. Contra el
# MISMO rango_y una de las dos es una linea plana. Los dos primeros
# estados (0.90 y 0.98) SI comparten rango_y — los dos se quedan por
# debajo de 1, y compartir la escala es lo que deja ver que el segundo se
# apaga mas despacio que el primero. El tercero (1.05) se sale de esa
# escala por completo, asi que se renormaliza a su PROPIO maximo y lo dice
# con un rotulo gris ("escala propia"): sin esa nota, el salto de escala
# se leeria como que la respuesta "solo" llega a la misma altura que
# antes, cuando en realidad son 17.8 veces mas.
class Clip(Pieza):
    NOMBRE = "TRANSFORMADA Z"
    TESIS = "el mundo a saltos"

    RADIO_PLANO = 1.5      # el radio DIBUJADO del circulo unidad
    ANCHO_RESP = 5.0
    ALTO_RESP = 1.65
    N = 60
    POLOS = (0.90, 0.98, 1.05)

    def _panel(self, a):
        """El plano con el polo (arriba) y su respuesta al impulso (abajo)."""
        plano = VGroup(tf.plano_z(self.RADIO_PLANO),
                       tf.aspa(a, self.RADIO_PLANO))

        _, y = tf.respuesta_polo(a, N=self.N)
        radio = tf.radio_polo(a)
        estable = radio < 1.0
        # Los dos estados estables comparten rango: es lo que deja ver que
        # 0.98 se apaga mas despacio que 0.90. El que explota no cabe ahi.
        rango = (0.0, 1.15) if estable else (0.0, float(np.max(y)) * 1.15)
        resp = tf.tallos(y, ancho=self.ANCHO_RESP, alto=self.ALTO_RESP,
                         color=AMBAR, grosor=tf.TRAZO_FINO, punta=0.045,
                         rango_y=rango)

        estado = rot("se apaga" if estable else "explota", color=AMBAR)
        estado.next_to(resp, DOWN, buff=0.24)
        abajo = VGroup(resp, estado)
        if not estable:
            nota = rot("escala propia", color=APAGADO, cuerpo=lz.MICRO)
            nota.next_to(resp, UP, buff=0.18)
            abajo.add(nota)

        panel = lz.dos_dominios(plano, abajo, "el polo", None, hueco=0.42)
        return panel, radio

    def pieza(self):
        L = self.L

        # --- 1. dentro del circulo: se apaga ---------------------------
        panel, radio = self._panel(self.POLOS[0])
        L.relevo(escena=panel,
                 dato=(medido(radio, 2), "radio del polo", False),
                 t=0.9)
        self.leer(6.0)

        # --- 2. se acerca al borde --------------------------------------
        panel, radio = self._panel(self.POLOS[1])
        L.relevo(escena=panel,
                 dato=(medido(radio, 2), "radio del polo", False),
                 t=0.7, salida=0.4)
        self.leer(6.0)

        # --- 3. cruza: fuera del circulo, explota ------------------------
        panel, radio = self._panel(self.POLOS[2])
        L.relevo(escena=panel,
                 dato=(medido(radio, 2), "radio del polo", False),
                 t=0.7, salida=0.4)
        self.leer(6.5)

        # --- 4. el remate: cuanto crece, de verdad -----------------------
        # `escena` queda IGUAL a proposito: el dibujo ya esta disparado, lo
        # unico que cambia es que la cifra deja de ser el parametro elegido
        # y pasa a ser lo que este render MIDIO que crecio.
        crecimiento = tf.crecimiento(self.POLOS[2], N=self.N)
        L.relevo(dato=(medido(crecimiento, 1), "veces mas grande"),
                 t=0.7, salida=0.4)
        self.leer(7.5)
