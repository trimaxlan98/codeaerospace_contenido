class Clip2(Scene):
    """2.3.2 - Formula de Rayleigh para Pitot supersonico.

    En supersonico el Pitot deja de medir lo que cree: delante de su boca se
    planta un choque desprendido, y lo que llega al manometro es la presion
    de estancamiento de DETRAS del choque, ya degradada. La formula de
    Rayleigh mete el choque en la cuenta. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El Pitot supersónico")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        flujo = remanso(radio=0.55, n_lineas=5, separacion=0.34, largo=2.4)
        flujo.move_to(LEFT * 2.4 + UP * 0.60)
        self.play(FadeIn(flujo), run_time=0.7)
        rot.mostrar(pie_curso(f"Ahora el mismo tubo, pero a Mach "
                              f"{M_SUPER:g}."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: el choque desprendido --------------------------------
        # Arco por delante del morro: un choque desprendido es curvo y no
        # toca el cuerpo. En el eje se comporta como un choque NORMAL, y por
        # eso valen las relaciones de la leccion 2.2.
        centro = flujo.centro_cuerpo()
        arco = Arc(radius=1.05, start_angle=PI - 0.95, angle=1.90,
                   arc_center=centro + RIGHT * 0.30, color=C_SUPER,
                   stroke_width=3.6)
        tag_arco = Text("choque desprendido", font_size=18, color=C_SUPER)
        tag_arco.next_to(arco, DOWN, buff=0.30)

        self.play(Create(arco), run_time=0.8)
        self.play(FadeIn(tag_arco), run_time=0.5)
        rot.mostrar(pie_curso("Delante de la boca se planta un choque. El "
                              "aire ya no llega como salió."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Justo en el eje, ese choque es normal: valen "
                              "las relaciones de la lección anterior."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: cuanto se equivocaria un Pitot ingenuo ---------------
        # Los dos numeros salen de la libreria; su cociente es el error.
        comparacion = VGroup(
            VGroup(Text("sin choque", font_size=19, color=C_TENUE),
                   Text(f"{ISENTROPICO:.3f}", font=FUENTE_HUD, font_size=27,
                        color=C_TENUE)).arrange(DOWN, buff=0.14),
            VGroup(Text("de verdad", font_size=19, color=C_SUPER),
                   Text(f"{RAYLEIGH:.3f}", font=FUENTE_HUD, font_size=27,
                        color=C_SUPER)).arrange(DOWN, buff=0.14))
        comparacion.arrange(DOWN, buff=0.55).move_to(RIGHT * 3.4 + UP * 0.55)

        self.play(FadeIn(comparacion, shift=0.12 * UP), run_time=0.9)
        rot.mostrar(pie_curso("Un Pitot que ignorase el choque leería "
                              f"{ISENTROPICO:.2f} veces la presión de "
                              "fuera."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso(f"Lee {RAYLEIGH:.2f}. Un "
                              f"{(1 - RAYLEIGH / ISENTROPICO) * 100:.0f} % "
                              "menos, y la diferencia se la comió el "
                              "choque."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Por eso a partir de Mach 1 se usa Rayleigh, y "
                              "no la isentrópica."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
