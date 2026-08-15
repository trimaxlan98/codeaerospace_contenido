class Clip3(Scene):
    """2.1.3 - Satelites con laser: las estaciones de telemetria laser
    (SLR) disparan a satelites cubiertos de espejos. LAGEOS a 5900 km:
    39.4 ms de ida y vuelta, orbita medida al milimetro. El eco vuelve
    debil: la potencia cae con 1/R^4. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Satélites con láser"),
                    zona="arriba", run_time=0.6)

        # --- momento: la estacion dispara al satelite -------------------------
        rot.mostrar(pie_curso("Las estaciones de telemetría láser "
                              "disparan a satélites cubiertos de "
                              "espejos."), zona="abajo", run_time=0.5)
        slr = satelite_slr()
        slr.scale(0.62).move_to(DOWN * 0.55)
        self.play(Create(slr.superficie), Create(slr.vista),
                  FadeIn(slr.estacion, slr.satelite), FadeIn(slr.rotulos),
                  run_time=0.9)
        self.wait(2.8)

        # --- momento: 39.4 ms -------------------------------------------------
        rot.mostrar(pie_curso("Treinta y nueve milisegundos: la órbita "
                              "queda medida al milímetro."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(slr.lectura), FadeIn(slr.halo, slr.pulso),
                  run_time=0.4)
        self.play(UpdateFromAlphaFunc(slr, lambda m, a: m.a_t(a)),
                  run_time=2.5, rate_func=linear)
        cifra_t = tag_hud(f"{T_LAGEOS_MS:.1f} ms", font_size=17,
                          color=C_MEDIDA)
        cifra_t.next_to(slr.lectura, DOWN, buff=0.20, aligned_edge=LEFT)
        self.play(FadeIn(cifra_t, shift=0.10 * UP), run_time=0.5)
        self.wait(2.8)

        # --- momento: el eco debil ---------------------------------------------
        rot.mostrar(pie_curso("El eco vuelve débil: la potencia cae con "
                              "la cuarta potencia de la distancia."),
                    zona="abajo", run_time=0.5)
        formula = MathTex(r"P_{eco} \propto \frac{1}{R^4}", font_size=34,
                          color=C_HAZ)
        formula.move_to(np.array([-3.9, 1.1, 0.0]))
        self.play(Write(formula), run_time=1.0)
        self.wait(5.0)

        # --- cierre -------------------------------------------------------------
        rot.mostrar(pie_curso("Así se pesa la Tierra y se vigila cómo "
                              "sube el mar."), zona="abajo")
        self.wait(9.0)
