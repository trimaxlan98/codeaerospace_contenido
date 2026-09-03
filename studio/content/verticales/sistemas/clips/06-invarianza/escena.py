# INVARIANZA — manana hace exactamente lo mismo.
#
# El verbo: la entrada se retrasa y la salida se retrasa IGUAL, sin
# deformarse. No se dibuja una caja de sistema (ya se ve en otras piezas
# del curso): aqui el protagonista es el desplazamiento en si, y por eso
# la entrada (CIAN, un impulso) y su respuesta (AMBAR, la respuesta al
# impulso) viven en dos paneles apilados que comparten el MISMO eje de
# muestras — para que "la misma columna" se pueda leer a ojo entre los
# dos paneles sin ninguna palabra.
#
# La salida NO se dibuja como un array de 54 muestras que hay que hacer
# Transform indice-a-indice (eso morfea "el pico viejo se hunde aqui" +
# "el pico nuevo nace alli", no lee como un desplazamiento). Se dibuja
# como UNA curva compacta (la respuesta, 24 muestras) posicionada en el
# eje compartido; desplazarla de un estado al otro (mismos valores, x
# corrida) es una traslacion limpia bajo Transform, que es exactamente
# el verbo que hace falta.
#
# La honestidad del remate: la curva "realineada" del plano 3 NO es la
# curva 1 copiada y movida a mano — sale de volver a cortar el resultado
# real de `sis.convolucion(x2, h)` (la salida de verdad cuando la entrada
# esta retrasada) en la ventana que le corresponde. Que las dos salgan
# bit a bit iguales no es un truco de dibujo: es lo que un sistema
# invariante en el tiempo hace de verdad.
class Clip(Pieza):
    NOMBRE = "INVARIANZA"
    TESIS = "manana hace exactamente lo mismo"

    # --- parametros elegidos (etiqueta apagada si se rotulan) ----------
    N = 54                      # ventana de muestras del eje compartido
    M = 24                      # cuantas muestras dura la respuesta
    N0 = 4                      # donde arranca la entrada, plano 1
    RETARDO = 20                # el retardo: tiene que verse a ojo
    TAU = 5.5
    FREQ = 0.16

    ANCHO_CAJA = ANCHO - 0.6
    ALTO_ENTRADA = 1.2
    ALTO_SALIDA = 2.7
    ALTO_REMATE = 3.5
    Y_ENTRADA = 1.65
    Y_SALIDA = -1.15

    # --- construccion de un estado (spike o curva), en su eje local ----
    def _spike(self, i):
        """La entrada: una sola raya vertical en la muestra `i`."""
        curva, punto = sis.traza(
            [i, i], [0.0, 1.0], ancho=self.ANCHO_CAJA, alto=self.ALTO_ENTRADA,
            rango_x=(0, self.N - 1), rango_y=(0.0, 1.15), grosor=sis.TRAZO,
            color=CIAN)
        marca = Line(punto(i, 1.0) + LEFT * 0.09, punto(i, 1.0) + RIGHT * 0.09,
                     stroke_color=CIAN, stroke_width=3.4)
        return VGroup(curva, marca)

    def _curva_salida(self, valores, i0, rango_y, alto=None, rango_x=None):
        """La salida: la respuesta dibujada a partir de la muestra `i0`.

        `rango_x` por defecto es el eje COMPARTIDO de N muestras (para que
        el desplazamiento de los planos 1-3 se lea contra el mismo eje que
        la entrada). El remate ya no comparte eje con nada — ahi se pasa
        `rango_x=(0, M-1)`, la longitud real de lo que se dibuja, para que
        la curva llene el ancho del cuadro en vez de apretarse en una
        esquina."""
        alto = alto if alto is not None else self.ALTO_SALIDA
        rango_x = rango_x if rango_x is not None else (0, self.N - 1)
        idx = np.arange(len(valores)) + i0
        curva, punto = sis.traza(
            idx, valores, ancho=self.ANCHO_CAJA, alto=alto,
            rango_x=rango_x, rango_y=rango_y, grosor=sis.TRAZO,
            color=AMBAR, escalones=True)
        marca = Line(punto(i0, valores[0]) + LEFT * 0.09,
                     punto(i0, valores[0]) + RIGHT * 0.09,
                     stroke_color=AMBAR, stroke_width=3.4)
        return VGroup(curva, marca)

    def pieza(self):
        L = self.L

        h = sis.h_amortiguada(N=self.M, tau=self.TAU, f=self.FREQ)
        hi, lo = float(np.max(h)), float(np.min(h))
        pad = 0.14 * (hi - lo)
        RANGO_SAL = (lo - pad, hi + pad)

        x1 = sis.impulso(N=self.N, n0=self.N0)
        y1_full = sis.convolucion(x1, h)
        y1 = y1_full[self.N0:self.N0 + self.M]

        x2 = sis.impulso(N=self.N, n0=self.N0 + self.RETARDO)
        y2_full = sis.convolucion(x2, h)
        y2 = y2_full[self.N0 + self.RETARDO:self.N0 + self.RETARDO + self.M]

        # --- los dos paneles: entrada arriba, salida abajo -------------
        suelo_e = -self.ALTO_ENTRADA / 2
        suelo_s = ((0.0 - RANGO_SAL[0]) / (RANGO_SAL[1] - RANGO_SAL[0])
                  * self.ALTO_SALIDA - self.ALTO_SALIDA / 2)

        axis_e = sis.cero(ancho=self.ANCHO_CAJA, y=suelo_e, color=LINEA)
        label_e = rot("ENTRADA")
        label_e.move_to([0, suelo_e - 0.30, 0])
        panel_e = VGroup(axis_e, label_e).shift(UP * self.Y_ENTRADA)

        axis_s = sis.cero(ancho=self.ANCHO_CAJA, y=suelo_s, color=LINEA)
        label_s = rot("SALIDA")
        label_s.move_to([0, suelo_s - self.ALTO_SALIDA / 2 - 0.30, 0])
        panel_s = VGroup(axis_s, label_s).shift(UP * self.Y_SALIDA)

        estado_e1 = self._spike(self.N0).shift(UP * self.Y_ENTRADA)
        estado_e2 = self._spike(self.N0 + self.RETARDO).shift(UP * self.Y_ENTRADA)
        estado_e2.set_stroke(opacity=0.0)

        estado_s1 = self._curva_salida(y1, self.N0, RANGO_SAL).shift(
            UP * self.Y_SALIDA)
        estado_s2 = self._curva_salida(y2, self.N0 + self.RETARDO,
                                       RANGO_SAL).shift(UP * self.Y_SALIDA)
        estado_s1.set_stroke(opacity=0.0)
        estado_s2.set_stroke(opacity=0.0)

        grupo1 = VGroup(panel_e, panel_s, estado_e1, estado_e2,
                        estado_s1, estado_s2)

        # --- 1. solo la entrada ------------------------------------------
        L.escena(grupo1, t=0.9)
        self.leer(2.6)

        # --- 2. aparece su respuesta, alineada con el mismo comienzo -----
        self.play(estado_s1.animate.set_stroke(opacity=1.0), run_time=0.8)
        self.leer(2.8)

        # --- 3. las dos se desplazan lo mismo -----------------------------
        estado_e2.set_stroke(opacity=1.0)
        estado_s2.set_stroke(opacity=1.0)
        self.play(Transform(estado_e1, estado_e2),
                  Transform(estado_s1, estado_s2), run_time=1.4,
                  rate_func=smooth)
        estado_e2.set_stroke(opacity=0.0)
        estado_s2.set_stroke(opacity=0.0)
        self.leer(2.6)

        L.relevo(dato=(medido(self.RETARDO, 0), "muestras de retardo", False),
                 t=0.5)
        self.leer(2.8)

        # --- 4. remate: la salida de antes, y la retrasada realineada ----
        # `y2` YA es el resultado real de convolucionar la entrada
        # retrasada con `h`; aqui solo se corre hacia atras para
        # compararla con `y1` en el mismo sitio — es la comparacion que
        # pide el guion, no un dibujo hecho a mano.
        suelo_r = ((0.0 - RANGO_SAL[0]) / (RANGO_SAL[1] - RANGO_SAL[0])
                  * self.ALTO_REMATE - self.ALTO_REMATE / 2)
        axis_r = sis.cero(ancho=self.ANCHO_CAJA, y=suelo_r, color=LINEA)
        label_r = rot("MISMA FORMA", color=AMBAR)
        label_r.move_to([0, suelo_r - self.ALTO_REMATE / 2 - 0.30, 0])

        # Las dos ya estan alineadas por su comienzo (cada una arranca en
        # su propia muestra 0): el eje de este cuadro es solo la longitud
        # de la respuesta, `rango_x=(0, M-1)`, no el eje de 54 muestras
        # que hacia falta para que el retardo se viera. Con el eje
        # correcto la curva ocupa el ancho entero del cuadro.
        # La referencia va en APAGADO OPACO y la de encima A TROZOS. La
        # primera version ponia el fondo en ambar al 32 % con trazo 7.0, y
        # medido sobre el fotograma renderizado el trazo salia (70,73,63) y
        # (164,121,34): oliva y ambar apagado, no ambar. La regla no es la
        # transparencia sino el ANCHO EFECTIVO — dos trazos de un par de
        # pixeles, uno dentro del otro, se mezclan en vez de leerse como
        # dos curvas, sean opacos o no. A trozos, en cada hueco se ve el
        # color de abajo y en cada trazo el de arriba, y "misma forma" se
        # lee porque se ven DOS curvas.
        fondo = self._curva_salida(y1, 0, RANGO_SAL, alto=self.ALTO_REMATE,
                                   rango_x=(0, self.M - 1))[0]
        fondo.set_stroke(color=APAGADO, opacity=1.0, width=8.0)
        crudo = self._curva_salida(y2, 0, RANGO_SAL, alto=self.ALTO_REMATE,
                                   rango_x=(0, self.M - 1))[0]
        crudo.set_stroke(color=AMBAR, width=sis.TRAZO_FINO)
        encima = DashedVMobject(crudo, num_dashes=48, dashed_ratio=0.55)
        encima.set_stroke(color=AMBAR, width=2.6)
        encima.set_stroke(opacity=0.0)

        grupo3 = VGroup(axis_r, label_r, fondo, encima)
        L.relevo(escena=grupo3, dato=None, t=0.9)
        self.leer(2.4)

        self.play(encima.animate.set_stroke(opacity=1.0), run_time=0.8)
        self.leer(2.6)

        err = float(sis.error_invarianza(h, x1, self.RETARDO))
        L.dato(medido(err, 4), "error de invarianza", medido=True, t=0.5)
        self.leer(2.8)
        self.leer(2.4)
