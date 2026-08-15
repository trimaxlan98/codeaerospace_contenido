class Clip1(Scene):
    """4.1.1 - El techo electrico: el Sol arranca electrones en la
    atmosfera alta y deja un perfil Ne(h) con tres capas, D/E/F. De
    noche la capa D desaparece entera — y con ella la absorcion que de
    dia se come la onda media. Abre el modulo 4. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El techo eléctrico")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el Sol como fuente (mencionado, no dibujado) --------
        rot.mostrar(pie_curso("El Sol golpea la atmósfera alta con "
                              "ultravioleta y arranca electrones: nace "
                              "un techo eléctrico sobre tu cabeza."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- momento: el perfil de dia --------------------------------------
        iono = capas_ionosfera()
        iono.move_to(DOWN * 0.15 + LEFT * 0.3)
        rot.mostrar(pie_curso("Este es el mapa: altura hacia arriba, "
                              "densidad de electrones hacia la derecha."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(iono.ejes), run_time=0.5)
        self.play(Create(iono.curva_dia), run_time=1.8)
        self.wait(4.6)

        # --- momento: las capas D, E, F --------------------------------------
        rot.mostrar(pie_curso("Tres capas: D abajo, E en medio, F "
                              "arriba, cada una un pico de ionización."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(iono.franjas, lag_ratio=0.2),
                  FadeIn(iono.etiquetas, lag_ratio=0.2), run_time=1.2)
        self.wait(4.6)

        # --- momento: cae la noche, la D desaparece ---------------------------
        rot.mostrar(pie_curso("Cae el Sol: el perfil de noche —fantasma "
                              "gris— se dibuja encima, y la capa D se "
                              "BORRA por completo."), zona="abajo",
                    run_time=0.5)
        self.play(Create(iono.curva_noche),
                  Circumscribe(iono.franjas[0], color=C_CALCULO,
                              buff=0.04, run_time=1.8),
                  run_time=1.8)
        self.wait(4.6)

        rot.mostrar(pie_curso("Sin Sol no hay electrones ahí abajo: esa "
                              "capa era la que absorbía la onda media. "
                              "Por eso de noche se oye más lejos."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Por debajo del techo hay una frecuencia "
                              "que manda. Vamos a medirla."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
