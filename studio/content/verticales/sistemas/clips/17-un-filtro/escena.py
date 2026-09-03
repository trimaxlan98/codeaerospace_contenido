# 17 · UN FILTRO — unas pasan y otras no.
#
# Es la pieza que junta el curso: una caja con un proposito. El verbo
# visual es literal: entra una senal con DOS tonos mezclados y sale con
# UNO. El otro no se pierde por casualidad -se mide cuanto se lleva la
# caja, en decibelios, y es la misma cuenta para el tono que pasa (casi 0)
# y para el que no (casi -65).
#
# EL ARCO, en seis planos:
#   1. Los dos tonos por separado (CIAN), para que se reconozcan.
#   2. La caja: el tono lento entra y sale casi igual; el agudo entra y
#      sale casi plano. Ahi nace la cifra, dos veces, sobre la MISMA caja.
#   3. Sumados: la entrada de verdad, emborronada por el agudo encima del
#      lento -el plano fuerte que pide el encargo.
#   4. Lo que sale de la caja: solo queda el lento.
#   5. Remate: la salida (AMBAR, gruesa) contra el tono lento solo (CIAN,
#      a trozos) -coinciden.
#
# DECISIONES QUE VALE LA PENA DEJAR ESCRITAS:
#
#   - **La ventana que se dibuja es la misma que mide la sonda**: empieza
#     en la muestra 80 (`DESDE`), ya lejos del transitorio de la
#     convolucion. Dibujar un tramo mas temprano ensenaria un filtro que
#     todavia se esta llenando y la cifra de al lado mentiria. El rotulo
#     de la salida lo declara ("YA ASENTADA").
#   - **El tope de cada cuadro se MIDE, no se elige**: `tope_chico` es el
#     mayor valor absoluto entre los dos tonos solos y sus dos salidas;
#     `tope_grande`, el de la entrada sumada. La razon entre los dos sale
#     ~2 (el par de razon 2 del contrato), y el rotulo de la entrada lo
#     declara ("ESCALA 2X") en vez de fingir que caben en el mismo cuadro.
#   - **El remate va a trozos**: la salida es AMBAR gruesa (abajo) y el
#     tono lento solo es CIAN fino a trozos (encima, `DashedVMobject`).
#     Dos trazos opacos y solidos de colores distintos, uno fino sobre
#     otro grueso, se funden en un gusano ilegible aunque no haya ninguna
#     transparencia -esta medido en el contrato. A trozos se ven las DOS
#     curvas y "coinciden" se lee de verdad.
#   - **La cifra no se toca entre la entrada, la salida y el remate**: es
#     la atenuacion del tono agudo, y sigue siendo cierta mientras se
#     enseña por que -no hace falta recalcularla porque el dibujo cambie.
class Clip(Pieza):
    NOMBRE = "UN FILTRO"
    TESIS = "unas pasan y otras no"

    # --- parametros elegidos: frecuencias, filtro, ventana -----------------
    FC = 0.10
    M = 61
    F1, F2 = 0.05, 0.25
    N = 600
    DESDE = 80               # el tramo ya asentado (ver cabecera)
    VENTANA = 80

    ANCHO_CAJA = ANCHO - 0.5
    ALTO_SIMPLE = 3.8         # cuadros de una sola traza

    ALTO_P = 1.5              # sub-panel de la caja entra/sale
    ALTO_GLIFO = 0.78
    Y_E = ALTO_GLIFO / 2 + 0.30 + ALTO_P / 2

    def _ventana(self, valores, corrimiento=0):
        """El tramo ya asentado. `corrimiento` adelanta el origen: sirve
        para leer una REFERENCIA en el instante en que la caja la escupe,
        no en el instante en que entro (ver `_remate`)."""
        ini = self.DESDE - corrimiento
        return valores[ini:ini + self.VENTANA]

    def _simple(self, valores, tope, color, etiqueta, color_eti=None):
        """Un cuadro con una sola traza y el cero DE VERDAD.

        El rango es simetrico (-tope, tope), asi que el cero cae en el
        CENTRO del cuadro, no en su suelo: `sis.cero(rango_y=...)` es la
        forma segura porque lo calcula ella (y aborta si no cuadra) en vez
        de asumir "abajo del todo", que aqui seria un cuadro entero de
        error. El rotulo cuelga de la CURVA, no del eje, porque el eje ya
        no vive en el borde de abajo."""
        idx = np.arange(self.VENTANA)
        curva, _ = sis.traza(idx, self._ventana(valores),
                             ancho=self.ANCHO_CAJA, alto=self.ALTO_SIMPLE,
                             color=color, grosor=sis.TRAZO,
                             rango_x=(0, self.VENTANA - 1),
                             rango_y=(-tope, tope))
        cero = sis.cero(ancho=self.ANCHO_CAJA, alto=self.ALTO_SIMPLE,
                        rango_y=(-tope, tope), color=LINEA)
        eti = rot(etiqueta, color=color_eti or color)
        eti.next_to(curva, DOWN, buff=0.24)
        return VGroup(cero, curva, eti)

    def _caja_tono(self, entra, sale, tope, etiqueta):
        """Entrada arriba (CIAN), la caja al centro, salida abajo (AMBAR).

        El mismo rango, fijo, para las dos: si la salida se normalizara a
        su propio pico, un tono aplastado se veria tan alto como uno que
        pasa entero, y eso es justo lo que la pieza tiene que ensenar."""
        idx = np.arange(self.VENTANA)
        c_ent, _ = sis.traza(idx, self._ventana(entra),
                             ancho=self.ANCHO_CAJA, alto=self.ALTO_P,
                             color=CIAN, grosor=sis.TRAZO,
                             rango_x=(0, self.VENTANA - 1),
                             rango_y=(-tope, tope))
        c_ent.shift(UP * self.Y_E)
        c_sal, _ = sis.traza(idx, self._ventana(sale),
                             ancho=self.ANCHO_CAJA, alto=self.ALTO_P,
                             color=AMBAR, grosor=sis.TRAZO,
                             rango_x=(0, self.VENTANA - 1),
                             rango_y=(-tope, tope))
        c_sal.shift(DOWN * self.Y_E)
        # La forma segura tambien aqui, aunque el rango simetrico haga que
        # coincida con y=0.0: que coincida hoy no es razon para no dejar
        # que lo calcule sis.cero, por si algun dia el rango deja de serlo.
        ejes = VGroup(*[sis.cero(ancho=self.ANCHO_CAJA, alto=self.ALTO_P,
                                 rango_y=(-tope, tope), color=LINEA
                                 ).shift(UP * yy)
                       for yy in (self.Y_E, -self.Y_E)])
        caja = sis.caja(texto="h", ancho=2.0, alto=self.ALTO_GLIFO,
                        color=AMBAR)
        eti = rot(etiqueta, color=CIAN)
        eti.move_to([0, -self.Y_E - self.ALTO_P / 2 - 0.24 - eti.height / 2,
                    0])
        return VGroup(ejes, caja, c_ent, c_sal, eti)

    def _remate(self, salida, referencia, tope, corrimiento):
        """La salida contra la referencia, ALINEADA por el retardo de
        grupo del filtro.

        Un FIR de fase lineal no solo atenua: tambien RETRASA lo que deja
        pasar, `corrimiento` muestras exactas (la pieza 14 mide ese mismo
        numero). Comparar sin correr esa cuenta las deja casi en
        antifase -el dibujo lo habria delatado si alguien hubiera
        mirado con cuidado el frame, y por eso el rotulo lo declara en
        vez de dejarlo en silencio."""
        idx = np.arange(self.VENTANA)
        c_sal, _ = sis.traza(idx, self._ventana(salida),
                             ancho=self.ANCHO_CAJA, alto=self.ALTO_SIMPLE,
                             color=AMBAR, grosor=sis.TRAZO,
                             rango_x=(0, self.VENTANA - 1),
                             rango_y=(-tope, tope))
        c_ref, _ = sis.traza(idx, self._ventana(referencia,
                                                 corrimiento=corrimiento),
                             ancho=self.ANCHO_CAJA, alto=self.ALTO_SIMPLE,
                             color=CIAN, grosor=sis.TRAZO_FINO,
                             rango_x=(0, self.VENTANA - 1),
                             rango_y=(-tope, tope))
        c_ref_trozos = DashedVMobject(c_ref, num_dashes=40, dashed_ratio=0.55)
        cero = sis.cero(ancho=self.ANCHO_CAJA, alto=self.ALTO_SIMPLE,
                        rango_y=(-tope, tope), color=LINEA)
        eti = rot("COINCIDEN", color=AMBAR)
        eti_corr = rot(f"ALINEADO {medido(corrimiento, 0)} MUESTRAS",
                       color=APAGADO)
        grupo_curvas = VGroup(c_sal, c_ref_trozos)
        eti.next_to(grupo_curvas, DOWN, buff=0.24)
        eti_corr.next_to(eti, DOWN, buff=0.18)
        return VGroup(cero, c_sal, c_ref_trozos, eti, eti_corr)

    def pieza(self):
        L = self.L

        # --- toda la materia, calculada por sis.* ---------------------------
        b = sis.paso_bajo(self.FC, M=self.M)
        x = sis.dos_tonos(self.F1, self.F2, N=self.N)
        y = sis.filtrar(b, [1.0], x)
        tono_bajo = sis.dos_tonos(self.F1, self.F2, N=self.N, a1=1.0, a2=0.0)
        tono_alto = sis.dos_tonos(self.F1, self.F2, N=self.N, a1=0.0, a2=1.0)
        sal_bajo = sis.filtrar(b, [1.0], tono_bajo)
        sal_alto = sis.filtrar(b, [1.0], tono_alto)

        w1, w2 = 2 * np.pi * self.F1, 2 * np.pi * self.F2
        aten_bajo = sis.atenuacion_db(b, w1)
        aten_alto = sis.atenuacion_db(b, w2)

        # El retardo de grupo (la pieza 14 mide este mismo numero): cuanto
        # se atrasa lo que la caja deja pasar. Un FIR de fase lineal lo
        # tiene CONSTANTE en toda la banda de paso, asi que basta leerlo en
        # w1. Sin compensarlo, superponer salida y tono lento los deja casi
        # en antifase -medido en la cabecera de `_remate`.
        wg, dg = sis.retardo_grupo(b, N=4096)
        corrimiento = int(round(float(np.interp(w1, wg, dg))))

        v = self._ventana
        tope_chico = 1.08 * max(float(np.max(np.abs(v(tono_bajo)))),
                                 float(np.max(np.abs(v(tono_alto)))),
                                 float(np.max(np.abs(v(sal_bajo)))),
                                 float(np.max(np.abs(v(sal_alto)))),
                                 float(np.max(np.abs(v(y)))))
        tope_grande = 1.05 * float(np.max(np.abs(v(x))))
        factor = tope_grande / tope_chico

        # --- 1. los dos tonos, por separado ---------------------------------
        g1 = self._simple(tono_bajo, tope_chico, CIAN, "TONO LENTO")
        L.escena(g1, t=0.8)
        self.leer(2.4)

        g2 = self._simple(tono_alto, tope_chico, CIAN, "TONO AGUDO")
        L.relevo(escena=g2, t=0.8)
        self.leer(2.4)

        # --- 2. la caja: el lento pasa, el agudo no --------------------------
        g3 = self._caja_tono(tono_bajo, sal_bajo, tope_chico, "TONO LENTO")
        L.relevo(escena=g3,
                 dato=(medido(aten_bajo, 2), "decibelios, pasa", True),
                 t=0.9)
        self.leer(2.8)

        g4 = self._caja_tono(tono_alto, sal_alto, tope_chico, "TONO AGUDO")
        L.relevo(escena=g4,
                 dato=(medido(aten_alto, 2), "decibelios, bloqueado", True),
                 t=0.9)
        self.leer(3.2)

        # --- 3. sumados: la entrada de verdad, emborronada -------------------
        g5 = self._simple(x, tope_grande, CIAN,
                          f"ENTRADA, ESCALA {medido(factor, 0)}X")
        L.relevo(escena=g5, t=0.9)
        self.leer(3.2)

        # --- 4. sale de la caja: solo queda el lento --------------------------
        g6 = self._simple(y, tope_chico, AMBAR, "SALIDA, YA ASENTADA")
        L.relevo(escena=g6, t=0.9)
        self.leer(3.2)

        # --- 5. remate: coinciden, YA ALINEADAS -------------------------------
        g7 = self._remate(y, tono_bajo, tope_chico, corrimiento)
        L.relevo(escena=g7, t=0.9)
        self.leer(3.2)
