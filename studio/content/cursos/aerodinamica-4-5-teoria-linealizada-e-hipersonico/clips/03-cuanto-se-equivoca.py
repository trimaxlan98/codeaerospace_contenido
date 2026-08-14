class Clip3(Scene):
    """4.5.3 - Comparacion con la teoria exacta de choque-expansion.

    El momento en que el modulo 4 se mide contra el modulo 3. La linealizada
    acierta muy bien a angulos pequeños y se separa al crecer alfa — y la
    separacion no se supone: se calcula punto a punto con las dos teorias.
    (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Cuánto se equivoca")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        comp = comparacion_teorias(mach=M_LINEAL, ancho=5.0, alto=2.6)
        comp.move_to(LEFT * 0.75 + DOWN * 0.40)
        self.play(FadeIn(comp.ejes), run_time=0.6)
        self.play(Create(comp.exacta), run_time=1.2)
        self.play(FadeIn(comp.etiquetas[0]), run_time=0.5)
        rot.mostrar(pie_curso(f"La placa plana a Mach {M_LINEAL:g}, resuelta "
                              "con choque-expansión. Exacta."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        self.play(Create(comp.lineal), run_time=1.2)
        self.play(FadeIn(comp.etiquetas[1]), run_time=0.5)
        rot.mostrar(pie_curso("Y encima, Ackeret. Una recta, porque cl es "
                              "proporcional a alfa."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: los errores, medidos ----------------------------------
        # Cada cifra es |lineal/exacto - 1| calculado por la pieza con las
        # DOS teorias: no es una estimacion.
        marcas = VGroup()
        for alfa, color in ((5.0, C_SUB), (15.0, C_SUPER)):
            punto = Dot(comp.punto_exacto(alfa), radius=0.07, color=color)
            cifra = Text(f"{comp.error(alfa) * 100:.1f} %", font=FUENTE_HUD,
                         font_size=18, color=color)
            cifra.next_to(punto, UL, buff=0.12)
            marcas.add(VGroup(punto, cifra))
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in marcas],
                              lag_ratio=0.4), run_time=1.2)

        rot.mostrar(pie_curso(f"A cinco grados se equivoca un "
                              f"{comp.error(5.0) * 100:.1f} %. Nadie va a "
                              "notarlo."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso(f"A quince, un {comp.error(15.0) * 100:.1f} %. "
                              "Y ahí ya conviene la exacta."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Una teoría aproximada no es una teoría peor. "
                              "Es una teoría con un rango."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)
