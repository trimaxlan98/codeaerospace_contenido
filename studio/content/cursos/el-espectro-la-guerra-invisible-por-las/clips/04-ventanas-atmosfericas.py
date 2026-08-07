class Clip4(Scene):
    """4 - Las ventanas atmosfericas. La curva de absorcion gaseosa se
    dibuja y en relevo se marcan sus dos rabietas moleculares (H2O en 22
    GHz, O2 en 60) antes de abrir las ventanas verdes donde viven las
    bandas comerciales."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo -------------------------------------------
        modulo = hud_modulo("Modulo 04")
        titulo = titulo_curso("Las ventanas atmosféricas")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.35)
        rot.mostrar(titulo, zona="arriba", run_time=0.35)
        self.wait(0.3)

        # --- momento: la curva se dibuja -----------------------------------------
        rot.mostrar(pie_curso("El aire también cobra: dos moléculas con "
                              "sus rabietas."), zona="abajo", run_time=0.35)
        gases = curva_gases()
        gases.move_to(np.array([0.0, -0.1, 0.0]))
        self.add(gases.ventanas)
        self.play(FadeIn(gases.ejes, gases.marcas, gases.etiquetas),
                  run_time=0.5)
        self.play(Create(gases.curva), run_time=1.2)
        self.wait(5.0)

        # --- momento: el pico de H2O en 22 GHz, en relevo ------------------------
        rot.mostrar(pie_curso("El vapor de agua resuena a 22 "
                              "gigahertz..."), zona="abajo", run_time=0.35)
        punto_h2o = punto_brillante(gases.punto_de(22.0), color=C_PERDIDA,
                                    radio=0.07)
        tag_h2o = etiqueta_hud("H2O · 22 GHz", font_size=12, color=C_PERDIDA)
        tag_h2o.next_to(punto_h2o, UP, buff=0.16)
        tag_h2o.align_to(punto_h2o, RIGHT)
        self.play(FadeIn(punto_h2o), FadeIn(tag_h2o), run_time=0.4)
        self.wait(5.4)

        # --- momento: el muro de O2 en 60 GHz, en relevo --------------------------
        rot.mostrar(pie_curso("...y el oxígeno levanta un muro de 15 dB "
                              "por kilómetro en 60."), zona="abajo",
                   run_time=0.35)
        punto_o2 = punto_brillante(gases.punto_de(60.0), color=C_PERDIDA,
                                   radio=0.07)
        tag_o2 = etiqueta_hud("O2 · 60 GHz", font_size=12, color=C_PERDIDA)
        tag_o2.next_to(punto_o2, UP, buff=0.16)
        tag_o2.align_to(punto_o2, RIGHT)
        self.play(FadeIn(punto_o2), FadeIn(tag_o2), run_time=0.4)
        self.wait(5.6)

        # --- momento: las ventanas se abren ---------------------------------------
        rot.mostrar(pie_curso("Entre pico y muro quedan las ventanas: "
                              "ahí viven las bandas comerciales."),
                   zona="abajo", run_time=0.35)
        self.play(*gases.abrir_ventanas(), run_time=0.9)
        self.wait(5.6)

        # --- momento: cierre --------------------------------------------------------
        rot.mostrar(pie_curso("Hasta el muro sirve: en 60 GHz la señal "
                              "muere pronto... y eso permite reusarla en "
                              "la esquina siguiente."), zona="abajo",
                   run_time=0.35)
        self.wait(6.4)
