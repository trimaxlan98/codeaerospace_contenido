class Clip1(Scene):
    """Intro de marca «Encendido» (~10 s, sin narracion).

    Consola de vuelo que despierta: un escaneo ambar barre la pantalla y
    enciende la reticula HUD, se dibujan las escuadras mientras CO.DE se
    ensambla en el centro, el punto ambar llega al final como cursor,
    ACADEMY y la etiqueta HUD cierran el bloque y todo funde a fondo
    limpio. Arranca y termina en negro puro para empalmar en post.
    """

    def construct(self):
        X0 = -config.frame_width / 2
        X1 = config.frame_width / 2
        Y1 = config.frame_height / 2
        OP_RET = 0.11          # reticula encendida
        OP_RET_MIN = 0.05      # reticula "en reposo" tras el ensamblado

        # --- piezas -------------------------------------------------
        ret = reticula(paso=0.9, opacidad=OP_RET)
        verticales = []
        horizontales = []
        for linea in ret:
            a, b = linea.get_start(), linea.get_end()
            if abs(a[0] - b[0]) < 1e-6:
                verticales.append((linea, a[0]))
            else:
                horizontales.append((linea, a[1]))
        ret.set_stroke(opacity=0.0)

        esquinas = esquinas_hud(opacidad=0.28)

        wm, co, punto, de = wordmark(96)
        aca = academy(30)
        aca.next_to(wm, DOWN, buff=0.35)
        bloque = VGroup(wm, aca)
        bloque.move_to(ORIGIN)

        tag = tag_hud("CIENCIA / INGENIERIA / ESPACIO", font_size=17)
        tag.to_edge(UP, buff=0.85)

        # --- 1. escaneo (fondo limpio -> reticula encendida) --------
        self.wait(0.6)

        xt = ValueTracker(X0 - 0.45)

        def encender(_grupo):
            x = xt.get_value()
            for linea, lx in verticales:
                linea.set_stroke(opacity=OP_RET if lx <= x else 0.0)
            xf = min(x, X1)
            for linea, ly in horizontales:
                if xf <= X0 + 0.06:
                    linea.set_stroke(opacity=0.0)
                else:
                    linea.put_start_and_end_on(np.array([X0, ly, 0.0]),
                                               np.array([xf, ly, 0.0]))
                    linea.set_stroke(opacity=OP_RET)

        ret.add_updater(encender)
        self.add(ret)

        barra = Line([X0 - 0.45, -Y1, 0], [X0 - 0.45, Y1, 0],
                     stroke_width=2.6, color=C_ACENTO)
        barra.set_stroke(opacity=0.85)
        barra.add_updater(lambda m: m.move_to([xt.get_value(), 0, 0]))
        self.add(barra)

        self.play(xt.animate.set_value(X1 + 0.7), run_time=1.5,
                  rate_func=rate_functions.ease_in_out_sine)

        # el escaneo sale de pantalla y se retira; la reticula queda fija
        barra.clear_updaters()
        self.remove(barra)
        ret.clear_updaters()
        for linea, ly in horizontales:
            linea.put_start_and_end_on(np.array([X0, ly, 0.0]),
                                       np.array([X1, ly, 0.0]))
        ret.set_stroke(color=C_EJE, opacity=OP_RET)

        # --- 2. ensamblado del wordmark ----------------------------
        self.play(
            Create(esquinas, lag_ratio=0.25),
            FadeIn(co, shift=RIGHT * 0.7),
            FadeIn(de, shift=LEFT * 0.7),
            run_time=1.4,
            rate_func=smooth,
        )
        self.play(FadeIn(punto, shift=DOWN * 0.45), run_time=0.5,
                  rate_func=rate_functions.ease_out_cubic)

        # el punto parpadea como cursor (dos veces, cadencia ~0.35 s)
        for _ in range(2):
            punto.set_fill(opacity=0.0)
            self.wait(0.18)
            punto.set_fill(opacity=1.0)
            self.wait(0.17)
        self.wait(0.3)

        # --- 3. ACADEMY + etiqueta HUD -----------------------------
        self.play(
            LaggedStart(*[FadeIn(letra, shift=UP * 0.14) for letra in aca],
                        lag_ratio=0.09),
            run_time=1.1,
        )
        self.play(
            FadeIn(tag, shift=DOWN * 0.16),
            ret.animate.set_stroke(opacity=OP_RET_MIN),
            run_time=0.9,
        )

        # --- 4. respiro, pulso del punto y fundido -----------------
        self.wait(0.45)
        self.play(punto.animate.scale(1.2).set_color("#ffd48a"),
                  run_time=0.7, rate_func=there_and_back)
        self.wait(0.9)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1.0)
        self.remove(*self.mobjects)
        self.wait(0.6)
