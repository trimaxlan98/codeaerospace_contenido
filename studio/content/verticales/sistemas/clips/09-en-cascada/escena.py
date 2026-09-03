# 09 · EN CASCADA — el orden no importa.
#
# La CAJA vuelve a ser protagonista: `sis.cadena([caja1, caja2], largo)`
# pone dos sistemas en fila y devuelve los dos puntos de sus extremos. El
# verbo visual: la señal ATRAVIESA la cadena h1 -> h2 y sale una forma
# (AMBAR); despues las dos cajas SE INTERCAMBIAN DE SITIO de verdad —cada
# una viaja por un arco distinto, no desaparece y reaparece— y la MISMA
# forma sale otra vez de la cadena h2 -> h1. El REMATE es lo que hace la
# cifra comprobable sin tener que recordar nada: las dos salidas se
# dibujan SUPERPUESTAS, mismo `rango_y`, mismo origen, y el ojo ve UNA
# linea en vez de tener que fiarse de la memoria de hace cinco segundos.
#
# Por que un arco y no un salto: `Rectangle.animate.move_to(...)` a secas
# dibujaria dos rectangulos identicos cruzandose en linea recta por el
# centro, que en un rectangulo sin relieve se lee como "uno de los dos
# desaparecio un instante". Dandoles a los dos el MISMO `path_arc` con
# signo contrario, cada caja recorre un arco que se curva para el lado
# opuesto del arco de la otra: se ve el intercambio, no una teletransportacion.
#
# LA GUARDIA NO ES `np.array_equal`, Y ESO SE MIDIO: las dos salidas son
# dos convoluciones calculadas por CAMINOS distintos (h1 primero o h2
# primero), y `sis.convolucion` suma en un bucle: sumar los mismos numeros
# en otro orden mueve el ultimo bit de un float64 aunque el resultado
# matematico sea identico. Medido con estos parametros: los arrays NO son
# iguales bit a bit, difieren en 1.3e-15 sobre un pico de 1.9 — el ruido
# de redondeo de la maquina, no un fallo. Un desfase de verdad (un indice
# corrido) daria una diferencia del orden de la propia señal, no del
# orden del epsilon de punto flotante. Por eso la comprobacion de mas
# abajo es una tolerancia muy por debajo de la señal y muy por encima de
# ese ruido: pasa el redondeo honesto y no pasaria un desfase disfrazado
# de "el error redondea a cero".
#
# La cadena, las dos formas de salida y el remate se construyen ANTES de
# la `L.escena`/`L.relevo` que los monta, en el MISMO grupo cada vez, para
# que compartan la escala que `encajar` decide una sola vez por plano. Las
# dos salidas comparten ademas el MISMO `rango_y` en las tres veces que se
# dibujan (junto a la cadena y en el remate): si cada una se normalizara
# por su cuenta, saldrian identicas en el dibujo aunque no lo fueran.
#
# El carril de la cifra NO se vacia durante el intercambio: en cuanto la
# señal atraviesa la cadena se pone "cuantas muestras salen" (sigue siendo
# cierto aunque las cajas cambien de sitio, porque el orden no cambia la
# longitud) y se deja puesto —sin pasar `dato=`— hasta que el remate prueba
# la igualdad y ahi si cambia a la cifra final.
#
# La animacion del intercambio (mover las dos cajas) y el rotulo que la
# nombra (`etiqueta.animate.set_opacity`) van en DOS `play` distintos a
# proposito: la casa mide que `Rotate`/movimiento y `set_color` en el
# mismo `play` se pisan, y aunque aqui no hay `set_color`, separar el
# movimiento de cualquier cambio de opacidad de OTRO mobject cuesta cero y
# deja fuera de duda esa trampa.
class Clip(Pieza):
    NOMBRE = "EN CASCADA"
    TESIS = "el orden no importa"

    # --- geometria: parametros elegidos (etiqueta apagada) --------------
    CAJA_ANCHO = 1.35
    CAJA_ALTO = 3.5
    LARGO = 0.6            # longitud de cada flecha de sis.cadena
    TRAZA_ANCHO = 1.05
    TRAZA_ALTO = 2.6
    HUECO = 0.10            # aire entre una traza y la punta de su flecha

    # el remate: una sola caja ancha donde las dos salidas se superponen
    REM_ANCHO = 5.26
    REM_ALTO = 3.6

    def pieza(self):
        L = self.L

        # --- 1. la materia: dos sistemas y la señal que los atraviesa --
        # N=30 y no 64: con 64 muestras en un cuadro de menos de un
        # centimetro la entrada era un borron cian ilegible en un movil.
        x = sis.dos_tonos(0.05, 0.30, N=30)
        h1 = sis.h_amortiguada(N=24, tau=6.0, f=0.09)
        h2 = sis.paso_bajo(0.12, M=15)
        y_h1_h2 = sis.convolucion(sis.convolucion(x, h1), h2)   # orden 1
        y_h2_h1 = sis.convolucion(sis.convolucion(x, h2), h1)   # orden 2
        error = sis.error_conmutar(h1, h2, x)

        # Guardia (ver cabecera): tolerancia muy por debajo de la señal
        # y muy por encima del ruido de redondeo, no una igualdad literal.
        diferencia = float(np.max(np.abs(y_h1_h2 - y_h2_h1)))
        if diferencia > 1e-9:
            raise lz.FueraDelLienzo(
                f"en-cascada: las dos salidas difieren {diferencia:.3e}, "
                f"mas de lo que explica el redondeo de punto flotante: "
                f"revisa el orden de la convolucion")

        # El MISMO rango para las dos salidas, en las TRES veces que se
        # dibujan: es la unica forma honesta de dibujar "identica".
        lo = float(min(y_h1_h2.min(), y_h2_h1.min()))
        hi = float(max(y_h1_h2.max(), y_h2_h1.max()))
        pad = 0.12 * (hi - lo)
        RANGO_SAL = (lo - pad, hi + pad)

        lo_x, hi_x = float(x.min()), float(x.max())
        pad_x = 0.12 * (hi_x - lo_x)
        RANGO_ENT = (lo_x - pad_x, hi_x + pad_x)

        # --- 2. el dibujo: TODO se construye antes de la primera L.escena
        caja1 = sis.caja(texto="h1", ancho=self.CAJA_ANCHO,
                         alto=self.CAJA_ALTO, acento=False)
        caja2 = sis.caja(texto="h2", ancho=self.CAJA_ANCHO,
                         alto=self.CAJA_ALTO, acento=False)
        cadena, p_ini, p_fin = sis.cadena([caja1, caja2], largo=self.LARGO)

        entrada, _ = sis.traza(np.arange(x.size), x, ancho=self.TRAZA_ANCHO,
                               alto=self.TRAZA_ALTO, color=CIAN,
                               grosor=sis.TRAZO, rango_x=(0, x.size - 1),
                               rango_y=RANGO_ENT, escalones=True)
        entrada.move_to([p_ini[0] - self.HUECO - self.TRAZA_ANCHO / 2, 0, 0])

        salida1, _ = sis.traza(np.arange(y_h1_h2.size), y_h1_h2,
                               ancho=self.TRAZA_ANCHO, alto=self.TRAZA_ALTO,
                               color=AMBAR, grosor=sis.TRAZO,
                               rango_x=(0, y_h1_h2.size - 1),
                               rango_y=RANGO_SAL, escalones=True)
        salida1.move_to([p_fin[0] + self.HUECO + self.TRAZA_ANCHO / 2, 0, 0])

        # La forma de la segunda ronda: MISMO rango, MISMA posicion. Se
        # cocina ya (lo que se construye despues de `L.escena` no hereda
        # su escala) y se enciende mas tarde.
        salida2, _ = sis.traza(np.arange(y_h2_h1.size), y_h2_h1,
                               ancho=self.TRAZA_ANCHO, alto=self.TRAZA_ALTO,
                               color=AMBAR, grosor=sis.TRAZO,
                               rango_x=(0, y_h2_h1.size - 1),
                               rango_y=RANGO_SAL, escalones=True)
        salida2.move_to(salida1.get_center())
        salida2.set_stroke(opacity=0.0)

        mid_x = (caja1.get_center()[0] + caja2.get_center()[0]) / 2.0
        techo = max(caja1.get_top()[1], caja2.get_top()[1])
        etiqueta = rot("SE INTERCAMBIAN")
        etiqueta.move_to([mid_x, techo + 0.30 + etiqueta.height / 2, 0])
        etiqueta.set_opacity(0.0)

        entrada.set_stroke(opacity=0.0)
        salida1.set_stroke(opacity=0.0)

        escena_completa = VGroup(cadena, entrada, salida1, salida2, etiqueta)

        # --- 3. la cadena, quieta: dos sistemas ya conocidos ------------
        L.escena(escena_completa, t=1.0)
        self.leer(2.6)

        # --- 4. la señal atraviesa: entra CIAN, sale AMBAR --------------
        self.play(entrada.animate.set_stroke(opacity=1.0),
                  salida1.animate.set_stroke(opacity=1.0), run_time=1.1)
        # Cierto ANTES del intercambio y cierto DESPUES: el orden no
        # cambia cuanto dura la salida. Se deja puesto durante el cambio.
        L.dato(medido(y_h1_h2.size, 0), "muestras de salida", medido=True,
              t=0.6)
        self.leer(3.0)

        # --- 5. las dos cajas SE INTERCAMBIAN, fisicamente ---------------
        self.play(etiqueta.animate.set_opacity(1.0), run_time=0.5)
        pos1 = caja1.get_center().copy()
        pos2 = caja2.get_center().copy()
        self.play(caja1.animate(path_arc=120 * DEGREES).move_to(pos2),
                  caja2.animate(path_arc=-120 * DEGREES).move_to(pos1),
                  run_time=1.8, rate_func=smooth)
        self.leer(2.6)

        # --- 6. la salida, otra vez: la cifra de arriba SIGUE en pie ----
        self.play(etiqueta.animate.set_opacity(0.0),
                  salida1.animate.set_stroke(opacity=0.0),
                  salida2.animate.set_stroke(opacity=1.0), run_time=0.9)
        self.leer(2.8)

        # --- 7. EL REMATE: las dos salidas, SUPERPUESTAS -----------------
        # Mismo rango_y, mismo origen, mismo ancho: si el orden de verdad
        # no importa, las dos polilineas caen una encima de la otra y se
        # ve UNA linea. El fondo (gruesa, translucida) es el orden
        # h1->h2; ENCIMA (fina) es el orden h2->h1 y aparece DESPUES, para
        # poder comparar el instante justo antes y justo despues de que
        # se encienda. El dato de arriba sigue siendo el de antes: todavia
        # no toca la cifra final, toca ENSEÑARLA primero.
        eje_r = sis.cero(ancho=self.REM_ANCHO, y=-self.REM_ALTO / 2,
                         color=LINEA)
        fondo, _ = sis.traza(np.arange(y_h1_h2.size), y_h1_h2,
                             ancho=self.REM_ANCHO, alto=self.REM_ALTO,
                             color=AMBAR, grosor=7.0,
                             rango_x=(0, y_h1_h2.size - 1),
                             rango_y=RANGO_SAL, escalones=True)
        fondo.set_stroke(opacity=0.32)
        encima, _ = sis.traza(np.arange(y_h2_h1.size), y_h2_h1,
                              ancho=self.REM_ANCHO, alto=self.REM_ALTO,
                              color=AMBAR, grosor=sis.TRAZO_FINO,
                              rango_x=(0, y_h2_h1.size - 1),
                              rango_y=RANGO_SAL, escalones=True)
        encima.set_stroke(opacity=0.0)
        etiqueta_r = rot("LAS DOS SALIDAS", color=AMBAR)
        etiqueta_r.next_to(eje_r, DOWN, buff=0.24)

        grupo_remate = VGroup(eje_r, etiqueta_r, fondo, encima)
        L.relevo(escena=grupo_remate, t=0.9)
        self.leer(2.2)

        self.play(encima.animate.set_stroke(opacity=1.0), run_time=0.8)
        self.leer(2.6)

        # --- 8. la cifra: cuanto cambio la salida al cambiar el orden ---
        L.dato(medido(error, 2), "diferencia entre ordenes", medido=True,
              t=0.7)
        self.leer(3.4)
        self.leer(2.8)
