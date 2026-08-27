class Clip(Scene):
    """00 · Intro — la identidad CO.DE Academy, recompuesta para 9:16.

    Misma coreografia que la intro horizontal de la marca (una consola que
    despierta: escaneo, reticula, ensamblado del wordmark, el punto ambar
    como cursor) pero recolocada en columna, y con una diferencia: aqui la
    intro NO es generica, presenta el curso. Despues del wordmark entra el
    titulo.

    Arranca y termina en fondo limpio para empalmar en el montaje sin
    corte visible.
    """

    marca_chica = False       # el wordmark grande ES la marca
    esquinas = False

    OP_RETICULA = 0.11
    OP_REPOSO = 0.05

    def construct(self):
        X0, X1 = -FMT.ancho / 2, FMT.ancho / 2
        Y1 = FMT.alto / 2

        ret = reticula(paso=0.9, opacidad=self.OP_RETICULA)
        verticales, horizontales = [], []
        for linea in ret:
            a, b = linea.get_start(), linea.get_end()
            (verticales if abs(a[0] - b[0]) < 1e-6
             else horizontales).append((linea, a[0] if abs(a[0] - b[0]) < 1e-6
                                        else a[1]))
        ret.set_stroke(opacity=0.0)

        esq = esquinas_hud(opacidad=0.26)
        wm, co, punto, de = wordmark(84)
        aca = academy(27)
        aca.next_to(wm, DOWN, buff=0.32)
        bloque = VGroup(wm, aca)
        bloque.move_to(UP * 1.9)

        tag = hud("ciencia . espacio", font_size=15)
        tag.move_to(UP * (FMT.tope - 0.5))

        titulo_curso = titulo("FRACTALES", font_size=58)
        titulo_curso.move_to(DOWN * 1.35)
        bajada = Text("la forma del infinito", weight="MEDIUM",
                      font_size=27, color=CODE_MUTED)
        bajada.next_to(titulo_curso, DOWN, buff=0.30)
        raya = subrayado_marca(titulo_curso, margen=0.16, grosor=3.0)

        # --- 1. el escaneo enciende la reticula ---------------------
        self.wait(0.5)
        xt = ValueTracker(X0 - 0.45)

        def encender(_grupo):
            x = xt.get_value()
            for linea, lx in verticales:
                linea.set_stroke(opacity=self.OP_RETICULA if lx <= x else 0.0)
            xf = min(x, X1)
            for linea, ly in horizontales:
                if xf <= X0 + 0.06:
                    linea.set_stroke(opacity=0.0)
                else:
                    linea.put_start_and_end_on(np.array([X0, ly, 0.0]),
                                               np.array([xf, ly, 0.0]))
                    linea.set_stroke(opacity=self.OP_RETICULA)

        ret.add_updater(encender)
        self.add(ret)
        barra = Line([X0 - 0.45, -Y1, 0], [X0 - 0.45, Y1, 0],
                     stroke_width=2.6, color=C_REGLA)
        barra.set_stroke(opacity=0.85)
        barra.add_updater(lambda m: m.move_to([xt.get_value(), 0, 0]))
        self.add(barra)
        self.play(xt.animate.set_value(X1 + 0.7), run_time=1.4,
                  rate_func=rate_functions.ease_in_out_sine)

        barra.clear_updaters()
        self.remove(barra)
        ret.clear_updaters()
        for linea, ly in horizontales:
            linea.put_start_and_end_on(np.array([X0, ly, 0.0]),
                                       np.array([X1, ly, 0.0]))
        ret.set_stroke(color=C_EJE, opacity=self.OP_RETICULA)

        # --- 2. el wordmark se ensambla -----------------------------
        self.play(Create(esq, lag_ratio=0.25),
                  FadeIn(co, shift=RIGHT * 0.7),
                  FadeIn(de, shift=LEFT * 0.7),
                  run_time=1.3, rate_func=smooth)
        self.play(FadeIn(punto, shift=DOWN * 0.45), run_time=0.5,
                  rate_func=rate_functions.ease_out_cubic)
        for _ in range(2):
            punto.set_fill(opacity=0.0)
            self.wait(0.17)
            punto.set_fill(opacity=1.0)
            self.wait(0.16)
        self.wait(0.25)

        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.14) for l in aca],
                              lag_ratio=0.09), run_time=1.0)
        self.play(FadeIn(tag, shift=DOWN * 0.16),
                  ret.animate.set_stroke(opacity=self.OP_REPOSO),
                  run_time=0.8)
        self.wait(0.4)

        # --- 3. y el titulo del curso -------------------------------
        self.play(FadeIn(titulo_curso, shift=UP * 0.22), run_time=0.9)
        self.play(Create(raya), FadeIn(bajada, shift=UP * 0.14),
                  run_time=0.9)
        self.play(punto.animate.scale(1.2).set_color("#ffd48a"),
                  run_time=0.7, rate_func=there_and_back)
        self.wait(1.6)

        # --- 4. fundido a fondo limpio ------------------------------
        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
        self.remove(*self.mobjects)
        self.wait(0.6)
