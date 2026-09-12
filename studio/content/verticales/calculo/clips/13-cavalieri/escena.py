# 13 · CAVALIERI — rebanada a rebanada.
#
# EL VERBO VISUAL: un corte del cilindro con la esfera dentro y los dos
# conos. Una altura cualquiera corta tres cosas, y el disco de la esfera
# mas el disco del cono dan EXACTAMENTE el disco del cilindro. La barra de
# abajo lo enseña: el ambar se encoge, el cian crece y la barra sigue
# llena. A todas las alturas.
#
# POR QUE LA BARRA Y NO LOS RADIOS: los radios NO se suman (se suman sus
# cuadrados), asi que dibujar dos segmentos y decir que dan el tercero
# seria mentir con un dibujo correcto. Lo que se suma son las AREAS, y un
# area se enseña como un trozo de barra.
#
# Es el argumento de Arquimedes, el que pidio que le grabaran en la tumba:
# la esfera es dos tercios de su cilindro.
class Clip(Pieza):
    NOMBRE = "CAVALIERI"
    TESIS = "rebanada a rebanada"

    R = 5.0
    ALTURAS = (0.0, 2.5, 4.2)
    LADO = 3.35
    ANCHO_BARRA = ANCHO - 1.10
    ALTO_BARRA = 0.42

    def barra(self, y):
        """La barra apilada: esfera (ambar) + cono (cian) = cilindro."""
        ae, ac, al = cal.areas_rebanada(y, self.R)
        f = ae / al
        Q = self.Q
        trozos = []
        for x0, x1, color, op in ((0.0, f, AMBAR, 0.55), (f, 1.0, CIAN, 0.55)):
            if x1 - x0 < 1e-9:
                continue
            esquinas = [Q(x0, 0.0), Q(x1, 0.0), Q(x1, 1.0), Q(x0, 1.0)]
            r = VMobject(stroke_width=0.0, fill_color=color, fill_opacity=op)
            r.set_points_as_corners(esquinas + [esquinas[0]])
            trozos.append(r)
        return lz.agrupar(*trozos)

    def corte(self, y):
        """La linea de la rebanada y los dos puntos que marca."""
        P = self.P
        re, rc, rl = cal.radios_rebanada(y, self.R)
        linea = cal.segmento(P, -self.R, y, self.R, y, color=TINTA,
                             grosor=1.6)
        puntos = VGroup(cal.marca_en(P, re, y, color=AMBAR, radio=0.050),
                        cal.marca_en(P, rc, y, color=CIAN, radio=0.050))
        return lz.agrupar(linea, puntos)

    def pieza(self):
        L = self.L
        R = self.R
        self.P = P = cal.marco_igual((-R - 0.25, R + 0.25),
                                     (-R - 0.25, R + 0.25),
                                     ancho=self.LADO, alto=self.LADO)
        self.Q = Q = cal.marco((0.0, 1.0), (0.0, 1.0),
                               ancho=self.ANCHO_BARRA, alto=self.ALTO_BARRA)

        cilindro = cal.recuadro(P, color=CIAN, grosor=cal.TRAZO_FINO)
        esfera = cal.circulo_en(P, 0.0, 0.0, R, color=AMBAR,
                                grosor=cal.TRAZO)
        conos = VGroup(*[cal.segmento(P, 0.0, 0.0, sx * R, sy * R,
                                      color=APAGADO, grosor=cal.TRAZO_FINO)
                         for sx in (-1, 1) for sy in (-1, 1)])
        cortes = [self.corte(y) for y in self.ALTURAS]
        barras = [self.barra(y) for y in self.ALTURAS]
        contorno = cal.recuadro(Q, color=TINTA, grosor=1.4)

        for c in cortes:
            c.set_opacity(0.0)
        for b in barras:
            b.set_opacity(0.0)
        contorno.set_stroke(opacity=0.0)

        figura = lz.agrupar(caja(P), cilindro, conos, esfera, *cortes)
        tabla = lz.agrupar(contorno, *barras)
        dibujo = lz.dos_dominios(figura, tabla, None,
                                 "esfera + cono = cilindro", hueco=0.45,
                                 ancho=ANCHO - 0.80)

        # --- 1. un cilindro con una esfera y dos conos dentro ---------
        L.escena(dibujo, t=1.2)
        soltar(tabla, *barras[1:])
        soltar(figura, *cortes[1:])
        for m in list(barras[1:]) + list(cortes[1:]):
            m.set_opacity(1.0)
        self.leer(3.0)

        # --- 2, 3, 4. una altura cualquiera ---------------------------
        for i, y in enumerate(self.ALTURAS):
            ae, ac, al = cal.areas_rebanada(y, R)
            cortes[i].set_opacity(1.0)
            barras[i].set_opacity(1.0)
            contorno.set_stroke(opacity=1.0)
            if i == 0:
                animaciones = [FadeIn(cortes[0]), FadeIn(barras[0]),
                               FadeIn(contorno)]
            else:
                animaciones = [Transform(cortes[0], cortes[i]),
                               Transform(barras[0], barras[i])]
            L.morfeo(None,
                     dato=(f"{(ae + ac) / al:.4f}", "esfera mas cono, "
                           "entre cilindro"),
                     animaciones=animaciones, t=1.2)
            self.leer(3.0 if i < len(self.ALTURAS) - 1 else 3.4)

        # --- 5. y por eso el volumen sale sin integrar nada -----------
        L.dato(f"{cal.razon_esfera_cilindro(R):.4f}",
               "la esfera, de su cilindro")
        self.leer(5.0)
