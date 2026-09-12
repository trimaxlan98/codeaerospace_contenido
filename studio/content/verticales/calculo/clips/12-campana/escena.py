# 12 · CAMPANA — un area sin formula, exacta.
#
# EL VERBO VISUAL: la campana se mide con rectangulos —1.7725, y nadie
# sabe de donde sale— y entonces GIRA. Vista desde arriba es una pila de
# anillos, y el area de un anillo de radio r trae un r DELANTE. Con ese r,
# la integral que no tenia primitiva elemental pasa a tenerla: el volumen
# sale pi, exacto, y el area de la campana es su raiz.
#
# ES LA UNICA PIEZA DEL CURSO QUE SALE AL PLANO, y sale para volver a
# entrar: los anillos convierten dos variables en una sola, el radio. Sin
# eso seria una pieza de calculo vectorial, que es del curso 21.
#
# LOS ANILLOS SE DIBUJAN CON LA OPACIDAD DE SU PESO: el de fuera casi no
# se ve porque casi no pesa. Es el perfil de la campana, dibujado sin
# salir del plano y sin fingir una perspectiva que este estilo no tiene.
class Clip(Pieza):
    NOMBRE = "CAMPANA"
    TESIS = "un area sin formula, exacta"

    RX = (-2.60, 2.60)
    RY = (0.0, 1.12)
    RR = (0.0, 2.60)
    RA = (0.0, 1.00)
    ANCHO_CAJA = ANCHO - 0.60
    ALTO_CAJA = 3.40

    def pieza(self):
        L = self.L
        P = cal.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)
        xs = np.linspace(self.RX[0], self.RX[1], 900)

        # --- 1 y 2: la campana y sus rectangulos ----------------------
        curva = cal.curva(xs, cal.campana(xs), P, color=AMBAR,
                          grosor=cal.TRAZO)
        area = cal.region(xs, cal.campana(xs), P, color=AMBAR,
                          opacidad=0.16)
        bordes = np.linspace(self.RX[0], self.RX[1], 41)
        rects = [(float(bordes[i]), float(bordes[i + 1]),
                  float(cal.campana((bordes[i] + bordes[i + 1]) / 2.0)))
                 for i in range(len(bordes) - 1)]
        barras = cal.rectangulos_dibujados(rects, P, color=AMBAR,
                                           opacidad=0.16)
        area.set_fill(opacity=0.0)
        barras.set_stroke(opacity=0.0)
        barras.set_fill(opacity=0.0)
        campana = lz.agrupar(cal.eje_x(P), curva, area, barras)

        # --- 3: la campana girada, vista desde arriba -----------------
        anillos = cal.anillos_concentricos(cal.radios_de_anillos(16, 2.5),
                                           escala=0.80, grosor=3.2)
        uno = Circle(radius=1.0 / np.sqrt(2.0) * 0.80, stroke_color=TINTA,
                     stroke_width=4.0)
        uno.set_fill(opacity=0.0)
        uno.set_stroke(opacity=0.0)
        vista = lz.agrupar(anillos, uno)

        # --- 4: la curva del anillo, que si se integra ----------------
        Q = cal.marco(self.RR, self.RA, ancho=self.ANCHO_CAJA, alto=3.40)
        rs = np.linspace(0.0, self.RR[1], 700)
        peso = cal.anillo(rs) / (2.0 * np.pi)
        curva_anillo = cal.curva(rs, peso, Q, color=AMBAR, grosor=cal.TRAZO)
        area_anillo = cal.region(rs, peso, Q, color=AMBAR, opacidad=0.18)
        panel = lz.agrupar(cal.eje_x(Q), cal.recuadro(Q), area_anillo,
                           curva_anillo)

        # --- 1. una campana --------------------------------------------
        L.escena(campana, t=1.2)
        self.leer(2.8)

        # --- 2. se mide con rectangulos, y sale un numero raro --------
        barras.set_stroke(opacity=0.85).set_fill(opacity=0.16)
        L.morfeo(None,
                 dato=(f"{cal.area_campana():.4f}", "el area, medida"),
                 animaciones=[FadeIn(barras)], t=1.2)
        self.leer(3.2)

        # --- 3. asi que se gira ----------------------------------------
        L.relevo(escena=vista, dato=None, t=1.2, salida=0.6)
        self.leer(2.8)

        # --- 4. y cada anillo trae un radio delante -------------------
        uno.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{1.0 / np.sqrt(2.0):.4f}", "el anillo que mas pesa"),
                 animaciones=[Create(uno, introducer=False)], t=1.0)
        self.leer(2.8)

        # --- 5. con ese radio, la integral si sale --------------------
        L.relevo(escena=panel,
                 dato=(f"{cal.volumen_campana():.4f}", "el volumen, exacto"),
                 t=1.2, salida=0.6)
        self.leer(3.2)

        # --- 6. y el area de la campana es su raiz --------------------
        L.dato(f"{cal.raiz_de_pi():.4f}", "su raiz: el area de antes")
        self.leer(3.8)
