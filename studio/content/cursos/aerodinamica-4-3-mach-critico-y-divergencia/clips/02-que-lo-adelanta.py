class Clip2(Scene):
    """4.3.2 - Efecto del espesor relativo y del angulo de ataque.

    Mcr no es una constante del avion: es una consecuencia de lo que el
    perfil le hace al aire. Todo lo que aumente la succion —mas espesor, mas
    angulo— lo adelanta. Y de ahi salen las dos decisiones de diseño del
    resto del modulo. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Qué lo adelanta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        grafico = curva_mach_critico(cp0=CP0_DELGADO, ancho=5.0, alto=2.6)
        grafico.move_to(LEFT * 0.35 + DOWN * 0.40)
        self.play(FadeIn(grafico.ejes), Create(grafico.critica),
                  run_time=1.0)
        self.play(Create(grafico.perfil), FadeIn(grafico.cruce), run_time=1.0)
        cifra_fino = MathTex(rf"M_{{cr}} = {MCR_DELGADO:.3f}", font_size=30,
                             color=C_SUB)
        cifra_fino.next_to(grafico.ejes[1], UP, buff=0.28).shift(RIGHT * 1.5)
        self.play(FadeIn(cifra_fino), run_time=0.5)
        rot.mostrar(pie_curso("Un perfil fino, poco cargado: su succión es "
                              "modesta y el cruce cae tarde."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        # --- momento: engorda el perfil ------------------------------------
        # Se cruza con la version gruesa: misma curva critica, otra del
        # perfil. El cruce se mueve solo porque los numeros cambian.
        grueso = curva_mach_critico(cp0=CP0_GRUESO, ancho=5.0, alto=2.6)
        grueso.move_to(grafico.get_center())
        cifra_grueso = MathTex(rf"M_{{cr}} = {MCR_GRUESO:.3f}", font_size=30,
                               color=C_SUPER)
        cifra_grueso.next_to(grueso.ejes[1], UP, buff=0.28).shift(RIGHT * 1.5)

        rot.mostrar(pie_curso("Engorda el perfil, o tira de la palanca. La "
                              "succión sube."), zona="abajo", run_time=0.5)
        self.wait(1.2)
        self.play(ReplacementTransform(grafico.perfil, grueso.perfil),
                  ReplacementTransform(grafico.cruce, grueso.cruce),
                  ReplacementTransform(cifra_fino, cifra_grueso),
                  run_time=1.3)
        self.wait(3.4)

        rot.mostrar(pie_curso(f"Y el cruce se adelanta: de "
                              f"{MCR_DELGADO:.2f} a {MCR_GRUESO:.2f}."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Ocho centésimas de Mach. A once kilómetros, "
                              "son veinticuatro kilómetros por hora."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("De aquí salen las dos decisiones de diseño "
                              "del resto del módulo: adelgazar y barrer."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
