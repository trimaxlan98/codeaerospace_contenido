# 14 · La vida de una pila
#
# El ultimo clip del curso. Tres imagenes y siete cifras: la escalera de
# consumo en decadas, la linea de tiempo del que despierta dos segundos
# cada hora, y — el remate — la autonomia contra cada cuanto despierta,
# con y sin la pila que se gasta sola.
#
# Por que la escalera va en LOG: los cuatro estados van de 10 uA a 160 mA,
# cuatro ordenes de magnitud. En lineal, tres de las cuatro barras serian
# una raya sobre el suelo.
#
# Cifras: los 160 mA y los 10 uA son hoja de datos (`chip.HOJA`, etiqueta
# APAGADA). La razon entre los dos, la corriente media, la autonomia y los
# dos techos de la grafica los calcula la libreria en el render (etiqueta
# AMBAR). Los dos numeros de la grafica se leen en el BORDE DERECHO de la
# ventana dibujada — despertar una vez por semana —, no en un punto que no
# se ve.
#
# Honestidad del remate: el 3 % anual de autodescarga NO lo calcula nadie,
# es el valor tipico de una pila de litio y por eso no aparece como cifra
# en pantalla. Lo que si esta calculado es la autonomia que sale de
# meterlo en `autonomia_dias(autodescarga_por_ano=0.03)`, que es lo que se
# rotula. Y la curva ambar no crece sin fin: se aplana. Ese techo es la
# ultima imagen del curso.
class Clip(Pieza):
    NUMERO = 14

    ESTADOS = ("DORMIR", "LIGERO", "PENSAR", "HABLAR")
    ANCHO_BARRAS, ALTO_BARRAS = 5.3, 4.2
    ANCHO_CURVA, ALTO_CURVA = 5.2, 3.7

    # La ventana del barrido: de despertar cada minuto a despertar una vez
    # por semana. El eje x va en decadas por el mismo motivo que la
    # escalera: en lineal, todo lo interesante se amontona en el origen.
    P0, P1 = 60.0, 7 * 24 * 3600.0
    AUTODESCARGA = 0.03            # tipico de una pila de litio, no medido
    T_DESPIERTO, PERIODO = 2.0, 3600.0
    CAPACIDAD_MAH = 2000.0

    # --- piezas -------------------------------------------------------
    def barras(self, colores):
        """La escalera de consumo. Misma geometria en los tres estados: lo
        unico que cambia es cual de las cuatro esta encendida."""
        return chip.escalones_log(self.corrientes, self.ESTADOS,
                                  ancho=self.ANCHO_BARRAS,
                                  alto=self.ALTO_BARRAS, colores=colores)

    def grafica(self, curvas):
        """Ejes en L, una o dos curvas, y el rotulo que dice que es la x.

        Sin el rotulo la grafica no significa nada: el eje no lleva marcas
        ni numeros (esa es la regla de `eje_ele`), asi que la unica pista
        de que la horizontal es "cada cuanto despierta" son esas tres
        palabras. Devuelve tambien el fondo y las trazas sueltas para
        poder animar el trazado por separado del resto."""
        ejes = chip.eje_ele(ancho=self.ANCHO_CURVA, alto=self.ALTO_CURVA)
        trazas = []
        for anos, color in curvas:
            ln, _ = chip.traza(np.log10(self.periodos), anos,
                               ancho=self.ANCHO_CURVA, alto=self.ALTO_CURVA,
                               color=color, rango_y=(0.0, self.techo))
            trazas.append(ln)
        cuerpo = VGroup(ejes, *trazas)
        etq = rot("CADA CUANTO DESPIERTA")
        etq.next_to(cuerpo, DOWN, buff=0.28)
        return VGroup(cuerpo, etq), VGroup(ejes, etq), trazas

    # --- la pieza -----------------------------------------------------
    def pieza(self):
        L = self.L
        H = chip.HOJA

        # Los cuatro estados, todos en microamperios para que la escalera
        # compare peras con peras.
        self.corrientes = [H["i_deep_sleep_ua"],
                           H["i_light_sleep_ua"],
                           H["i_modem_sleep_ma"] * 1000.0,
                           H["i_activo_ma"] * 1000.0]
        razon = self.corrientes[-1] / self.corrientes[0]
        i_media = chip.consumo_medio_ua(self.T_DESPIERTO, self.PERIODO)
        anos = chip.autonomia_dias(capacidad_mah=self.CAPACIDAD_MAH,
                                   t_despierto_s=self.T_DESPIERTO,
                                   periodo_s=self.PERIODO) / 365.0

        self.periodos = np.logspace(np.log10(self.P0), np.log10(self.P1), 60)
        kw = dict(capacidad_mah=self.CAPACIDAD_MAH,
                  t_despierto_s=self.T_DESPIERTO)
        ideal = chip.barrido_autonomia(self.periodos, **kw) / 365.0
        real = chip.barrido_autonomia(self.periodos,
                                      autodescarga_por_ano=self.AUTODESCARGA,
                                      **kw) / 365.0
        self.techo = float(ideal.max())

        # --- 1. lo que cuesta hablar ----------------------------------
        b1 = self.barras([APAGADO, APAGADO, APAGADO, AMBAR])
        L.escena(b1, animacion=FadeIn(b1, lag_ratio=0.12, run_time=1.5))
        self.wait(0.6)
        L.dato(f"{H['i_activo_ma']:.0f}", "miliamperios hablando",
               medido=False, t=0.6)
        self.wait(3.4)

        # --- 2. y lo que cuesta dormir --------------------------------
        # Relevo de los dos carriles a la vez: la barra encendida y la
        # cifra tienen que cambiar en el mismo movimiento, o quedan dos
        # segundos con la barra de dormir y el 160 debajo.
        b2 = self.barras([AMBAR, APAGADO, APAGADO, APAGADO])
        L.relevo(escena=b2,
                 dato=lz.dato(f"{H['i_deep_sleep_ua']:.0f}",
                              "microamperios durmiendo", medido=False))
        self.wait(3.6)

        # --- 3. los dos extremos, medidos uno contra otro -------------
        b3 = self.barras([TINTA, APAGADO, APAGADO, TINTA])
        L.relevo(escena=b3,
                 dato=lz.dato(lz.miles(int(round(razon))),
                              "veces entre los extremos"))
        self.wait(3.5)

        # --- 4. la integral: dos segundos cada hora -------------------
        # Cada rayita es un despertar. La autonomia no la decide el pico
        # de consumo sino cuanto tiempo pasa el chip en cada estado, y eso
        # es lo que dibuja esta linea.
        marcas = chip.marcas_tiempo((np.arange(6) + 0.5) * self.PERIODO,
                                    ancho=5.2, alto=3.4,
                                    t_max=6 * self.PERIODO, color=AMBAR,
                                    grosor=4.0)
        base = lz.regla(marcas.get_bottom()[1], ancho=5.5, color=APAGADO,
                        grosor=1.8)
        etq = rot("CADA HORA")
        etq.next_to(base, DOWN, buff=0.30)
        reloj = VGroup(base, marcas, etq)
        L.relevo(escena=reloj,
                 dato=lz.dato(str(int(round(i_media))),
                              "microamperios de media"),
                 animacion=FadeIn(reloj, lag_ratio=0.15, run_time=1.2))
        self.wait(3.6)

        # --- 5. lo que eso dura con una pila normal -------------------
        # El dibujo se queda: es el mismo regimen, solo que ahora la cifra
        # dice a cuanto tiempo equivale.
        L.dato(medido(anos, 1), "años de autonomia")
        self.wait(3.9)

        # --- 6. despertar menos: la autonomia sube --------------------
        # La grafica entra UNA vez y se queda hasta el final: las dos
        # curvas viven en el mismo grupo (el mismo ocupante del carril) y
        # lo que cambia es cual esta dibujada. Relevar el carril entero
        # para añadir la segunda curva apagaba la primera medio segundo y
        # la costura se leia como un corte, justo en el remate del curso.
        #
        # La cifra es el BORDE DERECHO de la curva dibujada (despertar una
        # vez por semana), no un punto cualquiera de la simulacion.
        grafica, fondo, (c_ideal, c_real) = self.grafica(
            [(ideal, TINTA), (real, AMBAR)])
        L.relevo(escena=grafica,
                 dato=lz.dato(medido(float(ideal[-1]), 1),
                              "años con una pila ideal"),
                 animacion=AnimationGroup(
                     FadeIn(fondo, run_time=0.8),
                     Create(c_ideal, run_time=1.7), lag_ratio=0.0))
        self.wait(3.3)

        # --- 7. el remate del curso: la pila se gasta sola ------------
        # La misma grafica y la misma escala, y encima la de verdad: una
        # pila de litio pierde sola un 2-3 % al año. La ideal sigue
        # subiendo; la ambar se aplana. A partir de ese techo ya no manda
        # el circuito, manda la pila.
        #
        # La cifra se apaga ANTES de trazar la curva nueva. Es la regla de
        # la casa: mientras se dibuja la ambar, el 21.7 hablaria de la
        # otra curva. Un hueco sin cifra es un estado valido del lienzo;
        # una cifra que no corresponde, no.
        L.quitar("dato", t=0.4)
        self.play(Create(c_real),
                  c_ideal.animate.set_stroke(color=APAGADO), run_time=1.6)
        L.dato(medido(float(real[-1]), 1), "años con una pila real")
        self.wait(5.2)
