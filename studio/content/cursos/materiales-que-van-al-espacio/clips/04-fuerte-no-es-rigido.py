class Clip4(Scene):
    """4 - Fuerte no es lo mismo que rígido. La curva esfuerzo-deformación
    de un metal se recorre con un punto brillante hasta la rotura, tras
    abrir su zona elastica; despues se transforma en la del ceramico, que
    no avisa: recta empinada y corte seco con su X roja pulsando.
    (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo -------------------------------------------
        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Fuerte no es lo mismo que rígido")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.2)

        # --- momento: la curva del metal aparece ------------------------------
        curva = curva_esfuerzo("metal", ancho=4.6, alto=2.6)
        curva.move_to(np.array([0.0, -0.1, 0.0]))

        self.play(Create(curva.ejes), FadeIn(curva.etiquetas), run_time=0.5)
        self.play(Create(curva.curva), run_time=0.5)
        rot.mostrar(pie_curso("Estira un metal y dibuja su biografía: la "
                              "curva esfuerzo-deformación."), zona="abajo",
                   run_time=0.5)
        self.wait(5.1)

        # --- momento: la zona elastica, aqui todo es reversible -----------------
        rot.mostrar(pie_curso("La pendiente inicial es la rigidez: aquí "
                              "todo es reversible."), zona="abajo",
                   run_time=0.5)
        self.play(*curva.abrir_zona(), run_time=0.8)

        vt = ValueTracker(0.0)
        punto = punto_brillante(curva.punto_en(0.0), color=C_MAT,
                                radio=0.075)
        punto.add_updater(lambda m: m.move_to(curva.punto_en(vt.get_value())))
        self.play(FadeIn(punto), run_time=0.4)
        self.wait(3.9)

        # --- momento: pasado el codo, fluencia --------------------------------
        rot.mostrar(pie_curso("Pasado el límite elástico, la deformación "
                              "se queda: fluencia."), zona="abajo",
                   run_time=0.5)
        self.play(vt.animate.set_value(0.35), run_time=1.4)
        self.wait(3.7)

        # --- momento: la meseta ductil, el metal se queja -----------------------
        rot.mostrar(pie_curso("Y la meseta dúctil avisa antes de romper: "
                              "el metal se queja."), zona="abajo",
                   run_time=0.5)
        self.play(vt.animate.set_value(1.0), run_time=1.4)
        self.wait(3.7)

        punto.clear_updaters()
        self.play(FadeOut(punto), run_time=0.4)

        # --- momento: acto 2, el ceramico no avisa ------------------------------
        rot.mostrar(pie_curso("El cerámico no avisa: rígido, fuerte... y "
                              "de repente, nada."), zona="abajo",
                   run_time=0.5)
        self.wait(0.6)

        ceramico = curva_esfuerzo("ceramico", ancho=4.6, alto=2.6)
        ceramico.move_to(np.array([0.0, -0.1, 0.0]))
        self.play(ReplacementTransform(curva, ceramico), run_time=1.2)
        self.play(Indicate(ceramico.marca_falla, color=C_FALLA,
                           scale_factor=1.3), run_time=0.9)
        self.wait(2.4)

        # --- momento: cierre, tres virtudes distintas ---------------------------
        rot.mostrar(pie_curso("Rigidez, resistencia y ductilidad: tres "
                              "virtudes distintas. Nadie tiene las tres."),
                   zona="abajo", run_time=0.5)
        self.wait(5.1)
