# 06 · BESSEL — el tambor no da notas.
#
# Una cuerda vibra en modos que van 1, 2, 3, 4 —multiplos exactos— y por eso
# una cuerda suena a NOTA. Una membrana redonda no: sus modos los fijan los
# ceros de la funcion de Bessel, que no son multiplos de nada. El segundo
# entre el primero da 1.5933, no 2. Por eso un tambor suena a golpe.
#
# El verbo visual son los ceros: primero como cruces de una curva, y
# despues como lo que de verdad son sobre el tambor — un CIRCULO que no se
# mueve mientras el resto de la membrana sube y baja.
#
# La rejilla de puntos no es un adorno de estilo: es la unica forma de que
# el cero se VEA. Con un mapa de intensidad, el cero es un tono intermedio
# que hay que buscar; con puntos cuyo tamaño va con la amplitud, en la
# linea nodal simplemente NO HAY PUNTOS.
#
# (Y de paso evita `ImageMobject`, que obligaria a `Group` y arrastra la
# trampa de mezclar grupos que costo tres piezas en el curso 32.)
class Clip(Pieza):
    NOMBRE = "BESSEL"
    TESIS = "el tambor no da notas"

    # PARAMETROS elegidos: hasta donde se dibuja J0, y la malla del tambor.
    X_MAX = 12.0
    MALLA = 140
    PASO = 5

    def pieza(self):
        L = self.L
        c0 = esp.ceros_J(0, 2)

        # --- 1. la curva, y sus cruces que no estan igual de lejos ----
        P = esp.marco((0.0, self.X_MAX), (-0.55, 1.10),
                      ancho=ANCHO - 0.55, alto=4.30)
        xs = np.linspace(0.0, self.X_MAX, 1800)
        j0 = esp.curva(xs, esp.bessel_J(0, xs), P, color=AMBAR,
                       grosor=esp.TRAZO)
        j0.set_stroke(opacity=0.0)
        eti = rot("J CERO", color=AMBAR)
        eti.move_to(P(1.35, 0.86))
        marca = esp.marca_en(P, float(c0[0]), 0.0)
        plom = esp.plomada(P, float(c0[0]), -0.40, color=TINTA, trozos=6)
        marca.set_opacity(0.0)
        plom.set_stroke(opacity=0.0)

        dibujo = lz.agrupar(esp.eje_x(P), esp.recuadro(P), j0, eti,
                            plom, marca)
        L.escena(dibujo, t=0.9)
        j0.set_stroke(opacity=1.0)
        self.play(Create(j0, introducer=False), run_time=2.2,
                  rate_func=smooth)
        self.leer(3.2)

        # --- 2. el primero de esos cruces ----------------------------
        L.morfeo(None, dato=(medido(c0[0], 4), "el primer cero de j0"),
                 animaciones=[marca.animate.set_opacity(1.0),
                              plom.animate.set_stroke(opacity=1.0)],
                 t=0.8)
        self.leer(3.8)

        # --- 3. y lo que ese cero es sobre el tambor ------------------
        # El modo (0,2) tiene un circulo nodal: la membrana sube dentro y
        # baja fuera, y en ese circulo no pasa nada. Su radio relativo es
        # el primer cero de J0 dividido por el segundo — dos numeros que
        # ya estan en pantalla.
        X, Y, U = esp.modo_tambor(0, 2, N=self.MALLA, M=300)
        granos = esp.campo_signo(X, Y, U, radio=2.05, paso=self.PASO,
                                 grano=0.040, recorte_circular=True)
        borde = esp.circunferencia(2.05, color=APAGADO,
                                   grosor=esp.TRAZO_FINO)
        radio_nodal = float(c0[0] / c0[1])
        quieto = esp.circunferencia(2.05 * radio_nodal, color=TINTA,
                                    grosor=esp.TRAZO)
        # El mismo modo medio periodo despues: los mismos puntos, los
        # mismos tamaños, los colores cambiados. Se construye AHORA y
        # dentro del grupo para que herede la escala y la posicion que le
        # de `encajar`; apagado, porque todavia no toca.
        invertido = esp.campo_signo(X, Y, -U, radio=2.05, paso=self.PASO,
                                    grano=0.040, recorte_circular=True)
        invertido.set_opacity(0.0)
        tambor = lz.agrupar(borde, granos, invertido, quieto)

        L.relevo(escena=tambor,
                 dato=(medido(radio_nodal, 4), "el radio del circulo"),
                 t=0.9)
        self.leer(3.4)

        # --- 4. la membrana vibra y el circulo sigue quieto -----------
        # El objetivo del Transform se copia con la opacidad puesta a 1:
        # transformar hacia un estado apagado deja el dibujo invisible,
        # porque `Transform` copia TAMBIEN el estilo del objetivo.
        derecho = granos.copy()
        for _ in range(2):
            self.play(Transform(granos, invertido.copy().set_opacity(1.0)),
                      run_time=1.0, rate_func=smooth)
            self.play(Transform(granos, derecho.copy()),
                      run_time=1.0, rate_func=smooth)
        self.leer(2.4)

        # --- 5. el remate: en una cuerda saldria 2 exacto -------------
        L.dato(medido(esp.razon_de_modos(), 4), "la razon de los modos")
        self.leer(3.8)
