# 06 · Hartley — Fourier sin numeros imaginarios.
#
# El verbo visual: la DFT de una señal real da DOS vectores (parte real y
# parte imaginaria). Se FUNDEN en uno solo, real (Hartley), y el espectro
# reconstruido SOLO con esos numeros reales cae exactamente encima del
# |FFT| de verdad.
#
# Honestidad: los dos vectores de entrada (parte real/imaginaria) y el
# vector de Hartley son la MISMA señal de ejemplo (`tf.señal_ejemplo`,
# parametro elegido). Lo que mide `transformadas.py` en este render es el
# vector de Hartley (`tf.dht`), el espectro que sale solo de el
# (`tf.espectro_desde_hartley`) y la cifra final
# (`tf.memoria_real_vs_compleja`).
#
# El dibujo usa N=128 y solo enseña los primeros 48 bins (con los 128
# puntos completos la traza es una mancha en 5.2 unidades de ancho); la
# cifra final usa N=1024, que es el numero real del curso. Por eso el
# primer plano lleva un rotulo gris declarando cuantos bins se ven: sin
# el, "2 veces menos" con N=1024 no cuadraria con lo que se acaba de ver
# dibujado a N=128. Y el carril del dato no se queda vacio en ese tramo:
# en cuanto se funde en Hartley se pone "48 numeros reales" (gris: es el
# mismo parametro elegido, no una medida) y se sostiene hasta la cifra
# final.
#
# CIAN esta permitido aqui: hay DOS señales (real e imaginaria) que hay
# que distinguir. En cuanto se funden en el vector de Hartley, CIAN
# desaparece — ya no hay dos cosas que separar, solo una.
#
# La prueba (paso 3/4) se enseña en DOS tiempos, no de golpe: primero el
# espectro de verdad solo (TINTA, trazo grueso), y despues el de Hartley
# ENCIMA (AMBAR, trazo fino) — se ve llegar y posarse exacto. Las dos
# curvas nacen JUNTAS, en el mismo grupo, antes de que `encajar` escale y
# posicione el grupo: si el trazo de Hartley se añadiera despues, no
# llevaria la escala ni el sitio que `encajar` le dio (la trampa de
# siempre). Nace con el trazo apagado
# (`set_stroke(opacity=0.0)`, NUNCA `set_opacity`, que enciende tambien
# el relleno y lo convierte en una mancha) y se enciende despues.
#
# Fusion (paso 2): `Transform` entre dos filas de 48 tallos (96
# submobjects, sin correspondencia uno a uno) y un solo vector de 48
# tallos sale papilla. Mas simple: se apaga TODO el panel y se enciende
# el vector de Hartley en su sitio, con `L.relevo`.
class Clip(Pieza):
    NOMBRE = "HARTLEY"
    TESIS = "Fourier sin numeros imaginarios"

    N = 128
    K = 48
    ANCHO_T = lz.ANCHO_SEGURO - 0.3
    ALTO_PANEL = 1.85
    ALTO_VECTOR = 2.6
    ALTO_ESPECTRO = 3.0

    def pieza(self):
        L = self.L
        # `señal_ejemplo` es tres senos puros (fase cero): su DFT sale casi
        # toda en la parte IMAGINARIA y la real queda practicamente vacia
        # (solo ruido), asi que "dos vectores" se veia como uno lleno y
        # otro plano. Un giro circular no toca el modulo del espectro
        # (es la misma señal, solo desplazada) y con 16 muestras sobre
        # N=128 los tres tonos (bins 5, 17 y 41, todos impares) caen
        # exactamente a 45 grados: real e imaginaria quedan del mismo
        # tamaño, que es lo honesto para enseñar DOS vectores que fundir.
        x = np.roll(tf.señal_ejemplo(N=self.N), 16)
        bins = np.arange(self.K)

        # --- 1. la DFT de una señal real: dos vectores ------------------
        X = np.fft.fft(x)
        parte_real = np.real(X)[:self.K]
        parte_imag = np.imag(X)[:self.K]
        m = float(max(np.abs(parte_real).max(), np.abs(parte_imag).max()))
        m *= 1.12
        ry = (-m, m)

        arriba = tf.tallos(parte_real, ancho=self.ANCHO_T,
                           alto=self.ALTO_PANEL, color=CIAN,
                           grosor=tf.TRAZO_FINO, rango_y=ry)
        abajo = tf.tallos(parte_imag, ancho=self.ANCHO_T,
                          alto=self.ALTO_PANEL, color=AMBAR,
                          grosor=tf.TRAZO_FINO, rango_y=ry)
        panel = lz.dos_dominios(arriba, abajo,
                                rotulo_arriba="parte real",
                                rotulo_abajo="parte imaginaria",
                                ancho=self.ANCHO_T)
        info_n = rot("primeros 48 bins", color=APAGADO, cuerpo=lz.MICRO)
        info_n.next_to(panel, DOWN, buff=0.22)
        L.escena(VGroup(panel, info_n), t=1.1)
        self.leer(4.8)

        # --- 2. se funden en UNO: el vector real de Hartley -------------
        H_dibujo = tf.dht(x)[:self.K]
        hartley = tf.tallos(H_dibujo, ancho=self.ANCHO_T,
                            alto=self.ALTO_VECTOR, color=AMBAR,
                            grosor=tf.TRAZO)
        etiqueta_h = rot("un solo vector real", color=AMBAR)
        etiqueta_h.next_to(hartley, UP, buff=0.28)
        L.relevo(escena=VGroup(hartley, etiqueta_h),
                dato=(medido(self.K, 0), "numeros reales", False),
                t=1.0, salida=0.5)
        self.leer(4.6)

        # --- 3/4. la prueba: el mismo espectro, en dos tiempos -----------
        H_completo = tf.dht(x)
        espectro_h = tf.espectro_desde_hartley(H_completo)[:self.K]
        espectro_fft = np.abs(np.fft.fft(x))[:self.K]
        techo = float(max(espectro_fft.max(), espectro_h.max())) * 1.12
        ry2 = (0.0, techo)

        de_verdad, _ = tf.traza(bins, espectro_fft, ancho=self.ANCHO_T,
                                alto=self.ALTO_ESPECTRO, color=TINTA,
                                grosor=tf.TRAZO, rango_y=ry2)
        desde_hartley, _ = tf.traza(bins, espectro_h, ancho=self.ANCHO_T,
                                    alto=self.ALTO_ESPECTRO, color=AMBAR,
                                    grosor=2.0, rango_y=ry2)
        # Nace apagado: solo el TRAZO, para no encender el relleno.
        desde_hartley.set_stroke(opacity=0.0)

        r_verdad = rot("espectro real", color=APAGADO)
        r_mismo = rot("el mismo espectro", color=AMBAR)
        r_dif = rot("diferencia cero", color=APAGADO, cuerpo=lz.MICRO)
        r_mismo.set_opacity(0.0)
        r_dif.set_opacity(0.0)
        curvas = VGroup(de_verdad, desde_hartley)
        for r in (r_verdad, r_mismo):
            r.next_to(curvas, UP, buff=0.28)
        r_dif.next_to(curvas, DOWN, buff=0.22)

        L.relevo(escena=VGroup(curvas, r_verdad, r_mismo, r_dif),
                t=1.0, salida=0.5)
        self.leer(2.4)
        # El ambar LLEGA y se posa encima del blanco: no hace falta
        # moverlo, ya nacio en su sitio exacto (misma traza, mismo rango).
        self.play(desde_hartley.animate.set_stroke(opacity=1.0),
                  r_verdad.animate.set_opacity(0.0),
                  r_mismo.animate.set_opacity(1.0),
                  r_dif.animate.set_opacity(1.0), run_time=0.7)
        self.leer(3.4)

        # --- 5. la cifra: la mitad de numeros que guardar ----------------
        compleja, real = tf.memoria_real_vs_compleja(1024)
        veces = compleja / real
        hartley_final = tf.tallos(H_dibujo, ancho=self.ANCHO_T,
                                  alto=self.ALTO_VECTOR, color=AMBAR,
                                  grosor=tf.TRAZO)
        L.relevo(escena=hartley_final,
                dato=(medido(veces, 0), "veces menos numeros"),
                t=1.0, salida=0.5)
        self.leer(4.4)
