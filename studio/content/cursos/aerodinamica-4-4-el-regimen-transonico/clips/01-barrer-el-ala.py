class Clip1(Scene):
    """4.4.1 - Ala en flecha: fundamento del Mach normal efectivo.

    La solucion mas barata del transonico, y la primera que se encontro: si
    la compresibilidad solo la nota la componente PERPENDICULAR al borde de
    ataque, basta con inclinar el ala para que el perfil crea que vuela mas
    despacio. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Barrer el ala")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        recta = ala_flecha(M_CRUCERO, 0.0, envergadura=2.6, cuerda=1.3)
        recta.move_to(LEFT * 3.2 + UP * 0.35)
        self.play(FadeIn(recta.planta), run_time=0.7)
        self.play(FadeIn(recta.corriente), run_time=0.6)
        rot.mostrar(pie_curso(f"Un ala recta a Mach {M_CRUCERO:g}. El perfil "
                              f"ve los {M_CRUCERO:g} enteros."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: barrerla ---------------------------------------------
        barrida = ala_flecha(M_CRUCERO, FLECHA, envergadura=2.6, cuerda=1.3)
        barrida.move_to(RIGHT * 3.2 + UP * 0.35)
        self.play(FadeIn(barrida.planta), FadeIn(barrida.corriente),
                  run_time=0.9)
        rot.mostrar(pie_curso(f"Ahora la misma ala, barrida "
                              f"{FLECHA:g} grados."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

        self.play(FadeIn(barrida.componentes), run_time=0.9)
        rot.mostrar(pie_curso("La corriente se descompone: una parte cruza "
                              "el borde y otra lo recorre."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Y la compresibilidad solo la nota la que "
                              "cruza."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: la cuenta ---------------------------------------------
        # Las dos cifras salen de la pieza, que las saca de mach_normal_flecha.
        cuenta = MathTex(rf"M_\perp = M \cos\Lambda = {M_CRUCERO:g} \cdot "
                         rf"{barrida.datos['coseno']:.3f} = "
                         rf"{barrida.mach_normal():.3f}", font_size=36,
                         color=C_SUB)
        cuenta.move_to(DOWN * 1.85)
        self.play(FadeIn(cuenta, shift=0.12 * UP), run_time=0.8)
        rot.mostrar(pie_curso(f"El perfil cree que vuela a "
                              f"{barrida.mach_normal():.2f}. Y se comporta "
                              "como tal."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("El avión va a 0.85 y su ala vuela a 0.70. "
                              "Eso es toda la idea."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)
