# 07 · LATA — gastar el minimo aluminio.
#
# EL VERBO VISUAL: la lata se estira y se achata mientras un punto recorre
# la curva del aluminio que hace falta. El valle de esa curva es una lata
# concreta: la que tiene la altura igual al diametro.
#
# Y EL REMATE NO ES "LA INDUSTRIA LO HACE MAL". Es lo contrario, y es lo
# que de verdad enseña la derivada: en el minimo la pendiente vale cero, o
# sea que alrededor la curva es PLANA. Por eso una lata real —que es mucho
# mas esbelta, porque tiene que caber en una mano— gasta solo un 3.2 % de
# mas, y equivocarse un 10 % en el radio cuesta un 1.07 %.
#
# LOS 330 ml SON UN PARAMETRO ELEGIDO y la esbeltez de la lata real es un
# DATO (11.5 cm de alto por 6.6 de diametro): las dos cosas van en gris.
# Lo que calcula la libreria —el optimo, el exceso, el coste de fallar—
# va en ambar.
#
# LA CAJA INVISIBLE DE LA LATA es obligatoria: la silueta cambia de alto y
# de ancho en cada estado, y sin un ancla de tamaño fijo el panel entero
# se recoloca en cada morfeo y el dibujo da un salto que no se sabe
# explicar.
class Clip(Pieza):
    NOMBRE = "LATA"
    TESIS = "gastar el minimo aluminio"

    RR = (2.40, 5.60)
    RS = (250.0, 322.0)
    ESCALA = 0.155
    ANCHO_PANEL = ANCHO - 0.75
    ALTO_PANEL = 1.90

    def silueta(self, r, h, color=AMBAR):
        return cal.silueta_lata(r, h, escala=self.ESCALA, color=color)

    def pieza(self):
        L = self.L
        Q = cal.marco(self.RR, self.RS, ancho=self.ANCHO_PANEL,
                      alto=self.ALTO_PANEL)
        r_opt, h_opt, s_opt = cal.lata_optima()
        r_real, h_real, s_real = cal.lata_de_esbeltez(cal.ESBELTEZ_REAL)

        # --- el panel de abajo: el aluminio que hace falta -------------
        rs = np.linspace(self.RR[0], self.RR[1], 700)
        curva = cal.curva(rs, cal.superficie_lata(rs), Q, color=AMBAR,
                          grosor=cal.TRAZO)
        valle = cal.marca_en(Q, r_opt, s_opt)
        plomo = cal.colgante(Q, r_opt, s_opt, color=APAGADO, trozos=9)
        corredor = cal.marca_en(Q, 2.80, float(cal.superficie_lata(2.80)),
                                color=CIAN, radio=0.055)
        real = cal.marca_en(Q, r_real, s_real, color=CIAN, radio=0.055)
        # El tramo plano: +-10 % alrededor del optimo. Es lo que hace
        # creible el remate, porque se VE que la curva casi no sube.
        rr = np.linspace(r_opt * 0.9, r_opt * 1.1, 200)
        plano = cal.curva(rr, cal.superficie_lata(rr), Q, color=TINTA,
                          grosor=5.0)

        # --- el panel de arriba: la lata ------------------------------
        ancla = Rectangle(width=2.60, height=2.50, stroke_opacity=0.0,
                          fill_opacity=0.0)
        latas = [self.silueta(2.80, 330.0 / (np.pi * 2.80 ** 2)),
                 self.silueta(r_opt, h_opt),
                 self.silueta(5.00, 330.0 / (np.pi * 5.00 ** 2)),
                 self.silueta(r_real, h_real, color=CIAN)]
        for la in latas:
            la.move_to(ancla.get_center())
        for m in (valle, plomo, corredor, real, plano, *latas[1:]):
            m.set_opacity(0.0) if isinstance(m, Dot) else \
                m.set_stroke(opacity=0.0)

        arriba = lz.agrupar(ancla, *latas)
        abajo = lz.agrupar(caja(Q), cal.recuadro(Q), curva, plano, plomo,
                           valle, corredor, real)
        dibujo = lz.dos_dominios(arriba, abajo, None,
                                 "aluminio de la lata", hueco=0.35,
                                 ancho=self.ANCHO_PANEL)

        # --- 1. una lata alta ------------------------------------------
        L.escena(dibujo, t=1.2)
        soltar(arriba, *latas[1:])
        for la in latas[1:]:
            la.set_stroke(opacity=1.0)
        corredor.set_opacity(1.0)
        self.play(FadeIn(corredor), run_time=0.5)
        L.dato("330", "mililitros, siempre", medido=False)
        self.leer(2.8)

        # --- 2. la del valle: la altura es el diametro ----------------
        valle.set_opacity(1.0)
        plomo.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{s_opt:.1f}", "centimetros cuadrados, el minimo"),
                 animaciones=[Transform(latas[0], latas[1]),
                              Transform(corredor, valle),
                              FadeIn(plomo)], t=1.4)
        self.leer(3.0)

        # --- 3. y por el otro lado vuelve a subir ---------------------
        gorda = float(cal.superficie_lata(5.00))
        L.morfeo(None,
                 dato=(f"{gorda:.1f}", "si se achata, otra vez mas"),
                 animaciones=[Transform(latas[0], latas[2])], t=1.4)
        self.leer(2.8)

        # --- 4. la lata de verdad no es la del valle ------------------
        real.set_opacity(1.0)
        L.morfeo(None,
                 dato=(f"{cal.exceso_de_la_real():.1f} %",
                       "de mas, la lata real"),
                 animaciones=[Transform(latas[0], latas[3]),
                              FadeIn(real)], t=1.4)
        self.leer(3.0)

        # --- 5. y no pasa nada, porque el valle es plano --------------
        plano.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{cal.coste_de_fallar(0.10):.2f} %",
                       "cuesta fallar un diez por ciento"),
                 animaciones=[Create(plano, introducer=False)], t=1.2)
        self.leer(3.6)
