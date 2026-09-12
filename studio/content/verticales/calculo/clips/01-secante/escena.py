# 01 · SECANTE — la pendiente de un instante.
#
# ES EL MOLDE DEL CURSO. Las otras diecisiete copian de aqui la forma:
#
#   1. UN solo `marco()` para toda la pieza. Todo lo que se dibuja pasa
#      por el mismo `P(x, y)`: dos curvas del mismo plano calculadas con
#      marcos distintos salen a escalas distintas y nadie lo nota.
#   2. TODOS los estados se construyen ANTES y se entregan al lienzo en
#      UN grupo, apagados con opacidad. Lo que se construye despues de
#      `L.escena` no lleva la escala ni la posicion que le dio `encajar`.
#   3. Los DESTINOS de un morfeo viajan dentro del grupo y se sacan con
#      `soltar()` justo despues de `L.escena` (ver su docstring). Y
#      `caja(P)` fija el encuadre para que ningun estado lo mueva.
#   4. Se encienden con `set_stroke(opacity=)` si son curvas —`set_opacity`
#      enciende tambien el RELLENO y convierte una polilinea en una mancha
#      maciza (curso 32)— y con `set_opacity` si son puntos o texto.
#   5. `Create(..., introducer=False)`. Con el defecto, al terminar la
#      animacion manim RE-AÑADE el mobject a la escena, lo saca del grupo
#      del carril, y el carril ya no puede apagarlo: aparece encimado en
#      el plano siguiente (curso 33).
#   6. Dibujo y cifra cambian EN EL MISMO gesto (`L.morfeo`). Encender el
#      punto y despues poner el numero deja dos segundos con la cifra
#      hablando de algo que todavia no esta.
#
# EL VERBO VISUAL: el segundo punto se acerca al primero y la recta DEJA
# DE GIRAR. La cifra no es un adorno: 5.00, 2.75, 1.81, 1.31 es la
# sucesion que se ve, y 1.0000 es donde para.
#
# POR QUE ESTA CUBICA: `x^3-2x` tiene un valle justo a la izquierda del
# punto, asi que la secante entra MUY inclinada y se endereza a la vista.
# Sobre una parabola la primera secante ya se parece a la tangente y la
# pieza no enseña nada.
#
# LOS CEROS QUE NO SE PUEDEN QUITAR: la cifra final se escribe con
# `f"{...:.4f}"` y no con `medido(..., 4)`. `medido` quita los ceros de
# adorno, y "1.0000" es justo el caso en que esos ceros NO son adorno:
# son la afirmacion de que la sucesion converge a uno clavado.
class Clip(Pieza):
    NOMBRE = "SECANTE"
    TESIS = "la pendiente de un instante"

    X0 = 1.0
    PASOS = (1.0, 0.5, 0.25, 0.1)
    RX = (-0.40, 2.05)
    RY = (-1.30, 4.60)
    ANCHO_CAJA = ANCHO - 0.55
    ALTO_CAJA = 4.70

    def tramo(self, m):
        """El trozo de secante que cabe en el cuadro, sin recortes feos.

        Se resuelve por donde sale la recta en vez de dibujarla entera y
        dejar que se salga: una recta que se sale mete puntos fuera del
        marco, `encajar` los cuenta y el dibujo entero se encoge."""
        y0, y1 = self.RY
        yA = float(cal.f_cubica(self.X0))
        xs = [self.X0 + (y0 - yA) / m, self.X0 + (y1 - yA) / m]
        return (max(self.RX[0], min(xs)), min(self.RX[1], max(xs)))

    def secante_de(self, h):
        """(recta, punto movil) para un paso h."""
        m = cal.secante(self.X0, h)
        a, b = self.tramo(m)
        xs = np.array([a, b])
        ys = cal.recta_por(self.X0, float(cal.f_cubica(self.X0)), m, xs)
        recta = cal.curva(xs, ys, self.P, color=CIAN, grosor=cal.TRAZO_FINO)
        punto = cal.marca_en(self.P, self.X0 + h,
                             float(cal.f_cubica(self.X0 + h)), color=CIAN,
                             radio=0.055)
        return recta, punto, m

    def pieza(self):
        L = self.L
        self.P = P = cal.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                               alto=self.ALTO_CAJA)

        # --- el mobiliario ---------------------------------------------
        eje = cal.eje_x(P)
        marco_fijo = caja(P)

        # --- la curva (AMBAR: lo que la pieza mira) --------------------
        xs = np.linspace(self.RX[0], self.RX[1], 1200)
        curva = cal.curva(xs, cal.f_cubica(xs), P, color=AMBAR,
                          grosor=cal.TRAZO)

        # --- el punto fijo, en TINTA porque es de donde sale la cifra --
        A = cal.marca_en(P, self.X0, float(cal.f_cubica(self.X0)))
        # Sin rotulo: el unico sitio con hueco de verdad es el cuadrante
        # de arriba a la izquierda, o sea lejisimos del punto, y una
        # etiqueta que no toca lo que nombra es peor que ninguna. Aqui no
        # hace falta: hay un punto blanco, un punto cian y una recta, y la
        # etiqueta de la cifra dice de que habla.

        # --- las cuatro secantes y la tangente (CIAN: lo que se compara)
        rectas, puntos, pendientes = [], [], []
        for h in self.PASOS:
            r, pt, m = self.secante_de(h)
            rectas.append(r)
            puntos.append(pt)
            pendientes.append(m)
        m_tan = float(cal.df_cubica(self.X0))
        a, b = self.tramo(m_tan)
        xt = np.array([a, b])
        tangente = cal.curva(xt, cal.recta_por(self.X0,
                                               float(cal.f_cubica(self.X0)),
                                               m_tan, xt),
                             P, color=TINTA, grosor=cal.TRAZO_FINO)
        for r in rectas + [tangente]:
            r.set_stroke(opacity=0.0)
        for pt in puntos:
            pt.set_opacity(0.0)

        dibujo = lz.agrupar(marco_fijo, eje, curva, A,
                            rectas[0], puntos[0],
                            *rectas[1:], *puntos[1:], tangente)

        # --- 1. una curva y un punto -----------------------------------
        # La curva entra ENCENDIDA y con el fundido del carril, no con un
        # `Create` posterior: el guardian de la fraccion mide lo que se
        # VE en el momento de encajar, y un primer estado entero a
        # opacidad 0 aborta el render con "ocupa el 0 %". El gesto de
        # esta pieza es la recta que gira, no la curva que se dibuja.
        L.escena(dibujo, t=1.3)
        soltar(dibujo, *rectas[1:], *puntos[1:], tangente)
        self.leer(3.0)

        # --- 2. dos puntos y una recta ---------------------------------
        # El trazo se ENCIENDE justo antes del Create y no antes: una
        # curva con `stroke_opacity=0` se "crea" entera sin pintar un
        # pixel, y el render sale limpio, sin aviso y sin recta.
        rectas[0].set_stroke(opacity=1.0)
        self.play(puntos[0].animate.set_opacity(1.0), run_time=0.45)
        L.morfeo(None,
                 dato=(f"{pendientes[0]:.2f}", "la pendiente entre dos puntos"),
                 animaciones=[Create(rectas[0], introducer=False)], t=1.2)
        self.leer(2.8)

        # --- 3, 4, 5. el segundo punto se acerca -----------------------
        # Un solo `Transform` por paso: la recta GIRA. Relevarla apagando
        # una y encendiendo otra se leeria como cinco rectas distintas, y
        # lo que la pieza afirma es que es LA MISMA recta moviendose.
        for i in range(1, len(self.PASOS)):
            rectas[i].set_stroke(opacity=1.0)
            puntos[i].set_opacity(1.0)
            L.morfeo(None,
                     dato=(f"{pendientes[i]:.2f}",
                           "la pendiente entre dos puntos"),
                     animaciones=[Transform(rectas[0], rectas[i]),
                                  Transform(puntos[0], puntos[i])],
                     t=1.0)
            self.leer(2.2 if i < len(self.PASOS) - 1 else 2.6)

        # --- 6. y deja de girar ----------------------------------------
        tangente.set_stroke(opacity=1.0)
        L.morfeo(None,
                 dato=(f"{m_tan:.4f}", "la pendiente en ese punto"),
                 animaciones=[Transform(rectas[0], tangente),
                              puntos[0].animate.set_opacity(0.0)],
                 t=1.2)
        self.leer(3.6)
