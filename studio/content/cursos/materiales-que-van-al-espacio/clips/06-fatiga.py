class Clip6(Scene):
    """6 - Fatiga: morir de mil ciclos. Una carga que nunca rompe de golpe
    empuja, ciclo a ciclo, una grieta invisible; la curva S-N pone precio
    en vidas a cada nivel de esfuerzo. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ------------------------------------------------
        modulo = hud_modulo("Modulo 06")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Fatiga: morir de mil ciclos")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(1.0)

        # --- momento: la carga que nunca rompe de golpe ---------------------
        rot.mostrar(pie_curso("Ninguna carga rompe el ala hoy. Pero sube "
                              "y baja diez mil veces por vuelo."),
                    zona="abajo", run_time=0.5)

        placa = placa_con_ciclos()
        placa.move_to(np.array([-3.0, -0.1, 0.0]))
        self.play(FadeIn(placa), run_time=0.6)
        for _ in range(3):
            self.play(Indicate(placa.flechas, color=C_FALLA,
                               scale_factor=1.12), run_time=0.35)
        self.wait(4.85)

        # --- momento: la grieta que crece paso a paso ------------------------
        rot.mostrar(pie_curso("Cada ciclo empuja una grieta invisible, "
                              "un paso más."), zona="abajo", run_time=0.5)

        borde_izq = float(placa.placa.get_left()[0])
        y_medio = float(placa.placa.get_center()[1])
        g1 = grieta(largo=0.5, dientes=4)
        g1.move_to(np.array([borde_izq + 0.25, y_medio, 0.0]))
        g2 = grieta(largo=1.0, dientes=7)
        g2.move_to(np.array([borde_izq + 0.5, y_medio, 0.0]))

        self.play(Create(g1), run_time=0.8)
        self.play(ReplacementTransform(g1, g2), run_time=1.0)
        self.wait(3.95)

        # --- momento: la curva S-N dicta sentencia ---------------------------
        rot.mostrar(pie_curso("La curva S-N dicta la sentencia: menos "
                              "carga, más vidas."), zona="abajo",
                    run_time=0.5)

        sn = curva_sn()
        sn.move_to(np.array([2.9, -0.1, 0.0]))
        self.play(FadeIn(sn.ejes), run_time=0.5)
        self.play(Create(sn.curva), run_time=0.9)
        self.wait(4.85)

        # --- momento: el limite de fatiga -------------------------------------
        rot.mostrar(pie_curso("Bajo el límite de fatiga, el acero vive "
                              "para siempre. El aluminio no lo tiene: "
                              "todo vuelo le cuesta vida."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(sn.limite), FadeIn(sn.etiquetas), run_time=0.4)
        self.play(Indicate(sn.limite, color=C_OK, scale_factor=1.05),
                  run_time=0.8)
        self.wait(4.85)

        # --- momento: cierre ---------------------------------------------------
        rot.mostrar(pie_curso("Por eso los aviones se retiran por "
                              "ciclos, no por años."), zona="abajo",
                    run_time=0.5)
        self.wait(5.75)
