class Clip1(Scene):
    """1 - Un cerebro en una caja. Portada del curso; un LLM (bloque cian)
    que solo produce burbujas de pensamiento que se relevan encima suyo,
    y un "mundo" de 3 mini-cajas violeta al otro lado de una linea
    punteada que no puede cruzar. Gancho: ¿y si le damos manos?"""

    def construct(self):
        rot = Rotulos(self)

        # --- Portada del curso -----------------------------------------
        portada = VGroup(
            titulo_marca("Agentes de IA", font_size=46),
            Text("máquinas que operan el mundo", font_size=25,
                 color=C_ACENTO),
        ).arrange(DOWN, buff=0.26)
        portada.move_to(ORIGIN)

        self.play(Write(portada[0]), run_time=1.3)
        self.play(FadeIn(portada[1], shift=0.18 * UP), run_time=0.7)
        self.wait(2.0)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.play(FadeOut(portada, shift=0.5 * UP), run_time=0.7)

        titulo = titulo_curso("Un cerebro en una caja")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.0)

        # --- El LLM: una caja que solo escribe --------------------------
        llm = bloque("LLM", ancho=2.6, alto=1.3, color=C_AGENTE,
                     tamano=28)
        llm.move_to(LEFT * 2.8)
        self.play(FadeIn(llm, scale=0.9), run_time=0.9)
        self.wait(1.4)

        pensamiento_1 = burbuja("el satélite pasa a las 14:32",
                                tipo="pensamiento", ancho_max=3.0,
                                font_size=16)
        pensamiento_1.next_to(llm, UP, buff=0.32)
        self.play(FadeIn(pensamiento_1, shift=0.15 * UP), run_time=0.5)
        self.wait(1.4)
        self.play(FadeOut(pensamiento_1), run_time=0.4)

        pensamiento_2 = burbuja("convendría grabar el pase",
                                tipo="pensamiento", ancho_max=3.0,
                                font_size=16)
        pensamiento_2.next_to(llm, UP, buff=0.32)
        self.play(FadeIn(pensamiento_2, shift=0.15 * UP), run_time=0.5)
        self.wait(1.4)
        self.play(FadeOut(pensamiento_2), run_time=0.4)

        rot.mostrar(pie_curso("Un LLM solo hace una cosa: escribir."),
                   zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- El mundo, inalcanzable --------------------------------------
        mundo = catalogo_herramientas(["correo", "archivos", "web"],
                                      columnas=3, ancho=1.25, alto=0.55,
                                      color=C_MUNDO, font_size=14)
        if mundo.width > 3.6:
            mundo.scale_to_fit_width(3.6)
        mundo.move_to(RIGHT * 2.6)
        self.play(FadeIn(mundo, lag_ratio=0.15, shift=0.15 * RIGHT),
                  run_time=1.0)
        self.wait(1.2)

        linea = DashedLine(np.array([-0.1, 2.2, 0.0]),
                           np.array([-0.1, -2.2, 0.0]), color=C_EJE,
                           dash_length=0.15, stroke_width=2.5)
        self.play(Create(linea), run_time=1.0)
        rot.mostrar(pie_curso("Puede describir el mundo... pero no "
                              "tocarlo."), zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- La linea pulsa: la frontera es real -------------------------
        self.play(linea.animate(rate_func=there_and_back).set_stroke(
            opacity=0.3), run_time=1.1)
        self.wait(1.2)

        # --- Gancho -------------------------------------------------------
        rot.mostrar(pie_curso("¿Y si le damos manos?"), zona="abajo",
                   run_time=0.5)
        self.wait(4.2)
