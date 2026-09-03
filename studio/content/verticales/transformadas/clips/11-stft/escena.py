# 11 · STFT — saber cuando, a medias.
#
# El verbo visual: una ventana DESLIZA sobre la señal y va pintando el
# espectrograma columna a columna. Y despues el precio: la ventana corta
# afila el tiempo y emborrona la frecuencia; la larga hace lo contrario.
# La cifra final es el producto de las dos borrosidades, que no se mueve.
#
# --- Lo que costo una vuelta entera y no es evidente -------------------
#
# 1. UN CHIRP SOLO NO PUEDE ENSEÑAR EL COMPROMISO EN LOS DOS EJES. La
#    cresta de un chirp en el plano tiempo-frecuencia es una RECTA de
#    pendiente k. Una mancha de borrosidad (sigma_t, sigma_f) proyectada
#    sobre esa recta da un grosor vertical sqrt(sigma_f^2 + k^2 sigma_t^2)
#    y uno horizontal que es exactamente ese dividido por k: los dos son
#    proporcionales, asi que el chirp NUNCA enseña afilarse en un eje y
#    emborronarse en el otro. Medido con tf.chirp(40,400) por defecto: la
#    ventana de 512 sale PEOR que la de 64 en los dos lados (63.8 Hz
#    contra 41.6), porque en medio segundo de ventana el tono barre 180 Hz
#    el solo. Con esa señal, el plano del clip enseñaba lo contrario de lo
#    que dice.
#    El rodeo: (a) un chirp mas lento — de 16 a 88 hercios en un segundo,
#    k = 72 Hz/s — con el que la ventana larga si afina de verdad: la
#    cresta mide 41.3 Hz de alto con L=64 y 13.8 con L=512, tres veces
#    mas fina; y (b) el coste EN TIEMPO se enseña con la ventana misma,
#    dibujada a escala sobre el espectrograma: la de 64 muestras es una
#    rendija y la de 512 se come medio dibujo, y ademas la larga deja los
#    dos extremos del tiempo en blanco porque no le caben. Eso si es el
#    compromiso, y se ve sin leer nada.
#
# 2. LOS TRES ESPECTROGRAMAS COMPARTEN LOS DOS EJES. `tf.stft` devuelve
#    solo las columnas que caben enteras, asi que con L=512 el primer
#    centro cae en t=0.25 y el ultimo en 0.75, y ademas cada L trae su
#    propia rejilla de frecuencias (16 Hz de paso con L=64, 2 Hz con
#    L=512). Estirar 65 columnas x 41 filas a la misma caja que 121 x 6
#    seria dibujar dos reglas distintas y compararlas. Aqui todos se
#    interpolan a la MISMA rejilla (132 x 72 sobre 0-1 s y 16-96 Hz), con
#    ceros en el tiempo que la ventana no alcanza: la larga se queda
#    literalmente sin saber que pasa en los extremos, que es la mitad de
#    la tesis. Interpolar no afina nada — la cresta sigue midiendo lo
#    que mide, 41 Hz de alto con L=64 y 14 con L=512 — pero convierte
#    cinco franjas horizontales en la mancha diagonal gorda que es.
#
#    (Con la fila de continua dentro, la cosa no funcionaba: en 62 ms la
#    ventana corta no ve ni un ciclo del tono grave, asi que el bin 0 se
#    lleva el MAXIMO de la matriz, la normalizacion de `tf.mapa` deja la
#    cresta en el 70 % y el borde de abajo sale con un rayado vertical de
#    aliasing. El dibujo empieza en el primer bin real de la ventana
#    corta, 16 Hz, que es tambien donde arranca el tono.)
#
# 3. `tf.mapa` NO respeta ancho y alto a la vez: los dos setters de manim
#    escalan UNIFORME, asi que el segundo deshace al primero y la imagen
#    sale con el aspecto de la matriz (72 x 132 saldria casi cuadrada,
#    nunca la caja de 5.2 x 3.0 que pide la franja). Se encaja con
#    `stretch_to_fit_*`, como hace `aprendizaje.py`.
#
# 4. EL ESPECTROGRAMA SE PINTA CON UNA TAPA, no con imagenes por etapa.
#    `become` entre ImageMobject de tamaños distintos no es de fiar y
#    renormalizar la matriz en cada etapa cambiaria el brillo de lo ya
#    pintado. Una tapa del color del fondo que se encoge hacia la derecha
#    da el barrido exacto. La imagen entra a opacidad 0 (si no, el FadeIn
#    la deja asomar hasta un 25 % por debajo de la tapa, que tambien se
#    esta fundiendo) y se enciende entre dos `play`, tapada.
#
# Honestidad: 64, 128 y 512 son ventanas ELEGIDAS (rotulo gris). Las
# dispersiones y el producto de Gabor los mide `transformadas.py` en este
# render (ambar). 0.0066 x 12 = 0.053 x 1.5 = 0.0796: el espectador puede
# multiplicar lo que ve.
class Clip(Pieza):
    NOMBRE = "STFT"
    TESIS = "saber cuando, a medias"

    F0, F1 = 16.0, 88.0        # el chirp: parametros ELEGIDOS
    T, FS = 1.0, 1024.0
    F_PISO, F_TOPE = 16.0, 96.0   # banda dibujada (el tono va de 16 a 88)
    SALTO = 8
    NCOL, NFIL = 132, 72       # la rejilla comun a las tres ventanas
    L_MEDIA, L_CORTA, L_LARGA = 128, 64, 512
    ANCHO_P = 5.2
    GAMMA = 1.3

    # --- la mitad de datos ---------------------------------------------
    def _rejilla(self, x, L):
        """|STFT| con ventana L, llevada a la rejilla COMUN a todas las
        ventanas: mismo tiempo, misma banda y mismos pixeles."""
        tt, ff, S = tf.stft(x, L, self.SALTO, fs=self.FS)
        reloj = np.linspace(0.0, self.T, self.NCOL)
        S = np.stack([np.interp(reloj, tt, fila, left=0.0, right=0.0)
                      for fila in S])
        banda = np.linspace(self.F_PISO, self.F_TOPE, self.NFIL)
        return np.stack([np.interp(banda, ff, col) for col in S.T]).T

    def _imagen(self, x, L, ancho, alto):
        """El espectrograma como imagen, encajado en la caja que se pide."""
        img = tf.mapa(self._rejilla(x, L), gamma=self.GAMMA)
        img.stretch_to_fit_width(ancho)
        img.stretch_to_fit_height(alto)
        return img

    def _marco(self, ancho, alto):
        """El borde del cuadro, del color del fondo un paso mas claro.

        No es adorno: sin el, el espectrograma de la ventana larga —que
        solo tiene datos en el medio— parece un panel MAS ESTRECHO que el
        de la corta, y la comparacion se lee como dos dibujos a distinta
        escala en vez de como el mismo tiempo peor conocido."""
        return Rectangle(width=ancho, height=alto, stroke_color=LINEA,
                         stroke_width=tf.TRAZO_PELO, fill_opacity=0.0)

    def _panel(self, x, L, ancho, alto, con_sigma=True):
        """Espectrograma + la ventana dibujada A ESCALA encima, y sus
        rotulos: gris el tamaño elegido, ambar lo que se mide."""
        img = self._imagen(x, L, ancho, alto)
        hueco = tf.ventana_sobre(x, (x.size - L) // 2, L, ancho=ancho,
                                 alto=alto)
        cuadro = Group(img, self._marco(ancho, alto), hueco)
        arriba = rot(f"{L} muestras", color=APAGADO)
        arriba.next_to(cuadro, UP, buff=0.24)
        piezas = [cuadro, arriba]
        if con_sigma:
            sigma_t, _ = tf.dispersion_ventana(L, fs=self.FS)
            abajo = rot(f"{medido(sigma_t, 4)} segundos", color=AMBAR)
            abajo.next_to(cuadro, DOWN, buff=0.24)
            piezas.append(abajo)
        return Group(*piezas)

    # --- la pieza -------------------------------------------------------
    def pieza(self):
        L = self.L
        t, x = tf.chirp(self.F0, self.F1, T=self.T, fs=self.FS)

        # --- 1. la señal: una onda que se aprieta ---------------------
        curva, _ = tf.traza(t, x, ancho=self.ANCHO_P, alto=2.9, color=TINTA,
                            grosor=tf.TRAZO_FINO, rango_y=(-1.15, 1.15))
        r1 = rot("la onda se aprieta", color=APAGADO)
        r1.next_to(curva, UP, buff=0.28)
        # La cifra es el tono con el que ARRANCA la onda, y se puede
        # contar en el dibujo: el primer ciclo ocupa un dieciseisavo del
        # ancho. Es un parametro elegido, asi que la etiqueta va gris.
        L.relevo(escena=VGroup(tf.cero(ancho=self.ANCHO_P), curva, r1),
                 dato=(medido(self.F0, 0), "hercios al empezar", False),
                 t=0.9)
        self.leer(3.0)

        # --- 2. la ventana desliza y pinta el espectrograma -----------
        senal, _ = tf.traza(t, x, ancho=self.ANCHO_P, alto=1.45, color=TINTA,
                            grosor=tf.TRAZO_PELO, rango_y=(-1.15, 1.15))
        ventana = tf.ventana_sobre(x, 0, self.L_MEDIA, ancho=self.ANCHO_P,
                                   alto=1.45)
        arriba = VGroup(tf.cero(ancho=self.ANCHO_P), senal, ventana)

        pintado = self._imagen(x, self.L_MEDIA, self.ANCHO_P, 2.5)
        pintado.set_opacity(0.0)
        tapa = Rectangle(width=self.ANCHO_P + 0.08, height=2.58,
                         stroke_width=0.0, stroke_opacity=0.0,
                         fill_color=AZUL, fill_opacity=1.0)
        tapa.move_to(pintado)
        # El marco va DESPUES de la tapa en el grupo: si no, la tapa —que
        # se come 0.04 de mas por cada lado— le borraria el borde.
        abajo = Group(pintado, tapa, self._marco(self.ANCHO_P, 2.5))

        columna = Group(arriba, abajo).arrange(DOWN, buff=0.5)
        r2 = rot("la ventana desliza", color=APAGADO)
        r2.next_to(columna, UP, buff=0.26)
        L.relevo(escena=Group(columna, r2), t=0.8, salida=0.45)

        # La imagen se enciende ENTRE dos `play`, con la tapa encima: no
        # hay un solo fotograma en el que se vea sin pintar.
        pintado.set_opacity(1.0)
        self.play(
            ventana.animate.shift(
                RIGHT * (senal.get_right()[0] - ventana.get_right()[0])),
            tapa.animate.stretch_to_fit_width(0.02, about_edge=RIGHT),
            run_time=3.6, rate_func=linear)
        self.leer(3.0)

        # --- 3. la raya que sube ES el tono ---------------------------
        grande = Group(self._imagen(x, self.L_MEDIA, self.ANCHO_P, 3.3),
                       self._marco(self.ANCHO_P, 3.3))
        r3 = rot("el tono sube", color=AMBAR)
        r3.next_to(grande, UP, buff=0.28)
        L.relevo(escena=Group(grande, r3),
                 dato=(medido(self.F1, 0), "hercios al acabar", False),
                 t=0.8, salida=0.45)
        self.leer(3.2)

        # --- 4. la ventana corta: afilada en tiempo, ciega en frecuencia
        _, sigma_f_corta = tf.dispersion_ventana(self.L_CORTA, fs=self.FS)
        L.relevo(escena=self._panel(x, self.L_CORTA, self.ANCHO_P, 3.0),
                 dato=(medido(sigma_f_corta, 1), "hercios de borrosidad"),
                 t=0.8, salida=0.45)
        self.leer(3.4)

        # --- 5. la larga: fina en frecuencia, ciega en los extremos ---
        _, sigma_f_larga = tf.dispersion_ventana(self.L_LARGA, fs=self.FS)
        L.relevo(escena=self._panel(x, self.L_LARGA, self.ANCHO_P, 3.0),
                 dato=(medido(sigma_f_larga, 1), "hercios de borrosidad"),
                 t=0.8, salida=0.45)
        self.leer(3.6)

        # --- 6. las dos a la vez, y el producto que no se mueve -------
        juntas = Group(
            self._panel(x, self.L_CORTA, 4.7, 1.6, con_sigma=False),
            self._panel(x, self.L_LARGA, 4.7, 1.6, con_sigma=False),
        ).arrange(DOWN, buff=0.36)
        L.relevo(escena=juntas,
                 dato=(medido(tf.producto_gabor(self.L_CORTA), 5),
                       "el producto no baja"),
                 t=0.8, salida=0.45)
        self.leer(4.6)
