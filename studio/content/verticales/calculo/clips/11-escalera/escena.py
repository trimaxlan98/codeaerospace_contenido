# 11 · ESCALERA — la longitud no se escalona.
#
# EL VERBO VISUAL: una escalera de peldaños rectos que envuelve la
# circunferencia. Se afina —2, 8, 32 peldaños por cuadrante— hasta que ya
# no se distingue de ella. Y su perimetro sigue midiendo 4. Exactamente 4,
# en los cuatro casos.
#
# ES LA DEMOSTRACION FALSA DE QUE PI VALE 4, y por eso entra: enseña que
# "se parecen mucho" NO implica "miden casi lo mismo". El area si se deja
# aproximar asi (pieza 08); la longitud no, y hace falta la derivada, que
# es lo unico que sabe hacia donde va la curva en cada punto.
#
# EL MARCO ES ISOTROPO (`marco_igual`). Con uno normal, x e y van a
# escalas distintas y la circunferencia sale elipse: la pieza estaria
# midiendo el perimetro de otra cosa.
#
# LA ESCALERA LA CONSTRUYE LA LIBRERIA y su longitud se MIDE sumando
# tramos, no se afirma. La primera version de `escalera_circulo` giraba
# los cuadrantes al reves, aparecian tramos en diagonal y medía 6.82 —o
# sea 2*pi—: el dibujo se veia perfecto y la pieza habria demostrado lo
# contrario de lo que dice.
class Clip(Pieza):
    NOMBRE = "ESCALERA"
    TESIS = "la longitud no se escalona"

    NIVELES = (1, 2, 8, 32)
    LADO = 4.90

    def pieza(self):
        L = self.L
        r = cal.RADIO
        P = cal.marco_igual((-0.62, 0.62), (-0.62, 0.62),
                            ancho=self.LADO, alto=self.LADO)

        circulo = cal.circulo_en(P, 0.0, 0.0, r, color=AMBAR,
                                 grosor=cal.TRAZO)
        escaleras = []
        for n in self.NIVELES:
            pts = cal.escalera_circulo(n, r)
            escaleras.append(cal.curva(pts[:, 0], pts[:, 1], P, color=CIAN,
                                       grosor=cal.TRAZO_FINO))
        for e in escaleras[1:]:
            e.set_stroke(opacity=0.0)

        dibujo = lz.agrupar(caja(P), circulo, *escaleras)

        # --- 1. una circunferencia y el cuadrado que la encierra ------
        L.escena(dibujo, t=1.2)
        soltar(dibujo, *escaleras[1:])
        for e in escaleras[1:]:
            e.set_stroke(opacity=1.0)
        largo = cal.longitud_poligonal(cal.escalera_circulo(self.NIVELES[0],
                                                            r))
        L.dato(f"{largo:.4f}", "lo que mide el cuadrado")
        self.leer(3.0)

        # --- 2, 3, 4. se dobla la escalera en cada esquina ------------
        for i, n in enumerate(self.NIVELES[1:], start=1):
            largo = cal.longitud_poligonal(cal.escalera_circulo(n, r))
            etiqueta = ("y doblando las esquinas" if i == 1 else
                        f"con {4 * n} peldaños, igual")
            L.morfeo(None,
                     dato=(f"{largo:.4f}", etiqueta),
                     animaciones=[Transform(escaleras[0], escaleras[i])],
                     t=1.4)
            self.leer(3.0 if i < len(self.NIVELES) - 1 else 3.4)

        # --- 5. y sin embargo la circunferencia mide otra cosa --------
        self.play(circulo.animate.set_stroke(width=5.0), run_time=0.6)
        L.dato(f"{cal.longitud_circunferencia(r):.4f}",
               "lo que mide la circunferencia")
        self.leer(3.2)

        # --- 6. la diferencia que no se ve ----------------------------
        exceso = (4.0 / cal.longitud_circunferencia(r) - 1.0) * 100.0
        L.dato(f"{exceso:.2f} %", "de mas, y pegadas")
        self.leer(3.6)
