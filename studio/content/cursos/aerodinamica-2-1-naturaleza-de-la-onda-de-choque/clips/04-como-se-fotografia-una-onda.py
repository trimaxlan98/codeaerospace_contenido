class Clip4(Scene):
    """2.1.4 - Visualizacion experimental: tecnicas Schlieren y sombra.

    El aire es transparente, asi que una onda de choque no se ve — pero se
    fotografia. El truco es que donde la densidad cambia de golpe el indice
    de refraccion tambien, y el rayo que la cruza sale desviado. Una
    cuchilla corta justo esos rayos y la onda aparece. Cierre de la leccion.
    (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Cómo se fotografía una onda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        banco = esquema_schlieren(n_rayos=9, ancho=8.2, alto=2.6,
                                  desviados=(3, 4))
        banco.move_to(DOWN * 0.15)

        self.play(FadeIn(banco.seccion), FadeIn(banco.pantalla), run_time=0.7)
        rot.mostrar(pie_curso("El aire es transparente. Una onda de choque "
                              "no se ve."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        self.play(LaggedStart(*[Create(r) for r in banco.rayos],
                              lag_ratio=0.10), run_time=1.6)
        rot.mostrar(pie_curso("Atraviésala con luz paralela y sigue sin "
                              "verse: casi todos los rayos pasan de largo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- momento: donde la densidad salta, la luz se dobla -------------
        self.play(Create(banco.onda), run_time=0.7)
        rot.mostrar(pie_curso("Casi todos. Donde la densidad salta, el "
                              "índice de refracción salta con ella."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Y esos pocos rayos salen torcidos."),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        # --- momento: la cuchilla ------------------------------------------
        self.play(FadeIn(banco.cuchilla, shift=0.2 * UP), run_time=0.7)
        rot.mostrar(pie_curso("Pon una cuchilla justo donde caen los "
                              "torcidos."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        self.play(FadeIn(banco.banda, scale=1.2), run_time=0.7)
        rot.mostrar(pie_curso("En la pantalla falta su luz. Y esa franja "
                              "oscura es la onda."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("No estás viendo el choque. Estás viendo el "
                              "hueco que deja."), zona="abajo", run_time=0.5)
        self.wait(5.0)
