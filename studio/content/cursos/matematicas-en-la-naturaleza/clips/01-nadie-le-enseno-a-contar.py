class Clip1(Scene):
    """1 - Nadie le enseño a contar. Portada del curso; el girasol nace
    semilla a semilla, brotan sus dos familias de espirales y los numeros
    de Fibonacci cruzan la base con 21 y 34 encendidos. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: portada del curso ----------------------------------
        portada = VGroup(
            titulo_marca("Matemáticas en la naturaleza", font_size=44),
            Text("el código que crece", font_size=24, color=C_CONSTANTE),
        ).arrange(DOWN, buff=0.26)
        portada.move_to(ORIGIN)

        self.play(Write(portada[0]), run_time=1.3)
        self.play(FadeIn(portada[1], shift=0.18 * UP), run_time=0.7)
        self.wait(2.4)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.play(FadeOut(portada, shift=0.5 * UP), run_time=0.7)

        titulo = titulo_curso("Nadie le enseñó a contar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: el girasol nace semilla a semilla -------------------
        rot.mostrar(pie_curso("Un girasol acomoda sus semillas una a una, "
                              "siempre con el mismo giro."), zona="abajo",
                    run_time=0.5)
        disco = filotaxis(N_SEMILLAS, escala=2.15).move_to(UP * 0.35)
        self.play(disco.aparecer(run_time=4.6))
        self.wait(1.4)

        # --- momento: las espirales que brotan ----------------------------
        rot.mostrar(pie_curso("Y de ese giro brotan espirales: 21 hacia un "
                              "lado, 34 hacia el otro."), zona="abajo",
                    run_time=0.5)
        p21 = disco.parastica(PARASTICAS[0], color=C_CONSTANTE)
        p34 = disco.parastica(PARASTICAS[1], color=C_ACENTO)
        self.play(Create(p21), run_time=1.3)
        self.play(Create(p34), run_time=1.3)
        self.wait(3.6)

        # --- momento: los numeros que se persiguen ------------------------
        fila = VGroup(*[Text(str(f), font=FUENTE_HUD, font_size=23,
                             color=C_TENUE) for f in FIB[:10]])
        fila.arrange(RIGHT, buff=0.40).move_to(DOWN * 2.45)
        self.play(LaggedStart(*[FadeIn(t, shift=0.12 * UP) for t in fila],
                              lag_ratio=0.08), run_time=1.2)
        idx21, idx34 = FIB.index(21), FIB.index(34)
        self.play(fila[idx21].animate.set_color(C_CONSTANTE).scale(1.25),
                  fila[idx34].animate.set_color(C_ACENTO).scale(1.25),
                  run_time=0.8)
        self.wait(1.6)

        # --- momento: la promesa del curso --------------------------------
        rot.mostrar(pie_curso("Números que se persiguen en toda planta. Ese "
                              "código es este curso."), zona="abajo",
                    run_time=0.5)
        self.wait(6.6)
