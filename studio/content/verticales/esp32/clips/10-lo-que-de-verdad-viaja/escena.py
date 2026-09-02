# 10 · Lo que de verdad viaja
#
# La hoja promete 65 megabits por segundo. Enviar una trama no es enviar
# la trama: es esperar a que nadie hable (DIFS), esperar otro rato al azar
# (backoff), mandar el preambulo, mandar los datos y esperar el ACK. La
# barra dibuja esos seis tramos a escala real de microsegundos, y solo uno
# de ellos es ambar.
#
# Cifras: los seis tramos y el total salen de `chip.tiempo_trama`, el
# porcentaje de `chip.eficiencia_aire` y el caudal de
# `chip.caudal_util_mbps`. Lo unico que no calcula la libreria es la tasa
# nominal (`chip.WIFI`, parametros del estandar): va con etiqueta APAGADA.
#
# Rotulo: la barra se explica con UNO. `barra_apilada` aborta el render si
# dos rotulos se encimarian, y con seis tramos de 34 a 192 us se encimaban
# todos. El color hace el resto del trabajo.
class Clip(Pieza):
    NUMERO = 10

    TRAMOS = ("difs", "backoff", "preambulo", "datos", "sifs", "ack")

    def barra(self, payload):
        """El tiempo de aire de una trama, tramo a tramo y a escala.

        Ancha y baja por naturaleza, asi que va anclada abajo. 2.8 de
        alto es lo mismo que mide el tren de pulsos del molde: con el
        rotulo debajo, el grupo ocupa 3.15 de los 5.59 de la franja (56 %)
        y la barra pesa lo que tiene que pesar. El ANCHO no se toca: es la
        escala de tiempo, y cambiarlo cambiaria lo que se enseña."""
        tramos, _ = chip.tiempo_trama(payload)
        partes = [("DATOS" if k == "datos" else None,
                   tramos[k],
                   AMBAR if k == "datos" else APAGADO)
                  for k in self.TRAMOS]
        return chip.barra_apilada(partes, ancho=5.2, alto=2.8)

    def pieza(self):
        L = self.L

        # --- lo que promete la hoja -----------------------------------
        onda = chip.seno(ciclos=4.0, ancho=5.3, amplitud=1.35, color=AMBAR)
        L.escena(onda, animacion=Create(onda, run_time=1.7))
        L.dato(lz.miles(int(chip.WIFI["tasa_mbps"])),
               "megabits por segundo", medido=False, t=0.6)
        self.wait(3.6)

        # --- lo que de verdad cuesta una trama ------------------------
        _, total_us = chip.tiempo_trama(1500)
        aire = self.barra(1500)
        L.escena(aire, animacion=FadeIn(aire, lag_ratio=0.12, run_time=1.5))
        # El total va por `lz.miles`, que redondea a entero y separa los
        # grupos: 369.75 us se ven como "370". (Con el `medido(x, 0)` del
        # bloque de estilo salia "37" hasta que el clip 04 le puso la
        # guarda del punto decimal; el camino de aqui nunca dependio de
        # ella.)
        L.dato(lz.miles(int(round(total_us))), "microsegundos de aire")
        self.wait(4.4)

        # --- y de todo ese aire, esto es tuyo -------------------------
        L.dato(f"{chip.eficiencia_aire(1500) * 100:.1f}",
               "por ciento son datos")
        self.wait(5.0)

        # --- el paquete pequeño: la misma espera para nada ------------
        # La cifra se apaga ANTES de cambiar la barra: si no, el 49.9 se
        # queda dos segundos debajo de la barra del paquete de 100 bytes,
        # que es otra trama y otro porcentaje. Un hueco vacio no miente.
        L.quitar("dato", t=0.35)
        menudo = self.barra(100)
        L.escena(menudo, animacion=FadeIn(menudo, lag_ratio=0.12,
                                          run_time=1.1))
        L.dato(f"{chip.eficiencia_aire(100) * 100:.1f}",
               "por ciento son datos")
        self.wait(5.0)

        # --- lo que queda de los 65 -----------------------------------
        L.quitar("dato", t=0.35)
        vuelta = self.barra(1500)
        L.escena(vuelta, animacion=FadeIn(vuelta, lag_ratio=0.12,
                                          run_time=1.1))
        L.dato(f"{chip.caudal_util_mbps(1500):.1f}", "megabits utiles")
        self.wait(5.4)
