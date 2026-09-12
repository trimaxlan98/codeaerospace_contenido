# 05 · VALOR MEDIO — el radar siempre te pilla.
#
# EL VERBO VISUAL: la cuerda que une el principio y el final del viaje
# baja sin inclinarse hasta tocar la curva. Donde toca, el velocimetro
# marcaba EXACTAMENTE la media de todo el trayecto. Y toca dos veces.
#
# LOS DOS PANELES SON EL ARGUMENTO, no una decoracion: arriba la posicion
# (lo que sabe el peaje: entraste a las cero y saliste a las dos con 175
# km detras), abajo la velocidad (lo que sabe el coche). La pieza enseña
# que lo primero OBLIGA a lo segundo.
#
# LOS DOS PANELES ENTRAN ENCENDIDOS: un solo panel ocupa 2 de las 5.39
# unidades de la franja, o sea el 37 %, y el guardian de la fraccion
# aborta —con razon: medio fotograma vacio y la cifra a dos unidades del
# dibujo se lee como un error de maquetacion—.
#
# 175 km y 2 h son PARAMETROS ELEGIDOS y van en gris. 87.5 y los dos
# instantes los calcula la libreria y van en ambar.
class Clip(Pieza):
    NOMBRE = "VALOR MEDIO"
    TESIS = "el radar siempre te pilla"

    RT = (0.0, 2.0)
    RS = (-6.0, 182.0)
    RV = (-6.0, 140.0)
    ANCHO_PANEL = ANCHO - 0.75
    ALTO_PANEL = 1.95

    def pieza(self):
        L = self.L
        A = cal.marco(self.RT, self.RS, ancho=self.ANCHO_PANEL,
                      alto=self.ALTO_PANEL)
        B = cal.marco(self.RT, self.RV, ancho=self.ANCHO_PANEL,
                      alto=self.ALTO_PANEL)
        ts = np.linspace(self.RT[0], self.RT[1], 700)
        media = cal.velocidad_media()
        t1, t2 = cal.instantes_de_la_media()

        # --- panel de arriba: el camino recorrido ---------------------
        camino = cal.curva(ts, cal.posicion(ts), A, color=AMBAR,
                           grosor=cal.TRAZO)
        extremos = VGroup(cal.marca_en(A, 0.0, 0.0, radio=0.052),
                          cal.marca_en(A, 2.0, 175.0, radio=0.052))
        cuerda = cal.segmento(A, 0.0, 0.0, 2.0, 175.0, color=CIAN,
                              grosor=cal.TRAZO_FINO)
        # La misma pendiente, apoyada en los dos puntos donde toca: es la
        # cuerda "bajada" sin girar, que es el gesto de la pieza.
        paralelas = VGroup()
        toques = VGroup()
        for t in (t1, t2):
            s0 = float(cal.posicion(t))
            xs = np.array([max(0.0, t - 0.62), min(2.0, t + 0.62)])
            paralelas.add(cal.curva(xs, s0 + media * (xs - t), A,
                                    color=TINTA, grosor=cal.TRAZO_FINO))
            toques.add(cal.marca_en(A, t, s0, radio=0.055))

        # --- panel de abajo: el velocimetro ---------------------------
        velocimetro = cal.curva(ts, cal.velocidad(ts), B, color=AMBAR,
                                grosor=cal.TRAZO)
        raya = cal.segmento(B, 0.0, media, 2.0, media, color=TINTA,
                            grosor=cal.TRAZO_FINO, a_trozos=True)
        cruces = VGroup(*[cal.marca_en(B, t, media, radio=0.055)
                          for t in (t1, t2)])
        # La punta del viaje: sirve para que la media no se confunda con
        # "la velocidad a la que iba". No coincide con ninguno de los dos
        # instantes que busca la pieza, y eso es justo lo que hay que ver.
        punta = cal.marca_en(B, 1.0, cal.velocidad_maxima(), radio=0.055)
        plomo_punta = cal.plomada(B, 1.0, cal.velocidad_maxima(),
                                  color=APAGADO, trozos=6)

        for m in (cuerda, *paralelas, raya, plomo_punta):
            m.set_stroke(opacity=0.0)
        for m in (*toques, *cruces, punta):
            m.set_opacity(0.0)

        arriba = lz.agrupar(caja(A), cal.eje_x(A), camino, extremos, cuerda,
                            paralelas, toques)
        abajo = lz.agrupar(caja(B), cal.eje_x(B), velocimetro, raya,
                           punta, plomo_punta, cruces)
        dibujo = lz.dos_dominios(arriba, abajo, "kilometros recorridos",
                                 "velocimetro", hueco=0.50,
                                 ancho=self.ANCHO_PANEL)

        # --- 1. el viaje ------------------------------------------------
        L.escena(dibujo, t=1.2)
        L.dato("175", "kilometros en dos horas", medido=False)
        self.leer(3.0)

        # --- 1bis. y no fue a velocidad constante ---------------------
        punta.set_opacity(1.0)
        plomo_punta.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{cal.velocidad_maxima():.2f}", "la punta del viaje"),
                 animaciones=[FadeIn(punta), FadeIn(plomo_punta)], t=0.9)
        self.leer(3.4)

        # --- 2. la media sale de los dos extremos ---------------------
        cuerda.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{media:.1f}", "kilometros por hora de media"),
                 animaciones=[Create(cuerda, introducer=False)], t=1.2)
        self.leer(3.0)

        # --- 3. y la cuerda baja sin inclinarse -----------------------
        for m in paralelas:
            m.set_stroke(opacity=1.0)
        for m in toques:
            m.set_opacity(1.0)
        L.morfeo(None,
                 dato=("2", "instantes a esa velocidad"),
                 animaciones=[FadeIn(paralelas), FadeIn(toques)], t=1.3)
        self.leer(4.0)

        # --- 4. y el velocimetro lo confirma --------------------------
        raya.set_stroke(opacity=1.0)
        for m in cruces:
            m.set_opacity(1.0)
        L.morfeo(None,
                 dato=(f"{media:.1f}", "clavados, dos veces"),
                 animaciones=[Create(raya, introducer=False),
                              FadeIn(cruces)], t=1.3)
        self.leer(3.6)
