class Clip2(Scene):
    """2 - El lazo: percibir, razonar, actuar. El lazo_agente se dibuja
    centrado y gira tramo a tramo mientras el pie releva las tres fases;
    luego un giro rapido (vueltas=3) muestra que operar es repetir el
    ciclo miles de veces."""

    def construct(self):
        rot = Rotulos(self)

        # --- Titulo del clip ----------------------------------------------
        titulo = titulo_curso("El lazo: percibir, razonar, actuar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.0)

        # --- El lazo aparece -------------------------------------------------
        lazo = lazo_agente(radio=1.55,
                           etiquetas=("PERCIBIR", "RAZONAR", "ACTUAR"),
                           color=C_ACENTO, font_size=15)
        lazo.move_to(ORIGIN)
        self.play(Create(lazo), run_time=2.4)
        self.wait(1.0)

        self.play(LaggedStart(*[Indicate(nodo, color=C_ACENTO,
                                         scale_factor=1.12)
                               for nodo in lazo.nodos], lag_ratio=0.35),
                  run_time=2.0)
        self.wait(1.3)

        rot.mostrar(pie_curso("Un agente vive en un ciclo."), zona="abajo",
                   run_time=0.5)
        self.wait(3.0)

        # --- Tramo 1: percibir ------------------------------------------------
        rot.mostrar(pie_curso("Percibe el estado del mundo..."),
                   zona="abajo", run_time=0.5)
        self.play(girar_lazo(lazo, vueltas=0.34, run_time=1.3))
        self.wait(1.6)

        # --- Tramo 2: razonar --------------------------------------------------
        rot.mostrar(pie_curso("...decide el siguiente paso..."),
                   zona="abajo", run_time=0.5)
        self.play(girar_lazo(lazo, vueltas=0.34, run_time=1.3))
        self.wait(1.6)

        # --- Tramo 3: actuar, y vuelve a empezar ---------------------------------
        rot.mostrar(pie_curso("...y actúa. Y vuelve a empezar."),
                   zona="abajo", run_time=0.5)
        self.play(girar_lazo(lazo, vueltas=0.34, run_time=1.3))
        self.wait(2.6)

        # --- Acto 2: operar es repetir el lazo, muchas veces ----------------------
        rot.mostrar(pie_curso("Miles de vueltas por tarea: eso es operar."),
                   zona="abajo", run_time=0.5)
        self.play(girar_lazo(lazo, vueltas=3, run_time=2.2))
        self.wait(6.0)
