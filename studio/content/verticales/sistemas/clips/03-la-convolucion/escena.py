# 03 · LA CONVOLUCION — deslizar, multiplicar, sumar.
#
# El verbo visual es la operacion entera, sin una sola frase: la respuesta
# se DA LA VUELTA, DESLIZA sobre la entrada y cada posicion en la que se
# para deja un tallo abajo. Cuando el pico ambar pasa por encima de la
# parte alta del cian, el tallo que nace debajo es alto; cuando solo se
# tocan por las colas, es bajo. Eso es multiplicar y sumar, dibujado.
#
# LA GEOMETRIA ES EL ARGUMENTO, y por eso los dos carriles comparten UNA
# sola rejilla de posiciones:
#
#   - el eje va de la posicion -(M-1) a la N+M-2, que es EXACTAMENTE el
#     recorrido del deslizamiento: la respuesta invertida nunca se sale
#     del cuadro ni entra por un borde;
#   - la entrada ocupa las posiciones 0..N-1, que caen centradas;
#   - el tallo de salida k se dibuja en la posicion k, que es donde esta
#     la PUNTA de la respuesta invertida en ese paso. Asi cada tallo nuevo
#     nace justo debajo del pico ambar que lo acaba de producir.
#
#   Y de regalo, la cifra del final se ve antes de leerla: el cian ocupa
#   seis posiciones y el ambar de abajo ocupa diez. La salida dura mas que
#   las dos entradas, y eso esta dibujado a la misma escala horizontal.
#
# TRES COSAS QUE COSTARON MEDIRLAS:
#
#   - El numero y el dibujo tienen que estar de acuerdo EN CADA INSTANTE,
#     y por eso cada paso son DOS `play` y no uno: primero desliza (el
#     contador sigue en el valor del tallo anterior, que es el ultimo
#     dibujado) y despues crece el tallo (el contador ya esta en su valor
#     y la respuesta esta QUIETA en su posicion). Con un solo `play` por
#     paso no hay ningun instante en el que la cifra, el solape y el tallo
#     digan los tres lo mismo.
#   - `contador_vivo` cocina sus estados en tiempo ABSOLUTO de la escena,
#     asi que el origen del deslizamiento se calcula sumando a
#     `renderer.time` los dos `play` que gasta el propio contador al
#     entrar (0.4 de salida del dato viejo + 0.6 de entrada). Su `paso` es
#     0.1 s y no 0.25: con 0.25 la cifra podia cambiar hasta 0.125 s antes
#     de que empezara a crecer el tallo, casi un cuarto de la animacion.
#   - El paso horizontal del deslizamiento se MIDE del eje ya colocado
#     (`eje.width / posiciones`), no se hereda de la constante: si
#     `encajar` tiene que escalar el grupo, un `shift` en unidades de
#     diseño desalinearia la respuesta de la rejilla poco a poco.
class Clip(Pieza):
    NOMBRE = "LA CONVOLUCION"
    TESIS = "deslizar, multiplicar, sumar"

    # Las dos secuencias son PARAMETROS elegidos (etiqueta gris), y son
    # CORTAS a proposito: con seis y cinco muestras el deslizamiento se
    # sigue a ojo. Con secuencias largas no se ve nada.
    X = (0.45, 0.85, 1.00, 0.75, 0.90, 0.55)
    H = (1.00, 0.80, 0.65, 0.55, 0.45)

    ANCHO_EJE = 5.40
    ALTO_ARR = 2.35
    ALTO_ABA = 1.95
    HUECO = 0.60
    PUNTA = 0.055
    T_DESLIZA = 0.55
    T_TALLO = 0.55

    def _luz(self, mob, encendido):
        """Enciende o apaga un dibujo SIN encender el relleno de las rayas.

        `set_opacity` sobre una polilinea le enciende el fill y la
        convierte en mancha; aqui se toca el trazo, y el relleno solo en
        los puntos, que es lo unico que de verdad es masa."""
        v = 1.0 if encendido else 0.0
        mob.set_stroke(opacity=v)
        for m in mob.family_members_with_points():
            if isinstance(m, Dot):
                m.set_fill(opacity=v)
        return mob

    def pieza(self):
        L = self.L
        x = np.array(self.X, dtype=float)
        h = np.array(self.H, dtype=float)
        y = sis.convolucion(x, h)
        largo = sis.largo_convolucion(x.size, h.size)

        # El dibujo y la cuenta son LA MISMA COSA: el tallo del paso k vale
        # el solape del paso k. Si algun dia dejaran de coincidir, el
        # render se para aqui en vez de publicar una pieza que miente.
        for k in range(largo):
            if abs(sis.solape(x, h, k)[2] - float(y[k])) > 1e-12:
                raise lz.FueraDelLienzo(
                    f"el tallo {k} dibuja {float(y[k]):.6f} y el solape de "
                    f"esa posicion vale {sis.solape(x, h, k)[2]:.6f}: el "
                    f"dibujo y la cuenta se han separado")

        # --- la rejilla, compartida por los dos carriles ---------------
        n_x, n_h = x.size, h.size
        i0, i1 = -(n_h - 1), n_x + n_h - 2      # el recorrido completo
        paso = self.ANCHO_EJE / (i1 - i0)
        centro = (i0 + i1) / 2.0

        def px(i):
            return (float(i) - centro) * paso

        vmax_arr = float(max(x.max(), h.max()))
        vmax_aba = float(y.max())
        y_a = 0.0                                # suelo del carril de arriba
        y_b = -(self.ALTO_ABA + self.HUECO)      # suelo del de abajo

        eje_a = sis.cero(ancho=self.ANCHO_EJE, y=y_a, color=LINEA)
        eje_b = sis.cero(ancho=self.ANCHO_EJE, y=y_b, color=LINEA)

        # La entrada y la respuesta van a la MISMA escala vertical: si cada
        # una se normalizara a su propio maximo, el solape que se ve no
        # seria el solape que se suma.
        t_x = sis.tallos(x, ancho=(n_x - 1) * paso, alto=self.ALTO_ARR,
                         color=CIAN, grosor=7.0, punta=0.075,
                         rango_y=(0.0, vmax_arr))
        t_x.shift([px((n_x - 1) / 2.0), y_a + self.ALTO_ARR / 2, 0])

        t_h = sis.tallos(h, ancho=(n_h - 1) * paso, alto=self.ALTO_ARR,
                         color=AMBAR, grosor=3.0, punta=self.PUNTA,
                         rango_y=(0.0, vmax_arr))
        t_h.shift([px(i0 + (n_h - 1) / 2.0), y_a + self.ALTO_ARR / 2, 0])

        # Un tallo por posicion del deslizamiento, cada uno ya en su sitio:
        # lo que se construye despues de `L.escena` no lleva su escala.
        salida = []
        for k in range(largo):
            s = sis.tallos([y[k]], ancho=0.0, alto=self.ALTO_ABA,
                           color=AMBAR, grosor=5.0, punta=self.PUNTA,
                           rango_y=(0.0, vmax_aba))
            s.shift([px(k), y_b + self.ALTO_ABA / 2, 0])
            salida.append(self._luz(s, False))

        eti = rot("LA SALIDA")
        eti.next_to(eje_b, DOWN, buff=0.20)

        # --- 1. la entrada -------------------------------------------
        # El carril de abajo se enseña vacio desde el primer fotograma: es
        # la promesa de donde va a aparecer la respuesta a lo que se ve.
        grupo = VGroup(eje_a, eje_b, eti, t_x, self._luz(t_h, False),
                       *salida)
        L.escena(grupo, t=0.9)
        self.leer(2.0)
        L.dato(medido(n_x, 0), "muestras de la entrada", medido=False)
        self.leer(2.0)

        # --- 2. la respuesta del sistema, encima ----------------------
        self._luz(t_h, True)
        self.play(FadeIn(t_h, run_time=0.7))
        L.dato(medido(n_h, 0), "muestras de la respuesta", medido=False,
               t=0.6)
        self.leer(2.0)

        # --- 3. se da la vuelta ---------------------------------------
        # Girar PI sobre el eje vertical es el espejo exacto: el pico pasa
        # de un extremo al otro y la respuesta queda lista para deslizar.
        self.play(Rotate(t_h, PI, axis=UP), run_time=1.0)
        self.leer(1.8)

        # --- 4. EL plano: deslizar, multiplicar, sumar ----------------
        paso_real = eje_a.width / (i1 - i0)
        dt = self.T_DESLIZA + self.T_TALLO
        t0 = self.renderer.time + 0.4 + 0.6      # lo que gasta el contador

        def valor_en(t):
            k = int((float(t) - t0) / dt)
            return medido(y[min(max(k, 0), largo - 1)], 2)

        L.contador_vivo("suma del solape", valor_en,
                        t_final=t0 + self.T_TALLO + (largo - 1) * dt,
                        paso=0.1, t=0.6, salida=0.4)

        for k in range(largo):
            if k:
                self.play(t_h.animate.shift(RIGHT * paso_real),
                          run_time=self.T_DESLIZA)
            self._luz(salida[k], True)
            self.play(GrowFromEdge(salida[k], DOWN), run_time=self.T_TALLO)
        self.leer(2.2)

        # --- 5. la sorpresa: la salida dura mas que las dos entradas ---
        # Se apaga la respuesta para dejar la comparacion sola: seis
        # posiciones de cian arriba, diez de ambar abajo, misma rejilla.
        L.parar_contadores()
        self.play(t_h.animate.set_stroke(opacity=0.0).set_fill(opacity=0.0),
                  run_time=0.6)
        L.dato(medido(largo, 0), "muestras que salen", medido=True, t=0.7)
        self.leer(2.8)
