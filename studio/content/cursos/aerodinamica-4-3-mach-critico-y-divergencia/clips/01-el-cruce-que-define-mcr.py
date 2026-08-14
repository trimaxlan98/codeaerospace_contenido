class Clip1(Scene):
    """4.3.1 - Definicion de Mcr y su determinacion grafica.

    Dos curvas y un corte. Una es del PERFIL (su succion, que crece al subir
    el Mach) y la otra es del AIRE (la succion que hace falta para llegar a
    Mach 1 local, que decrece). Donde se cruzan, el perfil tiene su primer
    punto sonico. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El cruce que define Mcr")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        grafico = curva_mach_critico(cp0=CP0_GRUESO, ancho=5.2, alto=2.7)
        grafico.move_to(LEFT * 0.35 + DOWN * 0.35)
        self.play(FadeIn(grafico.ejes), run_time=0.6)

        self.play(Create(grafico.perfil), run_time=1.1)
        self.play(FadeIn(grafico.etiquetas[0]), run_time=0.5)
        rot.mostrar(pie_curso("La succión del perfil, corregida por "
                              "compresibilidad. Crece con el Mach de "
                              "vuelo."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        self.play(Create(grafico.critica), run_time=1.1)
        self.play(FadeIn(grafico.etiquetas[1]), run_time=0.5)
        rot.mostrar(pie_curso("Y la succión que haría falta para que ahí el "
                              "aire llegara justo a Mach 1."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Esta segunda no depende del perfil. Es una "
                              "propiedad del aire."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: el cruce ---------------------------------------------
        # Mcr sale de la libreria; el punto cae sobre las dos curvas porque
        # es donde de verdad se cortan, no donde se ha dibujado.
        self.play(FadeIn(grafico.cruce), run_time=0.8)
        # Encima del grafico y no pegada al cruce: ahi mismo pasan la curva
        # del perfil y su propio rotulo.
        cifra = MathTex(rf"M_{{cr}} = {grafico.mcr():.3f}", font_size=34,
                        color=C_TRANS)
        cifra.next_to(grafico.ejes[1], UP, buff=0.30).shift(RIGHT * 1.6)
        self.play(FadeIn(cifra), run_time=0.5)
        rot.mostrar(pie_curso("Donde se cruzan, el perfil tiene su primer "
                              "punto a Mach 1."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Ese es el Mach crítico. Y el avión todavía "
                              "vuela muy por debajo de la velocidad del "
                              "sonido."), zona="abajo", run_time=0.5)
        self.wait(5.4)
