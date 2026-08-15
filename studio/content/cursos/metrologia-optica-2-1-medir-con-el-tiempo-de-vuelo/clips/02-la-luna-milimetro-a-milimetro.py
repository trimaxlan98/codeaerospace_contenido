class Clip2(Scene):
    """2.1.2 - La Luna, milimetro a milimetro: los retrorreflectores del
    Apolo devuelven el pulso; 2.564 s de ida y vuelta bastan para conocer
    la distancia con milimetros. La Luna se aleja 3.8 cm al año (cita).
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("La Luna, milímetro a milímetro"),
                    zona="arriba", run_time=0.6)

        # --- momento: los retrorreflectores del Apolo -----------------------
        rot.mostrar(pie_curso("En 1969 los astronautas dejaron espejos "
                              "en la Luna: retrorreflectores."),
                    zona="abajo", run_time=0.5)
        luna = tierra_luna_laser()
        luna.scale(0.86).move_to(UP * 0.30)
        self.play(Create(luna.camino), FadeIn(luna.tierra, luna.luna,
                  luna.estacion, luna.retrorreflector), FadeIn(luna.rotulos),
                  run_time=0.9)
        nota = tag_hud("tamanos no a escala; distancia si", font_size=13,
                       color=C_TENUE)
        nota.move_to(np.array([0.0, -1.55, 0.0]))
        self.play(FadeIn(nota), run_time=0.5)
        self.wait(2.4)

        # --- momento: 2.56 segundos de ida y vuelta --------------------------
        rot.mostrar(pie_curso("Un pulso tarda 2.56 segundos en ir y "
                              "volver."), zona="abajo", run_time=0.5)
        self.play(FadeIn(luna.lectura), FadeIn(luna.halo, luna.pulso),
                  run_time=0.4)
        self.play(UpdateFromAlphaFunc(luna, lambda m, a: m.a_t(a)),
                  run_time=2.5, rate_func=linear)
        # la lectura de la pieza ya rotula el tiempo total (T_LUNA_S)
        self.play(Indicate(luna.lectura, color=C_MEDIDA, scale_factor=1.08),
                  run_time=0.8)
        self.wait(2.5)

        # --- momento: la Luna se aleja ---------------------------------------
        rot.mostrar(pie_curso("Con eso se conoce la distancia con "
                              "milímetros: la Luna se aleja 3.8 cm al "
                              "año."), zona="abajo", run_time=0.5)
        cifra_aleja = tag_junto(nota, "se aleja 3.8 cm al año (cita)",
                                DOWN, buff=0.20, font_size=15)
        self.play(FadeIn(cifra_aleja), run_time=0.5)
        self.wait(6.0)

        # --- cierre ---------------------------------------------------------
        rot.mostrar(pie_curso("Cuatrocientos mil kilómetros, medidos "
                              "con un pulso de luz."), zona="abajo")
        self.wait(8.5)
