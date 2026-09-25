class Clip1(Scene):
    """3.1.1 - El acumulador de fase de un NCO (S.nco): la aguja avanza
    2*pi*f/fs por muestra y se pliega modulo 2*pi (da varias vueltas al
    circulo); cada muestra deja una fila I/Q (I azul = parte real, Q
    violeta = parte imaginaria) en la tabla que sale del acumulador.
    (~29 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El oscilador numerico"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        n_ext = 26
        n_tabla = 8
        z = S.nco(F_NCO, FS_NCO, n_ext)

        # --- el acumulador de fase: la aguja -------------------------------
        centro = LEFT * 3.3 + UP * 0.3
        radio = 2.1
        circ = Circle(radius=radio, color=C_EJE, stroke_width=1.6)
        circ.move_to(centro)
        nombre = tag_junto(circ, "acumulador de fase", DOWN, buff=0.3,
                           font_size=22, color=C_LO)
        self.play(Create(circ), FadeIn(nombre), run_time=0.8)
        self.wait(0.3)

        def punto_de(k):
            return centro + radio * np.array([z[k].real, z[k].imag, 0.0])

        aguja = Line(centro, punto_de(0), color=C_LO, stroke_width=3.4)
        punta = Dot(aguja.get_end(), radius=0.09, color=C_LO)
        self.play(FadeIn(aguja), FadeIn(punta), run_time=0.6)
        self.wait(0.4)

        # --- la tabla, fila a fila: sale del acumulador --------------------
        col_x = [2.6, 3.7, 4.8]
        fila_h = 0.58
        y0 = 1.8

        def fila_y(k):
            return y0 - k * fila_h

        header = VGroup(
            Text("n", font=FUENTE_HUD, font_size=20, color=C_TENUE),
            Text("I", font=FUENTE_HUD, font_size=20, color=C_I),
            Text("Q", font=FUENTE_HUD, font_size=20, color=C_Q),
        )
        for cel, x in zip(header, col_x):
            cel.move_to(RIGHT * x + UP * 2.5)
        linea = Line(RIGHT * (col_x[0] - 0.4) + UP * 2.2,
                    RIGHT * (col_x[-1] + 0.5) + UP * 2.2, color=C_EJE,
                    stroke_width=1.4)
        self.play(FadeIn(header), Create(linea), run_time=0.6)
        self.wait(0.3)

        def fila_de(k):
            celda_n = Text(str(k), font=FUENTE_HUD, font_size=20,
                          color=C_TENUE)
            celda_i = Text(fmt(z[k].real, 2), font=FUENTE_HUD, font_size=20,
                          color=C_I)
            celda_q = Text(fmt(z[k].imag, 2), font=FUENTE_HUD, font_size=20,
                          color=C_Q)
            for cel, x in zip((celda_n, celda_i, celda_q), col_x):
                cel.move_to(RIGHT * x + UP * fila_y(k))
            return VGroup(celda_n, celda_i, celda_q)

        fila0 = fila_de(0)
        punto0 = Dot(punto_de(0), radius=0.06, color=C_LO)
        self.play(FadeIn(fila0, shift=RIGHT * 0.1), FadeIn(punto0),
                  run_time=0.6)
        self.wait(0.3)

        for k in range(1, n_tabla):
            nuevo = Line(centro, punto_de(k), color=C_LO, stroke_width=3.4)
            punto = Dot(punto_de(k), radius=0.06, color=C_LO)
            fila = fila_de(k)
            self.play(Transform(aguja, nuevo), run_time=0.6)
            self.play(FadeIn(punto), FadeIn(fila, shift=RIGHT * 0.1),
                      run_time=0.6)
            self.wait(0.4)

        self.wait(0.6)

        # --- la aguja sigue: se pliega modulo 2*pi --------------------------
        for k in range(n_tabla, n_ext):
            nuevo = Line(centro, punto_de(k), color=C_LO, stroke_width=3.0)
            punto = Dot(punto_de(k), radius=0.035, color=C_LO)
            punto.set_opacity(0.55)
            self.play(Transform(aguja, nuevo), FadeIn(punto), run_time=0.22)
        self.wait(1.0)

        rot.mostrar(formula_pie(r"e^{-j 2\pi f n / f_s}"), zona="abajo",
                    run_time=0.5)
        self.wait(6.0)
