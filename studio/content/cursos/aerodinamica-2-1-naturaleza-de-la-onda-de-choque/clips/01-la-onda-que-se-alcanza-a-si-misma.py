class Clip1(Scene):
    """2.1.1 - Coalescencia de ondas de compresion.

    En el plano x-t no hay que explicar nada: cada pulso viaja sobre el gas
    que el anterior ya movio y calento, asi que va mas rapido, y rectas que
    se cierran acaban cortandose. Ahi nace el choque — no es un fenomeno
    aparte, es lo que le pasa al sonido cuando se comprime a si mismo.
    (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La onda que se alcanza a sí misma")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        xt = diagrama_xt(n_ondas=6, ancho=5.2, alto=2.9)
        xt.move_to(LEFT * 0.4 + DOWN * 0.30)
        self.play(FadeIn(xt.ejes), run_time=0.6)
        rot.mostrar(pie_curso("Un pistón que acelera despacio no manda una "
                              "onda: manda muchas, una tras otra."),
                    zona="abajo", run_time=0.5)
        self.wait(1.2)
        self.play(LaggedStart(*[Create(xt.caracteristica(i)) for i in range(6)],
                              lag_ratio=0.30), run_time=2.4)
        self.wait(2.6)

        rot.mostrar(pie_curso("Cada una viaja sobre el aire que la anterior "
                              "ya movió y calentó."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Así que va más rápido. Y en este plano eso "
                              "significa una recta menos inclinada."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: rectas que se cierran acaban cortandose --------------
        # El punto lo calcula la libreria del corte de las DOS primeras: es
        # el primero en ocurrir, y de ahi sale el frente.
        marca = Dot(xt.coalescencia(), radius=0.08, color=C_SUPER)
        tag = Text("aquí nace el choque", font_size=19, color=C_SUPER)
        tag.next_to(marca, RIGHT, buff=0.28)

        rot.mostrar(pie_curso("Rectas que se cierran acaban cortándose."),
                    zona="abajo", run_time=0.5)
        self.wait(1.0)
        self.play(FadeIn(marca, scale=1.8), FadeIn(tag, shift=0.1 * LEFT),
                  run_time=0.7)
        self.wait(3.6)

        self.play(Create(xt.choque), run_time=1.0)
        rot.mostrar(pie_curso("A partir de ahí las ondas ya no son varias: "
                              "son un único frente vertical."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Una onda de choque no es otro fenómeno. Es el "
                              "sonido comprimiéndose contra sí mismo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
