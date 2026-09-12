# 08 · RIEMANN — el area se deja rellenar.
#
# EL VERBO VISUAL: dos familias de rectangulos, los que se quedan cortos y
# los que se pasan, y la cifra que las separa. Rellenar mas fino no es
# "aproximar mejor": es ESTRECHAR LA PINZA, y cuando la pinza se cierra ya
# no hay nada que discutir sobre cuanto vale el area.
#
# POR QUE LA CIFRA ES EL HUECO Y NO LA SUMA: una suma sola no demuestra
# nada —¿cuanto se equivoca?—. Lo que demuestra que el area EXISTE es que
# la diferencia entre la de dentro y la de fuera se puede hacer tan
# pequeña como se quiera, y ese numero vale exactamente 1/n, que es lo que
# se ve encogerse.
#
# CIAN los de dentro, AMBAR los de fuera: son las dos unicas cosas que hay
# que distinguir, y por eso aqui si se gasta el quinto color.
class Clip(Pieza):
    NOMBRE = "RIEMANN"
    TESIS = "el area se deja rellenar"

    CUANTOS = (4, 16, 64)
    RX = (0.0, 1.0)
    RY = (0.0, 1.06)
    ANCHO_CAJA = ANCHO - 0.85
    ALTO_CAJA = 4.35

    def pieza(self):
        L = self.L
        P = cal.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)
        xs = np.linspace(0.0, 1.0, 600)
        curva = cal.curva(xs, cal.f_riemann(xs), P, color=TINTA,
                          grosor=cal.TRAZO)
        area = cal.region(xs, cal.f_riemann(xs), P, color=TINTA,
                          opacidad=0.10)
        cuadro = cal.recuadro(P)

        dentro, fuera = [], []
        for n in self.CUANTOS:
            dentro.append(cal.rectangulos_dibujados(
                cal.rectangulos(n, "inferior"), P, color=CIAN,
                opacidad=0.20))
            fuera.append(cal.rectangulos_dibujados(
                cal.rectangulos(n, "superior"), P, color=AMBAR,
                opacidad=0.10))
        for g in dentro + fuera:
            g.set_stroke(opacity=0.0)
            g.set_fill(opacity=0.0)

        dibujo = lz.agrupar(cuadro, area, curva, *dentro, *fuera)

        # --- 1. un area que no se sabe medir ---------------------------
        L.escena(dibujo, t=1.2)
        self.leer(3.2)

        # --- 2, 3, 4. la pinza ----------------------------------------
        for i, n in enumerate(self.CUANTOS):
            dentro[i].set_stroke(opacity=0.9).set_fill(opacity=0.20)
            fuera[i].set_stroke(opacity=0.9).set_fill(opacity=0.10)
            animaciones = [FadeIn(dentro[i]), FadeIn(fuera[i])]
            if i:
                animaciones = [FadeOut(dentro[i - 1]), FadeOut(fuera[i - 1]),
                               *animaciones]
            lo, hi, hueco = cal.pinza(n)
            L.morfeo(None,
                     dato=(f"{hueco:.4f}", f"lo que discrepan con {n}"),
                     animaciones=animaciones, t=1.2)
            self.leer(3.2 if i < len(self.CUANTOS) - 1 else 3.6)

        # --- 5. y cuando dejan de discrepar ---------------------------
        # El dibujo no cambia: con 64 rectangulos las dos familias ya se
        # confunden en pantalla. Lo que cambia es que ahora se puede
        # decir el numero.
        L.dato(f"{cal.area_riemann():.4f}", "el area, sin discusion")
        self.leer(4.4)
