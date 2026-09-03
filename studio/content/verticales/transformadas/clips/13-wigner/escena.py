# 13 · Fourier fraccional — girar el plano un angulo.
#
# La pieza no dibuja ninguna formula y sin embargo enseña exactamente lo que
# hace la transformada fraccional, porque usa el teorema de Radon-Wigner: el
# modulo al cuadrado de la FrFT de orden a ES la sombra de la distribucion de
# Wigner proyectada sobre un eje girado alpha = a*pi/2. Girar el plano y
# mirar su sombra no es una metafora de la FrFT: es la FrFT.
#
# El arco es un descarte:
#   1. En el TIEMPO, un chirp esta repartido de punta a punta.
#   2. En la FRECUENCIA, tambien: barre toda la banda. Fourier no lo aprieta.
#   3. En el plano de los dos a la vez es una RAYA. Ahi si esta concentrado.
#   4. Se gira el plano hasta poner la raya de canto, y la sombra se cierra
#      en un pico.
#
# El giro que lo cierra es 90 - arctan(2*beta) grados. El DOS no es de
# adorno: el eje de frecuencia de la matriz de Wigner va al doble que el de
# una FFT porque la correlacion se toma a desfase 2m. Con arctan(beta) la
# teoria decia 73.3 grados donde la medida daba 59.0.
#
# TRES cosas que costaron una vuelta y que son generales:
#
#   - Las sombras tienen que compartir ESCALA. La primera version le daba a
#     cada una su propio rango_y, asi que todas salian igual de altas y el
#     pico no crecia nunca: se veia girar el plano y no pasaba nada. Se
#     calculan todas antes y se dibujan contra el maximo global.
#   - El mapa se pinta con la PARTE POSITIVA. La distribucion de Wigner toma
#     valores negativos, asi que normalizar de min a max deja el cero en un
#     gris medio y el fondo del mapa se recorta contra el azul del lienzo
#     como una foto pegada encima. Con la parte positiva, el cero ES el
#     fondo y el mapa no lleva marco. En un chirp de una sola componente lo
#     que se recorta es ondulacion numerica, no informacion.
#   - Los bordes de la sombra se tiran. Al girar, las columnas de los
#     extremos caen medio fuera del cuadro y suman menos pixeles reales: dan
#     dos picos falsos, mas altos que el de verdad.
class Clip(Pieza):
    NOMBRE = "FOURIER FRACCIONAL"
    TESIS = "girar el plano un angulo"

    N = 256
    BETA = 0.6                 # pendiente del chirp: parametro ELEGIDO
    LADO = 2.50                # girado ocupa 2.50*sqrt(2) = 3.54 < 5.59
    ANCHO_T = 5.0
    MARGEN = 0.18              # fraccion de la sombra que se tira por lado

    def _sombra(self, W, grados, tope):
        """La sombra del plano girado, contra una escala COMUN."""
        p = tf.proyeccion_wigner(W, grados)
        corte = int(len(p) * self.MARGEN)
        p = p[corte:len(p) - corte]
        curva, _ = tf.traza(np.arange(p.size), p, ancho=self.LADO, alto=1.05,
                            color=AMBAR, grosor=2.4, rango_y=(0.0, tope))
        return curva

    def pieza(self):
        L = self.L
        t, x = tf.chirp_complejo(self.N, self.BETA)
        W = tf.wigner(x)
        Wpos = np.maximum(W, 0.0)

        # --- 1. en el tiempo esta repartido ---------------------------
        curva, _ = tf.traza(np.arange(self.N), np.real(x), ancho=self.ANCHO_T,
                            alto=3.0, color=TINTA, grosor=2.2,
                            rango_y=(-1.12, 1.12))
        r1 = rot("en el tiempo", color=APAGADO)
        r1.next_to(curva, UP, buff=0.28)
        L.escena(VGroup(tf.cero(ancho=self.ANCHO_T), curva, r1), t=0.9)
        self.leer(2.4)

        # --- 2. en la frecuencia, tampoco -----------------------------
        esp = np.abs(np.fft.fftshift(np.fft.fft(x)))
        espectro, _ = tf.traza(np.arange(esp.size), esp, ancho=self.ANCHO_T,
                               alto=3.0, color=TINTA, grosor=2.4,
                               rango_y=(0.0, float(esp.max()) * 1.02))
        r2 = rot("en la frecuencia", color=APAGADO)
        r2.next_to(espectro, UP, buff=0.28)
        L.relevo(escena=VGroup(espectro, r2), t=0.8, salida=0.45)
        self.leer(2.6)

        # --- 3. los dos a la vez: una raya ----------------------------
        # Todas las sombras se cocinan ANTES: dentro de un `play` no se
        # puede recalcular una proyeccion por fotograma sin que el render se
        # vaya a horas. Y de paso sale el tope comun de la escala.
        angulos = np.linspace(1.0, 179.0, 179)
        conc = tf.barrido_wigner(Wpos, angulos)
        mejor = float(angulos[int(np.argmax(conc))])
        veces = float(np.max(conc)
                      / tf.concentracion(tf.proyeccion_wigner(Wpos, 90.0)))
        pasos = np.linspace(90.0, mejor, 26)
        crudas = [tf.proyeccion_wigner(Wpos, g) for g in pasos]
        corte = int(len(crudas[0]) * self.MARGEN)
        tope = max(float(np.max(p[corte:len(p) - corte])) for p in crudas)

        plano = tf.mapa(Wpos, alto=self.LADO, gamma=0.55)
        plano.width = self.LADO
        sombra = self._sombra(Wpos, 90.0, tope)
        r3 = rot("los dos a la vez", color=APAGADO)
        # El hueco bajo el mapa se calcula para el mapa GIRADO: al girar 45
        # grados su esquina baja media diagonal, o sea LADO*(raiz(2)-1)/2 mas
        # que su lado. Con el hueco del mapa sin girar, la esquina se metia
        # encima de la sombra.
        holgura = self.LADO * (np.sqrt(2.0) - 1.0) / 2.0
        r3.next_to(plano, UP, buff=0.26 + holgura)
        sombra.next_to(plano, DOWN, buff=0.62 + holgura)
        L.relevo(escena=Group(plano, r3, sombra), t=0.9, salida=0.45,
                 anclaje="centro")
        self.leer(3.2)

        # --- 4. se gira hasta poner la raya de canto ------------------
        sombras = [self._sombra(Wpos, g, tope) for g in pasos]
        for s in sombras:
            s.match_width(sombra)
            s.align_to(sombra, DOWN)
            s.set_x(sombra.get_x())

        giro = rot(f"{medido(mejor, 1)} grados", color=AMBAR)
        giro.move_to(r3)
        self.play(FadeOut(r3, run_time=0.35))
        self.play(FadeIn(giro, run_time=0.35))

        def _paso(mob, alpha):
            i = min(int(alpha * len(sombras)), len(sombras) - 1)
            mob.become(sombras[i])

        self.play(
            Rotate(plano, angle=np.deg2rad(mejor - 90.0),
                   about_point=plano.get_center()),
            UpdateFromAlphaFunc(sombra, _paso),
            run_time=2.8, rate_func=smooth)
        self.leer(3.0)

        # --- 5. la cifra ----------------------------------------------
        L.dato(medido(veces, 0), "veces mas apretado", t=0.7)
        self.leer(6.0)
