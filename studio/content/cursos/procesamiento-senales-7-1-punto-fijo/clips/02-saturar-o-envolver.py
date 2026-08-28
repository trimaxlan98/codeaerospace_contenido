class Clip2(Scene):
    """7.1.2 - Al pasarse del tope hay dos comportamientos, y uno de ellos
    convierte un pico positivo en uno negativo. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("Saturar o envolver"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- una señal que se pasa ----------------------------------------
        t = T_Q
        on = Secuencia(X_GRANDE[::4], 0, (-1.6, 1.6), ancho=10.4, alto=3.0,
                       color=C_SENAL, radio=0.035)
        on.move_to(DOWN * 0.25)
        lim_sup = on.horizontal_en(1.0, color=C_RUIDO)
        lim_inf = on.horizontal_en(-1.0, color=C_RUIDO)
        et_lim = tag_hud("tope", font_size=19, color=C_RUIDO)
        et_lim.next_to(on.en(0, 1.0), UR, buff=0.08)
        self.play(FadeIn(on.ejes), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(on.tallo(i))
                                for i in range(len(X_GRANDE[::4]))],
                              lag_ratio=0.01),
                  LaggedStart(*[FadeIn(on.punto(i))
                                for i in range(len(X_GRANDE[::4]))],
                              lag_ratio=0.01), run_time=1.8)
        self.play(Create(lim_sup), Create(lim_inf), FadeIn(et_lim),
                  run_time=0.8)
        rot.mostrar(cifra_pie(f"{N_PASADAS} muestras pasadas"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        # --- saturar: se queda en el tope ---------------------------------
        gem_sat = on.con_valores(Y_SAT[::4], color=C_SALIDA)
        self.play(FadeOut(on.tallos), FadeOut(on.puntos), run_time=0.5)
        self.add(gem_sat.tallos, gem_sat.puntos)
        self.play(LaggedStart(*[FadeIn(gem_sat.tallo(i))
                                for i in range(len(Y_SAT[::4]))],
                              lag_ratio=0.01), run_time=1.4)
        rot.mostrar(cifra_pie(f"satura: {fmt(PICO_MALO, 1)} -> "
                              f"{fmt(SAT_MALO, 4)}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        # --- envolver: da la vuelta ---------------------------------------
        gem_env = on.con_valores(Y_ENV[::4], color=C_RUIDO)
        self.play(Transform(gem_sat.tallos, gem_env.tallos),
                  Transform(gem_sat.puntos, gem_env.puntos), run_time=1.4)
        rot.mostrar(cifra_pie(f"envuelve: {fmt(PICO_MALO, 1)} -> "
                              f"{fmt(ENV_MALO, 1)}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        panel = panel_cifras((f"entra {fmt(PICO_MALO, 1)}", C_TENUE),
                             (f"satura {fmt(SAT_MALO, 4)}", C_SALIDA),
                             (f"envuelve {fmt(ENV_MALO, 1)}", C_RUIDO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.0)
        rot.mostrar(cifra_pie("un pico se vuelve valle"), zona="abajo",
                    run_time=0.5)
        self.wait(6.6)
