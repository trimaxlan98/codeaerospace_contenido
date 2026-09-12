# 02 · LAMBERT — el despeje imposible.
#
# La ecuacion x·e^x = 1 no se puede despejar con funciones elementales, y
# no por falta de ingenio: se demostro que la solucion NO ES expresable
# asi. La salida fue ponerle nombre a la solucion, que es lo que hace este
# curso entero. Pero el numero existe y se puede encontrar SIN despejar
# nada: iterando.
#
# El verbo visual es la telaraña. Despejar x·e^x = 1 es lo mismo que
# buscar el x que cumple x = e^-x, o sea el cruce de la exponencial
# decreciente con la diagonal. La telaraña rebota entre las dos y se posa
# en el cruce. Nadie despeja, y el numero aparece.
#
# Tres decisiones que merece la pena dejar escritas:
#
#   - **La segunda telaraña empieza al otro lado y termina en el mismo
#     sitio.** Con una sola, un espectador razonable puede pensar que el
#     punto depende de por donde empezaste. Con dos, se ve que no. La
#     sonda lo comprueba desde 0.0, 0.4, 2.0 y 7.5.
#   - **La cifra NO cambia en toda la pieza**, y eso es el contenido: el
#     punto fijo, la solucion de x·e^x = 1 y el valor de W en 1 son el
#     mismo numero. Lo que se releva es la ETIQUETA y el dibujo.
#   - La curva de x·e^x se sale del cuadro por arriba a partir de x ~ 1.05:
#     se corta con `esp.recortar`, que devuelve los tramos que caben. Un
#     `np.clip` la aplastaria contra el borde y se leeria como que la
#     funcion se estanca, que es lo contrario de lo que hace.
class Clip(Pieza):
    NOMBRE = "LAMBERT"
    TESIS = "el despeje imposible"

    # PARAMETROS elegidos: los dos arranques de las telarañas y cuantos
    # rebotes se dibujan. El resultado no depende de ellos — que no
    # dependa es justo lo que la pieza afirma.
    X0_A = 0.05
    X0_B = 1.55
    REBOTES = 12

    RX = (0.0, 1.62)
    RY = (0.0, 1.62)
    ANCHO_CAJA = ANCHO - 0.60
    ALTO_CAJA = 4.55

    def pieza(self):
        L = self.L
        w = esp.omega()
        P = esp.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)

        # --- plano 1: las dos curvas que se cruzan una sola vez --------
        ejes = lz.agrupar(esp.eje_x(P), esp.eje_y(P))
        xs = np.linspace(self.RX[0], self.RX[1], 900)
        exp = esp.curva(xs, np.exp(-xs), P, color=AMBAR, grosor=esp.TRAZO)
        diag = esp.curva(xs, xs, P, color=CIAN, grosor=esp.TRAZO_FINO)
        # Los rotulos van DENTRO del cuadro, colocados con move_to sobre
        # coordenadas de datos elegidas en zona vacia. Con `next_to` sobre
        # un punto cercano al borde, el rotulo sobresale, el grupo pasa de
        # los 5.76 de zona segura, `encajar` lo encoge y el guardian de
        # legibilidad aborta con "el rotulo mas pequeño mide 0.143". El
        # sintoma no señala la causa: el problema no era el tamaño de la
        # letra, era un rotulo asomando por la derecha.
        rot_exp = rot("E A LA MENOS X", color=AMBAR)
        rot_diag = rot("LA DIAGONAL", color=CIAN)

        tela_a = esp.telarana(lambda v: float(np.exp(-v)), self.X0_A,
                              self.REBOTES, P, color=TINTA,
                              grosor=esp.TRAZO_FINO)
        tela_b = esp.telarana(lambda v: float(np.exp(-v)), self.X0_B,
                              self.REBOTES, P, color=TINTA,
                              grosor=esp.TRAZO_FINO)
        cruce = esp.marca_en(P, w, w)

        for c in (exp, diag, tela_a, tela_b):
            c.set_stroke(opacity=0.0)
        cruce.set_opacity(0.0)
        rot_exp.move_to(P(0.95, 1.38))
        rot_diag.move_to(P(1.02, 0.17))
        for r in (rot_exp, rot_diag):
            r.set_opacity(0.0)

        dibujo = lz.agrupar(ejes, exp, diag, tela_a, tela_b, cruce,
                            rot_exp, rot_diag)
        L.escena(dibujo, t=0.9)
        for c in (exp, diag):
            c.set_stroke(opacity=1.0)
        self.play(Create(exp, introducer=False),
                  Create(diag, introducer=False), run_time=1.7,
                  rate_func=smooth)
        self.play(rot_exp.animate.set_opacity(1.0),
                  rot_diag.animate.set_opacity(1.0), run_time=0.5)
        self.leer(2.6)

        # --- plano 2: la telaraña cae al cruce -------------------------
        tela_a.set_stroke(opacity=1.0)
        self.play(Create(tela_a, introducer=False), run_time=2.4,
                  rate_func=linear)
        L.morfeo(None, dato=(medido(w, 4), "el unico punto fijo"),
                 animaciones=[cruce.animate.set_opacity(1.0)], t=0.7)
        self.leer(2.8)

        # --- plano 3: y da igual por donde empieces --------------------
        tela_b.set_stroke(opacity=1.0)
        self.play(FadeOut(tela_a), run_time=0.5)
        self.play(Create(tela_b, introducer=False), run_time=2.0,
                  rate_func=linear)
        self.leer(2.6)

        # --- plano 4: el otro problema, la misma respuesta -------------
        # x·e^x = 1. Se sale del cuadro por arriba: se CORTA, no se
        # aplasta.
        P2 = esp.marco((-0.85, 1.62), (-0.85, 1.62), ancho=self.ANCHO_CAJA,
                       alto=self.ALTO_CAJA)
        xs2 = np.linspace(-0.85, 1.62, 1400)
        tramos = esp.recortar(xs2, xs2 * np.exp(xs2), (-0.85, 1.62))
        xex = lz.agrupar(*[esp.curva(a, b, P2, color=AMBAR,
                                     grosor=esp.TRAZO) for a, b in tramos])
        uno = esp.curva(np.array([-0.85, 1.62]), np.array([1.0, 1.0]), P2,
                        color=CIAN, grosor=esp.TRAZO_PELO)
        marca2 = esp.marca_en(P2, w, 1.0)
        plom2 = esp.plomada(P2, w, 1.0, color=TINTA)
        rot_xex = rot("X POR E A LA X", color=AMBAR)
        rot_xex.move_to(P2(-0.14, 1.30))
        dibujo2 = lz.agrupar(esp.eje_x(P2), esp.eje_y(P2), uno, xex,
                             plom2, marca2, rot_xex)

        L.relevo(escena=dibujo2,
                 dato=(medido(w, 4), "el x que hace uno"), t=0.9)
        self.leer(3.0)

        # --- plano 5: y por eso tiene nombre ---------------------------
        P3 = esp.marco((-0.80, 3.20), (-1.05, 3.20), ancho=self.ANCHO_CAJA,
                       alto=self.ALTO_CAJA)
        ys = np.linspace(-0.36, 3.20, 1200)
        curva_w = esp.curva(ys, esp.lambert_w(ys), P3, color=AMBAR,
                            grosor=esp.TRAZO)
        tramos3 = esp.recortar(xs2, xs2 * np.exp(xs2), (-1.05, 3.20))
        xex3 = lz.agrupar(*[esp.curva(a, b, P3, color=CIAN,
                                      grosor=esp.TRAZO_FINO)
                            for a, b in tramos3])
        espejo = esp.curva(np.array([-0.80, 3.20]), np.array([-0.80, 3.20]),
                           P3, color=APAGADO, grosor=esp.TRAZO_PELO,
                           a_trozos=True)
        marca3 = esp.marca_en(P3, 1.0, w)
        plom3 = esp.plomada(P3, 1.0, w, color=TINTA)
        rot_w = rot("W DE LAMBERT", color=AMBAR)
        rot_w.move_to(P3(2.30, -0.38))
        dibujo3 = lz.agrupar(esp.eje_x(P3), esp.eje_y(P3), espejo, xex3,
                             curva_w, plom3, marca3, rot_w)

        L.relevo(escena=dibujo3,
                 dato=(medido(w, 4), "lo que vale w en uno"), t=0.9)
        self.leer(3.2)
