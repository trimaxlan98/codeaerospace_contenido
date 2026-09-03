# 14 · Hilbert — la forma de una vibracion.
#
# El verbo visual: una nota pulsada (ataque rapido, caida lenta, portadora
# dentro) y una envolvente que APARECE abrazandola. Sin conocer la
# portadora, sin filtrar, sin promediar: sale de anular las frecuencias
# negativas del espectro y quedarse con el modulo de lo que sobra.
#
# Arco en cuatro planos:
#   1. Solo la señal (tinta): una oscilacion rapida dentro de una forma
#      lenta. Se sostiene largo para que se note que es UNA cosa con dos
#      escalas de tiempo, no ruido.
#   2. Un paso breve, deliberadamente corto (lo pide el contrato: el
#      corazon de la pieza es el plano 3): el espectro de la MISMA señal,
#      con la mitad negativa apagada y la positiva en tinta. Es justo lo
#      que hace `tf.analitica` antes de invertir.
#   3. La envolvente recuperada (`np.abs(tf.analitica(x))`) entra con un
#      `Create` de izquierda a derecha, en ambar y trazo grueso, por
#      arriba Y por abajo (su reflejo) para que se vea el abrazo por los
#      dos lados.
#   4. La prueba: la envolvente VERDADERA (la que `señal_modulada`
#      devuelve y que jamas se le paso a la transformada) se dibuja
#      PRIMERO, en tinta y gruesa: es la referencia. La recuperada
#      (`np.abs(analitica(x))`) se posa ENCIMA despues, con un `Create` de
#      izquierda a derecha, en ambar y mas fina — el mismo patron que ya
#      usa la pieza 06 (Hartley): la medida en ambar sobre la referencia
#      en tinta, nunca ambar sobre cian. Un primer intento puso la
#      verdadera en cian fino sobre la recuperada en ambar grueso, y el
#      anti-aliasing de las dos mezclaba un amarillo verdoso que no esta
#      en la paleta de cuatro colores del curso — se leia como "una curva
#      de un color raro", no como "dos curvas que coinciden". Con tinta
#      debajo y ambar encima, donde no coinciden se ve la tinta asomar: SI
#      demuestra "coinciden salvo un poco en la punta". La cifra es el
#      error maximo, y se declara que no cuenta los bordes:
#      `error_envolvente` descarta 64 muestras de cada extremo porque la
#      FFT supone la señal periodica y ahi el salto del ataque contamina
#      la medida — no es error de la transformada, es error de la
#      ventana.
#
# Trampa de la casa, la que avisa el contrato: las CINCO trazas (señal,
# envolvente +/-, verdadera +/-) comparten `RANGO_Y` EXACTAMENTE. Medido:
# max|x| = 0.997, pico de la envolvente recuperada = 1.0017 (el ringing
# del ataque abrupto se pasa un pelo de 1.0). Con rango (-1.05, 1.05)
# entran las cinco sin recortarse y sin sobrar espacio de mas.
#
# Lo que NO se dibuja: el espectro del plano 2 usa `np.fft.fft` en bruto,
# igual que ya hacen 06-hartley y 13-wigner en este mismo curso — no es
# una cifra (no hay numero en pantalla ahi), es una ilustracion del propio
# mecanismo de `tf.analitica`.
class Clip(Pieza):
    NOMBRE = "HILBERT"
    TESIS = "la forma de una vibracion"

    N = 1024
    F = 24.0
    ANCHO_T = 5.2
    ALTO_T = 3.0
    ALTO_ESP = 2.8
    RANGO_Y = (-1.05, 1.05)

    def _base(self):
        """El cero y la nota, reconstruidos identicos en cada plano: misma
        caja (ancho x alto) siempre, para que la señal no salte al
        relevar."""
        t, env, x = self._datos
        cero = tf.cero(ancho=self.ANCHO_T)
        traza, _ = tf.traza(t, x, ancho=self.ANCHO_T, alto=self.ALTO_T,
                            color=TINTA, grosor=tf.TRAZO_FINO,
                            rango_y=self.RANGO_Y)
        return VGroup(cero, traza)

    def _envolvente(self, valores):
        """La curva de arriba y su reflejo de abajo, en ambar grueso."""
        t, _, _ = self._datos
        arriba, _ = tf.traza(t, valores, ancho=self.ANCHO_T,
                             alto=self.ALTO_T, color=AMBAR,
                             grosor=tf.TRAZO, rango_y=self.RANGO_Y)
        abajo, _ = tf.traza(t, -valores, ancho=self.ANCHO_T,
                            alto=self.ALTO_T, color=AMBAR,
                            grosor=tf.TRAZO, rango_y=self.RANGO_Y)
        return arriba, abajo

    def pieza(self):
        L = self.L
        self._datos = tf.señal_modulada(N=self.N, f=self.F)
        t, env, x = self._datos

        # --- 1. la señal: una nota que golpea y se apaga ------------------
        base1 = self._base()
        r_nota = rot("una nota", TINTA)
        r_nota.next_to(base1, UP, buff=0.30)
        grupo1 = VGroup(base1, r_nota)
        L.escena(grupo1, t=1.6, animacion=AnimationGroup(
            FadeIn(base1[0], run_time=0.3),
            Create(base1[1], run_time=1.7),
            FadeIn(r_nota, run_time=0.5),
            lag_ratio=0.3))
        self.leer(6.5)

        # --- 2. la transformada: se anulan las negativas ------------------
        # Ilustracion del mecanismo de `tf.analitica`, no una cifra: la
        # mitad izquierda (frecuencias negativas) queda apagada, la
        # derecha (positivas, incluido el cero) en tinta.
        X = np.fft.fftshift(np.fft.fft(x))
        mag = np.abs(X)
        mitad = self.N // 2
        rango_mag = (0.0, float(mag.max()) * 1.15)
        neg, _ = tf.traza(np.arange(mitad), mag[:mitad], ancho=self.ANCHO_T,
                          alto=self.ALTO_ESP, color=APAGADO, grosor=2.0,
                          rango_x=(0, self.N - 1), rango_y=rango_mag)
        # Con el mismo color base la diferencia con la mitad positiva
        # apenas se nota: se apaga tambien la OPACIDAD (no es el fallo del
        # relleno de la trampa 1 — aqui es una curva recien creada, no un
        # toggle) para que la mitad anulada se vea de verdad mas debil.
        neg.set_stroke(opacity=0.5)
        pos, _ = tf.traza(np.arange(mitad, self.N), mag[mitad:],
                          ancho=self.ANCHO_T, alto=self.ALTO_ESP,
                          color=TINTA, grosor=2.0,
                          rango_x=(0, self.N - 1), rango_y=rango_mag)
        eje = tf.eje_ele(ancho=self.ANCHO_T, alto=self.ALTO_ESP)
        panel2 = VGroup(eje, neg, pos)
        r_esp = rot("se anulan negativas", APAGADO)
        r_esp.next_to(panel2, UP, buff=0.28)
        grupo2 = VGroup(panel2, r_esp)
        L.escena(grupo2, t=0.7, salida=0.4, animacion=AnimationGroup(
            FadeIn(eje, run_time=0.3),
            FadeIn(neg, run_time=0.4),
            FadeIn(pos, run_time=0.4),
            FadeIn(r_esp, run_time=0.4),
            lag_ratio=0.35))
        self.leer(2.6)

        # --- 3. la envolvente: aparece abrazando la señal -----------------
        rec = np.abs(tf.analitica(x))
        base3 = self._base()
        env_arriba, env_abajo = self._envolvente(rec)
        r_env = rot("su envolvente", AMBAR)
        r_env.next_to(VGroup(base3, env_arriba, env_abajo), UP, buff=0.30)
        grupo3 = VGroup(base3, env_arriba, env_abajo, r_env)
        L.escena(grupo3, t=1.6, salida=0.4, animacion=AnimationGroup(
            FadeIn(base3, run_time=0.5),
            AnimationGroup(Create(env_arriba, run_time=1.6),
                          Create(env_abajo, run_time=1.6)),
            FadeIn(r_env, run_time=0.5),
            lag_ratio=0.4))
        self.leer(7.2)

        # --- 4. la prueba: la recuperada se posa sobre la verdadera -------
        # La referencia (tinta, gruesa) esta desde el principio del plano;
        # la medida (ambar, mas fina) entra despues encima suyo. Verla
        # llegar y posarse es la demostracion; verlas ya juntas seria solo
        # una afirmacion.
        base4 = self._base()
        verdad_arriba, _ = tf.traza(t, env, ancho=self.ANCHO_T,
                                    alto=self.ALTO_T, color=TINTA,
                                    grosor=tf.TRAZO, rango_y=self.RANGO_Y)
        verdad_abajo, _ = tf.traza(t, -env, ancho=self.ANCHO_T,
                                   alto=self.ALTO_T, color=TINTA,
                                   grosor=tf.TRAZO, rango_y=self.RANGO_Y)
        rec_arriba, _ = tf.traza(t, rec, ancho=self.ANCHO_T,
                                 alto=self.ALTO_T, color=AMBAR,
                                 grosor=2.0, rango_y=self.RANGO_Y)
        rec_abajo, _ = tf.traza(t, -rec, ancho=self.ANCHO_T,
                                alto=self.ALTO_T, color=AMBAR,
                                grosor=2.0, rango_y=self.RANGO_Y)
        base_completa = VGroup(base4, verdad_arriba, verdad_abajo)
        fila = VGroup(rot("la verdadera", TINTA),
                      rot("sin los bordes", APAGADO, cuerpo=lz.MICRO))
        fila.arrange(RIGHT, buff=0.42)
        fila.next_to(VGroup(base_completa, rec_arriba, rec_abajo),
                     UP, buff=0.30)
        grupo4 = VGroup(base_completa, rec_arriba, rec_abajo, fila)
        error = tf.error_envolvente(N=self.N, f=self.F, borde=64)
        L.relevo(escena=grupo4,
                 dato=(medido(error, 2), "por ciento de error"),
                 t=1.2, salida=0.4, animacion=AnimationGroup(
                     AnimationGroup(FadeIn(base_completa, run_time=0.5),
                                   FadeIn(fila, run_time=0.5)),
                     AnimationGroup(Create(rec_arriba, run_time=1.3),
                                   Create(rec_abajo, run_time=1.3)),
                     lag_ratio=0.55))
        self.leer(7.5)
