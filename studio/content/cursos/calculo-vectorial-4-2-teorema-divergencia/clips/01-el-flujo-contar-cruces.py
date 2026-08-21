class Clip1(Scene):
    """4.2.1 - El flujo por una curva cerrada cuenta lo que la cruza: en
    cada trocito solo cuenta F . n, y la suma se mide. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El flujo: contar cruces")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el campo que empuja hacia fuera ---------------------
        pl = plano_leccion()
        campo = campo_flechas(pl, campo_radial, paso=0.9, escala=0.42,
                              x0=-3.6, x1=3.6, y0=-2.25, y1=2.25,
                              magnitud_max=MAG_MAX_RADIAL, opacidad=0.85)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Un campo que empuja hacia fuera desde el "
                              "origen: cuanto más lejos, más fuerte."),
                    zona="abajo", run_time=0.5)
        self.play(LaggedStart(*[FadeIn(f, scale=0.6) for f in campo.flechas],
                              lag_ratio=0.012), run_time=1.8)
        self.wait(3.4)

        # --- momento: la curva cerrada ------------------------------------
        rot.mostrar(pie_curso("Cerramos una curva alrededor y preguntamos: "
                              "¿cuánto la cruza?"), zona="abajo",
                    run_time=0.5)
        curva = camino(pl, CURVA_C1, color=C_REGION, grosor=3.4, n=220)
        self.play(Create(curva.trazo), run_time=1.3)
        self.wait(3.6)

        # --- momento: contar cruces ---------------------------------------
        rot.mostrar(pie_curso("Soltamos trazadores dentro: el campo los "
                              "lleva y todos salen por el borde."),
                    zona="abajo", run_time=0.5)
        puntos = VGroup(*[Dot(pl.p(np.array(s)), radius=0.075, color=C_VEC)
                          for s in SEMILLAS_C1])
        self.play(FadeIn(puntos, scale=0.5), run_time=0.5)
        self.play(*[d.animate.move_to(pl.p(np.array(s) * AVANCE_C1))
                    for d, s in zip(puntos, SEMILLAS_C1)],
                  run_time=2.2, rate_func=linear)
        self.wait(2.8)

        # --- momento: solo cuenta lo que sale por la normal ---------------
        rot.mostrar(pie_curso("En cada trocito solo cuenta la parte que "
                              "sale: la componente sobre la normal."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(puntos), run_time=0.4)
        normales = normales_borde(pl, CURVA_C1, n=N_NORMALES, largo=0.55,
                                  color=C_GRAD)
        self.play(LaggedStart(*[GrowArrow(n) for n in normales],
                              lag_ratio=0.07), run_time=1.8)
        panel = panel_derecha(MathTex(r"\oint F\cdot \hat n\, ds",
                                      font_size=34, color=C_CALCULO))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.2)

        # --- momento: las lecturas de F . n --------------------------------
        rot.mostrar(pie_curso("Aquí el campo sale de frente en todo el "
                              "borde: esa componente vale lo mismo en "
                              "cada punto."), zona="abajo", run_time=0.5)
        self.play(campo.animate.set_opacity(0.28), run_time=0.5)
        lecturas = VGroup()
        for t, v in zip(T_LECTURAS, FN_LECTURAS):
            q = np.asarray(CURVA_C1(t), float)
            n = normal_exterior(CURVA_C1, t)
            et = _con_fondo(tag_hud(f"F.n = {fmt(v, 2)}", font_size=18,
                                    color=C_CALCULO), buff=0.09,
                            opacidad=0.88)
            et.move_to(pl.p(q + n * 1.12))
            lecturas.add(et)
        self.play(LaggedStart(*[FadeIn(e, scale=0.6) for e in lecturas],
                              lag_ratio=0.35), run_time=1.5)
        self.wait(3.2)

        # --- momento: el flujo medido --------------------------------------
        rot.mostrar(pie_curso("Sumado a lo largo de toda la curva, eso es "
                              "el FLUJO: una sola cifra."), zona="abajo",
                    run_time=0.5)
        cuenta = tag_hud(f"{fmt(FN_LECTURAS[0], 2)} x {fmt(PERIMETRO_C1, 2)}"
                         f" = {fmt(FLUJO_C1, 2)}", font_size=20,
                         color=C_RES)
        total = tag_hud(f"flujo = {fmt(FLUJO_C1, 2)}", font_size=22,
                        color=C_RES)
        panel2 = panel_derecha(MathTex(r"\oint F\cdot \hat n\, ds",
                                       font_size=34, color=C_CALCULO),
                               cuenta, total, buff=0.24)
        self.play(FadeOut(panel), run_time=0.3)
        self.play(FadeIn(panel2, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.4)
