class Clip4(Scene):
    """4 - La vista polar del pase. Sobre la carta polar del cielo (borde =
    horizonte, centro = cenit) aparece la mascara de elevacion y luego dos
    pases: uno rasante (violeta, tenue, culmina bajo) y uno casi cenital
    (ambar, culmina alto), con sus tags en relevo. Un punto ambar recorre
    la traza alta completa: la elevacion maxima es lo que importa. (~37 s)
    """

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo -------------------------------------------
        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("No todos los pases valen lo mismo")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(1.2)

        # --- momento: la carta polar del cielo -----------------------------------
        vista = vista_polar(radio=2.35)
        vista.move_to(np.array([0.0, -0.15, 0.0]))
        self.play(FadeIn(vista), run_time=0.6)

        rot.mostrar(pie_curso("El cielo de tu estación, visto desde "
                              "arriba: el borde es el horizonte, el "
                              "centro el cénit."), zona="abajo",
                   run_time=0.45)
        self.wait(5.2)

        # --- momento: bajo la mascara no hay pase ---------------------------------
        mascara = mascara_elevacion(vista, el_min=8.0)
        self.play(FadeIn(mascara), run_time=0.5)

        rot.mostrar(pie_curso("Bajo ocho grados no hay pase: árboles, "
                              "edificios y demasiada atmósfera."),
                   zona="abajo", run_time=0.45)
        self.wait(5.0)

        # --- momento: un pase rasante, lejos y debil ------------------------------
        traza_rasante = traza_pase(vista, el_max=12.0, az_culminacion=-60.0,
                                   color=C_CIELO)
        traza_rasante.set_stroke(opacity=0.55)
        self.play(Create(traza_rasante), run_time=1.1)

        marca_rasante = Dot(traza_rasante.punto_en(0.5), radius=0.04,
                            color=C_CIELO)
        tag_rasante = tag_junto(marca_rasante, "rasante", direccion=UL,
                                buff=0.12)
        self.play(FadeIn(VGroup(marca_rasante, tag_rasante), shift=0.1 * UP),
                  run_time=0.35)

        rot.mostrar(pie_curso("Un pase rasante: lejos, corto y débil."),
                   zona="abajo", run_time=0.45)
        self.wait(5.0)

        # --- momento: un pase casi cenital, tag en relevo -------------------------
        traza_alta = traza_pase(vista, el_max=80.0, az_culminacion=25.0,
                                color=C_SAT)
        self.play(Create(traza_alta),
                  traza_rasante.animate.set_stroke(opacity=0.35),
                  run_time=1.2)

        # relevo secuencial: el tag anterior sale ANTES de que entre el nuevo.
        self.play(FadeOut(tag_rasante), FadeOut(marca_rasante), run_time=0.25)
        marca_alta = Dot(traza_alta.punto_en(0.5), radius=0.04, color=C_SAT)
        tag_alta = tag_junto(marca_alta, "casi cenital", direccion=DR,
                             buff=0.14)
        self.play(FadeIn(VGroup(marca_alta, tag_alta), shift=0.1 * UP),
                  run_time=0.35)

        rot.mostrar(pie_curso("Uno alto: cuatro veces más cerca — doce "
                              "decibelios más de señal."), zona="abajo",
                   run_time=0.45)
        self.wait(5.0)

        # --- momento: la elevacion maxima lo dice todo ----------------------------
        vt = ValueTracker(0.0)
        punto = punto_brillante(traza_alta.punto_en(0.0), color=C_SAT,
                                radio=0.07)
        punto.add_updater(lambda m: m.move_to(traza_alta.punto_en(
            vt.get_value())))
        self.play(FadeIn(punto), run_time=0.3)

        rot.mostrar(pie_curso("La elevación máxima lo dice todo: caza los "
                              "pases altos."), zona="abajo", run_time=0.45)
        self.play(vt.animate.set_value(1.0), run_time=2.3, rate_func=linear)
        self.wait(2.6)
        punto.clear_updaters()
