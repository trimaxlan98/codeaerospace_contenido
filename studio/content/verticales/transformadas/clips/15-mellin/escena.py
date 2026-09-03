# 15 · Mellin — igual aunque cambie de escala.
#
# El verbo visual: una forma se ESTIRA al triple sobre el eje del tiempo.
# Con ese mismo estiramiento, arriba (panel `lz.dos_dominios`) el espectro
# de Fourier se DESPLAZA -- el pico pasa de 0.875 a 0.250 hercios -- y
# abajo el espectro de Mellin no se mueve ni un indice: el pico se queda
# en el 5 las dos veces. Ese contraste es la pieza entera, y por eso los
# dos espectros se enseñan A LA VEZ, uno encima del otro, nunca por
# separado (si se enseñaran uno tras otro no se podria comparar "se
# movio" contra "no se movio" en el mismo instante).
#
# Antes de los dos espectros hay un puente que explica POR QUE Mellin no
# se mueve: la misma forma, con el tiempo remuestreado en u = ln(t).
# Sobre ese eje estirar deja de ser ensanchar y pasa a ser DESLIZAR (un
# desplazamiento puro), y un desplazamiento no cambia el modulo de una
# FFT — que es literalmente como calcula `tf.mellin_escala`. Las dos
# curvas del puente (TINTA para escala 1, CIAN para escala 3) son las
# UNICAS dos señales a la vez de toda la pieza, y viven en el mismo panel
# para que el desplazamiento se vea sin decir nada.
#
# El remate no puede pedir memoria. La primera version enseñaba la cifra
# "0 / se movio el pico" sobre el panel de la escala 3 solo, y para saber
# que eso es una prueba habia que acordarse del plano anterior. Ahora el
# panel de la escala 3 lleva, en APAGADO, un anillo hueco clavado en la
# posicion del pico de la escala 1 (dada, no medida aqui: por eso va en
# gris) -- arriba el punto ambar queda lejos de su anillo, abajo cae
# exactamente encima. El "0" tiene su prueba delante en el mismo
# fotograma.
#
# Honestidad: la escala x3 es ELEGIDA (gris), y tambien lo es el anillo
# de referencia (es la posicion de la escala 1, no algo que se mida en
# el estado de la escala 3). Los picos (0.875 y 0.250 hercios, el indice
# 5 dos veces) y el desplazamiento final (0) los mide `transformadas.py`
# en este render (ambar).
class Clip(Pieza):
    NOMBRE = "MELLIN"
    TESIS = "igual aunque cambie de escala"

    T_MIN, T_MAX = 0.05, 8.0
    N_FORMA = 600
    ANCHO_T = 5.2
    ALTO_T = 2.8
    RANGO_FORMA = (-0.4, 1.1)

    ANCHO_PANEL = 5.0
    ALTO_PANEL = 1.5
    FREQ_MAX = 2.5
    N_FFT = 1024
    M_SHOW = 30

    def _forma(self, escala):
        f = tf.forma_ejemplo(escala)
        t = np.linspace(self.T_MIN, self.T_MAX, self.N_FORMA)
        y = np.array([f(ti) for ti in t])
        return f, t, y

    def _espectro_fourier(self, f):
        """El espectro que se DIBUJA, sacado de la misma funcion de la que
        sale la cifra.

        La primera version reproducia aqui la FFT que `tf.pico_fourier`
        hace por dentro, con sus mismos `t_max` y `N`. Funcionaba, pero
        era fragil: si alguien cambiaba un valor por defecto en la
        libreria, el dibujo y la cifra se separaban sin que nada avisara.
        Lo levanto el agente que escribio la pieza y la libreria gano
        `tf.espectro_fourier`, del que `tf.pico_fourier` saca ahora su
        maximo. Ya no pueden divergir."""
        freqs, mag = tf.espectro_fourier(f, t_max=self.T_MAX, N=self.N_FFT)
        k = int(np.searchsorted(freqs, self.FREQ_MAX))
        return freqs[:k], mag[:k]

    def _panel_espectros(self, f, marca=None):
        """Fourier arriba, Mellin abajo, cada uno con su pico marcado.

        `marca=(freq_pico_1, indice_pico_1)` deja un anillo hueco APAGADO
        en la posicion del pico de la escala 1, calculado con las MISMAS
        funciones `punto_f`/`punto_m` de este panel: como los dos paneles
        (escala 1 y escala 3) comparten `ancho`/`alto`/`rango_y`/
        `rango_x`, esa posicion cae en el mismo pixel en los dos estados,
        y es lo que permite comparar sin memoria."""
        freqs, mag = self._espectro_fourier(f)
        magn = mag / mag.max()
        curva_f, punto_f = tf.traza(freqs, magn, ancho=self.ANCHO_PANEL,
                                    alto=self.ALTO_PANEL, color=AMBAR,
                                    grosor=tf.TRAZO,
                                    rango_y=(0.0, 1.1),
                                    rango_x=(0.0, self.FREQ_MAX))
        base_f = tf.cero(ancho=self.ANCHO_PANEL, y=punto_f(0.0, 0.0)[1])
        pico_f = tf.pico_fourier(f)
        dot_f = Dot(punto_f(pico_f, 1.0), radius=0.06, color=AMBAR)
        arriba = VGroup(base_f, curva_f, dot_f)

        mel = tf.mellin_escala(f)[:self.M_SHOW]
        meln = mel / mel.max()
        idx = np.arange(self.M_SHOW)
        curva_m, punto_m = tf.traza(idx, meln, ancho=self.ANCHO_PANEL,
                                    alto=self.ALTO_PANEL, color=TINTA,
                                    grosor=tf.TRAZO,
                                    rango_y=(0.0, 1.1),
                                    rango_x=(0.0, self.M_SHOW - 1))
        base_m = tf.cero(ancho=self.ANCHO_PANEL, y=punto_m(0.0, 0.0)[1])
        pico_m = tf.pico_mellin(f)
        dot_m = Dot(punto_m(pico_m, meln[pico_m]), radius=0.06, color=AMBAR)
        abajo = VGroup(base_m, curva_m, dot_m)

        if marca is not None:
            marca_f, marca_m = marca
            anillo_f = Circle(radius=0.09, stroke_color=APAGADO,
                              stroke_width=tf.TRAZO_PELO, fill_opacity=0.0)
            anillo_f.move_to(punto_f(marca_f, 1.0))
            arriba.add(anillo_f)
            anillo_m = Circle(radius=0.09, stroke_color=APAGADO,
                              stroke_width=tf.TRAZO_PELO, fill_opacity=0.0)
            anillo_m.move_to(punto_m(marca_m, 1.0))
            abajo.add(anillo_m)

        panel = lz.dos_dominios(arriba, abajo, "fourier", "mellin",
                                hueco=0.42, ancho=self.ANCHO_PANEL)
        return panel, pico_f, pico_m

    def pieza(self):
        L = self.L

        # --- 1. la forma --------------------------------------------------
        f1, t, y1 = self._forma(1.0)
        curva1, _ = tf.traza(t, y1, ancho=self.ANCHO_T, alto=self.ALTO_T,
                             color=TINTA, grosor=tf.TRAZO,
                             rango_y=self.RANGO_FORMA)
        eti_forma = rot("la forma")
        eti_forma.next_to(curva1, UP, buff=0.30)
        base1 = tf.cero(ancho=self.ANCHO_T)
        L.escena(VGroup(base1, curva1, eti_forma), t=0.9)
        self.leer(3.2)

        # --- 2. se estira al triple ----------------------------------------
        # `curva1` ya paso por `encajar` dentro de `L.escena`: la gemela se
        # construye DESPUES y se copia su escala/posicion (si se construyera
        # antes vendria sin ellas -- trampa 3 de la casa).
        f3, _, y3 = self._forma(3.0)
        gemela, _ = tf.traza(t, y3, ancho=self.ANCHO_T, alto=self.ALTO_T,
                             color=TINTA, grosor=tf.TRAZO,
                             rango_y=self.RANGO_FORMA)
        gemela.scale(curva1.width / gemela.width)
        gemela.move_to(curva1)
        nuevo_dato = lz.dato(medido(3, 0), "veces mas ancha", medido=False)
        L.ocupantes["dato"] = nuevo_dato
        self.play(Transform(curva1, gemela, run_time=1.1),
                  FadeIn(nuevo_dato, run_time=0.8))
        self.leer(3.6)

        # --- 3. el puente: en u = ln(t), estirar es deslizar ----------------
        u = np.log(t)
        curva_u1, _ = tf.traza(u, y1, ancho=self.ANCHO_T, alto=self.ALTO_T,
                               color=TINTA, grosor=tf.TRAZO_FINO,
                               rango_y=self.RANGO_FORMA,
                               rango_x=(u.min(), u.max()))
        curva_u3, _ = tf.traza(u, y3, ancho=self.ANCHO_T, alto=self.ALTO_T,
                               color=CIAN, grosor=tf.TRAZO,
                               rango_y=self.RANGO_FORMA,
                               rango_x=(u.min(), u.max()))
        base_u = tf.cero(ancho=self.ANCHO_T)
        eti_u = rot("se desliza", color=APAGADO)
        eti_u.next_to(VGroup(curva_u1, curva_u3), UP, buff=0.30)
        L.escena(VGroup(base_u, curva_u1, curva_u3, eti_u), t=0.9)
        self.leer(4.0)

        # --- 4. los dos espectros a la vez: uno se mueve, el otro no -------
        panel1, pico_f1, pico_m1 = self._panel_espectros(f1)
        L.relevo(escena=panel1,
                 dato=(medido(pico_f1, 3), "hercios del pico"),
                 t=0.9, salida=0.5)
        self.leer(4.4)

        # El anillo APAGADO marca donde estaba el pico de la escala 1: sin
        # el, "0" pide memoria; con el, la prueba esta en el fotograma.
        panel3, pico_f3, pico_m3 = self._panel_espectros(
            f3, marca=(pico_f1, pico_m1))
        L.relevo(escena=panel3,
                 dato=(medido(pico_f3, 3), "hercios del pico"),
                 t=0.7, salida=0.4)
        self.leer(5.2)

        # --- 5. el remate: cuanto se movio el pico de Mellin -----------------
        # `escena` queda IGUAL a proposito: el panel ya esta en pantalla y el
        # pico de Mellin no cambio de sitio al pasar de un estado al otro.
        movimiento = abs(pico_m3 - pico_m1)
        L.relevo(dato=(medido(movimiento, 0), "se movio el pico"),
                 t=0.7, salida=0.4)
        self.leer(4.8)
