# 10 · Chirp-Z — zoom donde de verdad importa.
#
# El verbo visual: la malla de puntos, repartida por todo el espectro, se
# CONCENTRA en un arco estrecho. Arriba once bins muy separados; abajo,
# colgando del trozo de eje que dos de ellos dejan libre, quinientos doce
# puntos metidos justo ahi.
#
# LO QUE ESTA PIEZA NO DICE, y es lo que la hace o la rompe: la chirp-Z NO
# da mas resolucion. Una primera version iba a afirmar que separa dos tonos
# que la DFT no separa, y es FALSO — por debajo de un ciclo por ventana no
# los separa ningun metodo lineal, porque esa informacion no esta en la
# señal. Por eso los dos tonos van a 20.0 y 21.6 ciclos por ventana: 1.6
# de separacion, resueltos de sobra por las dos. Lo que cambia no es lo
# que se ve, es DONDE se mira: la DFT reparte sus puntos por toda la
# circunferencia y solo sabe decir "entre el bin 21 y el 22"; la chirp-Z
# gasta los 512 suyos en ese hueco y dice 21.62. Es punteria, no
# resolucion, y por eso el rotulo de los dos paneles es el mismo par de
# palabras contadas: "un punto por bin" contra "512 puntos".
#
# La escala es COMUN a los dos paneles (rango_y de 0 al mismo tope), y eso
# no es cosmetico: hace que la curva de abajo salga exactamente a la
# altura del bin 21 por la izquierda y a la del 22 por la derecha, asi que
# las dos rayas discontinuas que unen los paneles son geometricamente
# ciertas y no un adorno. La chirp-Z interpola entre esas dos muestras del
# arco entero, y se ve.
#
# El maximo de la DFT se calcula sobre MEDIA circunferencia a proposito:
# sobre la entera el maximo cae en el bin espejo (el 236) y la cifra en
# pantalla habria sido 236 en vez de 20, que es la que cuenta la historia.
#
# Honestidad de las cifras: 21.6 es el tono que ELEGIMOS esconder (gris,
# es un parametro); 20 es el bin mas alto que MIDE la DFT en este render y
# 21.62 lo que MIDE la chirp-Z sobre el arco (los dos ambar). Las dos
# etiquetas de los extremos dicen lo mismo, "ciclos por ventana": la
# primera en gris es lo que se metio, la ultima en ambar es lo que se
# encontro, y que coincidan es toda la pieza.
class Clip(Pieza):
    NOMBRE = "CHIRP-Z"
    TESIS = "zoom donde de verdad importa"

    N = 256
    TONOS = (20.0, 21.6)      # ciclos por ventana: elegidos
    VENTANA = (16, 26)        # los bins de la DFT que se dibujan
    ARCO = (21.0, 22.0)       # el trozo donde la chirp-Z gasta sus puntos
    M = 512                   # cuantos puntos pone ahi dentro
    BORDES = (21, 22)         # los dos bins que abrazan el arco

    ANCHO_P = 5.2
    ALTO_ONDA = 3.9
    ALTO_DFT = 3.5            # la DFT cuando va sola
    ALTO_PAR = 2.00           # cada panel cuando van los dos
    HUECO_PAR = 1.25          # el aire que separa los dos paneles

    # --- lo que mide la libreria en este render ------------------------
    def _medir(self):
        self.x = tf.dos_tonos(*self.TONOS, N=self.N)
        # Media circunferencia: sobre la entera el maximo cae en el bin
        # espejo (236) y la cifra habria sido esa.
        self.espectro = tf.zoom_czt(self.x, 0.0, self.N / 2.0,
                                    M=self.N // 2)
        self.bin_alto = tf.pico_interpolado(self.espectro, 0.0, self.N / 2.0)
        self.arco = tf.zoom_czt(self.x, *self.ARCO, M=self.M)
        self.pico = tf.pico_interpolado(self.arco, *self.ARCO)
        b0, b1 = self.VENTANA
        self.bins = self.espectro[b0:b1 + 1]
        # Tope COMUN a los dos paneles. Sin el, la curva de abajo no
        # casaria con los bins de arriba y las rayas de union mentirian.
        self.tope = float(max(self.bins.max(), self.arco.max())) * 1.06

    # --- las coordenadas locales de `tf.tallos`, para colgar cosas -----
    def _x_bin(self, k):
        b0, b1 = self.VENTANA
        return -self.ANCHO_P / 2 + (k - b0) * self.ANCHO_P / (b1 - b0)

    def _y_val(self, v, alto):
        return -alto / 2 + float(v) / self.tope * alto

    # --- dibujos --------------------------------------------------------
    def _onda(self):
        """La señal: dos cosenos sumados, con su batido a la vista."""
        curva, _ = tf.traza(np.arange(self.N), self.x, ancho=self.ANCHO_P,
                            alto=self.ALTO_ONDA, color=AMBAR, grosor=2.0,
                            rango_y=(-2.15, 2.15))
        cuerpo = VGroup(tf.cero(ancho=self.ANCHO_P), curva)
        titulo = rot("dos tonos", color=APAGADO)
        titulo.next_to(cuerpo, UP, buff=0.28)
        return VGroup(cuerpo, titulo)

    def _panel_dft(self, alto, texto, con_hueco):
        """Los bins de la DFT, muy separados, con su rotulo.

        `con_hueco` añade el corchete que marca el trozo de eje donde la
        DFT no tiene NINGUN punto. Nace apagado y se enciende despues: si
        se construyera entonces vendria sin la escala que `encajar` le dio
        al grupo, y ademas el encuadre daria un salto al aparecer."""
        stems = tf.tallos(self.bins, ancho=self.ANCHO_P, alto=alto,
                          color=AMBAR, grosor=tf.TRAZO, punta=0.045,
                          rango_y=(0.0, self.tope))
        base = tf.cero(ancho=self.ANCHO_P, y=-alto / 2)
        # Los dos bins que abrazan el arco. En TINTA porque son los dos
        # unicos sitios de ese trozo donde la DFT tiene un valor.
        nodos = VGroup(*[
            Dot([self._x_bin(k), self._y_val(self.espectro[k], alto), 0],
                radius=0.09, color=TINTA)
            for k in self.BORDES])
        titulo = rot(texto, color=APAGADO)
        titulo.next_to(stems, UP, buff=0.28)
        panel = VGroup(base, stems, nodos, titulo)

        hueco = None
        if con_hueco:
            x1, x2 = (self._x_bin(k) for k in self.BORDES)
            y = -alto / 2 - 0.17
            corchete = VGroup(
                Line([x1, y, 0], [x2, y, 0], stroke_color=AMBAR,
                     stroke_width=tf.TRAZO_FINO),
                Line([x1, y, 0], [x1, y + 0.12, 0], stroke_color=AMBAR,
                     stroke_width=tf.TRAZO_FINO),
                Line([x2, y, 0], [x2, y + 0.12, 0], stroke_color=AMBAR,
                     stroke_width=tf.TRAZO_FINO))
            nota = rot("en medio, nada", color=AMBAR)
            nota.next_to(corchete, DOWN, buff=0.22)
            corchete.set_stroke(opacity=0.0)
            nota.set_opacity(0.0)
            nodos.set_opacity(0.0)
            hueco = VGroup(corchete, nota)
            panel.add(hueco)
        return panel, nodos, hueco

    def _pareja(self):
        """Los bins arriba, el arco denso abajo, y las dos rayas que unen.

        Las rayas nacen en el EJE, bajo los bins 21 y 22, y llegan a los
        dos EXTREMOS de la curva: dicen que ese trozo de eje es todo el
        panel de abajo, que es justo lo que hace la chirp-Z. Y como la
        escala es comun, esos extremos valen exactamente lo que valen esos
        dos bins, asi que la union tambien es cierta en altura.

        Nacen abajo y no en la punta de los bins por una razon medida: una
        raya que saliera de la punta cruzaba por encima de los bins 17 a 19
        y ensuciaba el panel entero."""
        arriba, nodos, _ = self._panel_dft(self.ALTO_PAR, "un punto por bin",
                                           con_hueco=False)

        frecuencias = np.linspace(self.ARCO[0], self.ARCO[1], self.M,
                                  endpoint=False)
        curva, punto = tf.traza(frecuencias, self.arco, ancho=self.ANCHO_P,
                                alto=self.ALTO_PAR, color=AMBAR,
                                grosor=tf.TRAZO, rango_y=(0.0, self.tope),
                                rango_x=self.ARCO)
        # El arco NO lleva raya de cero. La lleva el panel de arriba, y
        # como la escala es la misma seria la misma raya: dibujarla otra
        # vez abria medio panel de hueco muerto entre ella y la curva (la
        # curva vale de 63 a 124 sobre un tope de 131) y los dos paneles
        # se leian pegados por arriba y vacios por abajo. Truncar el eje
        # para llenarlo si que seria mentir, asi que se quita la raya.
        #
        # La aguja del pico nace apagada y se enciende en el remate. En una
        # LINEA se toca el trazo, nunca `set_opacity` (que encenderia
        # tambien el relleno y la volveria una mancha).
        cima = float(self.arco.max())
        alto_pico = punto(self.pico, cima)
        aguja = VGroup(
            Line(alto_pico, alto_pico + DOWN * 0.50,
                 stroke_color=TINTA, stroke_width=tf.TRAZO_FINO),
            Dot(alto_pico, radius=0.075, color=TINTA))
        aguja.set_stroke(opacity=0.0)
        aguja[1].set_fill(opacity=0.0)
        abajo = VGroup(curva, aguja)
        pie = rot(f"{self.M} puntos", color=AMBAR)
        pie.next_to(abajo, DOWN, buff=0.22)
        abajo.add(pie)
        abajo.next_to(arriba, DOWN, buff=self.HUECO_PAR)

        # Discontinuas a proposito: continuas tenian el mismo peso visual
        # que la curva, cerraban con ella una almendra y el conjunto se
        # leia como UN dibujo raro en vez de como dos paneles y un zoom.
        suelo = arriba[0].get_center()[1]      # el eje del panel de arriba
        union = VGroup(*[
            DashedVMobject(
                Line([nodo.get_center()[0], suelo, 0], extremo,
                     stroke_color=APAGADO, stroke_width=tf.TRAZO_PELO),
                num_dashes=24, dashed_ratio=0.42)
            for nodo, extremo in zip(nodos, (curva.get_start(),
                                             curva.get_end()))])
        return VGroup(arriba, abajo, union), aguja

    # --- la pieza -------------------------------------------------------
    def pieza(self):
        L = self.L
        self._medir()

        # --- 1. la señal: uno de los dos tonos no cae en un bin --------
        L.relevo(escena=self._onda(),
                 dato=(medido(self.TONOS[1], 1), "el tono que buscamos",
                       False),
                 t=0.9)
        self.leer(4.0)

        # --- 2. su DFT: bultos, y un maximo que cae en un entero -------
        panel, nodos, hueco = self._panel_dft(self.ALTO_DFT,
                                              "solo bins enteros",
                                              con_hueco=True)
        L.relevo(escena=panel,
                 dato=(medido(self.bin_alto, 0), "el bin mas alto"),
                 t=0.8, salida=0.45)
        self.leer(5.5)

        # --- 3. entre el 21 y el 22 la DFT no tiene nada ---------------
        self.play(nodos.animate.set_opacity(1.0),
                  hueco[0].animate.set_stroke(opacity=1.0),
                  hueco[1].animate.set_opacity(1.0), run_time=0.6)
        self.leer(4.5)

        # --- 4. la chirp-Z gasta TODOS sus puntos en ese hueco ---------
        pareja, aguja = self._pareja()
        L.relevo(escena=pareja, t=0.9, salida=0.45)
        self.leer(5.0)

        # --- 5. y por eso puede decir DONDE ----------------------------
        # El dibujo no cambia: solo se enciende la aguja del pico y la
        # cifra pasa del bin entero de la DFT a la frecuencia que mide la
        # chirp-Z. La etiqueta vuelve a ser la del principio.
        self.play(aguja[0].animate.set_stroke(opacity=1.0),
                  aguja[1].animate.set_opacity(1.0), run_time=0.5)
        L.relevo(dato=(medido(self.pico, 2), "ciclos por ventana"),
                 t=0.7, salida=0.4)
        self.leer(6.0)
