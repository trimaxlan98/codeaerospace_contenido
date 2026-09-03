# 02 · Transformada de Fourier — lo breve ocupa mucha banda.
#
# El verbo visual: un pulso que se ESTRECHA arriba y su espectro que se
# ENSANCHA abajo, a la vez, en un panel partido (`lz.dos_dominios`). Tres
# pasos — pulsos de 2.0, 1.0 y 0.5 segundos — y cada uno releva los dos
# paneles Y la cifra en un solo movimiento (`L.relevo`): la cifra es el
# primer nulo del espectro en hercios, medido por `tf.primer_nulo` sobre
# la malla real, no calculado a mano.
#
# El remate no cambia el dibujo: solo releva la cifra al producto
# ancho x nulo (`tf.producto_tiempo_banda`), que vale 1 siempre. Por eso
# la ultima pieza es el mismo panel de 0.5 s que ya esta en pantalla — el
# punto es que el numero no depende de cual de los tres estabas mirando.
#
# El ANCHO del pulso en segundos es un parametro ELEGIDO (no lo mide nadie
# en este render), asi que va como rotulo gris encima del panel, nunca
# como cifra ambar. Lo unico ambar es el nulo y el producto.
#
# Encuadre: el pulso se recorta a t en [-1.6, 1.6] (la ventana mas ancha,
# 2.0 s, cabe entera) y el espectro a |f| <= 5 Hz con rango_x FIJO en los
# tres pasos — si la ventana cambiara con el ancho, el ensanche del
# espectro dejaria de verse porque el eje se reescalaria con el.
class Clip(Pieza):
    NOMBRE = "FOURIER"
    TESIS = "lo breve ocupa mucha banda"

    ANCHO_PANEL = 5.0
    ALTO_PANEL = 1.5
    VENTANA_T = 1.6      # medio ancho de la ventana de tiempo (s)
    VENTANA_F = 5.0       # medio ancho de la ventana de frecuencia (Hz)
    ANCHOS = (2.0, 1.0, 0.5)

    def _texto_ancho(self, ancho_pulso):
        unidad = "segundo" if abs(ancho_pulso - 1.0) < 1e-9 else "segundos"
        return f"ancho {medido(ancho_pulso, 2)} {unidad}"

    def _paneles(self, ancho_pulso):
        """El pulso (arriba) y su espectro (abajo), con el nulo marcado."""
        t, x, f, mag = tf.pulso_y_espectro(ancho_pulso)

        dentro_t = (t >= -self.VENTANA_T) & (t <= self.VENTANA_T)
        pulso, _ = tf.traza(t[dentro_t], x[dentro_t], ancho=self.ANCHO_PANEL,
                            alto=self.ALTO_PANEL, color=AMBAR,
                            grosor=tf.TRAZO, rango_y=(-0.15, 1.25),
                            rango_x=(-self.VENTANA_T, self.VENTANA_T),
                            escalones=True)

        dentro_f = (f >= -self.VENTANA_F) & (f <= self.VENTANA_F)
        espectro, punto = tf.traza(f[dentro_f], mag[dentro_f],
                                   ancho=self.ANCHO_PANEL,
                                   alto=self.ALTO_PANEL, color=AMBAR,
                                   grosor=tf.TRAZO, rango_y=(-0.05, 1.10),
                                   rango_x=(-self.VENTANA_F, self.VENTANA_F))
        base = tf.cero(ancho=self.ANCHO_PANEL, y=punto(0, 0.0)[1])

        nulo = tf.primer_nulo(f, mag)
        marcas = VGroup(*[Dot(punto(signo * nulo, 0.0), radius=0.055,
                              color=AMBAR)
                          for signo in (-1, 1)])

        arriba = VGroup(pulso)
        abajo = VGroup(base, espectro, marcas)
        return arriba, abajo, nulo

    def _panel_completo(self, ancho_pulso):
        arriba, abajo, nulo = self._paneles(ancho_pulso)
        panel = lz.dos_dominios(arriba, abajo, "el pulso", "su espectro",
                                hueco=0.45, ancho=self.ANCHO_PANEL)
        rotulo_ancho = rot(self._texto_ancho(ancho_pulso), color=APAGADO,
                           cuerpo=lz.MICRO)
        rotulo_ancho.next_to(panel, UP, buff=0.22)
        return VGroup(panel, rotulo_ancho), nulo

    def pieza(self):
        L = self.L
        lecturas = (5.5, 5.5, 6.5)

        for i, ancho_pulso in enumerate(self.ANCHOS):
            grupo, nulo = self._panel_completo(ancho_pulso)
            L.relevo(escena=grupo,
                     dato=(medido(nulo, 2), "hercios del nulo"),
                     t=0.8, salida=0.45)
            self.leer(lecturas[i])

        # --- el remate: el mismo dibujo, otra cifra ------------------
        # `escena` queda IGUAL a proposito: lo que demuestra la pieza es
        # que el producto no depende de cual de los tres pasos mires.
        producto = tf.producto_tiempo_banda(self.ANCHOS[-1])
        L.relevo(dato=(medido(producto, 3), "el producto no cambia"),
                 t=0.7, salida=0.4)
        self.leer(7.5)
