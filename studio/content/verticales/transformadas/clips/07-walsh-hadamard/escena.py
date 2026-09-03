# 07 · Walsh-Hadamard — sin una sola multiplicacion.
#
# El verbo visual: las ondas SUAVES de Fourier (cuatro senos, frecuencia
# creciente, apilados) se relevan por las mismas cuatro "frecuencias" de
# Walsh, que solo valen +1 y -1. Ese relevo es el UNICO momento en que
# algo se convierte en otra cosa, y por eso se sostiene mas que el resto.
#
# Por que importa, sin decirlo con una frase: proyectarse sobre +1/-1 no
# es multiplicar, es copiar o cambiar el signo. Eso se enseña con el
# coste de las dos transformadas para N=1024: la FFT hace 5 120
# multiplicaciones (`tf.coste_fft`) y la WHT hace CERO (`tf.coste_wht`,
# el segundo numero de la tupla). La barra de Walsh no se infla para que
# se vea: `tf.barras` ya dibuja un valor nulo como una raya en la base, y
# esa raya minuscula frente a la barra llena es exactamente el punto.
#
# Orden deliberado: primero se enseña sola la barra de la FFT con su
# cifra (5 120), y SOLO DESPUES aparece la barra de Walsh junto al cero.
# Sin el 5 120 delante, un "0" a cuerpo 128 no significa nada.
#
# Honestidad: 5 120 y 0 los mide `transformadas.py` en este render
# (ambar); N=1024 es un parametro ELEGIDO (rotulo gris, nunca cifra).
class Clip(Pieza):
    NOMBRE = "WALSH-HADAMARD"
    TESIS = "sin una sola multiplicacion"

    N = 1024
    ANCHO_ONDA = 5.0
    ALTO_ONDA = 0.82
    HUECO_ONDA = 0.22
    ANCHO_BARRA = 3.2
    ALTO_BARRA = 3.0
    HUECO_BARRA = 0.4

    def _ancho_una_barra(self):
        """El ancho que ocupa CADA barra dentro del par, para que la barra
        solitaria del paso 3 ya nazca con el tamaño que tendra despues."""
        return self.ANCHO_BARRA / (2.0 + self.HUECO_BARRA)

    def _param_n(self):
        return rot(f"{medido(self.N, 0)} muestras", color=APAGADO,
                   cuerpo=lz.MICRO)

    # --- 1. la base de Fourier: cuatro senos, frecuencia creciente -----
    def _senos(self):
        g = VGroup()
        t = np.linspace(0.0, 1.0, 300, endpoint=False)
        for k in range(1, 5):
            y = np.sin(2.0 * np.pi * k * t)
            linea, _ = tf.traza(t, y, ancho=self.ANCHO_ONDA,
                                alto=self.ALTO_ONDA, color=TINTA,
                                grosor=tf.TRAZO_FINO, rango_y=(-1.3, 1.3),
                                escalones=False)
            g.add(linea)
        g.arrange(DOWN, buff=self.HUECO_ONDA)
        etiqueta = rot("senos", color=APAGADO)
        etiqueta.next_to(g, UP, buff=0.28)
        return VGroup(g, etiqueta)

    # --- 2. el relevo: las mismas cuatro, valiendo solo +-1 ------------
    def _walsh(self):
        g = tf.ondas_walsh(cuantos=4, ancho=self.ANCHO_ONDA,
                           alto=self.ALTO_ONDA, hueco=self.HUECO_ONDA, N=32)
        etiqueta = rot("mas o menos uno", color=APAGADO)
        etiqueta.next_to(g, UP, buff=0.28)
        return VGroup(g, etiqueta)

    # --- 3. la referencia: lo que cuesta la FFT del mismo tamaño -------
    def _barra_fft(self):
        barra = tf.barras([tf.coste_fft(self.N)],
                          ancho=self._ancho_una_barra(), alto=self.ALTO_BARRA,
                          color=APAGADO)
        etq = rot("fft", color=APAGADO, cuerpo=lz.MICRO)
        etq.next_to(barra, DOWN, buff=0.26)
        cuerpo = VGroup(barra, etq)
        param = self._param_n()
        param.next_to(cuerpo, UP, buff=0.30)
        return VGroup(cuerpo, param)

    # --- 4. la comparacion: aparece Walsh, y su coste es cero ----------
    def _barras_comparadas(self):
        valores = [tf.coste_fft(self.N), tf.coste_wht(self.N)[1]]
        barras = tf.barras(valores, ancho=self.ANCHO_BARRA,
                           alto=self.ALTO_BARRA, colores=[APAGADO, AMBAR],
                           hueco=self.HUECO_BARRA)
        n = 2
        w = self._ancho_una_barra()
        xs = [-self.ANCHO_BARRA / 2 + i * w * (1 + self.HUECO_BARRA) + w / 2
             for i in range(n)]
        etiquetas = VGroup()
        for x, texto in zip(xs, ("fft", "walsh")):
            r = rot(texto, color=APAGADO, cuerpo=lz.MICRO)
            r.move_to([x, -self.ALTO_BARRA / 2 - 0.26, 0])
            etiquetas.add(r)
        cuerpo = VGroup(barras, etiquetas)
        param = self._param_n()
        param.next_to(cuerpo, UP, buff=0.30)
        return VGroup(cuerpo, param)

    def pieza(self):
        L = self.L

        # --- 1. la base de Fourier -------------------------------------
        L.escena(self._senos(), t=0.8)
        self.leer(3.0)

        # --- 2. el relevo: EL momento de la pieza -----------------------
        L.relevo(escena=self._walsh(), t=0.9, salida=0.5)
        self.leer(3.6)

        # --- 3. lo que cuesta hacerlo con Fourier -----------------------
        L.relevo(escena=self._barra_fft(),
                dato=(lz.miles(tf.coste_fft(self.N)), "multiplicaciones"),
                t=0.8, salida=0.45)
        self.leer(2.6)

        # --- 4. y lo que cuesta hacerlo con Walsh: nada -----------------
        L.relevo(escena=self._barras_comparadas(),
                dato=(lz.miles(tf.coste_wht(self.N)[1]), "multiplicaciones"),
                t=0.8, salida=0.45)
        self.leer(5.2)
