# 08 · ESTABILIDAD — entrada acotada, salida acotada.
#
# El verbo: EL MISMO golpe (un impulso, CIAN) puede llegar a dos sistemas
# que solo se distinguen en UN numero, `a`. h[n] = a^n: con a=0.85 se
# apaga; con a=1.05 crece sin techo (una y otra empiezan igual de altas —
# el mismo golpe — y se separan solo con el tiempo). El criterio ES una
# suma: `sis.suma_absoluta(h)` finita = estable BIBO (entrada acotada,
# salida acotada); la que no lo es se dispara dentro de la misma ventana
# de 60 muestras.
#
# Decisiones que vienen del contrato, no a ojo:
#   - Las dos respuestas NUNCA comparten rango vertical. `sis.tallos` no
#     recorta (igual que `sis.traza`): meterlas en el mismo cuadro
#     aplastaria la que se apaga (max 1.00) contra el eje, al lado de la
#     que crece (max 17.79). Cada `_panel` vive en SU propio rango
#     (0, max(h)) — la unica diferencia por escrito entre los dos, en los
#     planos donde aparecen SOLOS, es la etiqueta "a = ...", que es el
#     parametro elegido, no una medida.
#   - `cota_salida(h, amplitud=1.0)` NO aparece: con amplitud=1 devuelve
#     exactamente `suma_absoluta(h)` (mismo numero, dos nombres), y
#     ponerla al lado seria fingir una segunda medida donde hay una sola.
#   - El remate pone los dos sistemas a la vez (cada uno en su propio
#     cuadro) para que "el mismo golpe, un solo numero distinto" se lea
#     de un vistazo, sin repetir la cifra: el carril del dato se deja
#     como esta (la ultima suma medida) en vez de vaciarse a mitad de
#     pieza.
#   - LA VUELTA QUE COSTO: al normalizar cada panel a su propio maximo,
#     los dos quedan dibujados a la MISMA altura en pantalla aunque sus
#     escalas verdaderas difieren 17.8 veces — dos cuadros apilados del
#     mismo tamano invitan a comparar alturas, y esa comparacion es
#     falsa. Es la trampa 5 del contrato: una escala que cambia se
#     DECLARA. Por eso el remate rotula cada cuadro con su factor real
#     (calculado contra el maximo de la referencia, nunca escrito a
#     mano): "ESCALA 1X" en el que se apaga (es la referencia) y
#     "ESCALA 18X" en el que crece — el mismo patron que usa el molde
#     en `01-el-impulso` para el salto entre pulsos.
class Clip(Pieza):
    NOMBRE = "ESTABILIDAD"
    TESIS = "entrada acotada, salida acotada"

    # --- parametros elegidos (grises si se rotulan) ----------------------
    N = 60
    A_ESTABLE = 0.85
    A_INESTABLE = 1.05
    ANCHO_CAJA = ANCHO - 0.5
    ALTO_SOLO = 4.3      # cada sistema, solo en pantalla
    ALTO_PAR = 1.85       # cada sistema, en el remate con los dos a la vez
    Y_TOP = 1.65
    Y_BOT = -1.75

    def _sistema(self, a, alto):
        """h[n] = a^n, dibujada en SU propio rango (0, max(h)). Nunca
        comparte eje con la otra: compartirlo aplastaria la que se apaga."""
        h = sis.h_geometrica(a, N=self.N)
        tope = float(h.max())
        curva = sis.tallos(h, ancho=self.ANCHO_CAJA, alto=alto, color=AMBAR,
                           grosor=1.7, punta=0.030, rango_y=(0.0, tope))
        return curva, h

    def _panel(self, a, alto, y_shift=0.0, escala_texto=None):
        """Un cuadro completo: suelo + la respuesta + la etiqueta del
        parametro `a`. Si se pasa `escala_texto` (solo en el remate, donde
        SI hay dos cuadros uno junto al otro), se anade debajo: es la
        escala vertical de ESTE cuadro declarada por escrito, calculada
        contra la referencia, nunca a ojo."""
        curva, h = self._sistema(a, alto)
        suelo = sis.cero(ancho=self.ANCHO_CAJA, y=-alto / 2, color=LINEA)
        eti = rot(f"a = {medido(a, 2)}")
        eti.next_to(suelo, DOWN, buff=0.24)
        piezas = [suelo, eti, curva]
        if escala_texto is not None:
            eti_escala = rot(escala_texto)
            eti_escala.next_to(eti, DOWN, buff=0.14)
            piezas.append(eti_escala)
        grupo = VGroup(*piezas).shift(UP * y_shift)
        return grupo, h

    def pieza(self):
        L = self.L

        # --- 0. el golpe, uno solo, comun a los dos sistemas -------------
        golpe = sis.impulso(N=9, n0=4)
        tallo0 = sis.tallos(golpe, ancho=self.ANCHO_CAJA, alto=self.ALTO_SOLO,
                            color=CIAN, grosor=2.8, punta=0.055,
                            rango_y=(0.0, 1.0))
        suelo0 = sis.cero(ancho=self.ANCHO_CAJA, y=-self.ALTO_SOLO / 2,
                          color=LINEA)
        eti0 = rot("EL MISMO GOLPE", color=CIAN)
        eti0.next_to(suelo0, DOWN, buff=0.24)
        L.escena(VGroup(suelo0, eti0, tallo0), t=0.9)
        self.leer(2.6)

        # --- 1. el primer sistema: se apaga -------------------------------
        panel1, h_ok = self._panel(self.A_ESTABLE, self.ALTO_SOLO)
        suma_ok = sis.suma_absoluta(h_ok)
        L.relevo(escena=panel1,
                dato=(medido(suma_ok, 2), "suma de |h|, se detiene", True),
                t=0.9)
        self.leer(4.2)

        # --- 2. el mismo golpe, solo cambia `a`: crece sin techo ----------
        panel2, h_mal = self._panel(self.A_INESTABLE, self.ALTO_SOLO)
        suma_mal = sis.suma_absoluta(h_mal)
        L.relevo(escena=panel2,
                dato=(medido(suma_mal, 2), "la misma suma, sin techo", True),
                t=0.9)
        self.leer(4.6)

        # --- 3. remate: los dos a la vez, con la escala DECLARADA ---------
        # (el dato se deja COMO ESTA: la ultima medida, la suma sin techo,
        # sigue siendo la que corresponde a lo que hay en pantalla)
        #
        # Los dos cuadros normalizan cada uno a su propio maximo (si no,
        # el que se apaga quedaria aplastado). Pero normalizados los dos
        # ocupan la MISMA altura en pantalla aunque sus escalas reales
        # difieren: eso se declara con el factor real entre los maximos,
        # no con un numero puesto a mano.
        factor_escala = float(np.max(h_mal)) / float(np.max(h_ok))
        panel_arriba, _ = self._panel(
            self.A_ESTABLE, self.ALTO_PAR, y_shift=self.Y_TOP,
            escala_texto="ESCALA 1X")
        panel_abajo, _ = self._panel(
            self.A_INESTABLE, self.ALTO_PAR, y_shift=self.Y_BOT,
            escala_texto=f"ESCALA {medido(factor_escala, 0)}X")
        L.relevo(escena=VGroup(panel_arriba, panel_abajo), t=0.9)
        self.leer(4.0)

        # --- 4. la diferencia entre los dos, en un solo numero -------------
        factor = suma_mal / suma_ok
        L.dato(medido(factor, 0), "veces mas grande", medido=True, t=0.6)
        self.leer(4.2)
        self.leer(3.4)
