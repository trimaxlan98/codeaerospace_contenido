# 11 · Hablar poco para durar mucho
#
# Cierra el modulo de la radio. La corriente media NO es el promedio de
# "encendido" y "apagado": es una integral ponderada por el tiempo, y el
# estado apagado dura mil veces mas que el anuncio. Cuatro pasos: el
# anuncio desmenuzado en sus tres canales, la linea de un segundo entero
# con muchisimo silencio entre anuncios, lo que cuesta hablar (hoja de
# datos) y el remate: la corriente media de verdad.
#
# Cifras: los microsegundos del evento y el ciclo de trabajo salen de
# `chip.anuncio_ble` y `chip.ciclo_trabajo`. La corriente media sale de
# `chip.corriente_media`, que integra encendido y apagado ponderados por
# tiempo — no es un promedio de los dos valores. Los 130 mA de transmision
# y los 10 uA de deep sleep son hoja de datos (`chip.HOJA`) y van con
# etiqueta APAGADA.
class Clip(Pieza):
    NUMERO = 11

    def pieza(self):
        L = self.L

        # --- el anuncio, canal a canal -----------------------------------
        us_canal, us_evento = chip.anuncio_ble(payload=31, canales=3)
        paquetes = chip.marcas_tiempo(
            [0.0, us_canal, 2 * us_canal], ancho=5.2, alto=3.0,
            t_max=us_evento, color=AMBAR)
        L.escena(paquetes, animacion=Create(paquetes, run_time=1.2),
                 anclaje="abajo")
        L.dato(str(int(round(us_evento))), "microsegundos de anuncio")
        self.wait(4.8)

        # --- un segundo entero: diez anuncios y casi todo silencio -------
        instantes = np.arange(10) * 0.1
        segundo = chip.marcas_tiempo(instantes, ancho=5.3, alto=3.0,
                                     t_max=1.0, color=AMBAR)
        L.escena(segundo, animacion=FadeIn(segundo, lag_ratio=0.14,
                                           run_time=1.3), anclaje="abajo")
        duty = chip.ciclo_trabajo(us_evento * 1e-6, 0.1) * 100
        L.dato(medido(duty, 1), "por ciento hablando")
        self.wait(5.0)

        # --- lo que cuesta hablar (hoja de datos) -------------------------
        # El dibujo se queda: los diez anuncios siguen en pantalla, solo
        # cambia el dato de abajo.
        L.dato(str(int(chip.HOJA["i_ble_tx_ma"])), "miliamperios al hablar",
              medido=False)
        self.wait(4.4)

        # --- el remate: la media es una integral, no un promedio ---------
        i_off_ma = chip.HOJA["i_deep_sleep_ua"] / 1000.0
        partes = [("HABLA", us_evento, AMBAR),
                  (None, 0.1 * 1e6 - us_evento, APAGADO)]
        reparto = chip.barra_apilada(partes, ancho=5.2, alto=2.4)
        L.escena(reparto, animacion=FadeIn(reparto, lag_ratio=0.12,
                                           run_time=1.3), anclaje="abajo")
        i_media_ua = chip.corriente_media(
            chip.HOJA["i_ble_tx_ma"], us_evento * 1e-6, i_off_ma, 0.1) * 1000
        L.dato(str(int(round(i_media_ua))), "microamperios de media")
        self.wait(5.2)

        # --- hablar aun menos: la misma cuenta, otro periodo --------------
        i_media_ua_1s = chip.corriente_media(
            chip.HOJA["i_ble_tx_ma"], us_evento * 1e-6, i_off_ma, 1.0) * 1000
        L.dato(str(int(round(i_media_ua_1s))), "microamperios cada segundo")
        self.wait(4.6)
