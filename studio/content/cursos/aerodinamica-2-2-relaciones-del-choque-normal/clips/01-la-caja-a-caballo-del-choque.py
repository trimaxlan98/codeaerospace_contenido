class Clip1(Scene):
    """2.2.1 - Volumen de control a traves del choque.

    El truco entero del modulo 2 es este: se pone la caja a caballo de la
    onda, con una cara delante y otra detras, y no hace falta saber NADA de
    lo que pasa dentro. Las tres cuentas de la leccion 1.4, aplicadas aqui,
    bastan para resolver el salto. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La caja a caballo del choque")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        vc = volumen_control(ancho=3.6, alto=2.2, etiquetas=("1", "2"),
                             con_calor=False, con_trabajo=False)
        vc.move_to(UP * 0.55)
        onda = Line(vc.dentro(0.0, -1.42), vc.dentro(0.0, 1.42),
                    stroke_width=4.0, color=C_SUPER)
        tag_onda = Text("choque", font_size=19, color=C_SUPER)
        tag_onda.next_to(onda, UP, buff=0.14)

        self.play(Create(onda), FadeIn(tag_onda), run_time=0.8)
        rot.mostrar(pie_curso("Una onda de choque. Por dentro pasan cosas "
                              "que no sabemos describir."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        self.play(Create(vc.superficie), run_time=0.9)
        self.play(FadeIn(vc.entrada, shift=0.2 * RIGHT),
                  FadeIn(vc.salida, shift=0.2 * RIGHT), run_time=0.8)
        rot.mostrar(pie_curso("Da igual. Pon la caja a caballo: una cara "
                              "delante, otra detrás."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: las tres cuentas, otra vez --------------------------
        # Son las mismas de la leccion 1.4; lo unico nuevo es donde se ponen.
        filas = VGroup(
            MathTex(r"\rho_1 V_1 = \rho_2 V_2", font_size=34, color=C_SUB),
            MathTex(r"p_1 + \rho_1 V_1^2 = p_2 + \rho_2 V_2^2",
                    font_size=34, color=C_TRANS),
            MathTex(r"h_1 + \tfrac{V_1^2}{2} = h_2 + \tfrac{V_2^2}{2}",
                    font_size=34, color=C_CALCULO))
        filas.arrange(DOWN, buff=0.30).move_to(DOWN * 1.85)

        for fila, pie in zip(filas, (
                "La masa que entra por delante sale por detrás.",
                "La fuerza sobre el aire le cambia la cantidad de "
                "movimiento.",
                "Y como no entra calor ni sale trabajo, la entalpía total no "
                "se mueve.")):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(fila, shift=0.12 * UP), run_time=0.7)
            self.wait(4.4)

        rot.mostrar(pie_curso("Tres ecuaciones. Y no hemos mirado ni una vez "
                              "dentro de la onda."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
