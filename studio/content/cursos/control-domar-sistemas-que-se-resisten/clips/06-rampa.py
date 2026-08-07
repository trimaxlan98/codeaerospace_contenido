class Clip6(Scene):
    """6 - La rampa que nunca alcanzas. Ante una rampa el error de un
    control proporcional puro se vuelve constante: el sistema persigue
    a distancia fija y jamas alcanza, hasta que la memoria integral
    funde ese rezago a cero. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo --------------------------------------------------
        modulo = hud_modulo("Modulo 06")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("La rampa que nunca alcanzas")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(0.4)

        # --- momento: la referencia nunca deja de moverse -------------------
        rampa = rampa_con_rezago(rezago=0.14)
        rampa.move_to((0.0, -0.1, 0.0))
        self.play(Create(rampa.ejes), FadeIn(rampa.etiquetas),
                  Create(rampa.ref), Create(rampa.sis), run_time=1.0)
        rot.mostrar(pie_curso("Un pase de satélite no es un escalón: la "
                              "orden nunca deja de moverse."), zona="abajo")
        self.wait(5.0)

        # --- momento: la flecha del error, con P puro nunca alcanza ---------
        p_ref, p_sis = rampa.brecha_en(0.6)
        flecha = DoubleArrow(p_sis, p_ref, buff=0.0, color=C_MAL,
                             stroke_width=3.0, tip_length=0.1,
                             max_tip_length_to_length_ratio=0.5)
        tag = tag_junto(flecha, "rezago", direccion=DOWN + RIGHT, buff=0.22,
                        color=C_MAL)
        self.play(GrowArrow(flecha), FadeIn(tag), run_time=0.45)
        rot.mostrar(pie_curso("Con P puro, el sistema persigue... a "
                              "distancia constante. Jamás alcanza."),
                    zona="abajo")
        self.wait(4.0)

        # --- momento: el error de arrastre, en formula -----------------------
        rot.mostrar(formula_pie(r"e_{ss} = v\,b\,/\,k_p"), zona="abajo")
        self.wait(4.0)

        rot.mostrar(pie_curso("Cinco grados por segundo de rampa: un "
                              "cuarto de grado de retraso. Fuera de "
                              "presupuesto."), zona="abajo")
        self.wait(4.6)

        # --- momento: la memoria integral funde el rezago a cero (pie ANTES) --
        self.play(FadeOut(flecha), FadeOut(tag), run_time=0.25)
        rot.mostrar(pie_curso("La memoria integral acumula ese error... "
                              "y lo funde a cero."), zona="abajo")
        alcanza = rampa_con_rezago(rezago=0.0, color_sis=C_OK)
        alcanza.move_to(rampa.get_center())
        self.play(ReplacementTransform(rampa, alcanza), run_time=0.9)
        self.wait(4.0)

        # --- momento: cierre narrativo -----------------------------------------
        rot.mostrar(pie_curso("Tipo 2: el perseguidor que sí alcanza."),
                    zona="abajo")
        self.wait(5.2)
