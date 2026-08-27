class Clip4(Scene):
    """2.1.4 - La entrada se descompone en impulsos pesados; cada uno
    arrastra su copia de h; al sumarlas aparece la salida. Cierre de la
    leccion. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Suma de impulsos"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        secx = Secuencia(X_DESCOMP, 0, ancho=7.4, alto=0.9, color=C_SENAL)
        secx.move_to(UP * 2.55)
        et_x = tag_junto(secx, "entrada", LEFT, buff=0.20, font_size=18,
                         color=C_SENAL)
        self.play(FadeIn(secx), FadeIn(et_x), run_time=1.0)
        self.wait(1.6)

        my = float(np.max(np.abs(Y_DESCOMP))) * 1.25
        base = Secuencia(np.zeros(len(Y_DESCOMP)), 0, (-my, my), 7.4, 0.36,
                         C_MUESTRA)
        n_h = len(H_LTI)
        n_y = len(Y_DESCOMP)
        y_rows = [1.55, 0.97, 0.39, -0.19, -0.77]
        filas = []
        marcas_x = []
        for k in range(len(X_DESCOMP)):
            contrib = np.zeros(n_y)
            contrib[k:k + n_h] = X_DESCOMP[k] * H_LTI
            fila = base.con_valores(contrib, color=C_MUESTRA)
            fila.move_to(np.array([0.0, y_rows[k], 0.0]))
            filas.append(fila)
            m = secx.marcar(k, color=C_MUESTRA)
            marcas_x.append(m)
            self.play(Create(m), FadeIn(fila), run_time=0.85)
        et_h = tag_junto(filas[2], "copias de h", RIGHT, buff=0.30,
                         font_size=19, color=C_MUESTRA)
        self.play(FadeIn(et_h), run_time=0.5)
        self.wait(2.2)

        fila_y = base.con_valores(Y_DESCOMP, color=C_SALIDA)
        fila_y.move_to(DOWN * 2.15)
        et_y = tag_junto(fila_y, "salida", LEFT, buff=0.20, font_size=18,
                         color=C_SALIDA)

        self.play(*[filas[k].animate.move_to(fila_y.get_center())
                    .set_opacity(0.0) for k in range(len(filas))],
                  FadeOut(et_h), run_time=1.4)
        self.remove(*filas)
        self.play(FadeIn(fila_y.ejes), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(fila_y.tallo(i)) for i in
                                range(n_y)], lag_ratio=0.07),
                  LaggedStart(*[FadeIn(fila_y.punto(i)) for i in
                                range(n_y)], lag_ratio=0.07),
                  FadeIn(et_y), run_time=1.8)
        self.wait(2.6)

        rot.mostrar(formula_pie(r"y[n] = \sum_k x[k]\,h[n-k]"),
                    zona="abajo", run_time=0.5)
        self.wait(3.8)

        cierre_leccion(self, rot,
                       "Un sistema LTI no guarda secretos.",
                       "Se confiesa con un impulso.",
                       secx, et_x, *marcas_x, fila_y, et_y)
