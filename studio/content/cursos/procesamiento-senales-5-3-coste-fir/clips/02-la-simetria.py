class Clip2(Scene):
    """5.3.2 - h[k] = h[N-k]: cada pareja simetrica multiplica al MISMO
    coeficiente, asi que 41 taps piden solo 21 multiplicaciones. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("La simetria"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        sec = Secuencia(H, 0, ancho=9.6, alto=2.1, color=C_MUESTRA,
                        radio=0.045, eje_y=False)
        sec.move_to(UP * 1.25)
        et_h = tag_hud("h[k]", font_size=18, color=C_MUESTRA)
        et_h.next_to(sec, LEFT, buff=0.26)
        self.play(FadeIn(sec.ejes), FadeIn(et_h), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in range(N_TAPS)],
                              lag_ratio=0.015),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in range(N_TAPS)],
                              lag_ratio=0.015), run_time=2.2)
        rot.mostrar(cifra_pie(f"{N_TAPS} coeficientes"), zona="abajo",
                    run_time=0.5)
        self.wait(1.8)

        # --- primero, UNA pareja marcada a mano ------------------------
        i0, j0 = 0, N_TAPS - 1
        marca_i = sec.marcar(i0, color=C_CALCULO)
        marca_j = sec.marcar(j0, color=C_CALCULO)
        self.play(FadeIn(marca_i, scale=1.4), FadeIn(marca_j, scale=1.4),
                  run_time=0.5)
        et_par = tag_hud("h[0] = h[40]", font_size=19, color=C_CALCULO)
        et_par.next_to(sec, UP, buff=0.32)
        self.play(FadeIn(et_par), run_time=0.5)
        self.wait(2.4)
        self.play(FadeOut(et_par), FadeOut(marca_i), FadeOut(marca_j),
                  run_time=0.5)

        # --- todas las parejas, unidas por debajo -----------------------
        y_base = sec.en(0, sec.y0)[1] - 0.55
        n_pares = N_TAPS // 2
        arcos = VGroup()
        for i in range(n_pares):
            j = N_TAPS - 1 - i
            p1 = np.array([sec.en(i, 0.0)[0], y_base, 0.0])
            p2 = np.array([sec.en(j, 0.0)[0], y_base, 0.0])
            arco = ArcBetweenPoints(p1, p2, angle=-0.9, color=C_CALCULO,
                                    stroke_width=1.4)
            if arco.get_center()[1] > y_base + 1e-6:
                arco = ArcBetweenPoints(p1, p2, angle=0.9, color=C_CALCULO,
                                        stroke_width=1.4)
            arcos.add(arco)
        self.play(LaggedStart(*[Create(a) for a in arcos], lag_ratio=0.04),
                  run_time=3.0)
        self.wait(2.4)

        panel = panel_cifras((f"{N_TAPS} coeficientes", C_MUESTRA),
                             (f"{MACS} multiplicaciones", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.0)
        rot.mostrar(cifra_pie(f"{MACS} de {N_TAPS}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.8)

        rot.mostrar(formula_pie(
            r"y[n] = \sum_k h[k]\,(x[n-k] + x[n-N+k])"), zona="abajo",
            run_time=0.5)
        self.wait(7.0)
