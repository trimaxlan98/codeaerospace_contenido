class Clip1(Scene):
    """1 - Sistemas que se resisten. Portada del curso Control: la masa
    sobre resorte y amortiguador se estira a mano y, al soltarse, rebota
    con un amortiguamiento decreciente antes de calmarse en reposo.
    (~35 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: portada del curso -----------------------------------
        portada = VGroup(
            titulo_marca("Control", font_size=46),
            Text("domar sistemas que se resisten", font_size=25,
                 color=C_ACENTO),
        ).arrange(DOWN, buff=0.26)
        portada.move_to(ORIGIN)

        self.play(Write(portada[0]), run_time=1.3)
        self.play(FadeIn(portada[1], shift=0.18 * UP), run_time=0.7)
        self.wait(3.0)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.play(FadeOut(portada, shift=0.5 * UP), run_time=0.7)

        titulo = titulo_curso("Sistemas que se resisten")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.4)

        # --- momento: se estira a mano y se suelta ------------------------
        mr = masa_resorte(ancho=3.0).move_to(DOWN * 0.2)
        self.play(FadeIn(mr), run_time=0.5)

        pie1 = pie_curso('Ordenas "muévete un metro"... y el mundo '
                         'responde tarde, se pasa y rebota.')
        rot.mostrar(pie1, zona="abajo", run_time=0.45)

        self.play(mr.animate.estirar(0.9), run_time=0.7,
                  rate_func=rate_functions.ease_out_sine)
        for dx, rt in zip((-0.6, 0.4, -0.25, 0.12, 0.0),
                          (0.5, 0.45, 0.4, 0.35, 0.35)):
            self.play(mr.animate.estirar(dx), run_time=rt,
                      rate_func=rate_functions.ease_in_out_sine)
        self.wait(4.2)

        # --- momento: es un patron universal -------------------------------
        pie2 = pie_curso("Una antena, un dron, un brazo robótico: todos "
                         "son este resorte.")
        rot.mostrar(pie2, zona="abajo", run_time=0.45)
        self.wait(8.3)

        # --- momento: el gancho ----------------------------------------------
        pie3 = pie_curso("Controlar es domar esta respuesta.")
        rot.mostrar(pie3, zona="abajo", run_time=0.45)
        self.wait(8.0)
