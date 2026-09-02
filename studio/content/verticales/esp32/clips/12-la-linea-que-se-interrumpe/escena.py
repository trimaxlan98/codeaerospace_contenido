# 12 · La linea que se interrumpe
#
# Abre el ultimo modulo. Un programa que pregunta "¿ha pasado algo?" en
# cada vuelta del bucle solo se entera cuando le toca preguntar. La
# interrupcion no pregunta: el hardware para la CPU y la manda a atender.
# La diferencia no es de estilo de programacion, y por eso el remate no es
# un adjetivo sino una razon entre dos peores casos.
#
# Cifras: las cuatro medidas salen de las dos simulaciones de 400 sucesos
# de `esp32.py` (`latencias_sondeo` y `latencias_isr`). Lo unico que no se
# mide es el periodo del bucle: es el parametro que uno ELIGE al escribir
# el programa, asi que va con etiqueta APAGADA como la hoja de datos.
#
# La regla de la casa dice que la estadistica se mide sobre la ventana
# DIBUJADA. Por eso los cuatro sucesos del dibujo no son cuatro
# cualesquiera: son tres tomados uno de cada ciento sesenta MAS el peor de
# los cuatrocientos, de modo que el 9.998 que se rotula es el trazo ambar
# que ocupa la vuelta entera y no una cifra traida de fuera del cuadro. El
# peor va en la PRIMERA vuelta a proposito: su espera dura una vuelta
# completa y, detras de cualquier otro suceso, los dos trazos ambar se
# tocarian y se leerian como uno solo.
#
# Y son CUATRO sobre CINCO vueltas, no cinco sobre seis: con seis vueltas
# en los 5.3 de ancho, la vuelta entera del peor caso median 60 px sobre
# 359 y no se distinguia de la espera de 0.76 vueltas de al lado. Menos
# sucesos y menos vueltas es mas ancho por vuelta, que es lo unico que
# hace visible el peor caso.
#
# La media va con el otro dibujo, el de las 400 esperas ORDENADAS: alli si
# esta dibujada la simulacion entera. La rampa recta es la distribucion
# uniforme y el nivel ambar cae justo en su mitad — medio periodo no es
# casualidad, es lo que tiene esperar a un reloj.
#
# El ultimo dibujo no lleva tren de pulsos porque la interrupcion no
# depende del bucle: solo la linea del tiempo, el suceso arriba y la
# atencion abajo, separados por los 2.7 microsegundos que la escala del
# dibujo no puede resolver. Que se vean como UN solo trazo partido por la
# linea es exactamente el mensaje.
class Clip(Pieza):
    NUMERO = 12

    T_MS = 10.0              # el periodo del bucle, en milisegundos
    N_VUELTAS = 5            # vueltas dibujadas (la ultima, vacia)
    ANCHO_T = 5.3
    ALTO_TREN = 2.0
    Y_MARCAS = 1.45
    ALTO_MARCAS = 0.62

    # --- ayudas de dibujo ---------------------------------------------
    def _x(self, t):
        """Instante (en vueltas) -> abscisa dentro del dibujo. Es la misma
        cuenta que hace `chip.marcas_tiempo` con `t_max=N_VUELTAS`, para
        que marcas y esperas caigan sobre el mismo sitio del tren."""
        return t / self.N_VUELTAS * self.ANCHO_T - self.ANCHO_T / 2

    def _tren(self, color):
        return chip.pulsos(n=self.N_VUELTAS, duty=0.5, ancho=self.ANCHO_T,
                           alto=self.ALTO_TREN, color=color)

    def _marcas(self, instantes, color):
        return chip.marcas_tiempo(instantes, y=self.Y_MARCAS,
                                  ancho=self.ANCHO_T, alto=self.ALTO_MARCAS,
                                  t_max=self.N_VUELTAS, color=color)

    @staticmethod
    def _encima(etq, mob, buff=0.30):
        etq.move_to([0, mob.get_top()[1] + buff + etq.height / 2, 0])
        return etq

    @staticmethod
    def _debajo(etq, mob, buff=0.30):
        etq.move_to([0, mob.get_bottom()[1] - buff - etq.height / 2, 0])
        return etq

    def pieza(self):
        L = self.L
        T = self.T_MS

        ls = chip.latencias_sondeo(periodo_ms=T, n=400, semilla=31)
        li = chip.latencias_isr(base_us=1.8, jitter_us=0.9, n=400)

        # Los cuatro sucesos del dibujo, en vueltas: el peor de los 400 y
        # tres tomados uno de cada 160. El suceso k cae dentro de la vuelta
        # k y el bucle lo atiende al empezar la k+1.
        idx = [int(ls.argmax()), 0, 160, 320]
        esperas = ls[idx] / T
        sucesos = np.array([(k + 1) - e for k, e in enumerate(esperas)])

        # --- 1. el bucle pregunta una vez por vuelta ------------------
        tren_a = self._tren(TINTA)
        marcas_a = self._marcas(sucesos, AMBAR)
        eti_a = self._encima(rot("SUCESOS", color=AMBAR), marcas_a)
        eti_b = self._debajo(rot("BUCLE"), tren_a)
        uno = VGroup(tren_a, marcas_a, eti_a, eti_b)
        L.escena(uno, animacion=AnimationGroup(
            Create(tren_a, run_time=1.6),
            Succession(Wait(0.9),
                       FadeIn(marcas_a, lag_ratio=0.20, run_time=0.9)),
            FadeIn(VGroup(eti_a, eti_b), run_time=0.8), lag_ratio=0.0))
        self.wait(0.7)

        L.dato(medido(T, 0), "milisegundos por vuelta", medido=False, t=0.6)
        self.wait(3.6)

        # --- 2. lo que espera cada suceso -----------------------------
        # El tren pasa a mobiliario y las esperas se quedan el ambar: lo
        # protagonista ya no es el reloj, es el hueco.
        tren_b = self._tren(APAGADO)
        marcas_b = self._marcas(sucesos, TINTA)
        esperas_g = VGroup()
        for t_suceso, hueco in zip(sucesos, esperas):
            w = hueco * self.ANCHO_T / self.N_VUELTAS
            trazo = lz.filete(ancho=w, color=AMBAR, grosor=5.0)
            trazo.move_to([self._x(t_suceso) + w / 2,
                           marcas_b.get_bottom()[1], 0])
            esperas_g.add(trazo)
        eti_c = self._encima(rot("ESPERA", color=AMBAR), marcas_b)
        eti_c2 = self._debajo(rot("BUCLE"), tren_b)
        dos = VGroup(tren_b, marcas_b, esperas_g, eti_c, eti_c2)
        L.escena(dos, animacion=AnimationGroup(
            FadeIn(VGroup(tren_b, marcas_b, eti_c2), run_time=0.9),
            Succession(Wait(0.5),
                       Create(esperas_g, lag_ratio=0.25, run_time=1.4)),
            Succession(Wait(0.5), FadeIn(eti_c, run_time=0.7)),
            lag_ratio=0.0))
        self.wait(0.6)

        # El peor de los 400 ES el trazo largo que se acaba de dibujar.
        L.dato(medido(ls.max(), 3), "milisegundos, el peor")
        self.wait(3.9)

        # --- 3. y de media, medio periodo -----------------------------
        # Las 400 esperas ordenadas: una recta. Eso es una uniforme, y por
        # eso el nivel ambar de la media cae en la mitad exacta.
        orden = np.sort(ls)
        rampa, punto = chip.traza(np.arange(orden.size), orden, ancho=5.2,
                                  alto=3.2, color=TINTA, rango_y=(0.0, T))
        eje = chip.eje_ele(ancho=5.2, alto=3.2)
        media = chip.nivel(float(ls.mean()), punto, ancho=5.2, color=AMBAR)
        eti_d = self._debajo(rot(f"{ls.size} ESPERAS"), eje)
        tres = VGroup(eje, rampa, media, eti_d)
        L.escena(tres, animacion=AnimationGroup(
            FadeIn(eje, run_time=0.6),
            Succession(Wait(0.3), Create(rampa, run_time=1.5)),
            Succession(Wait(1.2), FadeIn(media, run_time=0.7)),
            FadeIn(eti_d, run_time=0.8), lag_ratio=0.0))
        self.wait(0.6)

        L.dato(medido(ls.mean(), 2), "milisegundos de media")
        self.wait(3.9)

        # --- 4. la interrupcion no pregunta ---------------------------
        # Los mismos cuatro sucesos, sin bucle debajo. La atencion va a
        # `suceso + li`, que a esta escala es el mismo sitio: el par se lee
        # como un unico trazo partido por la linea del tiempo.
        atencion = sucesos + li[idx] / T
        linea_t = lz.regla(0.0, ancho=self.ANCHO_T, color=APAGADO,
                           grosor=1.6)
        m_suceso = chip.marcas_tiempo(sucesos, y=0.675, ancho=self.ANCHO_T,
                                      alto=1.25, t_max=self.N_VUELTAS,
                                      color=TINTA)
        m_isr = chip.marcas_tiempo(atencion, y=-0.675, ancho=self.ANCHO_T,
                                   alto=1.25, t_max=self.N_VUELTAS,
                                   color=AMBAR)
        eti_e = self._encima(rot("SUCESO"), m_suceso)
        eti_f = self._debajo(rot("ATENCION", color=AMBAR), m_isr)
        cuatro = VGroup(linea_t, m_suceso, m_isr, eti_e, eti_f)
        L.escena(cuatro, animacion=AnimationGroup(
            Create(linea_t, run_time=0.8),
            Succession(Wait(0.5),
                       FadeIn(m_suceso, lag_ratio=0.20, run_time=0.8)),
            Succession(Wait(1.0),
                       FadeIn(m_isr, lag_ratio=0.20, run_time=0.8)),
            FadeIn(VGroup(eti_e, eti_f), run_time=0.8), lag_ratio=0.0))
        self.wait(0.6)

        # La misma etiqueta que el peor caso del sondeo, cambiando de
        # unidad: las dos cifras son el mismo estadistico sobre las mismas
        # 400 llegadas, que es lo que hace legitima la razon del remate.
        L.dato(medido(li.max() * 1000, 2), "microsegundos, el peor")
        self.wait(3.8)

        # --- 5. el remate: la razon entre los dos peores casos ---------
        L.dato(lz.miles(int(round(ls.max() / li.max()))), "veces mas rapida")
        self.wait(5.4)
