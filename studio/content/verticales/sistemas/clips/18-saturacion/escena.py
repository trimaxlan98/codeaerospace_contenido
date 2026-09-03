# 18 · SATURACION — aparecen tonos que no entraron.
#
# LA ULTIMA PIEZA DE CONTENIDO, y cierra el arco. Las diecisiete
# anteriores se apoyan en lo mismo sin decirlo: la caja es LINEAL, y por
# eso UNA sola medida —la respuesta al impulso— la determina para siempre.
# Esta ensena que pasa cuando deja de serlo, que es exactamente lo que le
# da valor a todo lo anterior: si la caja recorta, no hay respuesta al
# impulso que la describa, porque lo que hace depende de cuanto le metas.
#
# EL VERBO VISUAL, uno solo: entra UN tono puro y salen tonos que NO
# estaban. Ninguno de los nuevos entro por la puerta.
#
# EL ARCO, cinco planos, y el primero no es de adorno: sin ver la caja NO
# hacer nada, lo que viene despues no significa nada.
#
#   1. umbral 1.5: la senal ni se acerca al recorte, y sale lo que
#      entro.                                              0 por ciento
#   2. el umbral se cierra a 0.8 y la onda se aplana contra las dos
#      discontinuas.                                    9.21 por ciento
#   3. EL ESPECTRO de ese mismo instante. La cifra no cambia —es la misma
#      medida sobre la misma senal—, cambia el dibujo: ahora se ve DE
#      DONDE sale ese tanto por ciento.
#   4. el umbral se cierra mas.                        19.43 por ciento
#   5. y mas.                                          24.56 por ciento
#
# POR QUE EL ESPECTRO NO SON DOS PANELES, que es la gramatica del resto
# del curso: porque a esta escala miente por omision. Los armonicos que
# fabrica el recorte valen el 13 % y el 3 % del tono que entro —eso es la
# fisica, no una eleccion—, y en un panel de 1.66 de alto el tercero mide
# 27 pixeles y el quinto no llega a 8. La solucion NO puede ser
# normalizar cada panel por su cuenta (que es lo que hace `tf.barras`,
# dividir por su propio maximo): entonces la raya nueva sale tan alta
# como la original y la pieza dice algo falso, que el tono que no entro
# pesa tanto como el que si. Asi que van los dos espectros en UN SOLO eje,
# que es la unica manera de que no haya dos escalas ni por descuido: en
# cada armonico, la raya CIAN de lo que entro y al lado la AMBAR de lo que
# salio. Con un eje entero para el, el tercer armonico mide 72 pixeles y
# el quinto 18, y lo que se lee de un vistazo es que en el 3 y en el 5 hay
# raya ambar y NO hay raya cian: nadie los metio.
#
# LO QUE PREMIA A QUIEN MIRE DOS VECES: los armonicos PARES se quedan
# pegados al suelo. Recortar un tono por arriba y por abajo por igual deja
# la senal simetrica, y una senal simetrica solo puede tener armonicos
# impares. No se cuenta con palabras —seria una frase en pantalla—: se
# dibujan las cinco posiciones siempre, y el 2 y el 4 no se levantan nunca.
#
# TRES DECISIONES MAS QUE VALE LA PENA DEJAR ESCRITAS:
#
#   - **Se MIDE sobre 600 muestras y se DIBUJA sobre 60.** Con f=0.05 la
#     ventana de medida son 30 periodos enteros, que es lo que hace exacta
#     la amplitud de cada armonico; 30 periodos dibujados serian una
#     mancha maciza. Se dibujan los tres primeros periodos de la MISMA
#     senal: es una ventana, no otra senal.
#   - **El cero se CALCULA** (`sis.cero(alto=..., rango_y=...)`). El panel
#     del tiempo va de -1.62 a 1.62 y un tono baja de cero: con
#     `y=-alto/2` la raya se habria ido al suelo del cuadro y el dibujo
#     diria que la senal nunca es negativa.
#   - **Ningun estado se apaga con opacidad.** Cada umbral tiene su cuadro
#     ENTERO construido y encajado (`lz.encajar`), y lo que se anima es un
#     `Transform` hacia el hijo del cuadro siguiente, que esta vivo y
#     opaco porque nunca se apago (un `Transform` copia tambien la
#     opacidad del objetivo, y ese es el modo tipico de acabar con el
#     dibujo invisible). Todos los cuadros llevan el mismo marco
#     invisible, asi que `encajar` los deja en el mismo sitio exacto y
#     nada salta al morfear.
class Clip(Pieza):
    NOMBRE = "SATURACION"
    TESIS = "aparecen tonos que no entraron"

    # --- parametros ELEGIDOS (no son medidas) --------------------------
    F0 = 0.05                # el tono que entra: una vuelta cada 20
    N = 600                  # ventana de MEDIDA: 30 periodos enteros
    NV = 60                  # ventana DIBUJADA: 3 periodos, que se leen
    CUANTOS = 5              # rayas del espectro: del 1 al 5, pares dentro
    UMBRALES = (1.5, 0.8, 0.6, 0.45)

    # --- geometria ------------------------------------------------------
    ANCHO_CAJA = ANCHO - 0.5
    MARCO = (-3.00, 2.35)    # la caja fija de TODOS los cuadros
    Y_ETI = -2.88            # el borde INFERIOR del rotulo de abajo

    # el cuadro del tiempo: dos paneles y la caja en medio
    ALTO_P = 1.66
    ALTO_GLIFO = 0.78
    ANCHO_GLIFO = 3.6
    RANGO_T = (-1.62, 1.62)  # cabe el umbral de 1.5 sin salirse
    Y_E = ALTO_GLIFO / 2 + 0.30 + ALTO_P / 2      # centro del panel de
    Y_S = -Y_E                                    # entrada y del de salida

    # el cuadro del espectro: UN eje para los dos, y por eso puede ser alto
    ALTO_ESP = 4.45
    ANCHO_ESP = ANCHO - 0.8
    RANGO_F = (0.0, 1.10)    # el rango COMPARTIDO por los dos espectros
    Y_ESP = -0.175           # centro del panel (el suelo en -2.40)
    SEPARA = 0.14            # cuanto se aparta cada raya de su armonico
    GRUESO = 9.0             # el trazo de una raya del espectro

    # --- piezas comunes -------------------------------------------------
    def _marco(self):
        """El rectangulo invisible que fija la caja del cuadro.

        Sin trazo ni relleno: entra en el `bounding box` que usa `encajar`
        —y por eso los cinco cuadros se apoyan exactamente igual, sin
        saltar en los cortes ni en los morfeos— y NO cuenta en el guardian
        del 45 %, que mide lo que se pinta."""
        r = Rectangle(width=self.ANCHO_CAJA,
                      height=self.MARCO[1] - self.MARCO[0],
                      stroke_opacity=0.0, fill_opacity=0.0)
        r.move_to([0, (self.MARCO[0] + self.MARCO[1]) / 2, 0])
        return r

    def _eti(self, texto):
        """El rotulo de abajo, apoyado por su BORDE INFERIOR: asi el cuadro
        mide lo mismo diga lo que diga."""
        e = rot(texto)
        e.move_to([0, 0, 0])
        e.align_to(np.array([0.0, self.Y_ETI, 0.0]), DOWN)
        return e

    # --- cuadro del tiempo ----------------------------------------------
    def _onda(self, valores, y, color, grosor):
        curva, punto = sis.traza(np.arange(self.NV), valores[:self.NV],
                                 ancho=self.ANCHO_CAJA, alto=self.ALTO_P,
                                 color=color, grosor=grosor,
                                 rango_x=(0, self.NV - 1),
                                 rango_y=self.RANGO_T, escalones=True)
        curva.shift(UP * y)
        return curva, punto

    def _cuadro_onda(self, x, umbral):
        """Un umbral entero: entrada, caja, salida y las dos discontinuas.

        En el panel de abajo hay DOS curvas: en APAGADO y fina, el tono sin
        tocar —la referencia, lo que habria salido de una caja lineal— y
        encima, en ambar, lo que sale de verdad. Con umbral 1.5 la ambar
        tapa entera a la gris; en cuanto el umbral baja, las puntas grises
        asoman por encima del recorte y se ve exactamente lo que la caja se
        ha comido. Gris OPACO y no ambar traslucido: el ambar al 30 % sobre
        este azul da verde oliva (medido en el curso 31)."""
        y = sis.saturar(x, umbral)
        ejes = VGroup(*[sis.cero(ancho=self.ANCHO_CAJA, alto=self.ALTO_P,
                                 rango_y=self.RANGO_T,
                                 color=LINEA).shift(UP * c)
                        for c in (self.Y_E, self.Y_S)])
        caja = sis.caja(texto="LA CAJA", ancho=self.ANCHO_GLIFO,
                        alto=self.ALTO_GLIFO, color=AMBAR)
        ent, _ = self._onda(x, self.Y_E, CIAN, sis.TRAZO)
        ref, punto = self._onda(x, self.Y_S, APAGADO, sis.TRAZO_FINO)
        sal, _ = self._onda(y, self.Y_S, AMBAR, sis.TRAZO)
        # `punto` es la escala del panel SIN el desplazamiento, asi que la
        # banda se construye con el y se baja despues, igual que la curva.
        corte = sis.banda(0.0, umbral, punto, ancho=self.ANCHO_CAJA,
                          color=AMBAR)
        corte.shift(UP * self.Y_S)
        grupo = VGroup(self._marco(), ejes, caja, self._eti("EN EL TIEMPO"),
                       ent, corte, ref, sal)
        return grupo, sal, corte

    # --- cuadro del espectro ---------------------------------------------
    def _rayas(self, valores, colores, dx):
        g = sis.tallos(valores, ancho=self.ANCHO_ESP, alto=self.ALTO_ESP,
                       grosor=self.GRUESO, punta=0.062,
                       rango_y=self.RANGO_F, colores=colores)
        g.shift(UP * self.Y_ESP + RIGHT * dx)
        return g

    def _cuadro_espectro(self, a_ent, a_sal):
        """Los dos espectros en UN eje y con el MISMO rango.

        En cada armonico, la raya CIAN de lo que entro y a su lado la
        AMBAR de lo que salio. Es el reparto de color de las dieciocho
        piezas del curso aplicado raya a raya, y aqui hace todo el
        trabajo: en el primer armonico hay pareja —el tono que entro salio
        mas bajo—, y en el tercero y el quinto hay raya ambar donde la
        cian se ha quedado en el suelo. Eso, sin una sola palabra, es
        "aparecen tonos que no entraron"."""
        eje = sis.cero(ancho=self.ANCHO_CAJA, alto=self.ALTO_ESP,
                       rango_y=self.RANGO_F, color=LINEA)
        eje.shift(UP * self.Y_ESP)
        ent = self._rayas(a_ent, [CIAN] * self.CUANTOS, -self.SEPARA)
        sal = self._rayas(a_sal, [AMBAR] * self.CUANTOS, self.SEPARA)
        grupo = VGroup(self._marco(), eje, self._eti("EL ESPECTRO"),
                       ent, sal)
        return grupo, sal

    # --- el relevo de un morfeo ------------------------------------------
    def _morfeo(self, animaciones, valor, cuerpo, t=1.3, entra=0.5):
        """Morfea el dibujo y cambia la cifra en el MISMO movimiento.

        `L.relevo` hace justo esto cuando el dibujo se releva entero, pero
        aqui el dibujo no se releva: se MORFEA —los mismos tallos
        cambiando de altura— y eso no cabe en `relevo`. Hacerlo a mano en
        dos pasos (`play(Transform...)` y despues `L.dato(...)`) deja tres
        segundos con el espectro nuevo y el numero viejo debajo, que es
        exactamente la mentira que `relevo` existe para evitar: la cifra
        estaria hablando de un dibujo que ya no esta. Lo destapo el
        fotograma 06 de la primera vuelta. Asi que la cifra vieja se apaga
        DENTRO del mismo `play` que el morfeo, y la nueva entra detras,
        que es la misma secuencia (salidas, y luego entradas) que hace
        `relevo`."""
        # Ya no hace falta tocar `L.ocupantes`: el lienzo tiene `morfeo`,
        # que es `relevo` para un dibujo que se transforma en vez de
        # relevarse. Lo pidio esta pieza.
        self.L.morfeo(None, animaciones=animaciones,
                      dato=lz.dato(valor, "por ciento de distorsion",
                                   medido=True, font_size=cuerpo),
                      t=t, rate_func=smooth)

    # --- la pieza ---------------------------------------------------------
    def pieza(self):
        L = self.L

        # La materia. El tono sale de `dos_tonos` con la segunda amplitud a
        # cero, que es como se pide un tono solo sin escribir un coseno a
        # mano.
        x = sis.dos_tonos(self.F0, self.F0, N=self.N, a1=1.0, a2=0.0)
        thd = [sis.distorsion_armonica(sis.saturar(x, u), self.F0)
               for u in self.UMBRALES]
        # `distorsion_armonica` YA devuelve tanto por ciento.
        cifras = [medido(v, 2) for v in thd]
        # Cuerpo comun para las cuatro: un "0" a cuerpo entero al lado de
        # un "24.56" a la mitad las haria parecer de distinto rango.
        cuerpo = lz.cuerpo_cifra(cifras)

        ondas = [self._cuadro_onda(x, u) for u in self.UMBRALES[:2]]

        # --- 1. la caja no llega a recortar: sale lo que entro -----------
        L.escena(ondas[0][0], t=1.0)
        self.leer(2.8)
        L.dato(cifras[0], "por ciento de distorsion", medido=True, t=0.6,
               font_size=cuerpo)
        self.leer(2.8)

        # --- 2. el umbral se cierra y la onda se aplana ------------------
        # El cuadro siguiente se encaja aparte y se morfea hacia sus hijos:
        # estan vivos y opacos porque ese cuadro no se ha apagado nunca.
        lz.encajar(ondas[1][0])
        self._morfeo([Transform(ondas[0][1], ondas[1][1]),
                      Transform(ondas[0][2], ondas[1][2])],
                     cifras[1], cuerpo)
        self.leer(3.2)

        # --- 3. el mismo instante, visto por frecuencia ------------------
        # La cifra NO cambia y por eso el relevo no la toca: es la misma
        # medida sobre la misma senal. Lo que cambia es que ahora se ve DE
        # DONDE sale.
        a_ent = sis.armonicos(x, self.F0, self.CUANTOS)
        espectros = [self._cuadro_espectro(
            a_ent, sis.armonicos(sis.saturar(x, u), self.F0, self.CUANTOS))
            for u in self.UMBRALES[1:]]

        L.relevo(escena=espectros[0][0], t=0.9)
        self.leer(3.4)

        # --- 4 y 5. se cierra mas, y mas --------------------------------
        # La raya del tono que entro se hunde mientras las que nadie metio
        # se levantan. Eso es el tanto por ciento subiendo, dibujado.
        for i in (1, 2):
            lz.encajar(espectros[i][0])
            self._morfeo([Transform(espectros[0][1], espectros[i][1])],
                         cifras[i + 1], cuerpo)
            self.leer(3.2)

        self.leer(2.6)
