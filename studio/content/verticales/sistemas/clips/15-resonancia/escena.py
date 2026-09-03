# 15 · RESONANCIA — un empujon a tiempo.
#
# El verbo visual, en dos tiempos.
#
# PRIMERO, en el TIEMPO: el mismo resonador `sis.resonador(f0, Q=4, N)`
# recibe un tono (CIAN) FUERA de f0 y sale poco; despues recibe OTRO tono,
# con la MISMA amplitud (1.0 en los dos casos: `np.cos(...)`, nunca se
# reescala) pero a f0, y la salida (AMBAR) se dispara. Los DOS casos
# comparten SIEMPRE el mismo `rango_y` de entrada Y de salida -fijado al
# maximo del caso resonante, nunca al de cada caso por separado-, que es
# la unica forma honesta de que "sale poco / sale mucho" se lea en la
# pantalla sin normalizar la diferencia hasta borrarla (trampa 5 del
# contrato). La salida no es un numero: es la convolucion de verdad
# (`sis.convolucion`) del tono con la respuesta al impulso, asi que lo
# que crece en pantalla es literalmente la señal entrando en resonancia,
# empujon a empujon -no una animacion que lo simula.
#
# SEGUNDO, en la FRECUENCIA: la campana |H(f)| de Q=4 se transforma -entre
# gemelas de la misma malla, el molde de 01-el-impulso- en la de Q=12 y
# despues en la de Q=40. LA DECISION QUE COSTO UNA VUELTA: cada campana se
# dibuja normalizada a SU PROPIO pico (rango_y=(0, 1.08) fijo, compartido
# sin miedo, siempre). Se midio la alternativa -tres |H(f)| SIN
# normalizar, con Q=40 nueve veces mas alta que Q=4 en la referencia
# fuera de resonancia- y esa version rompe la regla del 45%: mostrar Q=4
# SOLA (las otras dos a opacidad 0, sin pintar) dentro de un rango
# pensado para Q=40 la deja en el 10% de la franja, invisible antes de
# que el guardian la aborte. Normalizando a su propio pico, las tres
# llegan a la misma altura siempre y el unico verbo que queda es el
# real y medible: LA ANCHURA se aprieta con Q. Lo que crece con Q no es
# una altura de mentira -es la cifra de al lado, `sis.amplificacion`,
# que sale de la MISMA razon (ganancia en f0 entre ganancia fuera) que
# ya reportaba el ambar antes de dibujar nada.
#
# UN AVISO DE LA LIBRERIA, YA CORREGIDO: `sis.duracion` depende de
# CUANTAS muestras de `h` se generaron -no es una propiedad del sistema
# si se la mide sobre una ventana que todavia no termino de apagarse.
# Medido con Q=40: N=400 -> 384, N=600 -> 552, N=800 -> 620, N=900 ->
# 620, N=1200 -> 620, N=1600 -> 620. Por debajo de N=800 la cifra es el
# TAMANO DE LA VENTANA disfrazado de medida (el mismo error que tuvo la
# pieza 10 con sus "60 muestras que duran"); a partir de N~800 converge
# y deja de moverse. Aqui `h40` se genera con `N=1200` -bien dentro de
# la zona estable, comprobado contra 900 y 1600- para que la cifra en
# pantalla sea la del sistema, no la de la ventana que se eligio para
# dibujarlo.
#
# UN SEGUNDO AVISO, HERMANO DEL PRIMERO PERO EN EL EJE DE FRECUENCIA:
# `sis.amplificacion` tambien depende de la REJILLA con la que calcula
# el espectro (su parametro `N`, el de la FFT -nada que ver con la N de
# `resonador`). Con Q=4 la campana es ancha y cualquier rejilla cae
# cerca del pico: 3.89 en N=1024, 2048, 4096... no se mueve. Con Q=40 la
# campana es tan estrecha que una rejilla gruesa NO CAE en el pico y lo
# mide por debajo -exactamente "la profundidad de un nulo depende del
# numero de puntos" (trampa del contrato) pero en un pico en vez de un
# nulo. Medido sobre el `h40` de 1200 muestras: N=1024 -> 37.38, 2048 ->
# 37.72, 4096 -> 38.03, 8192 -> 38.20, 16384 -> 38.25. Redondeadas a
# ENTERO, las tres cifras (Q=4, Q=12, Q=40) son estables desde N=4096 y
# no se mueven en 8192, 16384 ni 32768: 4, 11, 38. Por eso las tres se
# calculan con `N_FFT=8192` (dentro de la zona estable, con margen) y se
# muestran como ENTERO (`medido(x, 0)`) -las tres a la misma precision:
# mostrar 3.89 / 11.46 / 38 seria fingir dos decimales de una cifra que
# no los tiene, y las tres cifras de la misma magnitud con precisiones
# distintas se leen como un descuido.
class Clip(Pieza):
    NOMBRE = "RESONANCIA"
    TESIS = "un empujon a tiempo"

    # --- parametros ELEGIDOS (grises en pantalla) ------------------------
    F0 = 0.08
    FUERA = 0.02
    N_TONO = 130
    N_FFT = 8192   # ver cabecera: la rejilla de amplificacion, no de raiz

    # --- geometria de la cadena entrada-caja-salida ----------------------
    CAJA_ANCHO = 1.5
    CAJA_ALTO = 3.3
    LARGO = 0.55
    TRAZA_ANCHO = 1.4
    TRAZA_ALTO = 3.0
    HUECO = 0.12

    # --- geometria de la campana ------------------------------------------
    VENTANA = 0.18                    # ciclos/muestra que se dibujan
    BELL_ANCHO = ANCHO - 0.4
    BELL_ALTO = 4.2
    RANGO_CAMPANA = (0.0, 1.08)       # cada campana normalizada a SU pico

    def _tono_cuadro(self, f, h, rango_ent, rango_sal, etiqueta):
        """entrada CIAN -> caja "h" -> salida AMBAR. Los DOS rangos son
        argumentos fijos desde fuera: nunca se recalculan por caso, que es
        lo que hace comparable "poco" con "mucho"."""
        n = np.arange(self.N_TONO)
        x = np.cos(2 * np.pi * float(f) * n)
        y = sis.convolucion(x, h)[:self.N_TONO]
        caja = sis.caja(texto="h", ancho=self.CAJA_ANCHO,
                        alto=self.CAJA_ALTO)
        cadena, p_ini, p_fin = sis.cadena([caja], largo=self.LARGO)
        entrada, _ = sis.traza(n, x, ancho=self.TRAZA_ANCHO,
                               alto=self.TRAZA_ALTO, color=CIAN,
                               grosor=sis.TRAZO_FINO,
                               rango_x=(0, n[-1]), rango_y=rango_ent,
                               escalones=True)
        entrada.move_to([p_ini[0] - self.HUECO - self.TRAZA_ANCHO / 2, 0, 0])
        salida, _ = sis.traza(n, y, ancho=self.TRAZA_ANCHO,
                              alto=self.TRAZA_ALTO, color=AMBAR,
                              grosor=sis.TRAZO_FINO,
                              rango_x=(0, n[-1]), rango_y=rango_sal,
                              escalones=True)
        salida.move_to([p_fin[0] + self.HUECO + self.TRAZA_ANCHO / 2, 0, 0])
        eti = rot(etiqueta)
        techo = cadena.get_top()[1]
        eti.move_to([cadena.get_center()[0], techo + 0.30 + eti.height / 2,
                    0])
        return VGroup(cadena, entrada, salida, eti)

    def _campana(self, h):
        """(f, |H|/pico) en la ventana visible. Normalizada a SU PROPIO
        maximo -ver cabecera: es lo que evita el 45% roto."""
        w, mag, _ = sis.respuesta_frecuencia(h, N=4096)
        f = w / (2 * np.pi)
        m = f <= self.VENTANA
        f_v, mag_v = f[m], mag[m]
        return f_v, mag_v / mag_v.max()

    def _curva_campana(self, f_v, mag_n):
        curva, _ = sis.traza(f_v, mag_n, ancho=self.BELL_ANCHO,
                             alto=self.BELL_ALTO, color=AMBAR,
                             grosor=sis.TRAZO, rango_x=(0.0, self.VENTANA),
                             rango_y=self.RANGO_CAMPANA)
        return curva

    def pieza(self):
        L = self.L

        # --- la materia del tramo temporal: un solo Q -------------------
        h4 = sis.resonador(self.F0, 4.0, N=400)
        n = np.arange(self.N_TONO)
        y_on_ref = sis.convolucion(np.cos(2 * np.pi * self.F0 * n), h4)[
            :self.N_TONO]
        tope_sal = float(np.max(np.abs(y_on_ref))) * 1.12
        RANGO_ENT = (-1.15, 1.15)
        RANGO_SAL = (-tope_sal, tope_sal)

        # --- 1. fuera de la resonancia: la misma amplitud, sale poco ----
        grupo1 = self._tono_cuadro(self.FUERA, h4, RANGO_ENT, RANGO_SAL,
                                   "FUERA DE RESONANCIA")
        L.escena(grupo1, t=0.9)
        self.leer(2.8)

        # --- 2. el mismo empujon, a tiempo: se dispara --------------------
        grupo2 = self._tono_cuadro(self.F0, h4, RANGO_ENT, RANGO_SAL,
                                   "EN RESONANCIA")
        amp4 = sis.amplificacion(h4, self.F0, self.FUERA, N=self.N_FFT)
        L.relevo(escena=grupo2,
                dato=(medido(amp4, 0), "veces mas grande", True), t=1.0)
        self.leer(3.0)

        # --- la materia del tramo en frecuencia --------------------------
        h12 = sis.resonador(self.F0, 12.0, N=400)
        h40 = sis.resonador(self.F0, 40.0, N=1200)  # ver cabecera: dentro
                                                     # de la zona estable
                                                     # (600 la truncaba)
        f_v, mag4 = self._campana(h4)
        _, mag12 = self._campana(h12)
        _, mag40 = self._campana(h40)

        # Todo se construye ANTES de la primera L.escena, en el MISMO
        # grupo: lo que se hace despues no hereda la escala de `encajar`
        # (trampa 3 del contrato).
        curva4 = self._curva_campana(f_v, mag4)
        curva12 = self._curva_campana(f_v, mag12)
        curva40 = self._curva_campana(f_v, mag40)
        curva12.set_stroke(opacity=0.0)
        curva40.set_stroke(opacity=0.0)

        suelo_c = sis.cero(ancho=self.BELL_ANCHO,
                           y=-self.BELL_ALTO / 2, color=LINEA)
        eti4 = rot("Q = 4")
        eti4.next_to(suelo_c, DOWN, buff=0.24)
        eti12 = rot("Q = 12")
        eti12.move_to(eti4.get_center())
        eti12.set_opacity(0.0)
        eti40 = rot("Q = 40")
        eti40.move_to(eti4.get_center())
        eti40.set_opacity(0.0)

        grupo_campana = VGroup(suelo_c, eti4, eti12, eti40,
                               curva4, curva12, curva40)

        # --- 3. la misma pregunta, en frecuencia: Q = 4 -------------------
        # (el dato se deja COMO ESTA: sigue siendo cierto que a Q=4 la
        # amplificacion es la de arriba, y todavia no toca medir otra)
        L.escena(grupo_campana, t=0.9)
        self.leer(2.6)

        # --- 4. Q sube a 12: la campana se ESTRECHA -----------------------
        curva12.set_stroke(opacity=1.0)
        eti12.set_opacity(1.0)
        self.play(Transform(curva4, curva12), Transform(eti4, eti12),
                  run_time=1.1, rate_func=smooth)
        curva12.set_stroke(opacity=0.0)
        eti12.set_opacity(0.0)
        amp12 = sis.amplificacion(h12, self.F0, self.FUERA, N=self.N_FFT)
        L.dato(medido(amp12, 0), "veces mas grande", medido=True, t=0.4)
        self.leer(2.8)

        # --- 5. Q sube a 40: mas selectiva, mas amplificacion -------------
        curva40.set_stroke(opacity=1.0)
        eti40.set_opacity(1.0)
        self.play(Transform(curva4, curva40), Transform(eti4, eti40),
                  run_time=1.1, rate_func=smooth)
        curva40.set_stroke(opacity=0.0)
        eti40.set_opacity(0.0)
        amp40 = sis.amplificacion(h40, self.F0, self.FUERA, N=self.N_FFT)
        L.dato(medido(amp40, 0), "veces mas grande", medido=True, t=0.4)
        self.leer(3.0)

        # --- 6. EL REMATE: un solo empujon, tunado a la mas selectiva -----
        golpe = sis.impulso(N=9, n0=4)
        ALTO_GOLPE = 1.2
        tallo_golpe = sis.tallos(golpe, ancho=1.8, alto=ALTO_GOLPE,
                                 color=CIAN, grosor=2.4, punta=0.045,
                                 rango_y=(0.0, 1.0))
        suelo_g = sis.cero(ancho=1.8, y=-ALTO_GOLPE / 2, color=LINEA)
        eti_golpe = rot("UN EMPUJON", color=CIAN)
        eti_golpe.next_to(suelo_g, DOWN, buff=0.18)
        panel_golpe = VGroup(suelo_g, tallo_golpe, eti_golpe)

        tope_h40 = float(np.max(np.abs(h40))) * 1.12
        n40 = np.arange(h40.size)
        ALTO_ECO = 3.0
        eco, _ = sis.traza(n40, h40, ancho=self.BELL_ANCHO, alto=ALTO_ECO,
                           color=AMBAR, grosor=sis.TRAZO_FINO,
                           rango_x=(0, n40[-1]),
                           rango_y=(-tope_h40, tope_h40), escalones=True)
        suelo_e = sis.cero(ancho=self.BELL_ANCHO, y=-ALTO_ECO / 2,
                           color=LINEA)
        eti_eco = rot("EL ECO", color=AMBAR)
        eti_eco.next_to(suelo_e, DOWN, buff=0.18)
        panel_eco = VGroup(suelo_e, eco, eti_eco)

        bloque = VGroup(panel_golpe, panel_eco).arrange(DOWN, buff=0.5)

        L.relevo(escena=bloque,
                dato=(medido(sis.duracion(h40), 0), "muestras de eco",
                      True), t=1.1)
        self.leer(3.4)
        self.leer(2.4)
