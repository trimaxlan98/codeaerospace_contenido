class Clip3(Scene):
    """2.2.3 - Dos realimentaciones: una decae y su suma converge, la
    otra crece sin freno. El criterio BIBO se ve. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Cuando la salida se dispara"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Dos carriles con RANGO PROPIO: los valores no son comparables
        # (una llega a 1, la otra a 31).
        sec_e = Secuencia(H_ESTABLE, 0, (-0.18, 1.15), ancho=8.8, alto=1.35,
                          color=C_SALIDA, radio=0.042, grosor=1.8,
                          eje_y=False)
        sec_e.move_to(UP * 1.55)
        sec_i = Secuencia(H_INESTABLE, 0, (-4.0, 33.5), ancho=8.8,
                          alto=1.35, color=C_RUIDO, radio=0.042,
                          grosor=1.8, eje_y=False)
        sec_i.move_to(DOWN * 0.95)

        et_e = tag_junto(sec_e, f"a = {A_ESTABLE}", LEFT, buff=0.28,
                         font_size=20, color=C_SALIDA)
        et_i = tag_junto(sec_i, f"a = {A_INESTABLE}", LEFT, buff=0.28,
                         font_size=20, color=C_RUIDO)

        # --- la que decae ---------------------------------------------------
        self.play(FadeIn(sec_e.ejes), FadeIn(et_e), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(sec_e.tallo(i))
                                for i in range(N_BIBO)], lag_ratio=0.018),
                  LaggedStart(*[FadeIn(sec_e.punto(i))
                                for i in range(N_BIBO)], lag_ratio=0.018),
                  run_time=2.8)
        env_e = sec_e.curva_de(np.arange(N_BIBO), H_ESTABLE,
                               color=C_SALIDA, grosor=2.0)
        self.play(Create(env_e), run_time=1.4)
        self.wait(1.0)

        t_e0 = tag_hud(f"h[0] = {fmt(H_ESTABLE[0], 2)}", font_size=19,
                       color=C_SALIDA)
        t_e0.next_to(sec_e.en(0, H_ESTABLE[0]), UR, buff=0.10)
        t_e59 = tag_hud(f"h[{N_BIBO - 1}] = {fmt(H_ESTABLE[-1], 5)}",
                        font_size=19, color=C_SALIDA)
        t_e59.next_to(sec_e.en(N_BIBO - 6, 0.0), UP, buff=0.26)
        self.play(FadeIn(t_e0), run_time=0.4)
        self.wait(0.8)
        self.play(FadeIn(t_e59), run_time=0.4)
        self.wait(1.2)

        rot.mostrar(cifra_pie(f"suma |h| = {fmt(SUMA_ESTABLE, 2)}",
                              color=C_SALIDA), zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- la que crece ---------------------------------------------------
        self.play(FadeIn(sec_i.ejes), FadeIn(et_i), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(sec_i.tallo(i))
                                for i in range(N_BIBO)], lag_ratio=0.018),
                  LaggedStart(*[FadeIn(sec_i.punto(i))
                                for i in range(N_BIBO)], lag_ratio=0.018),
                  run_time=2.8)
        env_i = sec_i.curva_de(np.arange(N_BIBO), H_INESTABLE,
                               color=C_RUIDO, grosor=2.0)
        self.play(Create(env_i), run_time=1.4)
        self.wait(1.0)

        t_i59 = tag_hud(f"h[{N_BIBO - 1}] = {fmt(ULTIMO_INESTABLE, 1)}",
                        font_size=19, color=C_RUIDO)
        t_i59.next_to(sec_i.en(N_BIBO - 1, ULTIMO_INESTABLE), UL, buff=0.10)
        self.play(FadeIn(t_i59), run_time=0.4)
        self.wait(1.6)

        # La suma NO converge: esto es lo que llevaba en 60 muestras.
        rot.mostrar(cifra_pie(f"{fmt(SUMA_INESTABLE, 0)} en "
                              f"{N_BIBO} muestras", color=C_RUIDO),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        rot.mostrar(formula_pie(r"\sum_n |h[n]| < \infty"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)

        panel = panel_cifras((f"suma |h| = {fmt(SUMA_ESTABLE, 2)}",
                              C_SALIDA),
                             (f"{fmt(SUMA_INESTABLE, 0)} en "
                              f"{N_BIBO} muestras", C_RUIDO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(4.2)
