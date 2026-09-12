# 04 · FRESNEL — girar sin dar un tiron.
#
# Entre una recta (curvatura 0) y una curva circular (curvatura 1/R) no se
# puede pasar de golpe: habria que girar el volante instantaneamente. Hace
# falta un tramo donde la curvatura suba POCO A POCO, y la unica curva cuya
# curvatura crece proporcional al camino recorrido es la clotoide, que se
# dibuja con las integrales de Fresnel — dos integrales sin primitiva
# elemental. Toda carretera y toda via de tren llevan ese trozo.
#
# El verbo visual va al reves de lo que uno esperaria: primero el PROBLEMA
# en el plano de la curvatura (un escalon imposible), luego la rampa que lo
# arregla, y solo despues la curva que produce esa rampa. Asi la espiral de
# Cornu no aparece como una curiosidad bonita sino como la respuesta a algo
# que ya se ha visto que hace falta.
#
# La curvatura del tramo de clotoide NO se escribe a mano: se MIDE sobre
# los puntos que se van a dibujar (`esp.curvatura`), que es la unica forma
# de que el panel de arriba y el de abajo hablen de la misma curva.
class Clip(Pieza):
    NOMBRE = "FRESNEL"
    TESIS = "girar sin dar un tiron"

    # PARAMETROS elegidos: el trozo de clotoide que hace de transicion y
    # hasta donde se dibuja la espiral entera. Por encima de s=5.5 los ojos
    # se empastan en una mancha maciza y dejan de leerse como vueltas.
    S_TRANSICION = 1.0
    S_ESPIRAL = 4.8
    ANCHO_CAJA = ANCHO - 0.60

    def _panel_curvatura(self, con_rampa):
        """El plano de la curvatura: cuanto hay que girar el volante.

        Sin rampa, la curvatura salta de 0 a su valor de golpe: eso es el
        tiron. Con rampa, sube por el tramo de clotoide."""
        s, x, y = esp.clotoide(self.S_TRANSICION, 900)
        mitad = len(s) // 2
        k_medida = esp.curvatura(x, y, s)[mitad:]      # solo s >= 0
        s_medida = s[mitad:] - s[mitad]
        k_fin = float(k_medida[-1])

        P = esp.marco((0.0, 3.0), (-0.12, k_fin * 1.30),
                      ancho=self.ANCHO_CAJA, alto=3.00)
        piezas = [esp.eje_x(P)]
        recta = esp.curva(np.array([0.0, 1.0]), np.array([0.0, 0.0]), P,
                          color=APAGADO, grosor=esp.TRAZO)
        circulo = esp.curva(np.array([2.0, 3.0]),
                            np.array([k_fin, k_fin]), P,
                            color=APAGADO, grosor=esp.TRAZO)
        piezas += [recta, circulo]
        if con_rampa:
            piezas.append(esp.curva(1.0 + s_medida, k_medida, P,
                                    color=AMBAR, grosor=esp.TRAZO))
        else:
            piezas.append(esp.curva(np.array([1.0, 1.0]),
                                    np.array([0.0, k_fin]), P,
                                    color=CIAN, grosor=esp.TRAZO))
        eti_r = rot("RECTA")
        eti_r.next_to(P(0.5, 0.0), DOWN, buff=0.20)
        eti_c = rot("CURVA")
        eti_c.next_to(P(2.5, k_fin), UP, buff=0.20)
        # El rotulo del eje va al hueco de arriba a la izquierda, que es
        # la unica zona del panel donde no hay datos. Colgado del eje con
        # `next_to` caia en mitad del cuadro y la rampa lo cruzaba.
        eti_y = rot("CUANTO GIRAS")
        eti_y.move_to(P(0.58, k_fin * 1.15))
        return lz.agrupar(*piezas, eti_r, eti_c, eti_y)

    def pieza(self):
        L = self.L

        # --- 1. el tiron: la curvatura salta de golpe -----------------
        L.escena(self._panel_curvatura(False), t=0.9)
        self.leer(3.0)

        # --- 2. la rampa que lo arregla -------------------------------
        L.relevo(escena=self._panel_curvatura(True), t=0.9)
        self.leer(3.0)

        # --- 3. y la curva que produce esa rampa ----------------------
        LADO = 4.15
        P = esp.marco((-0.84, 0.84), (-0.84, 0.84), ancho=LADO, alto=LADO)
        s, x, y = esp.clotoide(self.S_ESPIRAL, 4400)
        espiral = esp.curva(x, y, P, color=AMBAR, grosor=2.4)
        espiral.set_stroke(opacity=0.0)
        ojo = esp.marca_en(P, 0.5, 0.5)
        ojo.set_opacity(0.0)
        viajero = Dot(P(x[0], y[0]), radius=0.075, color=TINTA)
        viajero.set_opacity(0.0)
        dibujo = lz.agrupar(esp.eje_x(P), esp.eje_y(P), espiral, ojo,
                            viajero)

        # Los ejes entran solos y la espiral se dibuja encima: el grupo se
        # entrega al carril con el trazo apagado y se enciende justo antes
        # del `Create`.
        L.relevo(escena=dibujo, t=0.7)
        espiral.set_stroke(opacity=1.0)
        self.play(Create(espiral, introducer=False), run_time=2.6,
                  rate_func=smooth)
        self.leer(2.0)

        # --- 4. el viaje: la curvatura crece sin parar ----------------
        viajero.set_opacity(1.0)
        self.play(MoveAlongPath(viajero, espiral), run_time=2.6,
                  rate_func=linear)
        self.leer(1.8)

        # --- 5. lo que le falta para llegar a su ojo ------------------
        # La cifra habla del punto donde se ha parado el viajero, y el
        # viajero es el unico punto blanco en pantalla. El limite todavia
        # NO se marca: dos puntos blancos separados por 0.0663 caen a once
        # pixeles uno de otro y se leerian como uno solo, con lo que la
        # cifra estaria señalando algo que no se ve.
        falta = esp.ojo_de_la_espiral(self.S_ESPIRAL)
        L.dato(medido(falta, 4), "lo que aun le falta")
        self.leer(3.0)

        # --- 6. y a donde va, aunque no llegue nunca ------------------
        # Ahora si: el viajero se apaga y en su sitio queda el limite.
        C, S = esp.fresnel(np.array([60.0]))
        L.morfeo(None,
                 dato=(medido(float(C[0]), 4), "a donde va la espiral"),
                 animaciones=[ojo.animate.set_opacity(1.0),
                              viajero.animate.set_opacity(0.0)], t=0.8)
        self.leer(3.0)
