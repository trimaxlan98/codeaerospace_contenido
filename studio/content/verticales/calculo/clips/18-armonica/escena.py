# 18 · ARMONICA — crece siempre, y despacio.
#
# EL VERBO VISUAL: doce columnas de altura 1, 1/2, 1/3... apoyadas sobre la
# hiperbola. Cada columna sobresale, asi que la suma va SIEMPRE por encima
# del area — y el area es el logaritmo, que no para de crecer. Luego la
# suma tampoco para.
#
# Y el panel de abajo enseña a que ritmo: de uno a un millon de sumandos,
# la suma pasa de 1 a 14.39. Crece, pero como el logaritmo, o sea que para
# llegar a cien hacen falta mas terminos que atomos tiene la Tierra.
#
# LA COTA ES LO QUE CONVIERTE EL DIBUJO EN DEMOSTRACION: "crece despacio"
# no demuestra nada —muchas series que convergen tambien crecen despacio—.
# Lo que lo demuestra es que la suma esta ENCIMA de algo que se va al
# infinito, y eso es lo que se ve con las columnas.
#
# 1.5e43 es una ESTIMACION, no una suma: sale de H(n) ~ ln n + gamma con la
# gamma medida aqui. Se dice en la etiqueta.
class Clip(Pieza):
    NOMBRE = "ARMONICA"
    TESIS = "crece siempre, y despacio"

    COLUMNAS = 12
    RX = (0.60, 13.60)
    RY = (0.0, 1.12)
    RL = (0.0, 6.0)
    RS = (0.0, 15.6)
    ANCHO_PANEL = ANCHO - 0.70
    ALTO_PANEL = 1.85

    def pieza(self):
        L = self.L
        P = cal.marco(self.RX, self.RY, ancho=self.ANCHO_PANEL,
                      alto=self.ALTO_PANEL)
        Q = cal.marco(self.RL, self.RS, ancho=self.ANCHO_PANEL,
                      alto=self.ALTO_PANEL)

        xs = np.linspace(1.0, self.RX[1], 900)
        hiperbola = cal.curva(xs, cal.hiperbola(xs), P, color=TINTA,
                              grosor=cal.TRAZO)
        area = cal.region(xs, cal.hiperbola(xs), P, color=TINTA,
                          opacidad=0.16)
        columnas = cal.barras(cal.bloques(self.COLUMNAS), P, color=AMBAR,
                              hueco=0.10, opacidad=0.22)
        area.set_fill(opacity=0.0)
        columnas.set_stroke(opacity=0.0)
        columnas.set_fill(opacity=0.0)

        # --- el panel de abajo: la suma contra el logaritmo -----------
        n = 10 ** np.linspace(0.0, 6.0, 400)
        parciales = cal.sumas_parciales(1000000)
        sumas = parciales[np.round(n).astype(int) - 1]
        crecida = cal.curva(np.log10(n), sumas, Q, color=AMBAR,
                            grosor=cal.TRAZO)
        logaritmo = cal.curva(np.log10(n), np.log(n), Q, color=TINTA,
                              grosor=cal.TRAZO_FINO, a_trozos=True)
        for m in (crecida, logaritmo):
            m.set_stroke(opacity=0.0)

        arriba = lz.agrupar(cal.recuadro(P), area, hiperbola, columnas)
        abajo = lz.agrupar(cal.recuadro(Q), logaritmo, crecida)
        dibujo = lz.dos_dominios(arriba, abajo, "doce sumandos",
                                 "de uno a un millon", hueco=0.42,
                                 ancho=self.ANCHO_PANEL)

        # --- 1. doce columnas sobre la hiperbola ----------------------
        L.escena(dibujo, t=1.2)
        columnas.set_stroke(opacity=0.85).set_fill(opacity=0.22)
        L.morfeo(None,
                 dato=(f"{cal.armonica(self.COLUMNAS):.4f}",
                       "la suma de los doce primeros"),
                 animaciones=[LaggedStart(*[FadeIn(c) for c in columnas],
                                          lag_ratio=0.10)], t=1.8)
        self.leer(3.8)

        # --- 2. y ninguna cabe debajo ---------------------------------
        area.set_fill(opacity=0.16)
        L.morfeo(None,
                 dato=(f"{float(np.log(13.0)):.4f}", "el area que tapan"),
                 animaciones=[FadeIn(area)], t=1.0)
        self.leer(3.8)

        # --- 3. y esa area no para de crecer --------------------------
        for m in (crecida, logaritmo):
            m.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{cal.armonica(1000000):.4f}",
                       "con un millon de sumandos"),
                 animaciones=[Create(crecida, introducer=False),
                              Create(logaritmo, introducer=False)], t=2.0)
        self.leer(3.8)

        # --- 4. asi que llegar a cien es posible, pero no aqui --------
        L.dato(f"{cal.terminos_para(100.0):.1e}",
               "sumandos, estimados, para cien", medido=False)
        self.leer(4.8)
