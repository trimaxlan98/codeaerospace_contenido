class Clip1(Scene):
    """1.1.1 - La vibracion del lanzador se vuelve una lista de numeros:
    el reloj pregunta, quedan los tallos. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("La curva y sus numeros"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        sec = Secuencia(XK, 0, (-1.18, 1.18), ancho=10.2, alto=2.9,
                        color=C_MUESTRA)
        sec.move_to(DOWN * 0.32)
        et_n = tag_hud("n", font_size=20, color=C_TENUE)
        et_n.next_to(sec.en(N_MUESTRAS - 0.5, 0.0), RIGHT, buff=0.14)

        # --- el mundo continuo -------------------------------------------
        t_den = np.linspace(0.0, T_VENTANA, 900)
        curva = sec.curva_de(t_den * FS, vibracion(t_den), color=C_SENAL,
                             grosor=2.8)
        self.play(FadeIn(sec.ejes), FadeIn(et_n), run_time=0.6)
        self.play(Create(curva), run_time=2.2)
        self.wait(1.4)

        # --- el reloj pregunta -------------------------------------------
        relojes = VGroup(*[sec.vertical_en(k, color=C_REJILLA)
                           for k in range(0, N_MUESTRAS, 4)])
        self.play(LaggedStart(*[Create(l) for l in relojes], lag_ratio=0.05),
                  run_time=1.6)
        self.wait(0.9)

        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in
                                range(N_MUESTRAS)], lag_ratio=0.035),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in
                                range(N_MUESTRAS)], lag_ratio=0.035),
                  run_time=2.6)
        self.wait(1.6)

        # --- se apaga el mundo: quedan los numeros ------------------------
        self.play(curva.animate.set_stroke(opacity=0.30),
                  FadeOut(relojes), run_time=1.2)
        self.wait(1.8)

        panel = panel_cifras(f"fs = {fmt(FS, 0)} Hz",
                             f"N = {N_MUESTRAS}",
                             f"T = {fmt(T_MUESTRA_MS, 2)} ms")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.2)

        # --- la lista, escrita --------------------------------------------
        marcas = VGroup(*[sec.marcar(i, color=C_CALCULO) for i in (0, 1, 2,
                                                                   3, 4)])
        valores = VGroup(*[tag_hud(f"{XK[i]:+.3f}", font_size=21)
                           for i in range(5)])
        valores.arrange(RIGHT, buff=0.34)
        valores.move_to(np.array([0.0, sec.en(0, -1.18)[1] - 0.52, 0.0]))
        self.play(LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.12),
                  run_time=1.2)
        self.play(LaggedStart(*[FadeIn(v, shift=0.12 * UP) for v in valores],
                              lag_ratio=0.18), run_time=1.6)
        self.wait(2.6)

        rot.mostrar(cifra_pie(f"ventana = {fmt(T_VENTANA * 1000, 0)} ms"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)
        self.play(FadeOut(valores), FadeOut(marcas), run_time=0.7)
        rot.mostrar(formula_pie(r"x[n] = x_c(n\,T_s)"), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)
