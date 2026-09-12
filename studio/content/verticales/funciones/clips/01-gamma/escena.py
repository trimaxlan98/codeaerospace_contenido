# 01 · GAMMA — el factorial sin escalones.
#
# ES EL MOLDE DEL CURSO. Las otras diecisiete copian de aqui la forma:
#
#   1. UN solo `marco()` para toda la pieza. Todo lo que se dibuja pasa
#      por el mismo `P(x, y)`: dos curvas del mismo plano calculadas con
#      marcos distintos salen a escalas distintas y nadie lo nota.
#   2. TODOS los estados se construyen ANTES y se entregan al lienzo en
#      UN grupo, apagados con opacidad. Lo que se construye despues de
#      `L.escena` no lleva la escala ni la posicion que le dio `encajar`.
#   3. Se encienden con `set_stroke(opacity=)` si son curvas —`set_opacity`
#      enciende tambien el RELLENO y convierte una polilinea en una mancha
#      maciza (curso 32)— y con `set_opacity` si son puntos o texto.
#   4. `Create(..., introducer=False)`. Con el defecto, al terminar la
#      animacion manim RE-AÑADE el mobject a la escena, lo saca del grupo
#      del carril, y el carril ya no puede apagarlo: aparece encimado en
#      el plano siguiente (curso 33).
#   5. Dibujo y cifra cambian EN EL MISMO gesto (`L.morfeo`). Encender el
#      punto y despues poner el numero deja dos segundos con la cifra
#      hablando de algo que todavia no esta.
#
# EL VERBO VISUAL: el factorial solo existe en los enteros —cuatro puntos
# sueltos— y gamma es la curva que los enhebra y ademas sigue por donde no
# hay factoriales que interpolar. La cifra no es un adorno: 1.7725 es "el
# factorial de un medio", que es justo el numero que la pregunta del
# principio no podia tener.
#
# LO QUE COSTO UNA VUELTA Y VALE PARA TODAS LAS PIEZAS:
#
#   - **El guardian de la fraccion mide lo que se PINTA.** El primer plano
#     enseñaba solo los cuatro puntos del factorial: ocupaban el 38 % de
#     la franja y el render aborto. Se arregla eligiendo el RANGO del
#     cuadro (el eje y el punto de 3! ya suman el 47 %), no bajando el
#     umbral ni escalando el grupo.
#   - **Y el recorte de la curva NO se elige por el guardian.** La primera
#     version cortaba gamma a |y| <= 4 para que los puntos subieran dentro
#     del marco: la curva se quedaba por debajo del punto de 3! y el
#     dibujo afirmaba que la funcion no pasa por el factorial que dice
#     enhebrar. El recorte lo manda la CURVA (hasta 6.7, que es donde esta
#     3!) y el suelo lo manda la rama negativa (-4.3).
#   - **Gamma no pasa por sus polos: se dibuja en RAMAS.** Unir dos
#     infinitos con una raya vertical es la forma clasica de dibujar una
#     mentira — parece que la funcion pasa por ahi. `curva_gamma` devuelve
#     una lista de tramos, y cada uno es su propia polilinea.
class Clip(Pieza):
    NOMBRE = "GAMMA"
    TESIS = "el factorial sin escalones"

    # PARAMETROS elegidos (van en gris si alguna vez se rotulan): el
    # recorte de 4.0 no es estetico, decide el rango vertical y con el la
    # altura a la que caen los cuatro puntos dentro del cuadro.
    TECHO = 6.70
    PISO = -4.30
    RX = (-3.45, 4.60)
    RY = (-4.30, 6.70)
    ANCHO_CAJA = ANCHO - 0.55
    ALTO_CAJA = 4.95

    def pieza(self):
        L = self.L
        P = esp.marco(self.RX, self.RY, ancho=self.ANCHO_CAJA,
                      alto=self.ALTO_CAJA)

        # --- el mobiliario ---------------------------------------------
        eje = esp.eje_x(P)

        # --- los cuatro factoriales (CIAN: lo que ya existia) ----------
        puntos = VGroup()
        etiquetas = VGroup()
        for n in range(4):
            d = Dot(P(n + 1, esp.factorial(n)), radius=0.060, color=CIAN)
            e = rot(f"{n}!", color=CIAN)
            e.next_to(d, UP, buff=0.18)
            puntos.add(d)
            etiquetas.add(e)

        # --- gamma, en ramas (AMBAR: la funcion con nombre propio) -----
        ramas = esp.curva_gamma(self.RX[0], self.RX[1], N=5200,
                                recorte=self.TECHO, piso=self.PISO)
        principal = esp.curva(*ramas[-1], P, color=AMBAR, grosor=esp.TRAZO)
        izquierdas = VGroup(*[esp.curva(x, y, P, color=AMBAR,
                                        grosor=esp.TRAZO)
                              for x, y in ramas[:-1]])
        polos = VGroup(*[esp.vertical(P, -k) for k in range(0, 4)])
        for c in (principal, *izquierdas, *polos):
            c.set_stroke(opacity=0.0)

        # --- las dos marcas de medio camino ---------------------------
        g_medio = esp.gamma(0.5)
        g_menos = esp.gamma(-0.5)
        marca = esp.marca_en(P, 0.5, g_medio)
        guia = esp.plomada(P, 0.5, g_medio, color=TINTA)
        marca2 = esp.marca_en(P, -0.5, g_menos)
        guia2 = esp.plomada(P, -0.5, g_menos, color=TINTA)
        for m in (marca, marca2):
            m.set_opacity(0.0)
        for g in (guia, guia2):
            g.set_stroke(opacity=0.0)

        dibujo = lz.agrupar(eje, polos, izquierdas, principal, guia, guia2,
                            puntos, etiquetas, marca, marca2)

        # --- 1. el factorial solo existe en los enteros ----------------
        L.escena(dibujo, t=0.9)
        self.leer(2.8)

        # --- 2. una curva los enhebra ---------------------------------
        # El trazo se ENCIENDE justo antes del Create y no antes: una
        # curva con `stroke_opacity=0` se "crea" entera sin pintar un
        # pixel, y el render sale limpio, sin aviso y sin curva. (El
        # primer `ql` de este molde no tenia ni una de las cinco.) Encender
        # fuera del `play` no la enseña: `Create` empieza en alpha=0, o
        # sea con el camino vacio.
        principal.set_stroke(opacity=1.0)
        self.play(Create(principal, introducer=False), run_time=2.0,
                  rate_func=smooth)
        self.leer(2.4)

        # --- 3. y da respuesta donde no habia ninguna ------------------
        L.morfeo(None,
                 dato=(medido(g_medio, 4), "el factorial de un medio"),
                 animaciones=[marca.animate.set_opacity(1.0),
                              guia.animate.set_stroke(opacity=1.0)],
                 t=0.9)
        self.leer(3.2)

        # --- 4. y ese numero no es cualquiera -------------------------
        # El dibujo no cambia: cambia lo que se afirma DEL MISMO punto, y
        # la etiqueta lo dice. Es el unico relevo de cifra del curso sobre
        # un dibujo quieto, y se permite porque el segundo numero es el
        # cuadrado del primero — o sea, sigue hablando de lo que se ve.
        L.dato(medido(g_medio ** 2, 4), "su cuadrado, que es pi",
               medido=True)
        self.leer(2.6)

        # --- 5. la funcion sigue donde el factorial no significa nada --
        for c in izquierdas:
            c.set_stroke(opacity=1.0)
        self.play(*[Create(c, introducer=False) for c in izquierdas],
                  *[c.animate.set_stroke(opacity=1.0) for c in polos],
                  run_time=2.2, rate_func=smooth)
        self.leer(2.6)

        L.morfeo(None,
                 dato=(medido(g_menos, 4), "y el de menos un medio"),
                 animaciones=[marca2.animate.set_opacity(1.0),
                              guia2.animate.set_stroke(opacity=1.0)],
                 t=0.9)
        self.leer(3.0)
