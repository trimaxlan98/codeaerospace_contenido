# 13 · RESPUESTA EN FRECUENCIA — no puede inventar frecuencias.
#
# El verbo visual: entra un tono (CIAN) y sale EL MISMO tono (AMBAR), con
# otra amplitud y nada mas. Se repite con tres tonos -w = 0.2, 0.5, 0.9-
# sobre la MISMA caja h, y cada ganancia medida deja su punto sobre una
# curva que se dibuja sola: esa curva ES la respuesta en frecuencia. El
# remate demuestra que "meter un tono de verdad y medir" y "leer la curva
# calculada de h" son la misma cosa: los tres puntos caen encima del
# trazo, no al lado.
#
# DECISIONES QUE VALE LA PENA DEJAR ESCRITAS:
#
#   - **El rango vertical de los tres paneles de tono es el MISMO,
#     (-2.9, 2.9), y nunca se normaliza al pico de cada uno.** Es lo unico
#     que hace honrado el verbo: si cada salida se escalase a su propio
#     maximo, las tres se verian igual de altas aunque la ganancia real
#     vaya de 0.90 a 2.60. Con el rango fijo, la salida CRECE en pantalla
#     exactamente lo que crece de verdad -esta es la trampa 5 del
#     contrato, y aqui se evita de raiz en vez de declararla.
#   - **La ventana que se dibuja ya esta asentada**: empieza 20 muestras
#     despues de que se acaba `h`, el mismo tramo que mide
#     `sis.ganancia_medida` por dentro. Un tramo mas temprano todavia
#     arrastra el transitorio y la amplitud dibujada mentiria sobre la
#     cifra de al lado.
#   - **Los tres puntos del remate se construyen ANTES de encajar el
#     cuadro de la curva**, a opacidad 0, dentro del MISMO grupo que
#     `L.relevo` coloca: la funcion `punto()` que devuelve `sis.traza` da
#     coordenadas en el eje LOCAL del cuadro, y lo que se construye
#     DESPUES de `encajar` no hereda ni su escala ni su posicion (trampa 3
#     del contrato). Se registran invisibles en el mismo `FadeIn` que trae
#     la curva y se encienden despues con `set_opacity` -el mismo truco
#     que usa la pieza 07 con su tramo resaltado.
#   - **Los puntos caen sobre la curva sin trampa de dibujo**: la posicion
#     de cada uno sale de interpolar (`np.interp`) sobre el MISMO par de
#     arreglos (frecuencia, ganancia) que traza `sis.traza`, asi que cae
#     exactamente sobre el segmento recto que la curva ya dibujo ahi -no
#     es una coincidencia feliz, es la misma aritmetica.
class Clip(Pieza):
    NOMBRE = "RESPUESTA EN FRECUENCIA"
    TESIS = "no puede inventar frecuencias"

    # --- la caja y la malla: PARAMETROS elegidos ------------------------
    N_H = 48
    TAU = 9.0
    F_H = 0.11
    WS = (0.2, 0.5, 0.9)
    N_TONO = 400            # el N por defecto de sis.ganancia_medida
    VENTANA = 48             # muestras que se enseñan, ya asentadas
    N_FFT = 1024
    W_MAX = 1.05             # el tramo de la curva que se dibuja

    # --- geometria de los paneles de tono --------------------------------
    ANCHO_CAJA = ANCHO - 0.5
    ALTO_P = 1.5
    RANGO_TONO = (-2.9, 2.9)        # FIJO en los tres planos, ver cabecera
    ANCHO_GLIFO = 2.0
    ALTO_GLIFO = 0.78
    Y_E = ALTO_GLIFO / 2 + 0.30 + ALTO_P / 2
    Y_S = -Y_E

    # --- geometria de la curva --------------------------------------------
    ALTO_CURVA = 3.3

    # ---------------------------------------------------------------------
    def _tono(self, w):
        """(xv, yv, ganancia): la MISMA ventana ya asentada para las dos."""
        n = np.arange(self.N_TONO)
        x = np.cos(w * n)
        y = sis.convolucion(x, self.h)[:self.N_TONO]
        n0 = self.N_H + 20
        xv = x[n0:n0 + self.VENTANA]
        yv = y[n0:n0 + self.VENTANA]
        return xv, yv, sis.ganancia_medida(self.h, w)

    def _cuadro_tono(self, w):
        """El cuadro de un tono: entrada arriba, caja, salida abajo."""
        xv, yv, gm = self._tono(w)
        idx = np.arange(self.VENTANA)
        entrada, _ = sis.traza(idx, xv, ancho=self.ANCHO_CAJA,
                               alto=self.ALTO_P, color=CIAN,
                               grosor=sis.TRAZO,
                               rango_x=(0, self.VENTANA - 1),
                               rango_y=self.RANGO_TONO, escalones=True)
        entrada.shift(UP * self.Y_E)
        salida, _ = sis.traza(idx, yv, ancho=self.ANCHO_CAJA,
                              alto=self.ALTO_P, color=AMBAR,
                              grosor=sis.TRAZO,
                              rango_x=(0, self.VENTANA - 1),
                              rango_y=self.RANGO_TONO, escalones=True)
        salida.shift(DOWN * self.Y_E)
        ejes = VGroup(*[sis.cero(ancho=self.ANCHO_CAJA, y=0.0,
                                 color=LINEA).shift(UP * y)
                       for y in (self.Y_E, self.Y_S)])
        caja = sis.caja(texto="h", ancho=self.ANCHO_GLIFO,
                        alto=self.ALTO_GLIFO, color=AMBAR)
        eti = rot(f"w = {medido(w, 2)}", color=CIAN)
        eti.move_to([0, -self.Y_E - self.ALTO_P / 2 - 0.24 - eti.height / 2,
                    0])
        grupo = VGroup(ejes, caja, entrada, salida, eti)
        return grupo, entrada, salida, gm

    def _curva(self):
        """La curva de |H|, los tres puntos ya listos pero invisibles."""
        wf, mag, _ = sis.respuesta_frecuencia(self.h, N=self.N_FFT)
        m = wf <= self.W_MAX
        wf_c, mag_c = wf[m], mag[m]
        tope = float(mag_c.max()) * 1.08
        curva, punto = sis.traza(wf_c, mag_c, ancho=self.ANCHO_CAJA,
                                 alto=self.ALTO_CURVA, color=APAGADO,
                                 grosor=sis.TRAZO,
                                 rango_x=(0.0, self.W_MAX),
                                 rango_y=(0.0, tope))
        suelo = sis.cero(ancho=self.ANCHO_CAJA, y=-self.ALTO_CURVA / 2,
                         color=LINEA)
        eti = rot("CADA TONO SU PUNTO")
        eti.move_to([0, -self.ALTO_CURVA / 2 - 0.24 - eti.height / 2, 0])
        dots = []
        for w in self.WS:
            predicho = float(np.interp(w, wf_c, mag_c))
            d = Dot(punto(w, predicho), radius=0.10, color=AMBAR)
            d.set_opacity(0.0)
            dots.append(d)
        grupo = VGroup(suelo, curva, eti, *dots)
        return grupo, curva, suelo, eti, dots, wf_c, mag_c

    def pieza(self):
        L = self.L
        self.h = sis.h_amortiguada(N=self.N_H, tau=self.TAU, f=self.F_H)

        # --- ACTO 1: el mismo tono, tres veces, tres ganancias ---------
        g1, ent1, sal1, gm1 = self._cuadro_tono(self.WS[0])
        # `salida` se apaga ANTES de encajar y viaja invisible dentro del
        # grupo: el primer FadeIn no la enciende (su objetivo ya es
        # opacidad 0), y solo entonces se revela -asi entra primero el
        # tono, y despues sale.
        sal1.set_stroke(opacity=0.0)
        L.escena(g1, animacion=FadeIn(g1, run_time=0.7))
        self.play(sal1.animate.set_stroke(opacity=1.0), run_time=0.7)
        self.leer(2.4)
        L.dato(medido(gm1, 2), "la ganancia", medido=True, t=0.5)
        self.leer(2.6)

        g2, _, _, gm2 = self._cuadro_tono(self.WS[1])
        L.relevo(escena=g2, dato=(medido(gm2, 2), "la ganancia", True),
                t=0.9)
        self.leer(2.8)

        g3, _, _, gm3 = self._cuadro_tono(self.WS[2])
        L.relevo(escena=g3, dato=(medido(gm3, 2), "la ganancia", True),
                t=0.9)
        self.leer(2.8)

        # --- ACTO 2: la curva, y los tres puntos caen sobre ella --------
        gc, curva, suelo, etic, dots, wf_c, mag_c = self._curva()
        L.relevo(escena=gc, dato=None,
                 animacion=AnimationGroup(
                     FadeIn(VGroup(suelo, etic, *dots), run_time=0.6),
                     Create(curva, run_time=1.3),
                     lag_ratio=0.25, run_time=1.6))
        self.leer(2.4)

        self.play(AnimationGroup(
            *[d.animate.set_opacity(1.0) for d in dots], lag_ratio=0.45),
            run_time=1.6)
        self.leer(3.0)

        diffs = [abs(sis.ganancia_medida(self.h, w)
                     - float(np.interp(w, wf_c, mag_c))) for w in self.WS]
        L.dato(medido(max(diffs), 4), "diferencia con la curva",
              medido=True, t=0.5)
        self.leer(3.2)
