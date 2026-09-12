# 12 · CANTOR — sube sin subir nunca.
#
# Se quita el tercio central de un segmento. A los dos trozos que quedan,
# tambien. Y otra vez. Lo que sobrevive despues de infinitas veces es el
# conjunto de Cantor: no le queda NADA de longitud y sin embargo tiene
# tantos puntos como el segmento entero.
#
# La escalera del diablo es la funcion que sube de 0 a 1 usando solo esos
# puntos. Es continua, no baja nunca, y su derivada vale cero en casi todo
# el recorrido. Sube sin tener donde subir.
#
# COMO SE CONSTRUYE, y es lo que salvo la pieza: NO por expansion en base
# 3. Esa es la forma de libro y con flotantes no sobrevive — la escalera
# BAJABA en 41 sitios y en x=1 devolvia 0 en vez de 1. Se construye de la
# definicion geometrica, la misma que dibuja el peine: sobre el k-esimo
# intervalo que sobrevive, la funcion sube de k/2^n a (k+1)/2^n, y entre
# uno y otro se queda quieta. Monotona por construccion.
class Clip(Pieza):
    NOMBRE = "CANTOR"
    TESIS = "sube sin subir nunca"

    # PARAMETROS elegidos: los niveles del peine que se dibujan y los de
    # la escalera. Son distintos a proposito — el peine deja de verse a
    # partir del quinto corte, la escalera no.
    PEINE = 5
    NIVELES = 10
    ANCHO_CAJA = ANCHO - 0.55

    def pieza(self):
        L = self.L

        # --- 1. el peine: se quita el tercio central, y otra vez ------
        niveles = esp.tramos_cantor(self.PEINE)
        P = esp.marco((-0.02, 1.02), (-0.55, self.PEINE + 0.35),
                      ancho=self.ANCHO_CAJA, alto=4.30)
        filas = []
        for k, tramos in enumerate(niveles):
            y = self.PEINE - k
            fila = VGroup(*[Line(P(a, y), P(b, y), stroke_color=AMBAR,
                                 stroke_width=6.0) for a, b in tramos])
            if k:
                fila.set_stroke(opacity=0.0)
            filas.append(fila)
        peine = lz.agrupar(*filas)

        # `bajo=True` porque el primer plano es UN SEGMENTO: alto cero, y
        # el guardian de la fraccion —que mide lo que se PINTA— aborta con
        # "ocupa el 0 %". Es justo el caso para el que existe la valvula:
        # el dibujo no es bajo por descuido, es que el conjunto de Cantor
        # empieza siendo una raya.
        L.escena(peine, t=0.9, bajo=True)
        self.leer(2.6)
        for k in range(1, len(filas)):
            self.play(filas[k].animate.set_stroke(opacity=1.0),
                      run_time=0.55)
        L.dato(medido(esp.medida_cantor(self.PEINE) * 100.0, 2),
               "por ciento que queda")
        self.leer(3.4)

        # --- 2. la escalera que sube por esos huecos ------------------
        xs, ys = esp.escalera_cantor(self.NIVELES)
        Q = esp.marco((-0.02, 1.02), (-0.03, 1.03),
                      ancho=self.ANCHO_CAJA, alto=4.30)
        escalera = esp.curva(xs, ys, Q, color=AMBAR, grosor=2.6)
        escalera.set_stroke(opacity=0.0)
        diag = esp.curva(np.array([0.0, 1.0]), np.array([0.0, 1.0]), Q,
                         color=APAGADO, grosor=esp.TRAZO_PELO,
                         a_trozos=True)
        panel = lz.agrupar(esp.recuadro(Q), diag, escalera)

        L.relevo(escena=panel, dato=None, t=0.7)
        escalera.set_stroke(opacity=1.0)
        self.play(Create(escalera, introducer=False), run_time=2.8,
                  rate_func=linear)
        self.leer(2.6)

        # --- 3. plana en casi todo el recorrido ----------------------
        L.dato(medido(esp.mesetas(self.NIVELES) * 100.0, 2),
               "por ciento de llano")
        self.leer(3.6)

        # --- 4. y aun asi llega arriba -------------------------------
        # La cifra sale de la propia escalera dibujada: su ultimo valor.
        L.dato(medido(float(ys[-1]), 0), "lo que sube en total")
        self.leer(3.6)
