# 08 · Dos cables o cuatro
#
# Cierra el modulo "tocar el mundo": dos formas de hablar con un sensor.
# I2C manda cada byte con un ACK del esclavo pegado detras -- nueve bits
# por cada ocho de datos -- y SPI no lo necesita: ocho bits y a correr. La
# barra de la comparacion esta a la MISMA escala de tiempo: el ancho de la
# barra de I2C fija cuantas unidades vale un milisegundo, y el hilo de SPI
# se dibuja con ese mismo factor, con un ancho minimo garantizado para que
# no desaparezca del todo -- la comparacion tiene que doler, no ocultarse.
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
        self.wait(5.0)

        # --- mover 1 KB por I2C: esta barra fija la escala -----------------
        t_i2c_ms = chip.tiempo_i2c(1024, f_i2c) * 1000.0
        t_spi_ms = chip.tiempo_spi(1024, f_spi) * 1000.0

        ancho_barra = 5.2
        alto_barra = 0.85
        minimo = 0.07
        escala = ancho_barra / t_i2c_ms          # unidades por milisegundo

        def tramo(color, ms, x_izq):
            w = max(escala * ms, minimo)
            r = RoundedRectangle(width=w, height=alto_barra,
                                 corner_radius=min(0.07, w / 3),
                                 stroke_color=color, stroke_width=2.4,
                                 fill_color=AZUL, fill_opacity=1.0)
            r.move_to([x_izq + w / 2, 0, 0])
            return r, w

        i2c_solo, w_i2c = tramo(TINTA, t_i2c_ms, -ancho_barra / 2)
        L.escena(i2c_solo, animacion=Create(i2c_solo, run_time=1.2),
                 anclaje="abajo")
        L.dato(medido(t_i2c_ms, 0), "milisegundos", medido=True, t=0.6)
        self.wait(5.4)

        # --- lo mismo por SPI, a la MISMA escala ---------------------------
        # A esta escala le tocarian 0.046 unidades: mas fino que un trazo
        # visible. Se dibuja con el minimo garantizado (0.07) en vez de
        # desaparecer -- eso es justo lo que hay que ver.
        i2c_de_nuevo, w_i2c2 = tramo(TINTA, t_i2c_ms, -ancho_barra / 2)
        spi, w_spi = tramo(CIAN, t_spi_ms, -ancho_barra / 2 + w_i2c2 + 0.06)
        comparacion = VGroup(i2c_de_nuevo, spi)
        L.escena(comparacion, animacion=FadeIn(comparacion, run_time=0.9),
                 anclaje="abajo")
        L.dato(medido(t_spi_ms, 1), "milisegundos", medido=True, t=0.6)
        self.wait(5.8)

        # --- el remate: la ventaja, sobre el mismo dibujo ------------------
        ventaja = chip.ventaja_spi(1024, f_i2c, f_spi)
        L.dato(f"x{medido(ventaja, 0)}", "veces mas rapido", medido=True,
              t=0.6)
        self.wait(6.2)
