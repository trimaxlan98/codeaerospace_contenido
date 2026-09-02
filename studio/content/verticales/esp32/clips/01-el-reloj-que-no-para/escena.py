# 01 · El reloj que no para
#
# MOLDE del curso. Los demas clips copian de aqui la forma, no el
# contenido: una sola cosa en la franja del dibujo, un solo dato abajo, y
# los relevos siempre por los carriles del lienzo (nunca `self.add`).
#
# Cifras: los millones de ciclos los calcula `chip.serie_ciclos` a partir
# del reloj de la escena, asi que el numero que se ve en cada frame es
# exactamente el que corresponde a ese segundo de video. Los 240 MHz son
# hoja de datos y van con la etiqueta APAGADA.
class Clip(Pieza):
    NUMERO = 1

    def pieza(self):
        L = self.L

        # --- el chip, tal como se tiene en la mano ---------------------
        pastilla = chip.encapsulado(lado=4.6, pines_por_lado=11)
        L.escena(pastilla, animacion=Create(pastilla, run_time=2.0))
        self.wait(0.8)

        # --- lo unico que dice la hoja de datos ------------------------
        L.dato("240", "megahercios de reloj", medido=False, t=0.6)
        self.wait(2.6)

        # --- y lo que eso significa mientras miras ---------------------
        # El contador lee el reloj de la escena: arranca ya con los ciclos
        # que han pasado desde el primer frame, no desde cero.
        L.contador_vivo("millones de ciclos",
                        lambda t: lz.miles(int(chip.serie_ciclos(t))),
                        t_final=36.0, paso=0.20, medido=True)
        self.wait(1.4)

        # --- el chip se abre ------------------------------------------
        dentro = chip.rejilla_bloques(
            [("CPU 0", True), ("CPU 1", True),
             "SRAM 520K", "ROM 448K",
             "WI-FI", "BLUETOOTH",
             "RTC + ULP", "34 GPIO"],
            columnas=2, ancho=2.55, alto=0.95, buff=0.22)
        L.escena(dentro, animacion=FadeIn(dentro, lag_ratio=0.14,
                                          run_time=1.3))
        self.wait(4.6)

        # --- el latido que lo mueve todo ------------------------------
        reloj = chip.pulsos(n=9, duty=0.5, ancho=5.3, alto=2.8,
                            color=AMBAR)
        # Anclado ABAJO: un dibujo ancho y bajo centrado en la franja se
        # queda a dos unidades de su cifra y la composicion se parte en
        # dos. Pegado al suelo de la franja, dibujo y dato se leen juntos.
        L.escena(reloj, animacion=Create(reloj, run_time=1.6),
                 anclaje="abajo")
        self.wait(5.2)

        # --- y todo eso cabe aqui -------------------------------------
        cierre = chip.encapsulado(lado=4.6, pines_por_lado=11)
        L.escena(cierre, t=1.0)
        self.wait(5.0)
