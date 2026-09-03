# 12 · AUTOFUNCIONES — lo unico que no deforma.
#
# LA BISAGRA DEL CURSO. Explica POR QUE existen las transformadas sin
# contar ninguna: si hay UNA familia de senales que el sistema no
# deforma, descomponer cualquier senal en esa familia convierte la caja
# entera en una multiplicacion. La pieza no dice eso con palabras; lo
# ensena metiendo dos cosas por la misma caja.
#
# EL VERBO, EN DOS ACTOS, Y EL PRIMERO NO ES OPCIONAL:
#
#   1. Entra un pulso rectangular y sale un timbre que oscila y se apaga:
#      OTRA FORMA. Sin ensenar primero algo que se deforma, que el coseno
#      no se deforme no significa nada — seria un dibujo bonito sin
#      contraste.
#   2. Entra un coseno y sale EL MISMO coseno, mas grande y corrido. Y el
#      remate lo demuestra: la entrada se multiplica por el factor delante
#      de quien mira (un Transform que la hace crecer y correrse) y la
#      salida de verdad aterriza encima sin separarse.
#
# LOS DOS CUIDADOS QUE HACEN QUE ESTO NO SEA UNA MENTIRA:
#
#   - LOS CUATRO PANELES COMPARTEN `RANGO` (-1.9, 1.9). Si cada uno se
#     normalizara por su cuenta, el x1.5644 desapareceria del dibujo y la
#     cifra se quedaria sola diciendo algo que no se ve. Por eso el rango
#     es una constante de la pieza y no un argumento de cada panel.
#   - LA COMPARACION SE HACE EN EL TRAMO YA ASENTADO. La convolucion tarda
#     `h.size` muestras en llenarse; ahi la igualdad todavia no puede
#     cumplirse y medir en ese tramo daria un error grande y falso (lo
#     dice la propia `sis.error_autofuncion`, que arranca en `h.size`). La
#     ventana dibujada empieza exactamente donde empieza la de la cifra, y
#     el recorte se DECLARA con el rotulo micro "TRAMO ASENTADO".
#
# La curva de referencia del remate va en CIAN OPACO y gruesa, no en
# ambar traslucido: el ambar transparente sobre este azul da un gusano
# oliva ilegible (trampa medida por la pieza 05). Y ademas cian es lo que
# le toca: esa curva ES la entrada, solo que multiplicada.
class Clip(Pieza):
    NOMBRE = "AUTOFUNCIONES"
    TESIS = "lo unico que no deforma"

    # --- parametros ELEGIDOS (van con etiqueta gris si se rotulan) -----
    M_H = 48                 # cuantas muestras dura la caja
    TAU = 9.0
    FREQ = 0.11
    W = 0.4                  # radianes por muestra del coseno de prueba
    N1 = 90                  # ventana del acto 1
    A1, B1 = 8, 24           # donde empieza y acaba el pulso
    N2 = 200                 # cuanto coseno se convoluciona
    VENTANA = 63             # cuatro periodos, ya asentados

    # --- geometria -----------------------------------------------------
    ANCHO_CAJA = ANCHO - 0.6
    ALTO_PANEL = 2.05
    ALTO_REMATE = 3.9
    BANDA_CIAN = 11.0        # la referencia va gruesa: es una BANDA
    RANGO = (-1.9, 1.9)      # EL MISMO para los cuatro paneles
    Y_ENT = 1.50
    Y_SAL = -1.40

    def _panel(self, idx, valores, color, y, etiqueta, escalones=False):
        """Un panel: su eje de ceros, su curva y su nombre debajo.

        El eje va en el CENTRO del panel porque el rango es simetrico, asi
        que "por encima del eje" y "por debajo" significan lo mismo en los
        dos paneles y la comparacion se puede hacer a ojo."""
        curva, _ = sis.traza(idx, valores, ancho=self.ANCHO_CAJA,
                             alto=self.ALTO_PANEL, color=color,
                             grosor=sis.TRAZO,
                             rango_x=(float(idx[0]), float(idx[-1])),
                             rango_y=self.RANGO, escalones=escalones)
        eje = sis.cero(ancho=self.ANCHO_CAJA, y=0.0, color=LINEA)
        eti = rot(etiqueta)
        eti.move_to([0, -self.ALTO_PANEL / 2 - 0.30, 0])
        return VGroup(eje, eti, curva).shift(UP * y), curva

    def _curva_remate(self, idx, valores, color, grosor):
        curva, _ = sis.traza(idx, valores, ancho=self.ANCHO_CAJA,
                             alto=self.ALTO_REMATE, color=color,
                             grosor=grosor,
                             rango_x=(float(idx[0]), float(idx[-1])),
                             rango_y=self.RANGO)
        return curva

    def pieza(self):
        L = self.L
        h = sis.h_amortiguada(N=self.M_H, tau=self.TAU, f=self.FREQ)

        # === ACTO 1 · una senal cualquiera sale con otra forma ==========
        n1 = np.arange(self.N1)
        # El pulso se arma con dos escalones de la libreria: asi ni sus
        # muestras ni su duracion son numeros puestos a mano aqui.
        x1 = sis.escalon(self.N1, self.A1) - sis.escalon(self.N1, self.B1)
        y1 = sis.convolucion(x1, h)[:self.N1]

        pan_e1, cur_e1 = self._panel(n1, x1, CIAN, self.Y_ENT, "ENTRADA",
                                     escalones=True)
        pan_s1, cur_s1 = self._panel(n1, y1, AMBAR, self.Y_SAL, "SALIDA",
                                     escalones=True)
        cur_s1.set_stroke(opacity=0.0)

        L.relevo(escena=VGroup(pan_e1, pan_s1),
                 dato=(medido(sis.duracion(x1), 0),
                       "muestras dura la entrada"), t=0.9)
        self.leer(2.2)

        # La salida: ni empieza donde empezaba, ni acaba donde acababa, ni
        # tiene los lados rectos. Es OTRA forma.
        self.play(cur_s1.animate.set_stroke(opacity=1.0), run_time=0.9)
        self.leer(2.2)
        L.dato(medido(sis.duracion(y1), 0), "muestras dura la salida",
               medido=True, t=0.5)
        self.leer(2.2)

        # === ACTO 2 · el coseno entra y sale igual =====================
        desde = h.size                       # donde acaba el transitorio
        n2 = np.arange(desde, desde + self.VENTANA)
        # La exponencial compleja de la libreria; en la practica, su parte
        # real, que es lo que se puede dibujar.
        x2 = np.real(sis.exponencial(self.W, self.N2))
        y2 = sis.convolucion(x2, h)[:self.N2]

        pan_e2, cur_e2 = self._panel(n2, x2[desde:desde + self.VENTANA],
                                     CIAN, self.Y_ENT, "ENTRADA")
        pan_s2, cur_s2 = self._panel(n2, y2[desde:desde + self.VENTANA],
                                     AMBAR, self.Y_SAL, "SALIDA")
        cur_s2.set_stroke(opacity=0.0)

        L.relevo(escena=VGroup(pan_e2, pan_s2),
                 dato=(medido(self.W, 1), "radianes por muestra", False),
                 t=0.9)
        self.leer(2.4)

        self.play(cur_s2.animate.set_stroke(opacity=1.0), run_time=0.9)
        self.leer(2.4)

        # El autovalor es UN numero complejo: su modulo es cuanto
        # amplifica y su fase cuanto corre. Se ensenan por separado porque
        # son las dos unicas cosas que le pasan a la senal.
        lam = sis.autovalor(h, self.W)
        L.dato(medido(abs(lam), 4), "veces la amplitud", medido=True, t=0.5)
        self.leer(2.2)
        L.dato(medido(float(np.angle(lam)), 4), "radianes de corrimiento",
               medido=True, t=0.5)
        self.leer(2.0)

        # === ACTO 3 · la entrada por el factor ES la salida ============
        ent = self._curva_remate(n2, x2[desde:desde + self.VENTANA],
                                 CIAN, self.BANDA_CIAN)
        # El objetivo del Transform NO se dibuja a mano: es
        # `parte_permanente`, o sea la entrada multiplicada por el
        # autovalor. Que crezca y se corra es la multiplicacion en si.
        pp = sis.parte_permanente(h, self.W, self.N2)
        ent_por_lam = self._curva_remate(n2, pp[desde:desde + self.VENTANA],
                                         CIAN, self.BANDA_CIAN)
        ent_por_lam.set_stroke(opacity=0.0)
        # La salida va a TROZOS sobre la banda. Solida y fina no valia: el
        # ambar de 2.2 encima del cian se antialiasaba con el y las dos
        # curvas salian fundidas en UN gusano verde oliva — el mismo
        # sintoma de la trampa del ambar traslucido, esta vez por
        # superposicion de dos trazos opacos. Con la salida a trozos, en
        # cada hueco se ve el cian puro y en cada trozo el ambar puro:
        # "coinciden" se lee porque se ven DOS curvas, no una de color
        # raro.
        sal_solida = self._curva_remate(n2, y2[desde:desde + self.VENTANA],
                                        AMBAR, 4.5)
        sal = DashedVMobject(sal_solida, num_dashes=34, dashed_ratio=0.55)
        sal.set_stroke(color=AMBAR, width=4.5, opacity=0.0)

        eje_r = sis.cero(ancho=self.ANCHO_CAJA, y=0.0, color=LINEA)
        eti_a = rot("ENTRADA", color=CIAN)
        eti_b = rot("ENTRADA POR EL FACTOR", color=CIAN)
        for e in (eti_a, eti_b):
            e.move_to([0, -self.ALTO_REMATE / 2 - 0.32, 0])
        eti_b.set_opacity(0.0)
        micro = rot("TRAMO ASENTADO", cuerpo=lz.MICRO)
        micro.move_to([0, -self.ALTO_REMATE / 2 - 0.68, 0])

        L.relevo(escena=VGroup(eje_r, eti_a, eti_b, micro, ent,
                               ent_por_lam, sal), t=0.9)
        self.leer(2.2)

        # Multiplicar por el factor, delante de quien mira. El objetivo
        # tiene que estar VIVO durante el play: Transform copia tambien la
        # opacidad, y hacia un estado apagado el dibujo desaparece.
        ent_por_lam.set_stroke(opacity=1.0)
        self.play(Transform(ent, ent_por_lam),
                  eti_a.animate.set_opacity(0.0),
                  eti_b.animate.set_opacity(1.0),
                  run_time=1.2, rate_func=smooth)
        ent_por_lam.set_stroke(opacity=0.0)
        self.leer(2.4)

        # Y la salida de verdad aterriza encima.
        self.play(sal.animate.set_stroke(opacity=1.0), run_time=0.9)
        self.leer(2.4)

        L.dato(medido(sis.error_autofuncion(h, self.W), 2),
               "por ciento de error", medido=True, t=0.5)
        self.leer(2.6)
