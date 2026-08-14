class Clip1(Scene):
    """4.5.1 - Teoria de Ackeret: cl = 4 alfa / sqrt(M^2 - 1).

    La misma linealizacion del clip 1 de la 4.1, aplicada al lado
    supersonico. Y sale algo que en subsonico no ocurre: la sustentacion
    DISMINUYE al ir mas rapido, y no depende de la forma del perfil.
    (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La fórmula de Ackeret")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        formula = MathTex(r"c_l = \frac{4\alpha}{\sqrt{M_\infty^2 - 1}}",
                          font_size=58, color=C_CALCULO)
        formula.move_to(UP * 1.25)
        self.play(Write(formula), run_time=1.3)
        rot.mostrar(pie_curso("La misma linealización, al otro lado de "
                              "Mach 1."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        rot.mostrar(pie_curso("Y aquí la raíz no está debajo: está debajo "
                              "pero con el signo cambiado."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: lo que eso significa ---------------------------------
        # Tres Machs, tres pendientes, todas de la libreria.
        filas = VGroup()
        for m in (1.5, 2.0, 3.0, 5.0):
            datos = ackeret(m, 1.0)
            filas.add(VGroup(
                Text(f"M {m:g}", font=FUENTE_HUD, font_size=19,
                     color=C_TENUE),
                Text(f"{datos['pendiente']:.2f} /rad", font=FUENTE_HUD,
                     font_size=19, color=C_CALCULO)).arrange(RIGHT,
                                                             buff=0.45))
        filas.arrange(DOWN, aligned_edge=LEFT, buff=0.20)
        filas.move_to(DOWN * 1.05)

        self.play(LaggedStart(*[FadeIn(f, shift=0.12 * UP) for f in filas],
                              lag_ratio=0.3), run_time=1.4)
        rot.mostrar(pie_curso("Cuanto más rápido vuelas, menos sustenta el "
                              "mismo ángulo de ataque."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Al revés que en subsónico, donde la "
                              "compresibilidad la empinaba."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: lo que NO aparece -------------------------------------
        rot.mostrar(pie_curso("Y fíjate en lo que no aparece: ni el espesor, "
                              "ni la curvatura, ni la forma."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("En supersónico, para sustentar solo cuenta el "
                              "ángulo."), zona="abajo", run_time=0.5)
        self.wait(4.8)
