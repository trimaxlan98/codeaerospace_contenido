class Clip2(Scene):
    """1.3.2 - El espejo magnetico: donde las lineas se aprietan, la
    espiral se frena y rebota. Dos espejos enfrentados hacen una botella
    y la particula queda presa. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Atrapados en el campo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el tubo de campo que se aprieta ---------------------
        esp = espejo_magnetico()
        esp.scale(1.45)
        esp.move_to(DOWN * 0.25)
        rot.mostrar(pie_curso("Dos bobinas aprietan las líneas en los "
                              "extremos: allí el campo es más fuerte."),
                    zona="abajo", run_time=0.5)
        self.play(Create(esp.lineas, lag_ratio=0.15), run_time=1.6)
        self.play(FadeIn(esp.bobinas), run_time=0.5)
        self.wait(4.4)

        # --- momento: la espiral atada a la linea -------------------------
        rot.mostrar(pie_curso("La partícula gira atada a una línea y "
                              "avanza hacia el estrechamiento."),
                    zona="abajo", run_time=0.5)
        esp.trayectoria.set_stroke(opacity=0.32)
        self.play(Create(esp.trayectoria), run_time=2.2)
        self.wait(2.6)

        # --- momento: el rebote ------------------------------------------
        rot.mostrar(pie_curso("Donde las líneas se juntan, el avance se "
                              "frena… hasta REBOTAR: un espejo."),
                    zona="abajo", run_time=0.5)
        # El arranque sale de la propia curva (punto_en no sigue al
        # escalado; get_start si).
        particula = Dot(esp.trayectoria.get_start(), radius=0.09,
                        color=C_CARGA)
        self.play(FadeIn(particula, scale=1.6), run_time=0.4)
        self.play(MoveAlongPath(particula, esp.trayectoria),
                  run_time=7.0, rate_func=linear)
        self.wait(0.6)

        # --- momento: la botella -----------------------------------------
        rot.mostrar(pie_curso("Entre dos espejos, la partícula queda "
                              "presa: una botella magnética."),
                    zona="abajo", run_time=0.5)
        self.play(MoveAlongPath(particula, esp.trayectoria),
                  run_time=4.8, rate_func=linear)

        rot.mostrar(pie_curso("El campo de la Tierra hace esto mismo con "
                              "las partículas que escupe el Sol."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Botellas llenas a escala planetaria: los "
                              "cinturones. Vamos a verlos."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
