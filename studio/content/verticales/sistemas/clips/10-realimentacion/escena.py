# 10 · REALIMENTACION — la salida vuelve a entrar.
#
# La unica pieza del curso con un dibujo que se muerde la cola, y esa
# forma ES la pieza: `sis.lazo` pinta la caja, la flecha que entra (cian),
# la que sale (ambar) y el camino que devuelve esa salida al nodo de la
# entrada. Debajo, la respuesta al impulso de ese mismo lazo.
#
# EL VERBO: se CIERRA el camino de vuelta y, en el mismo movimiento, la
# respuesta se estira. Con el lazo cortado la caja no tiene memoria —
# entra un golpe y sale el mismo golpe, una sola muestra—; en cuanto la
# salida vuelve a entrar aparece un eco, y cuanto mas devuelve la vuelta
# mas dura. El rotulo del bloque de la vuelta dice cuanto devuelve
# (`sis.ganancia_lazo`, el polo del lazo) y la cifra dice que le pasa a la
# respuesta: causa arriba, efecto abajo.
#
# LA CIFRA CAMBIA DE UNIDAD EN EL ULTIMO PLANO, Y ES EL FONDO DE LA PIEZA.
# En los tres primeros planos la respuesta MUERE dentro de la ventana, asi
# que "cuantas muestras dura" (`sis.duracion`) es una propiedad del
# sistema: 1, 10 y 44 seguirian siendo 1, 10 y 44 con N=200. En el cuarto
# no muere, y ahi `duracion` devuelve 60 — que no es cuanto dura la
# respuesta, es cuanto mide `N`. Rotular eso seria rotular la malla: con
# N=200 la cifra diria 200 sin que el sistema haya cambiado en nada, que
# es exactamente lo que prohibe la regla de "lo que depende de la malla no
# se rotula". Asi que el remate mide lo que NO se mueve al cambiar la
# ventana — cuanto multiplica cada muestra a la anterior, leido de la
# respuesta dibujada (`h[-1] / h[-2]`)— y ademas es la frase de la pieza:
# pasar de uno significa que cada muestra es mayor que la anterior, para
# siempre. Que ese 1.08 coincida con el "X 1.08" del bloque de la vuelta
# no es repetirse: es el cierre del circulo, lo que metes en la vuelta es
# lo que acaba multiplicando a cada muestra.
#
# (Y `duracion` y no `cola`: aqui dan lo mismo, porque la respuesta
# arranca en la muestra 0 y no tiene ceros delante, pero la que
# corresponde al rotulo "muestras que duran" es `duracion`. Ver la
# cabecera del molde: confundirlas puso un 21 falso en la pieza 01.)
#
# LO QUE COSTO PENSAR (y lo avisaba el encargo): `sis.tallos` NO RECORTA.
# Las tres primeras respuestas valen como mucho 1.00 y la cuarta llega a
# 93.76. En un solo cuadro, o las tres primeras quedan pegadas al eje o la
# cuarta se va kilometros fuera del lienzo y el guardian aborta. Se parte
# igual que en el molde: un cuadro para las tres que caben en 1.00 y otro,
# con el salto de escala DECLARADO en el rotulo, para la que se va. Y el
# factor del rotulo se LEE de las respuestas (tope_b / tope_a), no se
# escribe a mano, para que diga el de verdad.
#
# EL PARAMETRO NO SIGNIFICA LO QUE PARECE: en `sis.lazo_cerrado(k, N,
# polo)` el unico camino es el de la vuelta, asi que k=0 no es "ganancia
# cero" sino LAZO CORTADO — y entonces la caja solo copia la entrada. Por
# eso el primer plano dibuja el lazo con la vuelta apagada: no es un lazo
# flojo, es un lazo que no esta.
#
# GEOMETRIA MEDIDA (para que no haya que descubrirlo otra vez): con estos
# numeros el grupo entero mide 5.34 de alto contra los 5.389 de la franja,
# asi que `encajar` NO lo escala. Importa: los rotulos de 22 puntos miden
# 0.214 y el minimo legible es 0.155, o sea que solo se pueden encoger un
# 27 % antes de que el render aborte. Si algo crece aqui, hay que bajar
# `ALTO_T` o `ALTO_LAZO`, no confiar en el escalado.
class Clip(Pieza):
    NOMBRE = "REALIMENTACION"
    TESIS = "la salida vuelve a entrar"

    # PARAMETROS elegidos: la ventana de la respuesta, el polo de la caja
    # directa y lo apretada que va la vuelta en cada plano. Lo que se MIDE
    # es que le pasa a la respuesta que sale de ahi.
    N = 60
    POLO = 0.6
    KS = (0.0, 1.0, 1.5, 1.8)

    ANCHO_LAZO = 3.2
    ALTO_LAZO = 1.7
    ANCHO_CAJA = 1.6
    ALTO_CAJA = 0.9
    ANCHO_VUELTA = 1.45
    ALTO_VUELTA = 0.55
    ANCHO_T = 5.2
    ALTO_T = 2.30

    def _h(self, k):
        return sis.lazo_cerrado(k, N=self.N, polo=self.POLO)

    def _caja_vuelta(self, k):
        """El bloque que va EN el camino de vuelta, rotulado con lo que
        devuelve. Ese numero es el polo del lazo: por debajo de 1 el eco
        se apaga, por encima no."""
        return sis.caja(f"x {medido(sis.ganancia_lazo(k, self.POLO), 2)}",
                        ancho=self.ANCHO_VUELTA, alto=self.ALTO_VUELTA,
                        color=AMBAR)

    def _lazo(self, caja_vuelta):
        """El diagrama, con el reparto de color del curso.

        El color va por TRAMO (`color_entrada` / `color_salida`), que es lo
        que hace legible de un vistazo que lo que regresa al nodo es
        exactamente lo que salio: `color_salida` pinta la flecha de salida
        y tambien la linea de vuelta.

        Del grupo solo se rescata la VUELTA, y no por indice sino por tipo:
        es el unico hijo que es un `VMobject` pelado (los demas son VGroup,
        Circle o Arrow). Hace falta el mobject porque la pieza la DIBUJA
        con `Create`. Si algun dia dejara de estar, el desempaquetado
        revienta en el acto en vez de animar el tramo equivocado callando."""
        caja_h = sis.caja("h", ancho=self.ANCHO_CAJA, alto=self.ALTO_CAJA,
                          color=AMBAR)
        g = sis.lazo(caja_h, caja_vuelta, ancho=self.ANCHO_LAZO,
                     alto=self.ALTO_LAZO, color_entrada=CIAN,
                     color_salida=AMBAR)
        vuelta = g.vuelta          # el tramo de vuelta, por nombre
        vuelta.set_stroke(width=sis.TRAZO)
        return g, vuelta

    def _tallos(self, h, tope):
        return sis.tallos(h, ancho=self.ANCHO_T, alto=self.ALTO_T,
                          color=AMBAR, grosor=sis.TRAZO_FINO, punta=0.028,
                          rango_y=(0.0, tope))

    def pieza(self):
        L = self.L
        h_ab, h_ce, h_ap, h_pa = [self._h(k) for k in self.KS]

        # El tope de cada cuadro se LEE de las respuestas. Las tres
        # primeras caben en 1.00; la cuarta necesita su propio cuadro y el
        # rotulo dice cuantas veces mas alto es.
        tope_a = max(float(h.max()) for h in (h_ab, h_ce, h_ap))
        tope_b = float(h_pa.max())

        # --- 1. el lazo dibujado, con la vuelta APAGADA ----------------
        # Todos los estados se construyen ANTES y entran en el mismo grupo:
        # asi comparten la escala y la posicion que les da `encajar`, y se
        # encienden con opacidad (la trampa 3 del contrato).
        caja_k1 = self._caja_vuelta(self.KS[1])
        caja_k2 = self._caja_vuelta(self.KS[2])
        lazo_a, vuelta = self._lazo(caja_k1)
        caja_k2.move_to(caja_k1)          # gemela apilada: solo cambia la cifra
        lazo_a.add(caja_k2)
        estados = [self._tallos(h, tope_a) for h in (h_ab, h_ce, h_ap)]
        vuelta.set_stroke(opacity=0.0)    # trampa 1: la polilinea, por el trazo
        for m in (caja_k1, caja_k2, estados[1], estados[2]):
            m.set_opacity(0.0)
        grupo_a = lz.dos_dominios(lazo_a, VGroup(*estados), None, "ESCALA 1X")

        L.escena(grupo_a, t=0.9)
        self.leer(2.8)
        L.dato(medido(sis.duracion(h_ab), 0), "muestra que dura", medido=True)
        self.leer(3.2)

        # --- 2. se cierra el lazo: aparece la memoria ------------------
        # La vuelta se DIBUJA (desde la salida hacia el nodo) a la vez que
        # la respuesta se estira: causa y efecto en el mismo movimiento.
        # `introducer=False` porque `Create` re-anade su mobject a la
        # escena al terminar, y este vive dentro del grupo del carril.
        vuelta.set_stroke(opacity=1.0)
        estados[1].set_opacity(1.0)       # el destino manda tambien el estilo
        self.play(Create(vuelta, introducer=False),
                  caja_k1.animate.set_opacity(1.0),
                  Transform(estados[0], estados[1]), run_time=1.6)
        estados[1].set_opacity(0.0)
        # El relevo de la cifra va corto a proposito: mientras dura, el
        # dibujo nuevo esta debajo del numero viejo.
        L.dato(medido(sis.duracion(h_ce), 0), "muestras que duran",
               medido=True, t=0.45, salida=0.3)
        self.leer(3.4)

        # --- 3. se aprieta la vuelta: el eco dura mucho mas ------------
        estados[2].set_opacity(1.0)
        self.play(Transform(estados[0], estados[2]),
                  caja_k1.animate.set_opacity(0.0),
                  caja_k2.animate.set_opacity(1.0), run_time=1.3)
        estados[2].set_opacity(0.0)
        L.dato(medido(sis.duracion(h_ap), 0), "muestras que duran",
               medido=True, t=0.45, salida=0.3)
        self.leer(3.4)

        # --- 4. se pasa de uno: la respuesta se va ---------------------
        # Cuadro nuevo porque el tope pasa de 1.00 a 93.76, y el salto se
        # DECLARA en el rotulo. Aqui la respuesta ya no arranca arriba y
        # cae: arranca pegada al eje y se dispara. Ese vuelco es la pieza.
        #
        # Y la cifra deja de contar muestras: cuenta cuanto multiplica cada
        # muestra a la anterior, medido sobre la respuesta dibujada. Ese
        # numero no depende de la ventana — con N=200 seguiria siendo el
        # mismo — y es el que cruza el 1.
        crecimiento = float(h_pa[-1] / h_pa[-2])
        lazo_b, _ = self._lazo(self._caja_vuelta(self.KS[3]))
        grupo_b = lz.dos_dominios(lazo_b, self._tallos(h_pa, tope_b), None,
                                  f"ESCALA {medido(tope_b / tope_a, 0)}X")
        L.relevo(escena=grupo_b,
                 dato=(medido(crecimiento, 2), "veces por muestra"),
                 t=0.9)
        self.leer(3.2)
        self.leer(2.8)
