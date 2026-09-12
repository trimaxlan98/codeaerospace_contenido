# 02 · EPSILON-DELTA — el limite sin trampas.
#
# EL VERBO VISUAL: un juego de dos bandas. Tu aprietas la de arriba —"lo
# quiero a menos de tanto de 9"— y yo contesto con una de al lado: "quedate
# a menos de tanto de 3". Mientras pueda contestar, el limite existe. Es la
# definicion entera, sin una sola letra griega en pantalla.
#
# POR QUE LA PARABOLA Y NO UNA RECTA: en una recta el margen que se
# contesta es el mismo que se pide y el juego no se ve. Aqui la curva
# empina, los dos lados de la banda NO son simetricos y hay que quedarse
# con el corto: 0.0166 por arriba contra 0.0167 por abajo.
#
# EL CUADRO NO LLEVA EJE: el cero no cae dentro (ni en x ni en y), asi que
# `eje_x` abortaria a proposito. Lleva `recuadro`, que es lo que dice
# "esto es una ventana sobre la curva" sin afirmar donde esta el origen.
class Clip(Pieza):
    NOMBRE = "EPSILON-DELTA"
    TESIS = "el limite sin trampas"

    X0 = 3.0
    EPS = (1.0, 0.3, 0.1)
    RX = (2.40, 3.60)
    RY = (5.40, 12.70)
    ANCHO_CAJA = ANCHO - 0.60
    ALTO_CAJA = 4.60

    def pieza(self):
        L = self.L
        P = cal.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)
        L9 = cal.limite_cuadrado(self.X0)

        cuadro = cal.recuadro(P)
        xs = np.linspace(self.RX[0], self.RX[1], 900)
        curva = cal.curva(xs, xs ** 2, P, color=AMBAR, grosor=cal.TRAZO)
        punto = cal.marca_en(P, self.X0, L9)

        # --- las bandas, una por tolerancia ---------------------------
        # CIAN lo que se pide, AMBAR lo que se contesta: son las dos
        # unicas cosas que hay que distinguir en la pieza.
        h_bandas, v_bandas, deltas = [], [], []
        for e in self.EPS:
            d = cal.delta_para(e, self.X0)
            deltas.append(d)
            h_bandas.append(cal.banda(P, L9 - e, L9 + e, color=CIAN))
            v_bandas.append(cal.banda(P, self.X0 - d, self.X0 + d,
                                      vertical_=True, color=AMBAR))
        doble = cal.banda(P, self.X0 - 2 * deltas[-1],
                          self.X0 + 2 * deltas[-1], vertical_=True,
                          color=APAGADO)
        # Los dos puntos por donde la curva SE SALE con el doble de
        # margen: sin marcarlos, el contraejemplo es un dibujo en el que
        # no pasa nada.
        fuga = VGroup(*[cal.marca_en(P, self.X0 + s * 2 * deltas[-1],
                                     (self.X0 + s * 2 * deltas[-1]) ** 2,
                                     color=TINTA, radio=0.050)
                        for s in (-1, 1)])

        eti_h = rot("pides")
        eti_h.move_to(P(2.60, 11.90))
        eti_v = rot("contesto")
        eti_v.move_to(P(3.30, 6.10))

        # El relleno no basta para decir de que color es una banda: el
        # ambar al 13 % sobre este azul marino sale gris verdoso (medido
        # en el curso 31). El color lo pone el BORDE, que va opaco; el
        # relleno solo dice "aqui dentro".
        for b in h_bandas:
            b.set_stroke(color=CIAN, width=1.4, opacity=0.85)
        for b in v_bandas:
            b.set_stroke(color=AMBAR, width=1.4, opacity=0.85)
        doble.set_stroke(color=APAGADO, width=1.2, opacity=0.8)
        for b in h_bandas + v_bandas + [doble]:
            b.set_fill(opacity=0.0)
            b.set_stroke(opacity=0.0)
        for m in (eti_h, eti_v, fuga):
            m.set_opacity(0.0)

        dibujo = lz.agrupar(cuadro, curva, punto, h_bandas[0], v_bandas[0],
                            eti_h, eti_v, doble, fuga,
                            *h_bandas[1:], *v_bandas[1:])

        # --- 1. la curva y el punto del que se habla -------------------
        L.escena(dibujo, t=1.2)
        soltar(dibujo, *h_bandas[1:], *v_bandas[1:])
        self.leer(2.6)

        # --- 2. se pide una tolerancia y se contesta un margen ---------
        h_bandas[0].set_fill(opacity=0.16).set_stroke(opacity=0.85)
        v_bandas[0].set_fill(opacity=0.16).set_stroke(opacity=0.85)
        self.play(FadeIn(h_bandas[0]), eti_h.animate.set_opacity(1.0),
                  run_time=0.8)
        self.leer(2.6)
        L.morfeo(None,
                 dato=(f"{deltas[0]:.4f}", "de margen a cada lado"),
                 animaciones=[FadeIn(v_bandas[0]),
                              eti_v.animate.set_opacity(1.0)], t=0.9)
        self.leer(2.6)

        # --- 3, 4. la tolerancia se aprieta y sigue habiendo respuesta -
        for i in range(1, len(self.EPS)):
            h_bandas[i].set_fill(opacity=0.16).set_stroke(opacity=0.85)
            v_bandas[i].set_fill(opacity=0.16).set_stroke(opacity=0.85)
            L.morfeo(None,
                     dato=(f"{deltas[i]:.4f}", "de margen a cada lado"),
                     animaciones=[Transform(h_bandas[0], h_bandas[i]),
                                  Transform(v_bandas[0], v_bandas[i])],
                     t=1.1)
            self.leer(2.6 if i < len(self.EPS) - 1 else 3.0)

        # --- 5. y no vale cualquier margen -----------------------------
        # El contraejemplo es la mitad de la definicion: si valiera el
        # doble, la respuesta no seria una respuesta.
        doble.set_fill(opacity=0.10).set_stroke(opacity=0.8)
        L.morfeo(None,
                 dato=(f"{2 * deltas[-1]:.4f}", "el doble ya se sale"),
                 animaciones=[FadeIn(doble),
                              fuga.animate.set_opacity(1.0)], t=1.0)
        self.leer(3.4)
