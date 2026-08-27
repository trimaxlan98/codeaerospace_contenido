class Clip(Scene):
    """10 · El zoom — bajar cien mil veces y encontrarse el principio.

    Diez saltos de x3.16 hacia el mismo punto del valle de los caballitos
    (-0.743643887 + 0.131825904 i). Cada salto se hace con una imagen NUEVA,
    calculada mas profunda y con mas iteraciones, que releva a la anterior
    justo cuando esta ha crecido lo mismo que el salto: el empalme no se ve
    porque el color depende de (iteraciones mod ciclo) y no de max_iter.

    Al final, a x100 000, aparece en el centro un Mandelbrot entero — con su
    cardioide, su bulbo y sus antenas. No es una figura parecida: es el
    mismo conjunto, otra vez.

    El aumento que sale en pantalla es el cociente REAL entre el ancho
    inicial y el de la imagen que se esta viendo.
    """

    CENTRO = complex(-0.743643887037151, 0.13182590420533)
    ANCHO0 = 3.2
    PASOS = 10
    FACTOR = 10.0 ** 0.5          # x3.162 por salto -> x100 000 en total
    DUR_PASO = 2.1
    # La malla va APAISADA como la ventana (8.0 x 6.4): asi la imagen
    # cubre la banda entera sin bandas negras al relevarse.
    RES = (620, 500)
    SOBRE = 1.5                   # sobremuestreo: al escalar sigue nitida

    # Ventana visible: banda a todo lo ancho, entre el HUD y el pie.
    VENTANA_ARRIBA = 4.55
    VENTANA_ABAJO = -1.85

    def construct(self):
        alto_ventana = self.VENTANA_ARRIBA - self.VENTANA_ABAJO
        y_ventana = (self.VENTANA_ARRIBA + self.VENTANA_ABAJO) / 2.0

        hud_top = hud_pieza("10 . el zoom")
        cortinas = self._cortinas()
        marco = Rectangle(width=FMT.ancho, height=alto_ventana,
                          stroke_width=1.4, stroke_color=C_EJE,
                          fill_opacity=0.0)
        marco.move_to(UP * y_ventana)
        marco.set_z_index(60)

        # z_index por encima de las cortinas (50): si no, el pie de cifra
        # queda tapado por la banda que oculta el desbordamiento.
        etiqueta = hud("aumento", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA).set_z_index(800)
        numero = cifra("1", font_size=96)
        numero.move_to(UP * Y_NUMERO).set_z_index(800)
        sub = hud("el mismo dibujo", font_size=18, color=C_REGLA)
        sub.move_to(UP * Y_SUB).set_z_index(800)

        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)

        actual = self._imagen(self.ANCHO0, alto_ventana)
        actual.move_to(UP * y_ventana)
        self.add(cortinas, marco)
        self.play(FadeIn(actual), Create(marco), run_time=1.4)
        self.play(FadeIn(etiqueta), FadeIn(numero), FadeIn(sub), run_time=0.6)
        self.wait(0.9)

        # =============================================================
        # Diez saltos, cada uno con su imagen nueva esperando debajo
        # =============================================================
        ancho = self.ANCHO0
        aumento = 1.0
        for paso in range(self.PASOS):
            ancho_sig = ancho / self.FACTOR
            aumento *= self.FACTOR
            siguiente = self._imagen(ancho_sig, alto_ventana)
            siguiente.move_to(UP * y_ventana)

            self.play(actual.animate.scale(self.FACTOR),
                      run_time=self.DUR_PASO,
                      rate_func=self._tasa(self.FACTOR))
            self.remove(actual)
            self.add(siguiente)
            actual = siguiente
            ancho = ancho_sig

            num_nuevo = cifra(f"{int(round(aumento))}", font_size=96)
            num_nuevo.move_to(UP * Y_NUMERO).set_z_index(800)
            self.remove(numero)
            self.add(num_nuevo)
            numero = num_nuevo

        self.wait(1.2)
        sub_nuevo = hud("y aparece el mismo", font_size=18, color=C_MEDIDO)
        sub_nuevo.move_to(UP * Y_SUB).set_z_index(800)
        cambiar(self, sub, sub_nuevo)
        sub = sub_nuevo
        self.play(Flash(numero, color=C_MEDIDO, line_length=0.24,
                        num_lines=14, flash_radius=1.0), run_time=0.9)
        self.wait(3.4)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in (hud_top, actual, marco, etiqueta,
                                         numero, sub)], run_time=1.1)
        self.remove(cortinas)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _imagen(self, ancho, alto_ventana):
        """Una clave del zoom, sobremuestreada y con las iteraciones que
        pide la profundidad.

        Las iteraciones tienen que CRECER al bajar o la frontera se
        emborrona (a x100 000 hacen falta miles). Y el sobremuestreo evita
        que la imagen se vea pixelada mientras la anterior crece antes del
        relevo.
        """
        profundidad = math.log10(self.ANCHO0 / ancho)
        iters = int(300 + 900 * profundidad)
        res_x = int(self.RES[0] * self.SOBRE)
        res_y = int(self.RES[1] * self.SOBRE)
        img = fr.imagen_mandelbrot(
            centro=self.CENTRO, ancho=ancho, res=(res_x, res_y),
            max_iter=iters, paleta="fuego", ciclo=24.0,
            interior=C_ATRAPADO, alto_escena=None)
        # Manda el ANCHO, no el alto: la imagen tiene que cubrir la banda de
        # lado a lado desde el primer frame de cada relevo. Lo que sobre por
        # arriba y por abajo lo tapan las cortinas.
        img.width = FMT.ancho + 0.25
        if img.height < alto_ventana:
            img.height = alto_ventana + 0.2
        img.set_z_index(5)
        return img

    def _cortinas(self):
        """Las dos bandas del color del fondo que tapan lo que se desborda.

        La imagen crece x3.16 en cada salto y acaba siendo mucho mayor que
        la pantalla; sin estas cortinas se comeria el HUD de arriba y el pie
        de cifra de abajo. Van por encima de la imagen y por debajo del
        texto.
        """
        g = VGroup()
        for y0, y1 in ((self.VENTANA_ARRIBA, FMT.alto / 2 + 0.6),
                       (-FMT.alto / 2 - 0.6, self.VENTANA_ABAJO)):
            r = Rectangle(width=FMT.ancho + 0.6, height=abs(y1 - y0),
                          stroke_width=0, fill_color=CODE_BG,
                          fill_opacity=1.0)
            r.move_to(UP * (y0 + y1) / 2.0)
            g.add(r)
        g.set_z_index(50)
        return g

    @staticmethod
    def _tasa(factor):
        """rate_func geometrica: velocidad de zoom constante al ojo."""
        lf = math.log(factor)

        def tasa(alpha):
            return float((math.exp(lf * alpha) - 1.0) / (factor - 1.0))
        return tasa
