class Clip2(Scene):
    """4.1.2 - Sumar las nueve baldosas: los tramos interiores se borran de
    dos en dos y solo sobrevive el contorno. El teorema de Green. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Solo queda el borde")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mosaico entero -----------------------------------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Sumemos ahora las circulaciones de las nueve "
                              "baldosas."), zona="abajo", run_time=0.5)
        # opacidad baja de fabrica: el campo es contexto y manda el
        # mosaico. (Ojo: fade() ANTES de FadeIn no sirve, FadeIn devuelve
        # el mobject a su opacidad plena.)
        campo = campo_flechas(pl, F_GREEN, paso=1.0, escala=0.55,
                              x0=-2.5, x1=2.5, y0=-1.5, y1=1.5,
                              opacidad=0.34)
        mos = mosaico_circulaciones(pl, X0, X1, Y0, Y1, nx=NX, ny=NY,
                                    margen=MARGEN_BALDOSA)
        self.play(FadeIn(campo), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(b, scale=0.7) for b in mos],
                              lag_ratio=0.12), run_time=1.8)
        self.wait(2.8)

        # --- momento: los tramos interiores -------------------------------
        rot.mostrar(pie_curso("Cada tramo INTERIOR pertenece a dos "
                              "baldosas, y cada una lo recorre al revés."),
                    zona="abajo", run_time=0.5)
        interiores = VGroup()
        for k in (1, 2):
            x = X0 + k * DX_B
            y = Y0 + k * DY_B
            interiores.add(Line(pl.p(x, Y0), pl.p(x, Y1), color=C_REGION,
                                stroke_width=5.0))
            interiores.add(Line(pl.p(X0, y), pl.p(X1, y), color=C_REGION,
                                stroke_width=5.0))
        self.play(LaggedStart(*[Create(l) for l in interiores],
                              lag_ratio=0.2), run_time=1.2)
        self.wait(3.4)

        # --- momento: el interior se borra --------------------------------
        rot.mostrar(pie_curso("Se cancelan de dos en dos. El interior "
                              "entero se borra."), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(interiores, color=C_RES, scale_factor=1.02),
                  run_time=0.9)
        self.play(FadeOut(interiores, scale=0.9), run_time=0.8)
        self.wait(3.2)

        # --- momento: sobrevive el borde ----------------------------------
        rot.mostrar(pie_curso("Solo sobrevive el contorno de la región, "
                              "recorrido antihorario."), zona="abajo",
                    run_time=0.5)
        reg = region_rect(pl, X0, X1, Y0, Y1, flechas=6)
        self.play(FadeOut(mos), FadeIn(reg), run_time=1.2)

        t = ValueTracker(1e-3)
        andar = always_redraw(lambda: Dot(pl.p(reg.curva(t.get_value())),
                                          radius=0.10, color=C_VEC))
        traza = always_redraw(lambda: VMobject(
            stroke_color=C_VEC, stroke_width=5.0).set_points_as_corners(
                [pl.p(reg.curva(u))
                 for u in np.linspace(0.0, t.get_value(), 90)]))
        self.add(traza, andar)
        self.play(t.animate.set_value(1.0), run_time=4.5, rate_func=linear)
        self.wait(1.6)

        # --- momento: el teorema ------------------------------------------
        rot.mostrar(pie_curso("El borde cuenta lo que pasa dentro: esa es "
                              "la promesa de Green."), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)
        traza.clear_updaters()
        andar.clear_updaters()
        # El campo se retira: la banda del pie es de la formula, y la fila
        # de flechas de abajo caeria justo debajo de los simbolos altos.
        self.play(FadeOut(campo), run_time=0.6)
        rot.mostrar(formula_pie(r"\oint_{\partial R} \mathbf{F}\cdot d\mathbf{r}"
                                r" \;=\; \iint_R (\nabla\times\mathbf{F})\, dA",
                                font_size=38), zona="abajo", run_time=0.5)
        self.wait(5.2)
