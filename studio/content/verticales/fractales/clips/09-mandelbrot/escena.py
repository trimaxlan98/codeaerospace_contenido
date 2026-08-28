class Clip(Scene):
    """09 · Mandelbrot — el mapa de todos los Julia.

    Cada c del plano tiene su propio Julia. Se cuelgan 42 de ellos en una
    rejilla, cada uno EN EL SITIO de su c, y se hace una sola pregunta:
    ¿esa figura es una pieza entera o es polvo? Las de una pieza se quedan
    encendidas y las demas se apagan.

    Lo que queda dibujado es el conjunto de Mandelbrot. No es una metafora:
    el criterio de encendido es exactamente `en_mandelbrot`, es decir, que
    la orbita de cero no escape — y ese es el teorema (Fatou-Julia) que dice
    que el Julia de c es conexo si y solo si c esta en M. Al final el mosaico
    funde a la imagen de M calculada en el MISMO encuadre.
    """

    COLS = 7
    FILAS = 6
    REAL = (-2.1, 0.7)
    IMAG = (-1.2, 1.2)
    CELDA = 0.86          # unidades de escena por celda
    LADO_MINI = 108

    def construct(self):
        paso_r = (self.REAL[1] - self.REAL[0]) / self.COLS
        paso_i = (self.IMAG[1] - self.IMAG[0]) / self.FILAS
        k = self.CELDA / paso_r
        cr = (self.REAL[0] + self.REAL[1]) / 2.0

        def a_pantalla(c):
            return np.array([(c.real - cr) * k, c.imag * k + Y_ESCENA, 0.0])

        # los 42 valores de c: el centro de cada celda
        ces = []
        for f in range(self.FILAS):
            for col in range(self.COLS):
                cr_i = self.REAL[0] + paso_r * (col + 0.5)
                ci_i = self.IMAG[0] + paso_i * (f + 0.5)
                ces.append(complex(cr_i, ci_i))
        dentro = [fr.en_mandelbrot(c, 400) for c in ces]
        n_dentro = sum(dentro)

        hud_top = hud_pieza("09 . mandelbrot")
        etiqueta = hud("julias", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA)
        numero = cifra(f"{len(ces)}", font_size=104)
        numero.move_to(UP * Y_NUMERO)
        sub = hud("uno por cada c", font_size=18, color=C_REGLA)
        sub.move_to(UP * Y_SUB)

        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)

        # =============================================================
        # 1. Cuarenta y dos Julia, cada uno en el sitio de su c
        # =============================================================
        minis = []
        for c, esta in zip(ces, dentro):
            img = fr.miniatura_julia(c, lado=self.LADO_MINI, ancho=3.2,
                                     max_iter=110, paleta="fuego",
                                     ciclo=20.0, interior=C_ATRAPADO,
                                     alto_escena=self.CELDA * 0.97)
            img.move_to(a_pantalla(c))
            img.set_z_index(10)
            minis.append(img)
        mosaico = Group(*minis)

        self.play(LaggedStart(*[FadeIn(m, scale=0.7) for m in minis],
                              lag_ratio=0.030), run_time=3.8)
        self.play(FadeIn(etiqueta), FadeIn(numero), FadeIn(sub), run_time=0.6)
        self.wait(3.0)

        # =============================================================
        # 2. La pregunta: ¿una pieza, o polvo?
        # =============================================================
        et_nuevo = hud("de una pieza", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{n_dentro}", font_size=104, color=C_ATRAPADO)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("los demas son polvo", font_size=18,
                        color=C_ATRAPADO)
        sub_nuevo.move_to(UP * Y_SUB)

        bordes = VGroup()
        for c, esta, img in zip(ces, dentro, minis):
            if not esta:
                continue
            b = Rectangle(width=self.CELDA, height=self.CELDA,
                          stroke_width=2.4, stroke_color=C_ATRAPADO,
                          fill_opacity=0.0)
            b.move_to(a_pantalla(c))
            b.set_z_index(30)
            bordes.add(b)
        self.play(LaggedStart(*[Create(b) for b in bordes], lag_ratio=0.10),
                  run_time=2.6)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.wait(3.0)

        # los que son polvo se apagan y queda la SILUETA
        apagar = [m for m, esta in zip(minis, dentro) if not esta]
        self.play(*[m.animate.set_opacity(0.06) for m in apagar],
                  run_time=2.0)
        self.wait(3.4)

        # =============================================================
        # 3. El mismo encuadre, con todos los c: el conjunto
        # =============================================================
        ancho_plano = self.REAL[1] - self.REAL[0]
        alto_plano = self.IMAG[1] - self.IMAG[0]
        res_x = 720
        res_y = int(round(res_x * alto_plano / ancho_plano))
        mandel = fr.imagen_mandelbrot(
            centro=complex(cr, 0.0), ancho=ancho_plano, res=(res_x, res_y),
            max_iter=420, paleta="fuego", ciclo=24.0, interior=C_ATRAPADO,
            alto_escena=alto_plano * k)
        mandel.move_to(UP * Y_ESCENA)
        mandel.set_z_index(5)

        # El cierre no puede dejar el renglon de la cifra vacio: la cuenta
        # que toca aqui es LA del clip — cada pixel del cuadro es un c, o
        # sea, un Julia entero. Se cuenta sobre la imagen que se ve.
        julias_en_cuadro = res_x * res_y
        et_nuevo = hud("julias", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{julias_en_cuadro}", font_size=96)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("uno por pixel", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        self.play(FadeOut(mosaico), FadeOut(bordes), FadeIn(mandel),
                  run_time=2.2)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.wait(6.2)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in (hud_top, mandel, etiqueta, numero,
                                         sub)], run_time=1.1)
        self.wait(0.5)
