class Clip2(Scene):
    """7.2.2 - El mismo filtro con a = -0.9: ya no se queda clavado,
    ALTERNA de signo para siempre. Una oscilacion sin entrada, fabricada
    por el redondeo. (~32 s)"""

    N_DIB = 40           # muestras de los dos carriles anchos
    N_COLA = (100, 140)  # tramo de la cola medida, ampliado

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("El ciclo que no acaba"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        n = self.N_DIB
        y_pos = Y_POS[BITS_DEMO][0]
        y_neg = Y_NEG[BITS_DEMO][0]

        # --- a = +0.9: se queda clavado (lo de antes) --------------------
        arr = Secuencia(y_pos[:n], 0, (-0.5, 0.5), ancho=8.8, alto=1.85,
                        color=C_SALIDA, radio=0.038)
        arr.move_to(LEFT * 0.7 + UP * 1.25)
        et_arr = tag_hud(f"a = +{fmt(A_POS, 1)}", font_size=18,
                         color=C_SALIDA)
        et_arr.next_to(arr, LEFT, buff=0.22)
        self.play(FadeIn(arr.ejes), FadeIn(et_arr), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(arr.tallo(i)) for i in range(n)],
                              lag_ratio=0.03),
                  LaggedStart(*[FadeIn(arr.punto(i)) for i in range(n)],
                              lag_ratio=0.03), run_time=1.7)
        rot.mostrar(cifra_pie(f"a = +{fmt(A_POS, 1)}: periodo "
                              f"{PERIODO_POS[BITS_DEMO]}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        # --- a = -0.9: alterna de signo ----------------------------------
        aba = Secuencia(y_neg[:n], 0, (-0.5, 0.5), ancho=8.8, alto=1.85,
                        color=C_RUIDO, radio=0.038)
        aba.move_to(LEFT * 0.7 + DOWN * 1.05)
        et_aba = tag_hud(f"a = {fmt(A_NEG, 1)}", font_size=18, color=C_RUIDO)
        et_aba.next_to(aba, LEFT, buff=0.22)
        self.play(FadeIn(aba.ejes), FadeIn(et_aba), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(aba.tallo(i)) for i in range(n)],
                              lag_ratio=0.03),
                  LaggedStart(*[FadeIn(aba.punto(i)) for i in range(n)],
                              lag_ratio=0.03), run_time=1.7)
        rot.mostrar(cifra_pie(f"a = {fmt(A_NEG, 1)}: periodo "
                              f"{PERIODO_NEG[BITS_DEMO]}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        v_arr = arr.ventana(24, n - 1, color=C_SALIDA, opacidad=0.10)
        v_aba = aba.ventana(24, n - 1, color=C_RUIDO, opacidad=0.10)
        self.play(FadeIn(v_arr), FadeIn(v_aba), run_time=0.8)
        rot.mostrar(cifra_pie("uno para, el otro no"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        # --- la cola, mucho despues y ampliada ---------------------------
        a, b = self.N_COLA
        self.play(FadeOut(arr), FadeOut(et_arr), FadeOut(v_arr),
                  FadeOut(aba), FadeOut(et_aba), FadeOut(v_aba),
                  run_time=0.7)

        zoom = Secuencia(y_neg[a:b], a, (-0.06, 0.06), ancho=9.2, alto=2.6,
                         color=C_RUIDO, radio=0.040)
        zoom.move_to(LEFT * 0.55 + DOWN * 0.30)
        et_z = tag_hud(f"n = {a}..{b}", font_size=18, color=C_TENUE)
        et_z.next_to(zoom, UP, buff=0.26)
        et_z.align_to(zoom, LEFT)
        self.play(FadeIn(zoom.ejes), FadeIn(et_z), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(zoom.tallo(i)) for i in range(b - a)],
                              lag_ratio=0.028),
                  LaggedStart(*[FadeIn(zoom.punto(i)) for i in range(b - a)],
                              lag_ratio=0.028), run_time=1.8)
        self.wait(1.2)

        amp = ATRAPADA_NEG[BITS_DEMO]
        lin_sup = zoom.horizontal_en(amp, color=C_CALCULO)
        lin_inf = zoom.horizontal_en(-amp, color=C_CALCULO)
        et_sup = tag_hud(f"+{fmt(amp, 5)}", font_size=18, color=C_CALCULO)
        et_sup.next_to(zoom.en(b - 1, amp), RIGHT, buff=0.24)
        et_inf = tag_hud(f"{fmt(-amp, 5)}", font_size=18, color=C_CALCULO)
        et_inf.next_to(zoom.en(b - 1, -amp), RIGHT, buff=0.24)
        self.play(Create(lin_sup), Create(lin_inf), FadeIn(et_sup),
                  FadeIn(et_inf), run_time=0.8)
        rot.mostrar(cifra_pie(f"amplitud {fmt(amp, 5)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        panel = panel_cifras((f"a = {fmt(A_NEG, 1)}", C_RUIDO),
                             (f"periodo = {PERIODO_NEG[BITS_DEMO]}",
                              C_CALCULO),
                             (f"amplitud = {fmt(amp, 5)}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        rot.mostrar(cifra_pie(f"periodo {PERIODO_NEG[BITS_DEMO]}, "
                              f"sin entrada"), zona="abajo", run_time=0.5)
        self.wait(2.8)
        rot.mostrar(formula_pie(r"x[n] = 0 \qquad y[n] \neq 0"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
