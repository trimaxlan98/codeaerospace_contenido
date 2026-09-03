# 01 · EL IMPULSO — no dura nada, pesa uno.
#
# ES EL MOLDE DEL CURSO. Las otras diecisiete copian de aqui la forma:
# construir TODOS los estados antes, entregarlos al lienzo en UN grupo
# para que compartan escala, y morfear entre ellos.
#
# El verbo visual: un rectangulo se estrecha y crece, y su AREA no se
# mueve. El impulso no es "una senal infinitamente alta porque si": es el
# limite de esa familia. Por eso la cifra de los cuatro primeros planos es
# la misma —el area, 1— y solo cambia al final, cuando lo dibujado deja de
# ser un rectangulo y pasa a ser el impulso. Un rectangulo tiene area; una
# muestra tiene duracion. Dejar el area de antes debajo de un tallo seria
# poner una medida al pie de otro dibujo.
#
# TRES COSAS QUE COSTARON UNA VUELTA Y VALEN PARA TODAS LAS PIEZAS:
#
#   - La altura del pulso NO es 1/ancho. Sobre una malla discreta el
#     rectangulo se queda con el numero ENTERO de muestras que caben
#     dentro, y con altura 1/ancho el area dibujada sale 0.9766 mientras
#     el rotulo dice 1. `sis.pulso_de_area` calcula la altura contra las
#     muestras que de verdad se dibujan.
#   - El salto de escala SE DECLARA. Entre el pulso de 0.8 y el de 0.2 hay
#     un factor 4 en altura; dibujarlos en el mismo cuadro sin decirlo
#     seria ensenar dos cosas distintas fingiendo que son la misma.
#   - **Dentro de un cuadro con el rango fijo, el estado mas bajo no puede
#     bajar de la mitad del mas alto.** La primera version encadenaba
#     1.6 -> 0.8 -> 0.4 en el mismo rango: el primer pulso quedaba en el
#     22 % de la franja y el fotograma se leia como un error de
#     maquetacion. De ahi salen los pares de razon 2 y el salto declarado
#     entre ellos. (Y de ahi salio tambien que el guardian de la fraccion
#     medee lo que se PINTA: con los estados apagados dentro del grupo, el
#     bounding box mentia y el guardian daba el visto bueno.)
#   - **La cifra del ultimo plano decia 21.** `sis.cola` mide DONDE se
#     acaba la senal contando desde el origen, asi que un impulso puesto
#     en la muestra 20 tiene cola 21 — y dura 1. El rotulo decia
#     "muestra que dura". Se separo en `sis.duracion`, con su
#     contraejemplo en la sonda: las dos cifras son utiles y son
#     distintas, y confundirlas pone un numero falso en pantalla.
class Clip(Pieza):
    NOMBRE = "EL IMPULSO"
    TESIS = "no dura nada, pesa uno"

    # Malla y ventana de tiempo: PARAMETROS elegidos.
    N = 1024
    T = 4.0
    ANCHO_CAJA = ANCHO - 0.5
    ALTO_CAJA = 4.6

    def _pulso(self, ancho, tope):
        t, x = sis.pulso_de_area(ancho, N=self.N, T=self.T)
        curva, _ = sis.traza(t, x, ancho=self.ANCHO_CAJA,
                             alto=self.ALTO_CAJA, color=CIAN,
                             grosor=sis.TRAZO,
                             rango_x=(-self.T / 2, self.T / 2),
                             rango_y=(0.0, tope), escalones=True)
        return curva, (t, x)

    def _cuadro(self, anchos, tope, etiqueta):
        """Un cuadro con sus estados, el suelo y el rotulo de escala."""
        curvas, datos = [], []
        for a in anchos:
            c, d = self._pulso(a, tope)
            curvas.append(c)
            datos.append(d)
        suelo = sis.cero(ancho=self.ANCHO_CAJA, y=-self.ALTO_CAJA / 2,
                         color=LINEA)
        eti = rot(etiqueta)
        eti.next_to(suelo, DOWN, buff=0.24)
        for c in curvas[1:]:
            c.set_stroke(opacity=0.0)
        return VGroup(suelo, eti, *curvas), curvas, datos

    def pieza(self):
        L = self.L

        # La altura de cada pulso la fija la libreria; los topes de los dos
        # cuadros se leen de ahi, no se eligen a ojo, para que el factor
        # del rotulo sea el de verdad.
        alto_de = lambda a: float(sis.pulso_de_area(a, N=self.N,
                                                    T=self.T)[1].max())
        tope_a, tope_b = alto_de(0.8), alto_de(0.2)
        factor = tope_b / tope_a

        # --- 1. el pulso ancho, y su area ------------------------------
        grupo_a, curvas_a, datos_a = self._cuadro(
            (1.6, 0.8), tope_a, "ESCALA 1X")
        L.escena(grupo_a, t=0.9)
        self.leer(2.4)

        L.dato(medido(sis.area(*datos_a[0]), 2), "el area, que no cambia",
               medido=True)
        self.leer(2.6)

        # --- 2. se estrecha a la mitad, y crece el doble ---------------
        curvas_a[1].set_stroke(opacity=1.0)
        self.play(Transform(curvas_a[0], curvas_a[1]), run_time=1.2,
                  rate_func=smooth)
        curvas_a[1].set_stroke(opacity=0.0)
        # El area se vuelve a MEDIR: si el dibujo y la cifra se separaran,
        # se veria aqui.
        L.dato(medido(sis.area(*datos_a[1]), 2), "el area, que no cambia",
               medido=True, t=0.4)
        self.leer(2.6)

        # --- 3. mucho mas estrecho, con el salto de escala DECLARADO ---
        grupo_b, curvas_b, datos_b = self._cuadro(
            (0.4, 0.2), tope_b, f"ESCALA {medido(factor, 1)}X")
        L.escena(grupo_b, t=0.9)
        self.leer(2.2)

        curvas_b[1].set_stroke(opacity=1.0)
        self.play(Transform(curvas_b[0], curvas_b[1]), run_time=1.2,
                  rate_func=smooth)
        curvas_b[1].set_stroke(opacity=0.0)
        L.dato(medido(sis.area(*datos_b[1]), 2), "el area, que no cambia",
               medido=True, t=0.4)
        self.leer(2.8)

        # --- 4. el limite: una sola muestra ---------------------------
        M = 41
        d = sis.impulso(N=M, n0=M // 2)
        tallo = sis.tallos(d, ancho=self.ANCHO_CAJA, alto=self.ALTO_CAJA,
                           color=AMBAR, grosor=3.4, punta=0.060,
                           rango_y=(0.0, 1.0))
        suelo = sis.cero(ancho=self.ANCHO_CAJA, y=-self.ALTO_CAJA / 2,
                         color=LINEA)
        nombre = rot("EL IMPULSO", color=AMBAR)
        nombre.next_to(suelo, DOWN, buff=0.24)

        L.relevo(escena=VGroup(suelo, nombre, tallo),
                 dato=(medido(sis.duracion(d), 0), "muestra que dura"), t=1.0)
        self.leer(2.8)
        self.leer(2.4)
