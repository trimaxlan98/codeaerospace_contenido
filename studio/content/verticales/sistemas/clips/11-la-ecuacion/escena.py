# 11 · LA ECUACION — el sistema como receta.
#
# La caja deja de ser una caja negra: se abre y dentro hay una receta.
# `sis.filtrar(b, a, x)` hace `y[n] = b0*x[n] + a1*y[n-1] + a2*y[n-2]` —
# cada muestra de salida se construye con las DOS anteriores de la propia
# salida. El verbo visual es exactamente eso, sin una formula en pantalla:
# se dibuja una ventana chica y fija de `sis.h_de_ecuacion(b, a, N)`, y se
# resaltan en AMBAR tres tallos seguidos (la muestra nueva y sus dos
# padres) mientras el resto queda APAGADO; el resalte avanza muestra a
# muestra por Transform, repitiendose varias veces, y eso ES la recursion.
#
# `b` y `a` son PARAMETROS elegidos (un segundo orden con polos complejos,
# r=0.75, para que la respuesta oscile un poco al morir: con un solo polo
# real la muestra "de antes" y la "de antes de esa" apenas se distinguen
# en el dibujo). Comprobado con numpy antes de fijar nada: con N=20 la
# respuesta ya vale menos del 1% de su pico (duracion=17 < 20), asi que la
# ventana entera que se dibuja en el remate SI contiene la caida completa
# — la cifra habla del sistema, no del cuadro (trampa de la pieza 10).
#
# LA MISMA VENTANA CHICA SE REUTILIZA PARA LAS SEIS FASES DEL RESALTE:
# siete estados con el MISMO array de datos (`tramo`, tallos de 9
# muestras) y solo el color por muestra distinto, todos construidos ANTES
# de `L.escena` y metidos en el mismo grupo (a opacidad 0 salvo el
# primero), tal y como lo resolvio la pieza 07. Asi el `Transform` entre
# fases mueve SOLO el color: source y target ya comparten la escala y la
# posicion que decidio `encajar`, y no hace falta declarar ningun salto de
# escala porque no hay ninguno — es el mismo dibujo, resaltado distinto.
class Clip(Pieza):
    NOMBRE = "LA ECUACION"
    TESIS = "el sistema como receta"

    # La ecuacion en diferencias: PARAMETROS elegidos (huella gris).
    R, THETA = 0.75, 0.6
    B = [1.0]
    A = [1.0, -2 * R * np.cos(THETA), R ** 2]
    N_VENTANA = 20   # >= duracion medida: la caida entera cabe dentro
    M = 9            # cuantas muestras entran en la ventana chica del truco

    ANCHO_CAJA = ANCHO - 0.5

    def _resalte(self, tramo, ancho, alto, rango, i_nuevo):
        """La ventana chica con tres tallos en AMBAR: la muestra `i_nuevo`
        y sus dos padres. El resto, APAGADO."""
        colores = [APAGADO] * tramo.size
        for j in (i_nuevo - 2, i_nuevo - 1, i_nuevo):
            if 0 <= j < tramo.size:
                colores[j] = AMBAR
        return sis.tallos(tramo, ancho=ancho, alto=alto, colores=colores,
                          grosor=2.8, punta=0.065, rango_y=rango)

    def pieza(self):
        L = self.L

        # `h` es la receta ya resuelta por la libreria (numericamente, no
        # a mano): son los mismos numeros que dibuja el remate.
        h = sis.h_de_ecuacion(self.B, self.A, N=self.N_VENTANA)
        tramo = h[:self.M]
        rango_chico = (float(tramo.min()) - 0.10, float(tramo.max()) + 0.10)
        ancho_chico = self.ANCHO_CAJA
        alto_chico = 4.1

        # --- 1..6. la ventana chica: nace la muestra, senala a sus dos --
        #           padres, y el resalte avanza. Siete fases, seis saltos.
        fases = [self._resalte(tramo, ancho_chico, alto_chico, rango_chico, i)
                 for i in range(2, 2 + self.M - 2)]
        for i, f in enumerate(fases):
            f.set_opacity(1.0 if i == 0 else 0.0)

        # El eje va donde de verdad esta el cero, no en el suelo del
        # cuadro: esta respuesta baja de cero (min -0.27) y una raya en el
        # suelo se lee como el eje sin serlo, diciendo que las muestras
        # negativas son positivas. El molde dibuja sobre rangos que
        # empiezan en 0, y de ahi se copio el `y=-alto/2`.
        suelo_chico = sis.cero(ancho=ancho_chico, alto=alto_chico,
                               rango_y=rango_chico, color=LINEA)
        titulo = rot("LA RECETA")
        titulo.next_to(fases[0], DOWN, buff=0.24)

        # Cuantos NUMEROS hacen falta para fabricar la respuesta entera: el
        # coeficiente de la entrada y los dos de la realimentacion. Se lee
        # de los propios arrays (no se escribe a mano), pero sigue siendo
        # un PARAMETRO elegido (gris) — B y A los puso quien escribio la
        # pieza, sistemas.py no los calcula en este render. Se queda en el
        # carril los seis saltos del resalte: sin ella el carril quedaba
        # vacio media pieza.
        numeros = len(self.B) + len(self.A) - 1
        L.relevo(escena=VGroup(suelo_chico, titulo, *fases),
                dato=(medido(numeros, 0), "numeros en la receta", False),
                t=0.9)
        self.leer(2.2)

        actual = fases[0]
        for siguiente in fases[1:]:
            objetivo = siguiente.copy().set_opacity(1.0)
            self.play(Transform(actual, objetivo), run_time=0.9,
                      rate_func=smooth)
            self.leer(2.0)

        # --- 7. el remate: la ventana entera, y la cifra ----------------
        #        (misma h, mismos numeros: la receta ya no se ve, pero es
        #        la que dejo esta forma)
        rango_grande = (float(h.min()) - 0.10, float(h.max()) + 0.10)
        alto_grande = 4.5
        tallo_final = sis.tallos(h, ancho=self.ANCHO_CAJA, alto=alto_grande,
                                 color=AMBAR, grosor=2.9, punta=0.055,
                                 rango_y=rango_grande)
        suelo_final = sis.cero(ancho=self.ANCHO_CAJA, alto=alto_grande,
                               rango_y=rango_grande, color=LINEA)
        etiqueta_final = rot("MUESTRA A MUESTRA", color=AMBAR)
        etiqueta_final.next_to(tallo_final, DOWN, buff=0.24)

        L.relevo(escena=VGroup(suelo_final, etiqueta_final, tallo_final),
                dato=(medido(sis.duracion(h), 0), "muestras de la receta",
                      True), t=1.2, salida=0.45)
        self.leer(3.4)
        self.leer(2.8)
