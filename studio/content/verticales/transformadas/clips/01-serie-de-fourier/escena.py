# 01 · Serie de Fourier — una esquina hecha de curvas.
#
# El verbo visual: senos que se van SUMANDO sobre la onda cuadrada gris. La
# cifra de abajo es el error, que baja de verdad. Y despues, de cerca, el
# sobreimpulso de Gibbs, que NO baja.
#
# Como se enseña que no baja, que es lo dificil de la pieza: con DOS zooms
# a distinta escala. Con 21 senos el pico esta en t = 0.4773 y hace falta
# una ventana de 0.081 para verlo; con 201 esta en t = 0.4975 y la ventana
# es de 0.0082, diez veces mas estrecha. En las dos, el pico toca la MISMA
# raya. O sea: el sobreimpulso no se encoge, se ESTRECHA.
#
# Dos intentos anteriores no lo enseñaban:
#   - una sola curva no demuestra nada (podria estar bajando);
#   - las dos en la misma ventana obligaba a un rango de y tan alto que el
#     sobreimpulso quedaba en el 7 % de la altura del dibujo, invisible.
#
# Las dos curvas se construyen ANTES de que el lienzo encaje el grupo, y se
# relevan apagando y encendiendo opacidad. Si se construyera la segunda
# despues, vendria sin la escala ni la posicion que `encajar` le dio al
# grupo, y saldria en otro sitio.
#
# Honestidad: la cuadrada es el objetivo (gris, es un dado); el error y el
# sobreimpulso los mide `transformadas.py` en este render (ambar).
class Clip(Pieza):
    NOMBRE = "SERIE DE FOURIER"
    TESIS = "una esquina hecha de curvas"

    ARMONICOS = (1, 3, 7, 21)
    ANCHO_T = 5.2
    ALTO_T = 3.2
    RANGO_ZOOM = (0.885, 1.225)
    VENTANAS = {21: (0.3900, 0.4830), 201: (0.48855, 0.49855)}

    def _cuadro(self, n_armonicos, con_suma=True):
        """La cuadrada gris y, encima, la suma parcial en ambar."""
        t, suma, cuad = tf.serie_cuadrada(n_armonicos, N=1600)
        rango = (-1.30, 1.30)
        meta, _ = tf.traza(t, cuad, ancho=self.ANCHO_T, alto=self.ALTO_T,
                           color=APAGADO, grosor=2.2, rango_y=rango,
                           escalones=True)
        piezas = [tf.cero(ancho=self.ANCHO_T), meta]
        if con_suma:
            aprox, _ = tf.traza(t, suma, ancho=self.ANCHO_T,
                                alto=self.ALTO_T, color=AMBAR,
                                grosor=tf.TRAZO, rango_y=rango)
            piezas.append(aprox)
        return VGroup(*piezas)

    def _lupa(self, n):
        """La curva de `n` armonicos dentro de su propia ventana."""
        t, suma, _ = tf.serie_cuadrada(n, N=60000)
        a, b = self.VENTANAS[n]
        dentro = (t >= a) & (t <= b)
        curva, punto = tf.traza(t[dentro], suma[dentro], ancho=self.ANCHO_T,
                                alto=self.ALTO_T, color=AMBAR,
                                grosor=tf.TRAZO, rango_y=self.RANGO_ZOOM)
        return curva, punto

    def pieza(self):
        L = self.L

        # --- 1. la meta: una señal con esquinas -----------------------
        objetivo = self._cuadro(1, con_suma=False)
        etiqueta = rot("la meta", color=APAGADO)
        etiqueta.next_to(objetivo, UP, buff=0.28)
        L.escena(VGroup(objetivo, etiqueta), t=0.9)
        self.leer(2.0)

        # --- 2. se suman armonicos, y el error baja -------------------
        for i, n in enumerate(self.ARMONICOS):
            cuadro = self._cuadro(n)
            cuantos = len(range(1, n + 1, 2))
            rotulo = rot(f"{cuantos} senos" if cuantos > 1 else "un seno",
                         color=AMBAR)
            rotulo.next_to(cuadro, UP, buff=0.28)
            error = tf.error_rms_cuadrada(n)
            L.relevo(escena=VGroup(cuadro, rotulo),
                     dato=(medido(error, 3), "error que queda"),
                     t=0.7, salida=0.4)
            self.leer(2.0 if i < len(self.ARMONICOS) - 1 else 2.4)

        # --- 3. la esquina de cerca ------------------------------------
        c21, punto = self._lupa(21)
        c201, _ = self._lupa(201)
        # La raya de abajo es la META (gris: es un dado) y la de arriba,
        # el pico que alcanzan LAS DOS aproximaciones (ambar: medido aqui).
        # Con la meta en color LINEA no se veia, y sin verla el
        # sobreimpulso no significa nada.
        techo = tf.nivel(1.0, punto, ancho=self.ANCHO_T, color=APAGADO)
        cima = tf.nivel(1.0 + 2.0 * tf.gibbs_por_ciento(201) / 100.0, punto,
                        ancho=self.ANCHO_T, color=AMBAR)
        r21 = rot("21 senos", color=AMBAR)
        r201 = rot("201 senos", color=AMBAR)
        mas = rot("diez veces mas cerca", color=APAGADO, cuerpo=lz.MICRO)
        # `set_opacity` sobre una polilinea enciende TAMBIEN el relleno:
        # la primera version dejaba la curva de 201 senos como una mancha
        # blanca maciza al encenderla. En una curva se toca el TRAZO.
        c201.set_stroke(opacity=0.0)
        for m in (r201, mas):
            m.set_opacity(0.0)
        for r in (r21, r201):
            r.next_to(VGroup(techo, cima, c21), UP, buff=0.28)
        mas.next_to(VGroup(techo, cima, c21), DOWN, buff=0.26)

        zoom = VGroup(techo, cima, c21, c201, r21, r201, mas)
        L.relevo(escena=zoom,
                 dato=(medido(tf.gibbs_por_ciento(201), 2),
                       "por ciento de mas"),
                 t=0.9, salida=0.5)
        self.leer(2.6)

        # --- 4. el mismo pico, diez veces mas cerca -------------------
        self.play(c21.animate.set_stroke(opacity=0.0),
                  r21.animate.set_opacity(0.0), run_time=0.4)
        self.play(c201.animate.set_stroke(opacity=1.0),
                  r201.animate.set_opacity(1.0),
                  mas.animate.set_opacity(1.0), run_time=0.6)
        self.leer(4.2)
