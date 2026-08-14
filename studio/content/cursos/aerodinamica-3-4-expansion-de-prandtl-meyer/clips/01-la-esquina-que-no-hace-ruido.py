class Clip1(Scene):
    """3.4.1 - Abanico de expansion centrado e isentropico.

    Una esquina que se abre no produce un choque: produce un abanico. Y la
    diferencia no es cosmetica — el abanico es un continuo de infinitas
    ondas de Mach, cada una infinitamente debil, asi que no genera entropia.
    Girar hacia fuera es gratis. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La esquina que no hace ruido")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        abanico = abanico_expansion(M_ESQUINA, THETA_ESQUINA, n_lineas=9,
                                    largo=3.0, entrada=2.6)
        abanico.move_to(DOWN * 0.15)
        self.play(Create(abanico.pared), run_time=0.9)
        self.play(FadeIn(abanico.flujo_entrada, shift=0.2 * RIGHT),
                  run_time=0.7)
        rot.mostrar(pie_curso(f"Mach {M_ESQUINA:g} y una esquina que se "
                              f"abre {THETA_ESQUINA:g} grados. Al revés que "
                              "la rampa."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        # Primera y ultima linea, que son las que definen el abanico; las de
        # en medio entran despues, y esa secuencia ES el mensaje.
        self.play(Create(abanico.linea(0)), run_time=0.6)
        rot.mostrar(pie_curso("La primera onda sale al ángulo de Mach de la "
                              "corriente que llega."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        self.play(Create(abanico.linea(-1)), run_time=0.6)
        rot.mostrar(pie_curso("La última, al de la corriente que sale, que "
                              "ya va más rápida."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        self.play(LaggedStart(*[Create(abanico.linea(i)) for i in range(1, 8)],
                              lag_ratio=0.18), run_time=1.6)
        self.play(FadeIn(abanico.flujo_salida, shift=0.2 * RIGHT),
                  run_time=0.6)
        rot.mostrar(pie_curso("Y entre las dos, todas las demás. No una "
                              "onda: infinitas."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Cada una infinitamente débil, así que ninguna "
                              "genera entropía."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Comprimir cuesta. Expandir, no."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
