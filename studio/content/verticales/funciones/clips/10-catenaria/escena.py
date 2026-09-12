# 10 · CATENARIA — la cadena no es parabola.
#
# Galileo dijo que una cadena colgada adopta una parabola. Se equivoco, y
# hicieron falta sesenta años y el calculo diferencial para saber que la
# curva es un coseno hiperbolico. Lo interesante de esta pieza es que el
# error de Galileo es PEQUEÑISIMO: con el mismo vano y la misma flecha, las
# dos curvas se separan un 0.71 % del vano. A ojo son la misma.
#
# Y aun asi la cadena es la que cuelga mas bajo de las dos, porque es la de
# minima energia. La naturaleza no escoge la que se parece: escoge la que
# minimiza, y esa resulta no ser una parabola.
#
# COMO SE ENSEÑA UNA DIFERENCIA QUE NO SE VE: no se exagera el dibujo. Se
# dibuja la RESTA de las dos curvas en su propio cuadro, con el factor
# declarado en pantalla. Deformar las curvas para que se separen seria
# enseñar dos cosas que no son las que dice la cifra.
class Clip(Pieza):
    NOMBRE = "CATENARIA"
    TESIS = "la cadena no es parabola"

    # PARAMETROS elegidos: el vano y la flecha del dibujo.
    VANO = 2.0
    FLECHA = 0.62
    AUMENTO = 60.0
    ANCHO_CAJA = ANCHO - 0.55

    def _cuadro(self, alto=3.9):
        return esp.marco((-self.VANO / 2 - 0.10, self.VANO / 2 + 0.10),
                         (-self.FLECHA - 0.14, 0.30),
                         ancho=self.ANCHO_CAJA, alto=alto)

    def _puente(self, con_parabola):
        """El puente entero, construido DESDE CERO cada vez.

        Nada de `.copy()` de un dibujo que ya paso por `encajar`: la copia
        se lleva encima el desplazamiento y la escala de aquel grupo, y el
        `encajar` del grupo nuevo se los aplica otra vez. Cazado en la
        pieza 08, donde el escalon de referencia salia flotando por encima
        de su cuadro."""
        P = self._cuadro()
        xc, yc = esp.catenaria(self.VANO, self.FLECHA, 1601)
        xp, yp = esp.parabola_equivalente(self.VANO, self.FLECHA, 1601)
        torres = VGroup()
        for lado in (-1, 1):
            x = lado * self.VANO / 2
            torres.add(Line(P(x, 0.30), P(x, -self.FLECHA - 0.14),
                            stroke_color=LINEA,
                            stroke_width=esp.TRAZO_FINO))
            torres.add(Dot(P(x, 0.0), radius=0.055, color=APAGADO))
        cadena = esp.curva(xc, yc, P, color=AMBAR, grosor=esp.TRAZO)
        eti_c = rot("CADENA", color=AMBAR)
        eti_c.move_to(P(0.0, 0.17))
        piezas = [torres, cadena, eti_c]
        # La parabola va ENCIMA y A TROZOS. Dos trazos opacos superpuestos
        # se funden en un color que no es ninguno de los dos, y estas dos
        # curvas coinciden en casi todo su recorrido: a trozos se ve el
        # ambar en cada hueco y "coinciden" se lee porque se ven DOS.
        parabola = esp.curva(xp, yp, P, color=CIAN, grosor=2.2,
                             a_trozos=True)
        eti_p = rot("PARABOLA", color=CIAN)
        eti_p.move_to(P(0.0, -0.03))
        if not con_parabola:
            parabola.set_stroke(opacity=0.0)
            eti_p.set_opacity(0.0)
        piezas += [parabola, eti_p]
        return lz.agrupar(*piezas), cadena, parabola, eti_p

    def pieza(self):
        L = self.L

        # --- 1. la cadena, colgada de sus dos torres -----------------
        dibujo, cadena, parabola, eti_p = self._puente(True)
        parabola.set_stroke(opacity=0.0)
        eti_p.set_opacity(0.0)
        cadena.set_stroke(opacity=0.0)
        L.escena(dibujo, t=0.9)
        cadena.set_stroke(opacity=1.0)
        self.play(Create(cadena, introducer=False), run_time=1.8,
                  rate_func=smooth)
        self.leer(3.6)

        # --- 2. la parabola de Galileo, encima -----------------------
        parabola.set_stroke(opacity=1.0)
        self.play(Create(parabola, introducer=False),
                  eti_p.animate.set_opacity(1.0), run_time=1.8,
                  rate_func=smooth)
        self.leer(4.0)

        # --- 3. la resta, aumentada y declarada ----------------------
        # El rango va de -1 a 0, no de 0 a 1: la resta es NEGATIVA en todo
        # el vano porque la cadena cuelga por DEBAJO de la parabola (es la
        # curva de minima energia, y eso es lo que significa). Con el
        # cuadro puesto de cero para arriba, la curva entera caia fuera por
        # abajo y cruzaba su propio rotulo. Llego asi al montaje y lo
        # destapo mirar un fotograma de la pelicula ya entregada.
        Q = esp.marco((-self.VANO / 2 - 0.10, self.VANO / 2 + 0.10),
                      (-1.08, 0.08), ancho=self.ANCHO_CAJA, alto=3.6)
        xc, yc = esp.catenaria(self.VANO, self.FLECHA, 1601)
        xp, yp = esp.parabola_equivalente(self.VANO, self.FLECHA, 1601)
        dif = (yc - yp) / self.VANO * 100.0        # en % del vano
        resta = esp.curva(xc, dif / float(np.max(np.abs(dif))), Q,
                          color=AMBAR, grosor=esp.TRAZO)
        eti_dif = rot(f"LA RESTA, X{medido(self.AUMENTO, 0)}", color=AMBAR)
        eti_dif.next_to(Q(0.0, -1.08), DOWN, buff=0.26)
        panel = lz.agrupar(esp.recuadro(Q), esp.eje_x(Q), resta, eti_dif)

        L.relevo(escena=panel,
                 dato=(medido(esp.separacion_maxima(self.VANO,
                                                    self.FLECHA), 2),
                       "por ciento del vano"), t=0.9)
        self.leer(4.6)

        # --- 4. y lo que eso cuesta en cable -------------------------
        puente, _, _, _ = self._puente(True)
        L.relevo(escena=puente,
                 dato=(medido(esp.exceso_de_cable(self.VANO,
                                                  self.FLECHA), 2),
                       "por ciento mas de cable"), t=0.9)
        self.leer(5.8)
