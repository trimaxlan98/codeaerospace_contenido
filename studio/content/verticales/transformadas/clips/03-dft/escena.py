# 03 · DFT — el ordenador no sabe integrar.
#
# El verbo visual, en dos movimientos:
#
#   1. Un coseno continuo (curva fina, gris) se muestrea en 64 puntos
#      (ambar), encima de la misma curva. Eso es toda la DFT: la integral
#      se vuelve una suma de 64 numeros. Los puntos aparecen en cascada
#      sobre la curva ya quieta — la curva no se mueve ni desaparece, solo
#      se le añaden los puntos, que es literalmente lo que hace muestrear.
#
#   2. Lo que cuesta: un tono que cabe un numero ENTERO de veces en la
#      ventana (k=8) enciende una sola raya del espectro; uno que no cabe
#      (k=8.5) se derrama por los 33 bins. Para que eso se entienda sin
#      palabras se enseña TAMBIEN la onda continua cortada por la ventana
#      y repetida dos veces: con k=8 el final de una ventana y el
#      principio de la siguiente quedan al mismo nivel (el corte casa, la
#      señal podria repetirse sin salto); con k=8.5 hay un salto brusco en
#      la costura, marcado con una linea vertical. Ese salto es la fuga
#      espectral, antes de que aparezca ningun numero. Es la ONDA
#      continua la que se corta (muchos puntos, se lee como onda de
#      verdad) — las 64 muestras discretas son otra cosa y ya aparecieron
#      en el primer movimiento.
#
# Cada caso son DOS pasos con L.relevo: primero la señal sola (mas grande,
# para leer el salto), despues el mismo dibujo encogido con el espectro
# debajo. La cifra nunca deja el carril vacio: en el primer paso de cada
# caso ya se muestra la que corresponde a esa ventana (se mide antes de
# dibujar el espectro, no despues), y si no cambia de un paso al
# siguiente no se toca — de ahi que la del caso A se quede quieta durante
# el primer paso del caso B, hasta que el nuevo espectro la reemplaza.
#
# Honestidad: 64 muestras y las frecuencias (8 y 8.5 ciclos por ventana)
# son parametros ELEGIDOS, van en gris. Los bins encendidos los mide
# `transformadas.py` en este render (ambar): 1 con k=8, 33 con k=8.5.
class Clip(Pieza):
    NOMBRE = "DFT"
    TESIS = "el ordenador no sabe integrar"

    MUESTRAS = 64
    K_ENTERO = 8
    K_FUGA = 8.5

    ANCHO_T = 5.2
    ALTO_T = 2.8
    RANGO_SENAL = (-1.15, 1.15)

    ANCHO_PANEL = 5.0
    ALTO_SENAL = 1.5
    ALTO_ESPECTRO = 1.6

    # --- numerico puro, solo para el dibujo (no son cifras en pantalla) --
    def _coseno_continuo(self, k, pasos=2000):
        t = np.linspace(0.0, float(self.MUESTRAS), pasos)
        return t, np.cos(2.0 * np.pi * float(k) * t / self.MUESTRAS)

    def _coseno_muestras(self, k):
        n = np.arange(self.MUESTRAS)
        return n, np.cos(2.0 * np.pi * float(k) * n / self.MUESTRAS)

    def _onda_extendida(self, k, pasos=2000):
        """La onda CONTINUA (no las 64 muestras) alrededor de la costura:
        la segunda mitad de una ventana seguida de la primera mitad de la
        siguiente (t se pliega modulo MUESTRAS), centrada en t = MUESTRAS.
        El ancho de vista es UNA ventana, la misma densidad de ciclos que
        el primer movimiento — mostrar dos ventanas enteras en el mismo
        ancho dobla los ciclos por unidad y hasta una onda de verdad se ve
        como un zigzag apretado. Con ~2000 puntos, ademas, no hay rectas
        entre 64 muestras (7.5 muestras/ciclo con k=8.5, eso SI sale en
        zigzag): se lee como lo que es, una onda cortandose."""
        medio = self.MUESTRAS / 2.0
        t = np.linspace(self.MUESTRAS - medio, self.MUESTRAS + medio, pasos)
        y = np.cos(2.0 * np.pi * float(k) * (t % self.MUESTRAS) / self.MUESTRAS)
        return t, y

    # --- dibujo -----------------------------------------------------------
    def _curva_y_puntos(self):
        """El coseno continuo (gris) con sus 64 muestras (ambar) encima,
        estas ultimas invisibles hasta que se revelan en cascada."""
        t_c, y_c = self._coseno_continuo(self.K_ENTERO)
        curva, punto = tf.traza(t_c, y_c, ancho=self.ANCHO_T, alto=self.ALTO_T,
                                color=APAGADO, grosor=tf.TRAZO_FINO,
                                rango_y=self.RANGO_SENAL,
                                rango_x=(0.0, float(self.MUESTRAS)))
        n, y_m = self._coseno_muestras(self.K_ENTERO)
        puntos = VGroup(*[Dot(punto(ni, yi), radius=0.045, color=AMBAR)
                          for ni, yi in zip(n, y_m)])
        for d in puntos:
            d.set_opacity(0.0)
        return curva, puntos

    def _ventana(self, k, ancho, alto):
        """La onda cortada por la ventana, dos ventanas seguidas, con la
        costura marcada. Es lo unico que cambia de tamaño entre el paso
        'sola' y el paso 'con espectro' de cada caso."""
        t_ext, y_ext = self._onda_extendida(k)
        curva, punto = tf.traza(t_ext, y_ext, ancho=ancho, alto=alto,
                                color=AMBAR, grosor=tf.TRAZO,
                                rango_y=self.RANGO_SENAL,
                                rango_x=(float(t_ext[0]), float(t_ext[-1])))
        seam_x = punto(self.MUESTRAS, 0.0)[0]
        seam = Line([seam_x, -alto / 2, 0], [seam_x, alto / 2, 0],
                    stroke_color=LINEA, stroke_width=tf.TRAZO_PELO)
        return VGroup(curva, seam)

    def _espectro(self, k):
        mag = tf.dft_tono(k, N=self.MUESTRAS)
        dibujo = tf.tallos(mag, ancho=self.ANCHO_PANEL, alto=self.ALTO_ESPECTRO,
                           color=AMBAR, grosor=tf.TRAZO_FINO,
                           rango_y=(0.0, 1.05))
        return dibujo, tf.bins_encendidos(mag)

    def _bins(self, k):
        return tf.bins_encendidos(tf.dft_tono(k, N=self.MUESTRAS))

    def _panel(self, k, texto_costura):
        arriba = self._ventana(k, self.ANCHO_PANEL, self.ALTO_SENAL)
        abajo, bins = self._espectro(k)
        panel = lz.dos_dominios(arriba, abajo, rotulo_arriba=texto_costura,
                                rotulo_abajo=None, hueco=0.5)
        return panel, bins

    def pieza(self):
        L = self.L

        # --- 1. la integral se vuelve una suma: 64 numeros -------------
        curva, puntos = self._curva_y_puntos()
        etiqueta = rot("64 muestras", color=APAGADO)
        grupo = VGroup(curva, puntos)
        etiqueta.next_to(grupo, UP, buff=0.30)
        L.escena(VGroup(grupo, etiqueta), t=0.9)
        self.leer(2.9)
        self.play(LaggedStart(*[d.animate.set_opacity(1.0) for d in puntos],
                              lag_ratio=0.035), run_time=2.0)
        self.leer(3.4)

        # --- 2. un tono que cabe entero: la costura casa ----------------
        bins_a = self._bins(self.K_ENTERO)
        ventana_a = self._ventana(self.K_ENTERO, self.ANCHO_T, self.ALTO_T)
        rot_a = rot("el corte casa", color=APAGADO)
        rot_a.next_to(ventana_a, UP, buff=0.30)
        L.relevo(escena=VGroup(ventana_a, rot_a),
                 dato=(medido(bins_a, 0), "bin encendido"),
                 t=0.8, salida=0.45)
        self.leer(3.2)

        panel_a, _ = self._panel(self.K_ENTERO, "el corte casa")
        L.relevo(escena=panel_a, t=0.8, salida=0.45)  # la cifra ya es la que toca
        self.leer(3.8)

        # --- 3. lo que no cabe se derrama: la costura no casa ------------
        ventana_b = self._ventana(self.K_FUGA, self.ANCHO_T, self.ALTO_T)
        rot_b = rot("el corte no casa", color=APAGADO)
        rot_b.next_to(ventana_b, UP, buff=0.30)
        # la cifra se queda como esta (1 bin encendido, del caso A) hasta
        # que el espectro nuevo llega en el paso siguiente y la reemplaza.
        L.relevo(escena=VGroup(ventana_b, rot_b), t=0.8, salida=0.45)
        self.leer(3.4)

        panel_b, bins_b = self._panel(self.K_FUGA, "el corte no casa")
        L.relevo(escena=panel_b,
                 dato=(medido(bins_b, 0), "bins encendidos"),
                 t=0.9, salida=0.5)
        self.leer(3.8)
