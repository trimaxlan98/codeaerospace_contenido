# 14 · CEBOLLA — desenrollar para medir.
#
# EL VERBO VISUAL: el circulo es una pila de anillos. Los anillos salen,
# se desenrollan y se apilan: sale un TRIANGULO de base 2*pi*R y altura R.
# Y el area de un triangulo la sabe cualquiera.
#
# CADA TIRA ES UN TRAPECIO, NO UN RECTANGULO, y no es un detalle: el area
# de verdad del anillo entre ri y re es pi(re^2-ri^2), que es exactamente
# el area del trapecio de bases 2*pi*ri y 2*pi*re. Apilar RECTANGULOS
# dejaria escalones y el triangulo saldria aproximado; con trapecios sale
# EXACTO para cualquier numero de anillos, y la sonda lo comprueba con 1,
# 3, 8, 40 y 400.
#
# Y DE PROPINA sale por que la derivada del area es el perimetro: añadir
# un anillo de grosor dr al borde cuesta 2*pi*R*dr, que es la ultima tira
# del triangulo.
class Clip(Pieza):
    NOMBRE = "CEBOLLA"
    TESIS = "desenrollar para medir"

    R = 5.0
    ANILLOS = 9
    LADO = 2.55
    ANCHO_PANEL = ANCHO - 0.70
    ALTO_PANEL = 1.35

    def pieza(self):
        L = self.L
        R = self.R
        P = cal.marco_igual((-R - 0.3, R + 0.3), (-R - 0.3, R + 0.3),
                            ancho=self.LADO, alto=self.LADO)
        # El rango vertical va AL REVES (de R a 0) a proposito: asi el
        # anillo de fuera —el mas largo— cae abajo, sobre la base, y el
        # triangulo se apoya en el perimetro en vez de colgar de el. Con
        # el rango normal salia con la punta hacia abajo y la linea de la
        # base quedaba justo donde el triangulo no mide nada.
        Q = cal.marco((-np.pi * R * 1.03, np.pi * R * 1.03), (R * 1.04, 0.0),
                      ancho=self.ANCHO_PANEL, alto=self.ALTO_PANEL)

        anillos = cal.anillos_circulo(R, self.ANILLOS)
        circulo = cal.circulo_en(P, 0.0, 0.0, R, color=AMBAR,
                                 grosor=cal.TRAZO)
        aros = VGroup(*[cal.circulo_en(P, 0.0, 0.0, re, color=AMBAR,
                                       grosor=1.4)
                        for _ri, re, _rm, _g in anillos[:-1]])
        borde = cal.circulo_en(P, 0.0, 0.0, R, color=TINTA, grosor=4.5)
        borde.set_stroke(opacity=0.0)

        triangulo = cal.tiras(anillos, Q, color=AMBAR, opacidad=0.22)
        base = cal.segmento(Q, -np.pi * R, R, np.pi * R, R, color=TINTA,
                            grosor=4.5)
        triangulo.set_stroke(opacity=0.0)
        triangulo.set_fill(opacity=0.0)
        base.set_stroke(opacity=0.0)

        arriba = lz.agrupar(caja(P), circulo, aros, borde)
        abajo = lz.agrupar(caja(Q), triangulo, base)
        dibujo = lz.dos_dominios(arriba, abajo, "nueve anillos",
                                 "los mismos, desenrollados", hueco=0.40,
                                 ancho=self.ANCHO_PANEL)

        # --- 1. un circulo hecho de anillos ---------------------------
        L.escena(dibujo, t=1.2)
        self.leer(3.4)

        # --- 2. el de fuera, desenrollado, mide el perimetro ----------
        borde.set_stroke(opacity=1.0)
        base.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{cal.perimetro_circulo(R):.4f}",
                       "el borde, estirado: la base"),
                 animaciones=[Create(borde, introducer=False),
                              Create(base, introducer=False)], t=1.4)
        self.leer(3.0)

        # --- 3. y los demas debajo, cada uno mas corto ----------------
        triangulo.set_stroke(opacity=0.85).set_fill(opacity=0.22)
        self.play(LaggedStart(*[FadeIn(t) for t in triangulo],
                              lag_ratio=0.12), run_time=2.2)
        self.leer(3.2)

        # --- 4. un triangulo, y el area de un triangulo se sabe -------
        L.dato(f"{cal.area_por_tiras(R, self.ANILLOS):.4f}",
               "su area, y la del circulo")
        self.leer(3.8)

        # --- 5. y de propina, por que derivar el area da el borde -----
        L.dato(f"{cal.derivada_del_area(R):.4f}",
               "lo que crece al ensanchar")
        self.leer(4.2)
