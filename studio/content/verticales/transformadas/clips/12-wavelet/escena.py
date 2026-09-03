# 12 · Wavelet de Haar — un zoom que se adapta.
#
# El verbo visual: una señal suave con UN salto brusco. Fourier necesita
# cientos de senos para dibujar esa esquina, porque cada seno vive en TODO
# el dominio y no sabe DONDE esta el salto. Haar lo resuelve con un puñado
# de coeficientes, porque sus ondas son CORTAS: cada una vive en un trozo.
#
# Cuatro planos, sin mas palabras que los rotulos cortos de cada uno:
#   1. la señal con su salto (tf.traza);
#   2. las ondas de Haar a distintas escalas — anchas para lo lento,
#      estrechas para lo rapido — dibujadas a mano sobre tres puntos por
#      escala con `tf.traza(..., escalones=True)`;
#   3. los coeficientes de DETALLE por nivel (`tf.dwt_haar`), cada uno
#      contra su POSICION: una columna de picos alineados, mas ancha
#      cuanto mas grueso el nivel;
#   4. la comparacion honrada: cuantos coeficientes hacen falta para el
#      99 % de la energia, en las dos bases ortonormales.
#
# --- Dos trampas MEDIDAS, ninguna supuesta -----------------------------
#
# 1) La primera version del plano 3 dibujaba `tf.coeficientes_haar(x)` tal
#    cual (el vector de los 512, concatenado grueso-a-fino) contra su
#    PROPIO INDICE. Se veia un racimo, pero pegado al borde IZQUIERDO del
#    dibujo: eso no demuestra que la ondicula sepa DONDE esta el salto,
#    solo que los niveles gruesos son grandes (seria igual de cierto con
#    el salto en cualquier otro sitio). El indice del vector concatenado
#    mezcla ESCALA y POSICION en un solo eje, y pierde justo lo que la
#    pieza quiere enseñar.
#
# 2) Al separar los niveles con `tf.dwt_haar` y graficar cada uno contra
#    su posicion real (index * scale), con `señal_con_salto` por defecto
#    (n_salto=384) el "pico alineado en todos los niveles" que se esperaba
#    NO APARECIA — se comprobo aislando el salto puro (una señal jump_only,
#    sin el seno): sus 512 coeficientes de detalle son EXACTAMENTE CERO en
#    todos los niveles salvo el mas grueso (d2) y la aproximacion final.
#    La razon: 384 = 512*0.75 es multiplo de 2, 4, 8, ..., 128 a la vez, y
#    la DWT de Haar parte el dominio en fronteras diadicas — si el salto
#    cae EXACTO en una frontera, ningun nivel fino lo ve, porque a ambos
#    lados de esa frontera el intervalo es una meseta constante y su
#    diferencia es cero. Es un caso degenerado del PARAMETRO n_salto, no
#    un fallo de `dwt_haar`.
#    Arreglo: mover el salto a una muestra IMPAR (385: nunca es multiplo
#    de una potencia de dos, asi que nunca cae en una frontera diadica).
#    Con n_salto=385 se midio, en la señal completa (con el seno), que en
#    los tres niveles mas finos (escala 2, 4 y 8) el coeficiente junto al
#    salto es 66.9x, 16.0x y 3.3x el mayor del resto del nivel — un pico
#    que domina de verdad, no un empate con el seno. En los niveles mas
#    gruesos (16 en adelante) manda el seno, no el salto: por eso el plano
#    3 usa SOLO los tres niveles mas finos.
#    Este cambio de parametro se propaga a TODA la pieza (el mismo `y` se
#    dibuja en el plano 1 y alimenta el plano 4), asi que el numero de
#    Haar del remate pasa de 28 a 30 (Fourier no se mueve: sigue en 49).
#    La tesis no cambia — Haar sigue necesitando muchos menos que Fourier
#    — pero la cifra exacta si, porque ahora sale de un parametro distinto
#    y honesto en vez de uno que hacia el plano 3 imposible de dibujar.
#
# Honestidad: 30 y 49 los mide `tf.cuantos_para_energia` en este mismo
# render (ambar, en la cifra y en los rotulos de las dos barras). N=512, la
# muestra 385 del salto y el 99 % de energia son parametros elegidos: no se
# escriben como cifra en pantalla, asi que no hace falta declarar su color.
class Clip(Pieza):
    NOMBRE = "WAVELET DE HAAR"
    TESIS = "un zoom que se adapta"

    N = 512
    N_SALTO = 385           # impar: nunca cae en una frontera diadica
    ANCHO_T = 5.0
    ALTO_SIG = 2.8

    # --- 1. la señal con su salto ---------------------------------------
    def _panel_senal(self, y):
        x = np.arange(y.size)
        pad = 0.15 * (float(y.max()) - float(y.min()))
        rango = (float(y.min()) - pad, float(y.max()) + pad)
        curva, punto = tf.traza(x, y, ancho=self.ANCHO_T, alto=self.ALTO_SIG,
                                color=AMBAR, grosor=tf.TRAZO, rango_y=rango)
        cero_ln = tf.nivel(0.0, punto, ancho=self.ANCHO_T, color=LINEA,
                           discontinua=False)
        etiqueta = rot("un salto", color=APAGADO)
        etiqueta.next_to(curva, UP, buff=0.30)
        return VGroup(cero_ln, curva, etiqueta)

    # --- 2. las ondas de Haar, cortas a cada escala ----------------------
    def _panel_ondas(self):
        # +1 en la primera mitad del soporte, -1 en la segunda. Cada fila
        # solo dibuja su fraccion `s` del ancho total: el resto queda en
        # blanco, que es exactamente lo que significa "soporte compacto".
        escalas = (1.0, 0.5, 0.25, 0.125)
        filas = VGroup()
        for s in escalas:
            onda, _ = tf.traza([0.0, s / 2, s], [1.0, -1.0, -1.0],
                               ancho=self.ANCHO_T, alto=0.78, color=AMBAR,
                               grosor=tf.TRAZO_FINO, rango_y=(-1.0, 1.0),
                               rango_x=(0.0, 1.0), escalones=True)
            filas.add(onda)
        filas.arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        etiqueta = rot("ondas cortas", color=APAGADO)
        etiqueta.next_to(filas, UP, buff=0.32)
        return VGroup(filas, etiqueta)

    # --- 3. los coeficientes de detalle, nivel a nivel, contra su POSICION
    def _panel_coeficientes(self, y):
        _, detalles = tf.dwt_haar(y)
        # Solo los tres niveles MAS FINOS (escala 2, 4, 8): son los unicos
        # donde el salto domina sobre el propio seno (medido: 66.9x, 16.0x
        # y 3.3x el resto del nivel). De grueso a fino, de arriba a abajo,
        # para que leer hacia abajo sea leer "mas cerca".
        filas = VGroup()
        for i in (2, 1, 0):
            d = detalles[i]
            maxv = float(np.max(np.abs(d))) or 1.0
            rango = (-maxv * 1.15, maxv * 1.15)
            fila = tf.tallos(d, ancho=self.ANCHO_T, alto=0.85, color=AMBAR,
                             grosor=tf.TRAZO_PELO, punta=0.025, rango_y=rango)
            filas.add(fila)
        filas.arrange(DOWN, buff=0.22)

        # La referencia gris: la MISMA señal, mismo eje de posicion, para
        # que se vea que la columna de picos cae justo bajo el escalon.
        pad = 0.2 * (float(y.max()) - float(y.min()))
        ref, _ = tf.traza(np.arange(y.size), y, ancho=self.ANCHO_T,
                          alto=0.55, color=APAGADO, grosor=tf.TRAZO_FINO,
                          rango_y=(float(y.min()) - pad, float(y.max()) + pad))

        etiqueta = rot("el racimo", color=AMBAR)
        nota = rot("grueso a fino", color=APAGADO, cuerpo=lz.MICRO)
        return VGroup(etiqueta, ref, filas, nota).arrange(DOWN, buff=0.24)

    # --- 4. la comparacion: cuantos hacen falta para el 99 % -------------
    def _panel_comparacion(self, n_h, n_f):
        barras = tf.barras([n_h, n_f], ancho=3.4, alto=2.5,
                           colores=[AMBAR, CIAN])
        num_h = rot(medido(n_h, 0), color=AMBAR)
        num_f = rot(medido(n_f, 0), color=CIAN)
        num_h.next_to(barras[0], UP, buff=0.18)
        num_f.next_to(barras[1], UP, buff=0.18)
        eti_h = rot("haar", color=APAGADO)
        eti_f = rot("fourier", color=APAGADO)
        eti_h.next_to(barras[0], DOWN, buff=0.20)
        eti_f.next_to(barras[1], DOWN, buff=0.20)
        return VGroup(barras, num_h, num_f, eti_h, eti_f)

    def pieza(self):
        L = self.L
        y = tf.señal_con_salto(self.N, n_salto=self.N_SALTO)

        # --- 1 -----------------------------------------------------------
        L.escena(self._panel_senal(y), t=1.0)
        self.leer(4.5)

        # --- 2 -----------------------------------------------------------
        L.relevo(escena=self._panel_ondas(), t=1.0, salida=0.5)
        self.leer(5.5)

        # --- 3 -----------------------------------------------------------
        L.relevo(escena=self._panel_coeficientes(y), t=1.0, salida=0.5)
        self.leer(6.5)

        # --- 4 -----------------------------------------------------------
        coefs = tf.coeficientes_haar(y)
        cf = tf.coefs_fourier_ortonormales(y)
        n_h = tf.cuantos_para_energia(coefs, 0.99)
        n_f = tf.cuantos_para_energia(cf, 0.99)
        L.relevo(escena=self._panel_comparacion(n_h, n_f),
                 dato=(medido(n_h, 0), "coeficientes haar"),
                 t=1.2, salida=0.6)
        self.leer(8.0)
