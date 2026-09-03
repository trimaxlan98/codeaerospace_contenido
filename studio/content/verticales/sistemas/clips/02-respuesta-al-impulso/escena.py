# 02 · RESPUESTA AL IMPULSO — un golpe lo dice todo.
#
# Primera aparicion de verdad de `sis.caja`, y el verbo visual ES el
# diagrama de sistema: una caja neutra que nadie conoce todavia, un golpe
# (CIAN) que entra por la izquierda, y lo que sale por la derecha (AMBAR)
# una vez que el golpe ya paso — la caja se enciende porque a partir de
# ahi queda determinada para siempre. El remate tira la caja: la forma que
# dejo ES el contenido, y ya no hace falta el dibujo que la produjo.
#
# `sis.h_amortiguada()` se llama con sus parametros por defecto (N, tau,
# f, retardo son ELEGIDOS: no se rotulan, no son una medida). La unica
# cifra que se rotula es `sis.cola(h)`: con `retardo=0` la señal empieza
# en la muestra 0 (a diferencia del impulso desplazado de la pieza 01), asi
# que aqui `cola` SI es cuanto dura la respuesta.
class Clip(Pieza):
    NOMBRE = "RESPUESTA AL IMPULSO"
    TESIS = "un golpe lo dice todo"

    def pieza(self):
        L = self.L

        # --- 1. la caja sola: nadie sabe todavia lo que hace -----------
        caja1 = sis.caja(texto="h", ancho=2.8, alto=3.2, acento=False)
        L.escena(VGroup(caja1), t=1.0)
        self.leer(4.4)

        # --- 2. entra el impulso por la izquierda (CIAN) ----------------
        caja2 = sis.caja(texto="h", ancho=2.0, alto=2.8, acento=False)
        caja2.shift(RIGHT * 1.3)
        entrada = sis.tallos(sis.impulso(N=9, n0=4), ancho=1.6, alto=2.0,
                             color=CIAN, grosor=2.6, punta=0.05,
                             rango_y=(0.0, 1.0))
        entrada.next_to(caja2, LEFT, buff=0.9)
        flecha_in = sis.flecha(entrada.get_right() + RIGHT * 0.06,
                               caja2.get_left(), color=CIAN,
                               grosor=sis.TRAZO_FINO)
        L.escena(VGroup(entrada, flecha_in, caja2), t=1.0, salida=0.45)
        self.leer(4.4)

        # --- 3. sale la respuesta por la derecha (AMBAR): la caja se ---
        #        enciende, porque el golpe ya la determino para siempre
        caja3 = sis.caja(texto="h", ancho=2.0, alto=2.8, acento=True)
        caja3.shift(LEFT * 1.3)
        h = sis.h_amortiguada()   # N, tau, f, retardo: parametros elegidos
        salida = sis.tallos(h, ancho=2.6, alto=2.8, color=AMBAR,
                            grosor=2.2, punta=0.045)
        salida.next_to(caja3, RIGHT, buff=0.7)
        flecha_out = sis.flecha(caja3.get_right() + RIGHT * 0.05,
                                salida.get_left() + LEFT * 0.05,
                                color=AMBAR, grosor=sis.TRAZO_FINO)
        grupo3 = VGroup(caja3, flecha_out, salida)
        L.relevo(escena=grupo3,
                dato=(medido(sis.cola(h), 0), "muestras de cola"),
                t=1.1, salida=0.45)
        self.leer(5.0)

        # --- 4. remate: la forma se agranda y ocupa el cuadro entero ---
        #        (la cifra no cambia: es la misma cola de la misma h; a
        #        partir de aqui la caja se puede tirar, la forma la
        #        sustituye)
        grande = sis.tallos(h, ancho=ANCHO - 0.4, alto=4.4, color=AMBAR,
                            grosor=3.0, punta=0.06)
        L.relevo(escena=VGroup(grande), t=1.1, salida=0.5)
        self.leer(4.0)
        self.leer(3.4)
