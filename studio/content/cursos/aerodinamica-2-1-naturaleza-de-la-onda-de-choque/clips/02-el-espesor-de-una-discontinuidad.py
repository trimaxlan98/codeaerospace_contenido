class Clip2(Scene):
    """2.1.2 - Espesor real de la onda y validez del modelo de discontinuidad.

    El choque se dibuja como una raya porque a escala de vehiculo lo es,
    pero tiene grosor: unas doscientas milmillonesimas de metro, unos pocos
    recorridos libres medios. Ese es exactamente el argumento que permite
    tratarlo como discontinuidad sin remordimientos. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El espesor de una discontinuidad")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        perfil = perfil_choque(salto=SALTO["p2/p1"], ancho=5.6, alto=2.5,
                               etiqueta=f"{ESPESOR_NM:.0f} nm")
        perfil.move_to(DOWN * 0.10)
        self.play(FadeIn(perfil.ejes), run_time=0.6)
        self.play(Create(perfil.curva), run_time=1.6)
        rot.mostrar(pie_curso("Al cruzar un choque, la presión no sube: "
                              "salta."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # El salto que se dibuja es el del choque de referencia del modulo,
        # calculado por la libreria: no es un escalon decorativo.
        rot.mostrar(pie_curso(f"A Mach {M_CHOQUE:g}, por "
                              f"{SALTO['p2/p1']:.1f}. De golpe."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: de golpe, pero ¿en cuanto espacio? ------------------
        self.play(FadeIn(perfil.escala, shift=0.12 * UP), run_time=0.8)
        rot.mostrar(pie_curso("«De golpe» tiene una medida. Y es esta."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso(f"Unos {ESPESOR_NM:.0f} nanómetros: la "
                              "diezmilésima parte del grosor de un pelo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso(f"Apenas {GROSORES:.0f} recorridos libres "
                              "medios. Lo que tarda una molécula en chocar "
                              "tres veces."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Por eso vale tratarlo como una superficie sin "
                              "grosor: al lado de un ala, lo es."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
