# 16 · TRANSITORIO — una parte se apaga.
#
# El verbo visual: la respuesta al escalon se PARTE EN DOS. Un trozo
# oscila, se calma y muere; el otro es el valor donde se queda para
# siempre. La libreria no distingue esas dos mitades en una sola cifra,
# asi que el dibujo tampoco las junta en una sola curva: son DOS trazas
# (`sis.traza` dos veces, con el mismo `ancho`/`alto`/`rango_x`/`rango_y`
# y por tanto la MISMA malla de coordenadas) que arrancan pintadas del
# mismo AMBAR y se leen como una curva unica hasta que llega el remate y
# la primera se apaga de color. Partirla en dos objetos desde el
# principio evita tener que recolorear un TROZO de una sola polilinea,
# que no es una operacion que ofrezca la libreria.
#
# Los cuatro planos viven en el MISMO cuadro (mismo `ancho`, `alto` y
# `rango_y`): no hace falta ningun salto de escala en esta pieza, asi que
# se construye TODO una vez —las dos curvas, la banda, el nivel, la
# marca del asentamiento y los cuatro rotulos— y el resto de la pieza es
# solo encender y apagar opacidad, como manda el molde.
#
# DOS TRAMPAS QUE COSTARON UNA VUELTA:
#
#   - `sis.traza` NO recorta. El maximo de esta respuesta (3.34) y su
#     minimo (-0.07) se midieron con numpy ANTES de fijar `RANGO_Y`, para
#     que la curva entera caiga dentro del cuadro.
#   - El eje del cero no es `-alto/2`: como `RANGO_Y` no empieza en 0
#     (empieza en -0.3), el cero real cae un poco por encima del suelo
#     del cuadro. Se lo dejo calcular a `sis.cero(rango_y=..., alto=...)`.
class Clip(Pieza):
    NOMBRE = "TRANSITORIO"
    TESIS = "una parte se apaga"

    # Parametros elegidos (malla y sistema, no medidas): etiqueta gris si
    # se rotulan. Con N=140 la oscilacion de las 8 ultimas muestras baja a
    # 0.0005 -- ya esta asentada dentro de la ventana -- y el asentamiento
    # medido (77) es del sistema, no del cuadro.
    N = 140
    TAU = 16.0
    F = 0.05
    ANCHO_CAJA = ANCHO - 0.5
    ALTO_CAJA = 4.4
    RANGO_Y = (-0.3, 3.6)

    def pieza(self):
        L = self.L

        h = sis.h_amortiguada(N=self.N, tau=self.TAU, f=self.F)
        y = sis.respuesta_escalon(h)
        n = np.arange(self.N)
        final = sis.valor_final(h)
        maximo = float(y.max())
        asiento = sis.tiempo_asentamiento(y)

        # --- las dos mitades de la misma curva, ya coloreadas igual -----
        curva_va, punto = sis.traza(
            n[:asiento + 1], y[:asiento + 1], ancho=self.ANCHO_CAJA,
            alto=self.ALTO_CAJA, color=AMBAR, grosor=sis.TRAZO,
            rango_x=(0, self.N - 1), rango_y=self.RANGO_Y, escalones=True)
        curva_queda, _ = sis.traza(
            n[asiento:], y[asiento:], ancho=self.ANCHO_CAJA,
            alto=self.ALTO_CAJA, color=AMBAR, grosor=sis.TRAZO,
            rango_x=(0, self.N - 1), rango_y=self.RANGO_Y, escalones=True)
        suelo = sis.cero(ancho=self.ANCHO_CAJA, alto=self.ALTO_CAJA,
                         rango_y=self.RANGO_Y, color=LINEA)

        # La banda de tolerancia y el nivel permanente se construyen
        # AHORA, con el `punto` de estas mismas trazas: lo que se
        # construye DESPUES de L.escena no hereda el encaje del grupo.
        # Entran apagadas.
        semiancho = abs(final) * 0.02
        banda = sis.banda(final, semiancho, punto, ancho=self.ANCHO_CAJA,
                          color=APAGADO)
        banda.set_stroke(opacity=0.0)

        nivel = tf.nivel(final, punto, ancho=self.ANCHO_CAJA, color=AMBAR,
                         discontinua=True)
        nivel.set_stroke(opacity=0.0)

        marca = Dot(punto(asiento, y[asiento]), radius=0.075, color=TINTA)
        marca.set_opacity(0.0)

        eti_1 = rot("SALE: OSCILA", color=AMBAR)
        eti_1.next_to(suelo, DOWN, buff=0.24)
        eti_2 = rot("BANDA DE TOLERANCIA", color=APAGADO)
        eti_2.move_to(eti_1).set_opacity(0.0)
        eti_3 = rot("ASENTAMIENTO", color=TINTA)
        eti_3.move_to(eti_1).set_opacity(0.0)
        eti_4 = rot("QUEDA PARA SIEMPRE", color=AMBAR)
        eti_4.move_to(eti_1).set_opacity(0.0)

        grupo = VGroup(suelo, curva_va, curva_queda, banda, nivel, marca,
                       eti_1, eti_2, eti_3, eti_4)
        L.escena(grupo, t=0.9)
        L.dato(medido(maximo, 2), "el maximo", medido=True)
        self.leer(3.2)

        # --- 2. la banda de tolerancia alrededor del valor final -------
        self.play(banda.animate.set_stroke(opacity=1.0),
                  eti_1.animate.set_opacity(0.0),
                  eti_2.animate.set_opacity(1.0), run_time=0.8)
        L.dato(medido(final, 2), "valor final", medido=True)
        self.leer(3.4)

        # --- 3. el instante en que entra y ya no vuelve a salir --------
        self.play(marca.animate.set_opacity(1.0),
                  eti_2.animate.set_opacity(0.0),
                  eti_3.animate.set_opacity(1.0), run_time=0.7)
        self.play(Indicate(marca, color=TINTA, scale_factor=2.2),
                  run_time=0.7)
        L.dato(medido(asiento, 0), "muestras hasta asentar", medido=True)
        self.leer(3.2)

        # --- 4. remate: una mitad se apaga, la otra se queda -----------
        # `curva_va` (la mitad que oscila antes del asentamiento) pierde
        # color y trazo; `curva_queda` (la que ya estaba plana) se queda
        # exactamente donde estaba, en AMBAR, y el nivel la subraya.
        self.play(curva_va.animate.set_stroke(color=APAGADO, opacity=0.4),
                  marca.animate.set_opacity(0.0),
                  banda.animate.set_stroke(opacity=0.0),
                  nivel.animate.set_stroke(opacity=1.0),
                  eti_3.animate.set_opacity(0.0),
                  eti_4.animate.set_opacity(1.0),
                  run_time=1.3, rate_func=smooth)
        L.dato(medido(final, 2), "el valor que queda", medido=True, t=0.9)
        self.leer(3.6)
        self.leer(2.8)
