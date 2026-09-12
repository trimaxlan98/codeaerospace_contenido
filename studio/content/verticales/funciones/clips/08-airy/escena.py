# 08 · AIRY — el borde de la sombra.
#
# La optica de rayos promete un escalon: luz de un lado, nada del otro. Lo
# que hay de verdad es la funcion de Airy: franjas que se apagan hacia la
# luz y un desvanecimiento suave hacia la sombra. Ni el borde esta donde
# dice la geometria, ni el punto mas brillante esta en el borde.
#
# Airy no salio de un problema de matematicas: salio de mirar un arcoiris.
# Los arcos supernumerarios que a veces se ven por dentro del arcoiris
# principal son estas franjas.
#
# El verbo visual es la sustitucion: primero el escalon que promete la
# geometria (CIAN, la version facil), y encima lo que de verdad mide un
# fotometro (AMBAR). Se dibujan en el MISMO cuadro para que la sustitucion
# se vea, y el escalon se queda APAGADO de fondo en vez de desaparecer:
# la pieza es la diferencia entre los dos.
class Clip(Pieza):
    NOMBRE = "AIRY"
    TESIS = "el borde de la sombra"

    # PARAMETROS elegidos: la ventana. Por debajo de x = -9 la serie de
    # Airy empieza a perder cifras por cancelacion y el curso no dibuja
    # ahi.
    RX = (-8.6, 3.0)
    RY = (-0.10, 1.18)
    ANCHO_CAJA = ANCHO - 0.55
    ALTO_CAJA = 4.30

    def pieza(self):
        L = self.L
        P = esp.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)

        # --- el escalon que promete la optica de rayos ---------------
        xs = np.linspace(self.RX[0], self.RX[1], 1600)
        escalon = esp.curva(xs, (xs < 0.0).astype(float), P, color=CIAN,
                            grosor=esp.TRAZO)
        eti_luz = rot("LUZ", color=APAGADO)
        eti_luz.move_to(P(-6.0, 1.09))
        eti_sombra = rot("SOMBRA", color=APAGADO)
        eti_sombra.move_to(P(1.5, 1.09))
        dibujo = lz.agrupar(esp.recuadro(P), esp.eje_x(P), escalon,
                            eti_luz, eti_sombra)

        L.escena(dibujo, t=0.9)
        self.leer(3.4)

        # --- lo que de verdad hay -------------------------------------
        xr, inten = esp.borde_de_sombra(self.RX[0], self.RX[1], 2400)
        real = esp.curva(xr, inten, P, color=AMBAR, grosor=esp.TRAZO)
        real.set_stroke(opacity=0.0)
        pico = esp.pico_de_sombra()
        marca = esp.marca_en(P, pico, 1.0)
        plom = esp.plomada(P, pico, 1.0, color=TINTA, trozos=9)
        marca.set_opacity(0.0)
        plom.set_stroke(opacity=0.0)
        # Las piezas del segundo cuadro se CONSTRUYEN otra vez, no se
        # copian del primero. Un mobject que ya paso por `encajar` lleva
        # encima el desplazamiento y la escala que le dio aquel grupo; si
        # se mete en un grupo nuevo, el nuevo `encajar` se los aplica
        # ENCIMA y la pieza llega descolocada. En el primer render el
        # escalon de referencia salia flotando por encima del cuadro.
        #
        # Y el escalon de referencia va en APAGADO OPACO, no en cian al
        # 30 %: sobre este azul, un trazo traslucido se convierte en un
        # color que no es ninguno de los dos (medido en el curso 31).
        escalon2 = esp.curva(xs, (xs < 0.0).astype(float), P,
                             color=APAGADO, grosor=esp.TRAZO_FINO)
        luz2 = rot("LUZ", color=APAGADO)
        luz2.move_to(P(-6.0, 1.09))
        sombra2 = rot("SOMBRA", color=APAGADO)
        sombra2.move_to(P(1.5, 1.09))
        dibujo2 = lz.agrupar(esp.recuadro(P), esp.eje_x(P), escalon2,
                             real, plom, marca, luz2, sombra2)

        L.relevo(escena=dibujo2, t=0.7)
        real.set_stroke(opacity=1.0)
        self.play(Create(real, introducer=False), run_time=2.4,
                  rate_func=smooth)
        self.leer(2.8)

        # --- donde brilla mas no es el borde -------------------------
        L.morfeo(None, dato=(medido(pico, 4), "donde mas brilla"),
                 animaciones=[marca.animate.set_opacity(1.0),
                              plom.animate.set_stroke(opacity=1.0)],
                 t=0.8)
        self.leer(3.4)

        # --- y en el borde no hay ni la mitad ------------------------
        L.dato(medido(esp.luz_en_el_borde() * 100.0, 2),
               "por ciento de luz ahi")
        self.leer(3.4)

        # --- la funcion que hay detras -------------------------------
        RY2 = (-0.48, 0.62)
        Q = esp.marco(self.RX, RY2, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)
        ai = esp.curva(xr, esp.airy_Ai(xr), Q, color=AMBAR,
                       grosor=esp.TRAZO)
        c1 = float(esp.ceros_Ai(1)[0])
        marca_c = esp.marca_en(Q, c1, 0.0)
        eti_ai = rot("AIRY", color=AMBAR)
        eti_ai.move_to(Q(-7.0, 0.52))
        panel = lz.agrupar(esp.recuadro(Q), esp.eje_x(Q), ai, marca_c,
                           eti_ai)

        L.relevo(escena=panel,
                 dato=(medido(c1, 4), "su primer cero"), t=0.9)
        self.leer(3.6)
