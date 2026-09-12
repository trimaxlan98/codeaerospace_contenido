# 15 · ANILLO — manda el agujero.
#
# EL VERBO VISUAL: dos esferas muy distintas —radio 4 y radio 9— taladradas
# de lado a lado hasta dejar un anillo de la MISMA altura, 6 cm. La de
# nueve necesita un agujero enorme y la de cuatro uno pequeño, y los dos
# anillos que quedan tienen el mismo volumen. A cualquier altura, ademas:
# las dos barras de abajo miden lo mismo siempre.
#
# POR QUE BARRAS OTRA VEZ: lo que coincide son AREAS de corona, y un area
# no se puede enseñar con un segmento. Dos coronas de anchura distinta y la
# misma area son justo lo que hay que creerse, asi que se miden.
#
# LAS DOS CIRCUNFERENCIAS VAN CONCENTRICAS y a la misma escala. Ponerlas
# una al lado de la otra habria obligado a un cuadro de 40 unidades de
# ancho en un lienzo vertical, y a escalas distintas la comparacion seria
# trampa: la gracia es que el agujero de una es casi toda la otra.
class Clip(Pieza):
    NOMBRE = "ANILLO"
    TESIS = "manda el agujero"

    H = 6.0
    RADIOS = (4.0, 9.0)
    ALTURAS = (0.0, 2.2)
    LADO = 3.05
    ANCHO_BARRA = ANCHO - 1.20
    ALTO_BARRA = 0.70

    def barras_de(self, y):
        """Las dos coronas a la altura y, como barras de igual longitud."""
        Q = self.Q
        grupo = VGroup()
        for i, R in enumerate(self.RADIOS):
            f = cal.area_corona(y, R, self.H) / cal.area_corona(0.0, R,
                                                                self.H)
            y0, y1 = (0.56, 1.0) if i == 0 else (0.0, 0.44)
            color = (AMBAR, CIAN)[i]
            esquinas = [Q(0.0, y0), Q(max(f, 1e-4), y0),
                        Q(max(f, 1e-4), y1), Q(0.0, y1)]
            r = VMobject(stroke_width=0.0, fill_color=color, fill_opacity=0.6)
            r.set_points_as_corners(esquinas + [esquinas[0]])
            grupo.add(r)
        return grupo

    def corte(self, y):
        P = self.P
        linea = cal.segmento(P, -9.4, y, 9.4, y, color=TINTA, grosor=1.6)
        return lz.agrupar(linea)

    def pieza(self):
        L = self.L
        H = self.H
        self.P = P = cal.marco_igual((-9.6, 9.6), (-9.6, 9.6),
                                     ancho=self.LADO, alto=self.LADO)
        self.Q = Q = cal.marco((0.0, 1.0), (0.0, 1.0), ancho=self.ANCHO_BARRA,
                               alto=self.ALTO_BARRA)

        esferas, taladros = VGroup(), VGroup()
        for i, R in enumerate(self.RADIOS):
            color = (AMBAR, CIAN)[i]
            esferas.add(cal.circulo_en(P, 0.0, 0.0, R, color=color,
                                       grosor=cal.TRAZO))
            c = cal.radio_del_agujero(R, H)
            taladros.add(VGroup(*[
                cal.segmento(P, s * c, -H / 2, s * c, H / 2, color=color,
                             grosor=cal.TRAZO_FINO) for s in (-1, 1)]))
        tapas = VGroup(*[cal.segmento(P, -9.4, s * H / 2, 9.4, s * H / 2,
                                      color=APAGADO, grosor=1.2,
                                      a_trozos=True) for s in (-1, 1)])
        cortes = [self.corte(y) for y in self.ALTURAS]
        barras = [self.barras_de(y) for y in self.ALTURAS]
        contorno = cal.recuadro(Q, color=LINEA, grosor=1.2)

        taladros.set_stroke(opacity=0.0)
        for m in cortes + barras:
            m.set_opacity(0.0)
        contorno.set_stroke(opacity=0.0)

        figura = lz.agrupar(caja(P), esferas, tapas, taladros, *cortes)
        tabla = lz.agrupar(contorno, *barras)
        dibujo = lz.dos_dominios(figura, tabla, None,
                                 "la corona, en las dos", hueco=0.40,
                                 ancho=ANCHO - 0.90)

        # --- 1. dos esferas muy distintas, con la misma banda ---------
        L.escena(dibujo, t=1.2)
        soltar(tabla, *barras[1:])
        soltar(figura, *cortes[1:])
        for m in list(barras[1:]) + list(cortes[1:]):
            m.set_opacity(1.0)
        L.dato(f"{H:.0f}", "centimetros de alto, las dos", medido=False)
        self.leer(3.0)

        # --- 2. el taladro: uno pequeño y otro enorme -----------------
        taladros.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{cal.radio_del_agujero(self.RADIOS[1], H):.2f}",
                       "el agujero de la grande"),
                 animaciones=[Create(taladros, introducer=False)], t=1.4)
        self.leer(3.0)

        # --- 3, 4. las coronas, a dos alturas -------------------------
        for i, y in enumerate(self.ALTURAS):
            cortes[i].set_opacity(1.0)
            barras[i].set_opacity(1.0)
            contorno.set_stroke(opacity=1.0)
            if i == 0:
                animaciones = [FadeIn(cortes[0]), FadeIn(barras[0]),
                               FadeIn(contorno)]
                etiqueta = "de corona, en las dos"
            else:
                animaciones = [Transform(cortes[0], cortes[i]),
                               Transform(barras[0], barras[i])]
                etiqueta = "y mas arriba, tambien"
            L.morfeo(None,
                     dato=(f"{cal.area_corona(y, self.RADIOS[0], H):.2f}",
                           etiqueta),
                     animaciones=animaciones, t=1.2)
            self.leer(3.2)

        # --- 5. asi que el anillo entero mide lo mismo ----------------
        L.dato(f"{cal.volumen_anillo(self.RADIOS[0], H):.2f}",
               "centimetros cubicos, las dos")
        self.leer(4.6)
