class Clip1(Scene):
    """3.1.1 - Descomposicion en componentes normal y tangencial.

    Un choque oblicuo parece un problema nuevo y no lo es. Basta con mirar la
    velocidad en los ejes de la ONDA en vez de en los del tunel: una
    componente la atraviesa de frente y la otra la recorre de lado.
    (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El mismo choque, de lado")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        onda = onda_oblicua(M_RAMPA, THETA_RAMPA, largo=3.4, entrada=2.6)
        onda.move_to(DOWN * 0.55)
        self.play(Create(onda.pared), run_time=0.9)
        self.play(FadeIn(onda.flujo_entrada, shift=0.2 * RIGHT), run_time=0.7)
        rot.mostrar(pie_curso(f"Corriente a Mach {M_RAMPA:g} contra una rampa "
                              f"de {THETA_RAMPA:g} grados."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        self.play(Create(onda.choque), run_time=0.8)
        self.play(FadeIn(onda.flujo_salida, shift=0.2 * RIGHT), run_time=0.6)
        # El rotulo cuelga del localizador de la pieza: si el dibujo se
        # mueve, la etiqueta de beta se mueve con su onda.
        tag_beta = MathTex(rf"\beta = {onda.beta():.1f}^\circ", font_size=32,
                           color=C_SUPER)
        # Cerca de la esquina y a la IZQUIERDA de la onda: arriba, donde la
        # onda es mas larga, es justo donde luego se dibujan los vectores.
        tag_beta.move_to(onda.sobre_onda(0.28) + LEFT * 0.92)
        self.play(FadeIn(tag_beta), run_time=0.5)
        rot.mostrar(pie_curso("Sale una onda inclinada, y el flujo la cruza "
                              "sin pararse: sigue supersónico."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: cambiar de ejes --------------------------------------
        rot.mostrar(pie_curso("Parece un problema nuevo. No lo es."),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        self.play(FadeOut(VGroup(onda.flujo_entrada, onda.flujo_salida)),
                  run_time=0.5)
        self.play(FadeIn(onda.vectores[0]), run_time=0.9)
        rot.mostrar(pie_curso("Mira la velocidad en los ejes de la ONDA: una "
                              "parte la cruza de frente y otra la recorre de "
                              "lado."), zona="abajo", run_time=0.5)
        self.wait(5.4)

        self.play(FadeIn(onda.vectores[1]), run_time=0.9)
        rot.mostrar(pie_curso("Al otro lado, la que iba de lado sigue igual. "
                              "Solo cambió la que cruzaba."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Y eso convierte un choque oblicuo en uno "
                              "normal disfrazado."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
