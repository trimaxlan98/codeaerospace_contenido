# 15 · CICLOIDE — el camino mas rapido.
#
# Johann Bernoulli lo planteo como un reto en 1696: entre dos puntos, ¿por
# que curva baja antes una cuenta que resbala sin rozamiento? La recta no.
# Galileo habia propuesto el arco de circunferencia, y tampoco. Es la
# cicloide, la curva que traza un punto del borde de una rueda que gira.
#
# El verbo visual es una carrera, y toda la honradez de la pieza esta en
# que las tres cuentas caen a la velocidad que manda la GRAVEDAD y no la
# que manda el `run_time`. `esp.ritmo_fisico` convierte el tiempo de video
# en fraccion de camino recorrida segun los tiempos reales de caida, y las
# tres comparten el mismo total: normalizar cada una con el suyo las haria
# llegar a la vez, que es justo lo contrario de lo que hay que enseñar.
#
# EL ARCO ES EL DE GALILEO, el que arranca vertical. Por los mismos dos
# puntos pasan infinitas circunferencias: la tangente a la horizontal sale
# del reposo sin pendiente y tarda 4.11 s —cinco veces la cicloide—, y
# habria convertido la comparacion en un espantapajaros. El de Galileo
# pierde por un 2.2 %, y que pierda por poco es lo que hace buena la
# carrera.
class Clip(Pieza):
    NOMBRE = "CICLOIDE"
    TESIS = "el camino mas rapido"

    # PARAMETROS elegidos: el desnivel de la carrera y lo que dura en
    # video. La camara lenta va DECLARADA en pantalla.
    DX, DY = 2.0, 1.0
    LENTO = 3.6
    ANCHO_CAJA = ANCHO - 0.55
    ALTO_CAJA = 4.20

    def pieza(self):
        L = self.L
        # El suelo del cuadro lo fija el ARCO, no la meta: la
        # circunferencia de Galileo tiene radio 1.25 y baja hasta -1.25,
        # mas de lo que baja la meta. Con el cuadro ajustado a la meta, la
        # curva se salia, el grupo media mas que la franja, `encajar` lo
        # encogia todo y el rotulo acababa encima del arco.
        P = esp.marco((-0.08, self.DX + 0.08), (-1.35, 0.12),
                      ancho=self.ANCHO_CAJA, alto=self.ALTO_CAJA)

        pistas, cuentas, ritmos, tiempos = [], [], [], []
        datos = (("recta", esp.recta, APAGADO, "LA RECTA"),
                 ("arco", esp.arco_circular, CIAN, "EL ARCO"),
                 ("cicloide", esp.cicloide, AMBAR, "LA CICLOIDE"))
        for nombre, fabrica, color, texto in datos:
            x, y = fabrica(self.DX, self.DY)
            pista = esp.curva(x, y, P, color=color,
                              grosor=esp.TRAZO if color == AMBAR else 2.0)
            pistas.append(pista)
            cuentas.append(Dot(P(0.0, 0.0), radius=0.085, color=color))
            t, frac = esp.avance_en_tiempo(x, y)
            ritmos.append((t, frac))
            tiempos.append(esp.tiempo_descenso(x, y))
        total = max(tiempos)

        salida = Dot(P(0.0, 0.0), radius=0.05, color=APAGADO)
        meta = Dot(P(self.DX, -self.DY), radius=0.05, color=APAGADO)
        eti_lento = rot(f"A CAMARA LENTA X{medido(self.LENTO / total, 1)}",
                        color=APAGADO)
        eti_lento.next_to(P(self.DX / 2, -1.35), DOWN, buff=0.26)
        dibujo = lz.agrupar(*pistas, salida, meta, *cuentas, eti_lento)

        # --- 1. las tres pistas, mismo principio y mismo final -------
        L.escena(dibujo, t=0.9)
        self.leer(3.2)

        # --- 2. la carrera, a la velocidad de la gravedad ------------
        self.play(*[MoveAlongPath(c, p,
                                  rate_func=esp.ritmo_fisico(t, f, total))
                    for c, p, (t, f) in zip(cuentas, pistas, ritmos)],
                  run_time=self.LENTO)
        self.leer(2.4)

        # --- 3. los tres tiempos -------------------------------------
        for (nombre, _, _, texto), t in zip(datos, tiempos):
            L.dato(medido(t, 4), f"segundos, {nombre}")
            self.leer(2.6)

        # --- 4. y el otro milagro de la misma curva ------------------
        # Tautocrona: se suelten donde se suelten, las tres llegan al
        # fondo a la vez. La cifra es la DISPERSION de esos tres tiempos,
        # que es lo que hace falta para poder decir "a la vez".
        tt = esp.tautocrona()
        L.dato(medido((max(tt) - min(tt)) * 1000.0, 1),
               "milesimas de diferencia")
        self.leer(3.4)
