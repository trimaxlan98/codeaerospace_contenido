# 04 · EL ESCALON — la suma de infinitos impulsos.
#
# El verbo visual: el escalon (CIAN) se enciende y se queda encendido para
# siempre. Se descompone resaltando, uno a uno, cada muestra que esta
# encendida -- cada una es su propio impulso. Entra en la caja `h` y sale
# (AMBAR) la respuesta al escalon, que la libreria calcula como la suma
# acumulada de la respuesta al impulso (`np.cumsum(h)`, sin volver a medir
# el sistema). La cifra final es donde se asienta esa suma.
#
# Sigue el molde de 01-el-impulso: todos los estados de cada cuadro se
# construyen ANTES de entregarlo al lienzo, y lo que cambia despues
# (colores, opacidad) actua sobre objetos que ya viven dentro del grupo
# colocado -- nunca sobre piezas nuevas.
class Clip(Pieza):
    NOMBRE = "EL ESCALON"
    TESIS = "la suma de infinitos impulsos"

    # Parametros elegidos (malla, no medidas): etiqueta gris si se rotulan.
    N_ENTRADA = 16
    N0 = 5
    # N_H=32 se midio y mentia: las ultimas 8 muestras seguian oscilando
    # un 18% de su propio "valor final", y ese valor final se alejaba un
    # 2.2% de donde la respuesta se asienta de verdad. Con N_H=80 la
    # oscilacion de las ultimas 8 muestras baja a 0.0005 -- ya esta
    # asentada -- y el numero rotulado coincide con el dibujo.
    N_H = 80
    TAU = 9.0
    F = 0.11
    ANCHO_CAJA = ANCHO - 0.5
    ALTO_CAJA = 4.2

    def pieza(self):
        L = self.L

        # --- 1. el escalon: se enciende y se queda ---------------------
        x = sis.escalon(N=self.N_ENTRADA, n0=self.N0)
        tallo_in = sis.tallos(x, ancho=self.ANCHO_CAJA, alto=self.ALTO_CAJA,
                              color=CIAN, grosor=3.0, punta=0.05,
                              rango_y=(0.0, 1.0))
        suelo_in = sis.cero(ancho=self.ANCHO_CAJA, y=-self.ALTO_CAJA / 2,
                            color=LINEA)
        eti_in = rot("ENTRA EL ESCALON", color=CIAN)
        eti_in.next_to(suelo_in, DOWN, buff=0.24)

        grupo_in = VGroup(suelo_in, tallo_in, eti_in)
        L.escena(grupo_in, t=1.0)
        self.leer(3.0)

        # --- 1b. se descompone: cada muestra encendida es un impulso ---
        # `tallo_in` guarda, por muestra, una Line seguida de un Dot (el
        # `punta` pasado es distinto de cero): el indice 2*i, 2*i+1 es la
        # muestra i entera, y siguen vivos -- ya escalados -- dentro del
        # grupo que `L.escena` acaba de colocar.
        # Solo se escala el Dot (su centro es la propia punta, asi que
        # crecer no lo mueve); la Line SOLO cambia de color y vuelve, sin
        # escalar -- escalar una raya que nace en el suelo la habria
        # estirado hacia abajo, por debajo del eje, encima del rotulo.
        anims = []
        for i in range(self.N0, self.N_ENTRADA):
            linea, punto = tallo_in[2 * i], tallo_in[2 * i + 1]
            anims.append(AnimationGroup(
                Indicate(punto, color=AMBAR, scale_factor=1.6),
                linea.animate(rate_func=there_and_back).set_stroke(
                    color=AMBAR)))
        self.play(LaggedStart(*anims, lag_ratio=0.45), run_time=2.2)
        self.leer(2.8)

        # --- 2. entra en la caja ----------------------------------------
        mini_in = sis.tallos(x, ancho=3.0, alto=1.6, color=CIAN,
                             grosor=2.2, punta=0.035, rango_y=(0.0, 1.0))
        caja = sis.caja(texto="h", ancho=1.8, alto=1.1, color=AMBAR)
        caja.move_to(ORIGIN)
        mini_in.next_to(caja, UP, buff=0.5)
        flecha_in = sis.flecha(mini_in.get_bottom(), caja.get_top(),
                               color=CIAN, grosor=sis.TRAZO_FINO)
        eti_caja = rot("ENTRA EN LA CAJA", color=CIAN)
        eti_caja.next_to(caja, DOWN, buff=0.3)

        grupo_caja = VGroup(mini_in, flecha_in, caja, eti_caja)
        L.escena(grupo_caja, t=1.0)
        self.leer(3.0)

        # --- 3. sale la respuesta: la suma acumulada --------------------
        # No se vuelve a medir el sistema: `respuesta_escalon` es el
        # cumsum de `h`, la misma respuesta al impulso de siempre. Con 80
        # muestras una peineta de tallos es ilegible, asi que se dibuja
        # con `traza` (escalonada, para no fingir que hay algo entre
        # muestras): el maximo/minimo real de esta `y` se midio con
        # numpy antes de fijar `rango_y` (`traza` no recorta).
        h = sis.h_amortiguada(N=self.N_H, tau=self.TAU, f=self.F)
        y = sis.respuesta_escalon(h)
        n = np.arange(self.N_H)
        curva, punto = sis.traza(n, y, ancho=self.ANCHO_CAJA,
                                 alto=self.ALTO_CAJA, color=AMBAR,
                                 grosor=sis.TRAZO,
                                 rango_x=(0, self.N_H - 1),
                                 rango_y=(0.0, 1.9), escalones=True)
        suelo_out = sis.cero(ancho=self.ANCHO_CAJA, y=-self.ALTO_CAJA / 2,
                             color=LINEA)
        eti_out = rot("SALE: SUMA ACUMULADA", color=AMBAR)
        eti_out.next_to(suelo_out, DOWN, buff=0.24)

        # El nivel de asentamiento se construye AHORA (con el `punto` de
        # esta misma traza, en su misma escala) y entra apagado en el
        # grupo: lo que se construye DESPUES de `L.escena` no hereda el
        # encaje del grupo. `set_stroke(opacity=0)` lo apaga sin encender
        # ningun relleno.
        valor_final = sis.valor_final(h)
        nivel = tf.nivel(valor_final, punto, ancho=self.ANCHO_CAJA,
                         color=LINEA, discontinua=True)
        nivel.set_stroke(opacity=0.0)

        grupo_out = VGroup(suelo_out, curva, nivel, eti_out)
        L.escena(grupo_out, t=1.0)
        self.leer(3.0)

        # --- 4. remate: se asienta en un valor ---------------------------
        # El dibujo de la curva no cambia -- sigue siendo la misma
        # respuesta ya asentada -- pero el nivel se enciende A LA VEZ que
        # la cifra: es lo que permite comprobar a ojo que el numero es el
        # sitio exacto donde la curva se queda quieta.
        self.play(nivel.animate.set_stroke(opacity=1.0), run_time=0.5)
        L.relevo(dato=(medido(valor_final, 2), "valor final"), t=0.9)
        self.leer(3.2)
        self.leer(3.4)
