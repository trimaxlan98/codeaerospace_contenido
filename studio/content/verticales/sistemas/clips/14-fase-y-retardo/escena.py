# FASE Y RETARDO — la forma se rompe sola.
#
# La pieza mas contraintuitiva del curso: la senal se destroza sin tocar
# ni una amplitud. Por eso los dos actos usan LA MISMA senal de entrada y
# la MISMA escala vertical — lo unico que cambia entre ellos es COMO se
# mueven las fases.
#
#   1. EL RETARDO HONRADO. Un filtro de fase lineal (`sis.paso_bajo`, 61
#      taps) gira la fase de cada frecuencia lo justo para retrasarlas a
#      todas por igual: la salida es la entrada corrida 30 muestras y
#      nada mas. El remate lo demuestra: se adelanta la salida esas 30
#      muestras medidas y cae encima de la entrada.
#   2. LA FASE QUE ROMPE. `sis.deformar_fases` mueve las fases de otra
#      manera (cuadratica) y deja el espectro de AMPLITUD exactamente
#      igual. El dibujo se deshace mientras la cifra sigue diciendo 0.
#      Esa pareja —0 de cambio y dos senales que no se parecen en nada—
#      ES la pieza.
#
# DECISIONES QUE COSTARON MEDIRLO:
#
#   - Los dos tonos van en 0.04 y 0.09, no en 0.11. Con corte en 0.12 el
#     filtro tiene ganancia 0.79 en 0.11 y 1.00 en 0.09 (medido con
#     `sis.ganancia_medida`): con el tono de 0.11 la salida SI cambiaba
#     de forma —por amplitud, no por fase— y el primer acto afirmaba en
#     pantalla justo lo contrario de lo que se veia. Dentro de la banda
#     plana el residuo del realineado es 0.00055 sobre un pico de 2.
#   - El remate no compara la ventana entera: los primeros 60 puntos de
#     la salida son el filtro llenandose y ahi la igualdad todavia no
#     puede cumplirse. Se compara desde la muestra 60, y el corrimiento
#     que se aplica es el retardo MEDIDO, no un 30 escrito a mano.
#   - `sis.respuesta_frecuencia` se llama con N = len(x) EXACTO. Con la
#     malla mas larga rellena de ceros, las dos senales se interpolan de
#     forma distinta y el "cambio" deja de ser cero sin que nada falle.
#   - Los dos paneles comparten `RANGO_Y`. Si cada uno se normalizara por
#     su cuenta, la comparacion no valdria nada: media pieza consiste
#     precisamente en mirar dos dibujos y creerse que son comparables.
class Clip(Pieza):
    NOMBRE = "FASE Y RETARDO"
    TESIS = "la forma se rompe sola"

    # --- parametros ELEGIDOS (etiqueta apagada si se rotulan) ----------
    N = 160                    # muestras de la senal
    F1, F2 = 0.04, 0.09        # los dos tonos, dentro de la banda plana
    FC = 0.12                  # corte del filtro
    TAPS = 61                  # impar: fase lineal exacta
    GIROS = (0.0, 4.0, 12.0)   # cuanto se retuercen las fases
    VENTANA = 100              # muestras que compara el remate

    # --- geometria -----------------------------------------------------
    ANCHO_CAJA = ANCHO - 0.5
    ALTO_PANEL = 2.05
    ALTO_REMATE = 4.0
    RANGO_Y = (-2.30, 2.30)    # cubre los picos de TODOS los estados
    Y_ARRIBA = 1.42
    Y_ABAJO = -1.38

    def _curva(self, valores, color, alto, grosor=sis.TRAZO):
        """Una senal dentro de su caja, siempre con el mismo rango_y."""
        v = np.asarray(valores, dtype=float)
        curva, _ = sis.traza(np.arange(v.size), v, ancho=self.ANCHO_CAJA,
                             alto=alto, color=color, grosor=grosor,
                             rango_x=(0, v.size - 1), rango_y=self.RANGO_Y)
        return curva

    def _panel(self, texto, y, alto=None):
        """Eje de cero y rotulo debajo. La curva se le suma aparte."""
        alto = self.ALTO_PANEL if alto is None else alto
        eje = sis.cero(ancho=self.ANCHO_CAJA, y=0.0, color=LINEA)
        eti = rot(texto)
        eti.move_to([0, -alto / 2 - 0.30, 0])
        return VGroup(eje, eti).shift(UP * y)

    def _cambio_amplitudes(self, x, xd):
        """Cuanto se mueve el espectro de AMPLITUD entre las dos senales.

        Sale de `sis.respuesta_frecuencia`, y la malla es la de la propia
        senal (N = su longitud): rellenar de ceros interpolaria cada una
        de una manera y el cero dejaria de serlo."""
        _, mag, _ = sis.respuesta_frecuencia(x, len(x))
        _, mag_d, _ = sis.respuesta_frecuencia(xd, len(x))
        return float(np.max(np.abs(mag_d - mag)))

    def pieza(self):
        L = self.L

        x = sis.dos_tonos(self.F1, self.F2, N=self.N)
        b = sis.paso_bajo(self.FC, M=self.TAPS)
        y = np.asarray(sis.convolucion(x, b))

        # El retardo de grupo, MEDIDO en la banda de paso. Es plano ahi
        # —esa es la definicion de fase lineal— asi que la mediana lo
        # resume sin inventar nada.
        w, grupo = sis.retardo_grupo(b)
        banda = w < 2 * np.pi * self.FC
        retardo = float(np.median(grupo[banda]))
        salto = int(round(retardo))

        # --- 1. la entrada -----------------------------------------------
        panel_e = self._panel("ENTRADA", self.Y_ARRIBA)
        panel_s = self._panel("SALIDA", self.Y_ABAJO)
        curva_x = self._curva(x, CIAN, self.ALTO_PANEL)
        curva_x.shift(UP * self.Y_ARRIBA)
        curva_y = self._curva(y[:self.N], AMBAR, self.ALTO_PANEL)
        curva_y.shift(UP * self.Y_ABAJO)
        curva_y.set_stroke(opacity=0.0)

        L.escena(VGroup(panel_e, panel_s, curva_x, curva_y), t=0.9)
        self.leer(2.2)

        # --- 2. sale la misma forma, mas tarde ---------------------------
        self.play(curva_y.animate.set_stroke(opacity=1.0), run_time=0.9)
        self.leer(2.2)

        L.dato(medido(retardo, 0), "muestras de retardo", medido=True,
               t=0.5)
        self.leer(3.2)

        # --- 3. adelantarla esas muestras la devuelve a su sitio ---------
        # `salto` es el retardo medido, y el tramo empieza en TAPS-1
        # porque antes de eso la salida todavia se esta llenando.
        ini = self.TAPS - 1
        tramo_x = x[ini - salto:ini - salto + self.VENTANA]
        tramo_y = y[ini:ini + self.VENTANA]

        eje_r = sis.cero(ancho=self.ANCHO_CAJA, y=0.0, color=LINEA)
        # La referencia va en APAGADO OPACO y gruesa, y la salida encima a
        # TRAZOS. La primera version la puso en cian grueso con el ambar
        # fino dentro y el resultado fue una sola curva verde palida: dos
        # trazos de un pixel y medio uno dentro del otro no se leen como
        # dos curvas, se mezclan. Con la referencia neutra y la salida
        # discontinua se ve el ambar montado sobre el gris, que es
        # exactamente lo que la pieza esta afirmando.
        ref = self._curva(tramo_x, APAGADO, self.ALTO_REMATE, grosor=8.0)
        encima = DashedVMobject(
            self._curva(tramo_y, AMBAR, self.ALTO_REMATE, grosor=3.4),
            num_dashes=56, dashed_ratio=0.5)
        encima.set_stroke(opacity=0.0)
        eti_r = rot("MISMA FORMA", color=AMBAR)
        eti_r.move_to([0, -self.ALTO_REMATE / 2 - 0.30, 0])
        eti_r.set_opacity(0.0)

        L.relevo(escena=VGroup(eje_r, eti_r, ref, encima), t=0.9)
        self.leer(2.8)

        self.play(encima.animate.set_stroke(opacity=1.0),
                  eti_r.animate.set_opacity(1.0), run_time=0.8)
        self.leer(3.2)

        # --- 4. el otro modo de mover las fases --------------------------
        # Misma entrada, misma escala. Lo unico distinto es que ahora el
        # giro de cada frecuencia no es proporcional a la frecuencia.
        panel_e2 = self._panel("ENTRADA", self.Y_ARRIBA)
        panel_f = self._panel("SOLO LAS FASES", self.Y_ABAJO)
        curva_x2 = self._curva(x, CIAN, self.ALTO_PANEL)
        curva_x2.shift(UP * self.Y_ARRIBA)

        deformadas = [sis.deformar_fases(x, g) for g in self.GIROS]
        estados = []
        for d in deformadas:
            c = self._curva(d, AMBAR, self.ALTO_PANEL)
            c.shift(UP * self.Y_ABAJO)
            estados.append(c)
        for c in estados[1:]:
            c.set_stroke(opacity=0.0)

        cambios = [self._cambio_amplitudes(x, d) for d in deformadas]
        L.relevo(escena=VGroup(panel_e2, panel_f, curva_x2, *estados),
                 dato=(medido(cambios[0], 2), "cambio en las amplitudes",
                       True), t=0.9)
        self.leer(3.0)

        # --- 5. la forma se rompe y la cifra no se mueve -----------------
        # El cambio se vuelve a MEDIR en cada estado: si el dibujo y la
        # cifra se separaran, se veria aqui.
        for i in (1, 2):
            estados[i].set_stroke(opacity=1.0)
            self.play(Transform(estados[0], estados[i]), run_time=1.2,
                      rate_func=smooth)
            estados[i].set_stroke(opacity=0.0)
            L.dato(medido(cambios[i], 2), "cambio en las amplitudes",
                   medido=True, t=0.4)
            self.leer(3.3 if i == 1 else 2.9)

        self.leer(3.3)
