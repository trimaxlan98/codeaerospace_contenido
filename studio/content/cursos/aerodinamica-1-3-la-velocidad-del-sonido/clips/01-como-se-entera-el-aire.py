class Clip1(Scene):
    """1.3.1 - Propagacion de una perturbacion infinitesimal.

    Antes de deducir nada: QUE es la velocidad del sonido. Un escalon de
    presion minusculo recorre el tubo, y delante de el el aire literalmente
    no sabe todavia que algo ha pasado. Esa frontera viaja a `a`. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Cómo se entera el aire")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # El tubo se pinta con el gris CLARO y no con el de mobiliario: la
        # mitad derecha —la que el frente aun no ha alcanzado— es justo lo
        # que hay que poder ver, y sobre negro el gris oscuro desaparece.
        pulso = pulso_conducto(0.12, largo=7.0, alto=1.3, salto=0.5,
                               color_tubo=C_TENUE)
        pulso.move_to(UP * 0.15)
        self.play(FadeIn(pulso.tubo), run_time=0.6)
        self.play(FadeIn(pulso.traza), FadeIn(pulso.rotulo),
                  FadeIn(pulso.frente), FadeIn(pulso.tenido), run_time=0.7)
        rot.mostrar(pie_curso("Empuja un pistón un milímetro. Esa "
                              "perturbación tiene que viajar."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- momento: hay un antes y un despues del frente -----------------
        rot.mostrar(pie_curso("Detrás del frente el aire ya está un poco más "
                              "apretado. Delante, aún no sabe nada."),
                    zona="abajo", run_time=0.5)
        self.wait(1.2)
        self.play(pulso.a_avance(0.55), run_time=1.8)
        self.wait(3.6)

        self.play(pulso.a_avance(0.93), run_time=1.6)
        rot.mostrar(pie_curso("La velocidad con la que avanza esa frontera "
                              "es la velocidad del sonido."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: por que tiene que ser infinitesimal ------------------
        rot.mostrar(pie_curso("Y es la del escalón diminuto: el aire apenas "
                              "cambia al pasar el frente."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Si el salto fuese grande, ya no sería sonido. "
                              "Sería una onda de choque."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Pero eso es el módulo 2."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)
