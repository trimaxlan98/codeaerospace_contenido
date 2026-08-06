class Clip1(Scene):
    """1 - Puede una maquina aprender. Portada del curso y una recta que
    se equivoca y se corrige, en tres pasos, hasta separar dos nubes de
    datos: la idea central de todo el curso en una sola imagen."""

    def construct(self):
        rot = Rotulos(self)

        # --- Portada del curso -----------------------------------------
        portada = VGroup(
            titulo_marca("Redes neuronales", font_size=46),
            Text("la máquina que aprende", font_size=25, color=C_ACENTO),
        ).arrange(DOWN, buff=0.26)
        portada.move_to(ORIGIN)

        self.play(Write(portada[0]), run_time=1.3)
        self.play(FadeIn(portada[1], shift=0.18 * UP), run_time=0.7)
        self.wait(1.8)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.play(FadeOut(portada, shift=0.5 * UP), run_time=0.8)

        # --- Titulo del clip ---------------------------------------------
        titulo = titulo_curso("¿Puede una máquina aprender?")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- Dos nubes de datos -------------------------------------------
        ejes = ejes_plano()
        self.play(Create(ejes), run_time=1.2)

        X, y = datos_dos_nubes(n=60, separacion=1.5, semilla=7)
        puntos = puntos_datos(ejes, X, y)
        self.play(FadeIn(puntos, lag_ratio=0.02), run_time=2.4)
        rot.mostrar(pie_curso("¿Cómo distinguirías estos dos grupos?"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- Una recta que se equivoca --------------------------------------
        recta = recta_modelo(ejes, m=0.3, b=1.7)
        self.play(Create(recta), run_time=1.0)
        self.wait(1.9)

        rot.mostrar(pie_curso("Una máquina aprende así: se equivoca y se "
                              "corrige."), zona="abajo", run_time=0.5)

        # --- ...y se corrige, en tres pasos -----------------------------------
        recta_media = recta_modelo(ejes, m=-0.4, b=0.3)
        self.play(Transform(recta, recta_media), run_time=1.2)
        self.wait(1.1)

        recta_buena = recta_modelo(ejes, m=-1.1, b=0.05)
        self.play(Transform(recta, recta_buena), run_time=1.2)
        self.wait(1.1)

        recta_final = recta_modelo(ejes, m=-1.35, b=-0.05)
        self.play(Transform(recta, recta_final), run_time=1.2)
        self.wait(1.9)

        # --- Destello de cierre -----------------------------------------------
        self.play(destello(recta, color=C_ACENTO, ancho=6, cola=0.4),
                  run_time=1.5)
        rot.mostrar(pie_curso("Ocho pasos para entender cómo lo hace."),
                    zona="abajo", run_time=0.5)
        self.wait(3.6)
