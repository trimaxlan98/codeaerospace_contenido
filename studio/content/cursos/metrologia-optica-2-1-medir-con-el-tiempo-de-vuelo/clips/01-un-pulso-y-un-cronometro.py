class Clip1(Scene):
    """2.1.1 - Un pulso y un cronometro: la medida de distancia mas
    directa que hay. El pulso sale, rebota y vuelve; el cronometro mide
    t y de ahi sale d = c t / 2. Un milimetro son 6.7 picosegundos: por
    eso los telemetros se pelean por el picosegundo. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Un pulso y un cronómetro"),
                    zona="arriba", run_time=0.6)

        # --- momento: se lanza el pulso, arranca el cronometro -------------
        rot.mostrar(pie_curso("Se lanza un pulso, se arranca el "
                              "cronómetro y se espera el eco."),
                    zona="abajo", run_time=0.5)
        pulso = pulso_ida_vuelta(d=1.5)
        pulso.shift(UP * 0.35)
        self.play(Create(pulso.camino), FadeIn(pulso.emisor, pulso.blanco),
                  FadeIn(pulso.rotulos), FadeIn(pulso.medida), run_time=0.8)
        self.play(FadeIn(pulso.lectura), FadeIn(pulso.halo, pulso.pulso),
                  run_time=0.5)
        self.play(UpdateFromAlphaFunc(pulso, lambda m, a: m.a_t(a)),
                  run_time=3.0, rate_func=linear)
        self.wait(3.0)

        # --- momento: la formula -------------------------------------------
        rot.mostrar(pie_curso("La distancia es la mitad del tiempo por "
                              "la velocidad de la luz."), zona="abajo",
                    run_time=0.5)
        formula = MathTex(r"d = \frac{c\,t}{2}", font_size=36,
                          color=C_MEDIDA)
        formula.move_to(np.array([0.0, -1.95, 0.0]))
        self.play(Write(formula), run_time=1.0)
        self.wait(4.0)

        # --- momento: el picosegundo ------------------------------------------
        rot.mostrar(pie_curso("Un milímetro son 6.7 picosegundos: hay "
                              "que medir el tiempo muy fino."),
                    zona="abajo", run_time=0.5)
        cifra = tag_hud(f"1 mm = {PS_POR_MM:.2f} ps", font_size=17,
                        color=C_MEDIDA)
        cifra.next_to(formula, RIGHT, buff=0.55)
        self.play(FadeIn(cifra, shift=0.12 * UP), run_time=0.6)
        self.wait(6.0)

        # --- cierre ---------------------------------------------------------
        rot.mostrar(pie_curso("Medir lejos es medir tiempo. Y el tiempo "
                              "se mide muy bien."), zona="abajo")
        self.wait(6.5)
