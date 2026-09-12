# 09 · TEOREMA FUNDAMENTAL — derivar deshace integrar.
#
# EL VERBO VISUAL: dos paneles sincronizados. Arriba se llena el area bajo
# una curva; abajo se dibuja, a la vez, cuanta area llevamos. Y entonces la
# pregunta que lo une todo: ¿a que ritmo crece la de abajo? A la ALTURA de
# la de arriba. Exactamente, en todos los puntos.
#
# LAS DOS COMPROBACIONES SON EL ARGUMENTO: con una sola, el espectador
# tiene derecho a pensar que es casualidad o que el punto esta elegido. La
# segunda se hace donde la curva de arriba esta BAJA (x = 4.2, altura
# 0.33) y la de abajo casi no sube: la misma ley, con otro numero.
#
# EL CUADRO DE ABAJO SE VE DESDE EL PRINCIPIO aunque este vacio. No es
# decorativo: sin el, lo unico pintado en el primer estado es el panel de
# arriba, que ocupa el 37 % de la franja, y el guardian aborta. Ademas dice
# "aqui va a pasar algo", que es verdad.
class Clip(Pieza):
    NOMBRE = "TEOREMA FUNDAMENTAL"
    TESIS = "derivar deshace integrar"

    CORTES = (1.6, 3.2, 5.0)
    PRUEBAS = (2.0, 4.2)
    RX = (0.0, 5.0)
    RF = (0.0, 2.35)
    RA = (0.0, 7.20)
    ANCHO_PANEL = ANCHO - 0.80
    ALTO_PANEL = 1.95

    def pieza(self):
        L = self.L
        A = cal.marco(self.RX, self.RF, ancho=self.ANCHO_PANEL,
                      alto=self.ALTO_PANEL)
        B = cal.marco(self.RX, self.RA, ancho=self.ANCHO_PANEL,
                      alto=self.ALTO_PANEL)
        xs = np.linspace(self.RX[0], self.RX[1], 900)

        curva = cal.curva(xs, cal.f_tfc(xs), A, color=AMBAR,
                          grosor=cal.TRAZO)
        areas, tramos = [], []
        for c in self.CORTES:
            x = np.linspace(0.0, c, 700)
            areas.append(cal.region(x, cal.f_tfc(x), A, color=AMBAR,
                                    opacidad=0.18))
            tramos.append(cal.curva(x, cal.area_tfc(x), B, color=CIAN,
                                    grosor=cal.TRAZO))
        for m in areas + tramos:
            m.set_stroke(opacity=0.0)
            m.set_fill(opacity=0.0)

        # --- las dos comprobaciones -----------------------------------
        alturas, pendientes, marcas = [], [], []
        for x0 in self.PRUEBAS:
            alt = float(cal.f_tfc(x0))
            alturas.append(cal.segmento(A, x0, 0.0, x0, alt, color=TINTA,
                                        grosor=4.0))
            m = cal.ritmo_del_area(x0)
            xt = np.array([x0 - 0.75, x0 + 0.75])
            pendientes.append(cal.curva(
                xt, float(cal.area_tfc(x0)) + m * (xt - x0), B, color=TINTA,
                grosor=cal.TRAZO_FINO))
            marcas.append(cal.marca_en(B, x0, float(cal.area_tfc(x0)),
                                       radio=0.052))
        for m in alturas + pendientes:
            m.set_stroke(opacity=0.0)
        for m in marcas:
            m.set_opacity(0.0)

        arriba = lz.agrupar(cal.recuadro(A), curva, *areas, *alturas)
        abajo = lz.agrupar(cal.recuadro(B), *tramos, *pendientes, *marcas)
        dibujo = lz.dos_dominios(arriba, abajo, "la curva",
                                 "el area que llevamos", hueco=0.45,
                                 ancho=self.ANCHO_PANEL)

        # --- 1. una curva, y un cuadro vacio debajo -------------------
        L.escena(dibujo, t=1.2)
        self.leer(2.6)

        # --- 2, 3, 4. el area se llena y la de abajo la va contando ---
        for i, c in enumerate(self.CORTES):
            areas[i].set_fill(opacity=0.18)
            tramos[i].set_stroke(opacity=1.0)
            animaciones = [FadeIn(areas[i]),
                           Create(tramos[i], introducer=False)]
            if i:
                animaciones.append(FadeOut(areas[i - 1]))
            L.morfeo(None,
                     dato=(f"{float(cal.area_tfc(c)):.4f}",
                           "de area, hasta aqui"),
                     animaciones=animaciones, t=1.3)
            self.leer(2.6)

        # --- 5, 6. y el ritmo al que crece es la altura de arriba -----
        for i, x0 in enumerate(self.PRUEBAS):
            alturas[i].set_stroke(opacity=1.0)
            pendientes[i].set_stroke(opacity=1.0)
            marcas[i].set_opacity(1.0)
            alto, ritmo = cal.altura_y_ritmo(x0)
            L.morfeo(None,
                     dato=(f"{ritmo:.4f}",
                           "la altura, y la pendiente"),
                     animaciones=[Create(alturas[i], introducer=False),
                                  FadeIn(marcas[i]),
                                  Create(pendientes[i], introducer=False)],
                     t=1.2)
            self.leer(3.0 if i == 0 else 3.8)
