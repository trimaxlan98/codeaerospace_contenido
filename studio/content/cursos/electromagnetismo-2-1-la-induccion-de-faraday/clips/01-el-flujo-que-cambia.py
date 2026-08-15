class Clip1(Scene):
    """2.1.1 - El flujo que cambia enciende la corriente. Primero el
    experimento: el iman quieto no hace nada, solo el MOVIMIENTO mueve
    la aguja, en ambos sentidos. Despues las curvas Phi(t) y -dPhi/dt,
    alineadas: la fem es la derivada del MISMO flujo, no otra formula.
    (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El flujo que cambia")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el iman quieto, lejos ---------------------------------
        eim = espira_iman()
        self.play(FadeIn(eim), run_time=0.7)
        rot.mostrar(pie_curso("Un imán y una bobina. Nada las toca. "
                              "¿Qué podría pasar?"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- momento: entra y se detiene: la aguja vuelve a cero -----------
        rot.mostrar(pie_curso("Empuja el imán hacia el centro… y "
                              "detente ahí. Mira la aguja."),
                    zona="abajo", run_time=0.5)
        aguja_1 = eim.aguja_a(0.85)
        self.play(eim.iman.animate.move_to(ORIGIN),
                  ReplacementTransform(eim.aguja, aguja_1), run_time=1.4)
        eim.aguja = aguja_1
        aguja_0a = eim.aguja_a(0.0)
        self.play(ReplacementTransform(eim.aguja, aguja_0a), run_time=0.6)
        eim.aguja = aguja_0a
        self.wait(3.6)

        # --- momento: sale y se detiene: simetrico, tambien vuelve a cero --
        rot.mostrar(pie_curso("Ahora sácalo. Salta al lado contrario — "
                              "y si lo dejas quieto ahí fuera, vuelve a "
                              "cero otra vez."), zona="abajo", run_time=0.5)
        aguja_2 = eim.aguja_a(-0.85)
        self.play(eim.iman.animate.move_to(LEFT * 2.6),
                  ReplacementTransform(eim.aguja, aguja_2), run_time=1.4)
        eim.aguja = aguja_2
        aguja_0b = eim.aguja_a(0.0)
        self.play(ReplacementTransform(eim.aguja, aguja_0b), run_time=0.6)
        eim.aguja = aguja_0b
        self.wait(3.4)

        # --- momento: las dos curvas alineadas -------------------------------
        rot.mostrar(pie_curso("No importa la posición: importa si el "
                              "flujo CAMBIA. Dibujemos Φ y la fem "
                              "juntas."), zona="abajo", run_time=0.5)
        cff = curvas_flujo_fem()
        cff.shift(DOWN * 0.35)
        self.play(FadeOut(eim), FadeIn(cff.cajas), run_time=0.9)
        self.play(Create(cff.curva_flujo), Create(cff.curva_fem),
                  run_time=1.8)
        self.wait(2.0)

        # --- momento: fem cero donde el flujo es maximo ----------------------
        rot.mostrar(pie_curso("Donde Φ es MÁXIMO (el imán centrado), la "
                              "fem es CERO."), zona="abajo", run_time=0.5)
        p_flujo_0 = Dot(cff.punto_flujo(0.0), radius=0.07, color=C_B)
        p_fem_0 = Dot(cff.punto_fem(0.0), radius=0.07, color=C_CALCULO)
        self.play(FadeIn(p_flujo_0, scale=1.6), FadeIn(p_fem_0, scale=1.6),
                  run_time=0.6)
        self.wait(4.6)

        # --- momento: fem maxima donde el flujo cambia mas rapido -----------
        rot.mostrar(pie_curso("Donde Φ cambia MÁS RÁPIDO, la fem es "
                              "máxima. Es la misma pendiente."),
                    zona="abajo", run_time=0.5)
        p_flujo_1 = Dot(cff.punto_flujo(0.35), radius=0.07, color=C_B)
        p_fem_1 = Dot(cff.punto_fem(0.35), radius=0.07, color=C_CALCULO)
        self.play(FadeIn(p_flujo_1, scale=1.6), FadeIn(p_fem_1, scale=1.6),
                  run_time=0.6)
        self.wait(4.6)

        rot.mostrar(pie_curso("No hay dos fórmulas: la fem ES la "
                              "pendiente del flujo, medida en cada "
                              "instante."), zona="abajo", run_time=0.5)
        self.wait(4.8)
