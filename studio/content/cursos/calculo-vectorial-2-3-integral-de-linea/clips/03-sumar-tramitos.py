class Clip3(Scene):
    """2.3.3 - Trocear el camino en pasos dr, sumar lo que cobra cada uno y
    afinar los pasos: la suma se vuelve la integral de linea, medida por el
    contador hasta 7.22. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Sumar tramitos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el camino entero, no un tramito ---------------------
        pl = plano_leccion()
        campo = campo_leccion(pl, ancho=4.05, opacidad=0.55)
        guia = camino(pl, R_CAM, grosor=2.2, flechas=3, opacidad=0.4)
        self.play(FadeIn(pl), FadeIn(campo), run_time=0.9)
        rot.mostrar(pie_curso("Un tramito solo no dice nada: hay que "
                              "sumarlos TODOS, de A a B."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(guia), run_time=0.7)
        self.wait(3.9)

        # --- momento: trocear el camino en pasos --------------------------
        rot.mostrar(pie_curso("Troceamos el camino en pasos dr, uno detrás "
                              "de otro."), zona="abajo", run_time=0.5)
        pasos = VGroup(*[
            flecha_libre(pl, R_CAM(k / N_TRAMOS), R_CAM((k + 1) / N_TRAMOS),
                         color=C_CIFRA, grosor=3.4, punta_len=0.13)
            for k in range(N_TRAMOS)])
        self.play(LaggedStart(*[GrowArrow(f) for f in pasos],
                              lag_ratio=0.25), run_time=2.2)
        self.wait(2.8)

        # --- momento: pasos mas finos -------------------------------------
        rot.mostrar(pie_curso("Cuanto más finos son los pasos, mejor "
                              "pegados van al camino."), zona="abajo",
                    run_time=0.5)
        finos = VGroup(*[
            flecha_libre(pl, R_CAM(k / (2 * N_TRAMOS)),
                         R_CAM((k + 1) / (2 * N_TRAMOS)),
                         color=C_CIFRA, grosor=2.8, punta_len=0.10)
            for k in range(2 * N_TRAMOS)])
        self.play(FadeOut(pasos), FadeIn(finos), run_time=1.0)
        self.wait(3.6)

        # --- momento: el contador acumula ---------------------------------
        rot.mostrar(pie_curso("Sumemos lo que cobra cada paso, de A a B, "
                              "sin perder cuenta."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(finos), run_time=0.5)
        marcador, num, etiq = contador("trabajo acumulado", 0.0)
        tt = ValueTracker(0.0)
        num.add_updater(lambda m: m.set_value(trabajo_hasta(tt.get_value())))
        num.add_updater(lambda m: m.next_to(etiq, DOWN, buff=0.16))
        movil = Dot(pl.p(R_CAM(0.0)), radius=0.095, color=C_VEC)
        movil.add_updater(lambda d: d.move_to(pl.p(R_CAM(tt.get_value()))))
        vivo = camino(pl, R_CAM, grosor=3.8)
        self.play(FadeIn(marcador), FadeIn(movil, scale=0.5), run_time=0.6)
        self.play(Create(vivo.trazo), tt.animate.set_value(1.0),
                  run_time=5.6, rate_func=linear)
        self.play(FadeIn(vivo.marcas), run_time=0.4)
        self.wait(1.8)

        # --- momento: el contador se para ---------------------------------
        num.clear_updaters()
        movil.clear_updaters()
        rot.mostrar(pie_curso("El contador se para: eso es lo que el "
                              "viento ha trabajado por nosotros."),
                    zona="abajo", run_time=0.5)
        num.set_value(W_TOTAL)
        num.next_to(etiq, DOWN, buff=0.16)
        self.play(Indicate(num, color=C_RES, scale_factor=1.15),
                  run_time=0.9)
        self.wait(3.8)

        # --- momento: la suma es una integral -----------------------------
        rot.mostrar(formula_pie(r"\int_C \vec F \cdot d\vec r = "
                                + fmt(W_TOTAL, 2)),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
