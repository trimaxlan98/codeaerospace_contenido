# 08 · Dos cables o cuatro
#
# Cierra el modulo "tocar el mundo": dos formas de hablar con un sensor.
# I2C manda cada byte con un ACK del esclavo pegado detras -- nueve bits
# por cada ocho de datos -- y SPI no lo necesita: ocho bits y a correr.
#
# La comparacion son DOS BARRAS APILADAS, alineadas a la izquierda y a la
# MISMA escala de tiempo (la fija la barra de I2C, que ocupa el ancho
# entero). La de SPI se dibuja con su ancho REAL, sin minimo de trazo
# inventado: a esta escala le tocan 0.041 unidades, el 0.89 % de la barra
# de I2C, y a un stroke_width de 2.4 se ve perfectamente como un hilo. Que
# case apenas se note al lado de la de I2C es exactamente lo que el clip
# tiene que enseñar.
class Clip(Pieza):
    NUMERO = 8

    def pieza(self):
        L = self.L
        f_i2c = 400e3
        f_spi = 40e6

        # --- un byte por I2C, desmenuzado en sus bits ---------------------
        # El "9" no se escribe a mano: es el coste MARGINAL de un byte de
        # mas en la formula de la libreria, lo que cancela el overhead fijo
        # (start + direccion con su propio ACK + stop) y deja solo lo que
        # cuesta cada byte de datos.
        periodo_bit = 1.0 / f_i2c
        n_bits = round((chip.tiempo_i2c(2, f_i2c)
                        - chip.tiempo_i2c(1, f_i2c)) / periodo_bit)

        partes = [(None, 1, APAGADO)] * (n_bits - 1) + [("ACK", 1, AMBAR)]
        byte = chip.barra_apilada(partes, ancho=5.3, alto=1.7, buff=0.06)
        L.escena(byte, animacion=Create(byte, lag_ratio=0.06, run_time=1.5),
                 anclaje="abajo")
        L.dato(n_bits, "bits por cada byte", medido=True, t=0.6)
        self.wait(6.0)

        # --- mover 1 KB: dos barras, misma escala, alineadas a la izquierda
        t_i2c_ms = chip.tiempo_i2c(1024, f_i2c) * 1000.0
        t_spi_ms = chip.tiempo_spi(1024, f_spi) * 1000.0

        ancho_barra = 4.6
        alto_barra = 0.9
        buff_filas = 0.9
        x_izq = -0.9                     # donde arranca el borde de las barras
        escala = ancho_barra / t_i2c_ms  # unidades por milisegundo

        def fila(ms, color, texto, y):
            w = escala * ms
            barra = RoundedRectangle(width=w, height=alto_barra,
                                     corner_radius=min(0.07, w / 3),
                                     stroke_color=color, stroke_width=2.4,
                                     fill_color=AZUL, fill_opacity=1.0)
            barra.move_to([x_izq + w / 2, y, 0])
            etq = rot(texto, color=color, cuerpo=lz.MICRO)
            etq.move_to([x_izq - 0.18 - etq.width / 2, y, 0])
            return VGroup(etq, barra), w

        y_i2c = (alto_barra + buff_filas) / 2
        y_spi = -(alto_barra + buff_filas) / 2

        # --- I2C sola: fija la escala y entra primero ----------------------
        fila_i2c, w_i2c = fila(t_i2c_ms, AMBAR, "I2C", y_i2c)
        L.escena(fila_i2c, animacion=Create(fila_i2c, run_time=1.2),
                 anclaje="abajo")
        L.dato(medido(t_i2c_ms, 0), "milisegundos", medido=True, t=0.6)
        self.wait(4.8)

        # --- SPI se suma debajo, a la MISMA escala: casi no ocupa nada -----
        fila_i2c2, _ = fila(t_i2c_ms, AMBAR, "I2C", y_i2c)
        fila_spi, w_spi = fila(t_spi_ms, CIAN, "SPI", y_spi)
        comparacion = VGroup(fila_i2c2, fila_spi)
        lz.encajar(comparacion, anclaje="abajo")
        dato_spi = lz.dato(medido(t_spi_ms, 1), "milisegundos", medido=True)
        viejo_escena = L.ocupantes["escena"]
        viejo_dato = L.ocupantes["dato"]
        L.ocupantes["escena"] = comparacion
        L.ocupantes["dato"] = dato_spi
        self.play(FadeOut(viejo_escena, run_time=0.8),
                 FadeOut(viejo_dato, run_time=0.8),
                 FadeIn(comparacion, run_time=0.8),
                 FadeIn(dato_spi, run_time=0.8))
        self.wait(5.8)

        # --- el remate: la ventaja, sobre el mismo dibujo -------------------
        ventaja = chip.ventaja_spi(1024, f_i2c, f_spi)
        L.dato(f"x{medido(ventaja, 0)}", "veces mas rapido", medido=True,
              t=0.6)
        self.wait(6.0)
