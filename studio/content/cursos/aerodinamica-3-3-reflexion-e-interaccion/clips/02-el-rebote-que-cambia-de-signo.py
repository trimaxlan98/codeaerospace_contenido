class Clip2(Scene):
    """3.3.2 - Reflexion en una frontera libre: inversion de tipo de onda.

    Misma onda, otro contorno, resultado opuesto. En un borde libre lo que
    no puede cambiar es la PRESION, y como el choque la subio, el reflejo
    tiene que bajarla: sale un abanico. Ese cambio de signo es lo que hace
    los diamantes de Mach del clip 4. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El rebote que cambia de signo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        onda = reflexion_onda(tipo="libre", mach1=M_TUNEL, theta=THETA_TUNEL,
                              ancho=6.6, alto=2.5)
        onda.move_to(DOWN * 0.20)
        self.play(FadeIn(onda.contorno), run_time=0.6)
        rot.mostrar(pie_curso("Ahora la de abajo no es una pared: es el "
                              "borde de un chorro, con aire libre detrás."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        self.play(Create(onda.incidente), run_time=0.9)
        rot.mostrar(pie_curso("Llega el mismo choque y sube la presión."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        rot.mostrar(pie_curso("Pero un borde libre no puede sostener una "
                              "presión distinta de la de fuera."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: el reflejo tiene que deshacer lo hecho ---------------
        self.play(Create(onda.reflejada), run_time=1.0)
        rot.mostrar(pie_curso("Así que el reflejo tiene que bajarla otra "
                              "vez. Y eso no es un choque: es un abanico."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # Las dos presiones salen de la pieza: el producto vuelve a 1, que es
        # justo la condicion de contorno cumpliendose.
        cifras = VGroup(
            Text(f"tras el choque   p/p1 = {LIBRE['p2/p1']:.3f}",
                 font=FUENTE_HUD, font_size=18, color=C_SUPER),
            Text(f"tras el abanico  p/p1 = {LIBRE['p3/p1']:.3f}",
                 font=FUENTE_HUD, font_size=18,
                 color=C_SUB)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        cifras.next_to(onda, DOWN, buff=0.30)
        self.play(FadeIn(cifras, shift=0.10 * UP), run_time=0.7)
        rot.mostrar(pie_curso("La presión vuelve exactamente a la de fuera. "
                              "El contorno se ha salido con la suya."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Contra una pared, choque. Contra un borde "
                              "libre, expansión. La misma onda."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
