class Clip1(Scene):
    """3.3.1 - Reflexion regular en una pared solida.

    Una onda que llega a una pared no se refleja como un espejo: se refleja
    como lo exige la condicion de contorno. La pared impone que el flujo sea
    paralelo a ella, y como el primer choque lo torcio, hace falta un segundo
    que lo enderece. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El rebote contra la pared")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        onda = reflexion_onda(tipo="pared", mach1=M_TUNEL, theta=THETA_TUNEL,
                              ancho=6.6, alto=2.5)
        onda.move_to(DOWN * 0.20)
        self.play(FadeIn(onda.contorno), run_time=0.6)
        self.play(Create(onda.incidente), run_time=0.9)
        rot.mostrar(pie_curso(f"Un choque oblicuo dentro de un conducto, a "
                              f"Mach {M_TUNEL:g}."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

        # La marca cuelga del localizador de la pieza: si el dibujo se mueve,
        # el punto de impacto se mueve con el.
        impacto = Dot(onda.impacto(), radius=0.075, color=C_TRANS)
        self.play(FadeIn(impacto, scale=1.6), run_time=0.5)
        rot.mostrar(pie_curso("Al cruzarlo, el flujo queda torcido hacia "
                              "abajo. Y abajo hay una pared."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("La pared no admite que nada la atraviese: el "
                              "flujo tiene que volver a ser paralelo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: el segundo choque ------------------------------------
        self.play(Create(onda.reflejada), run_time=0.9)
        rot.mostrar(pie_curso("Así que hace falta otro choque, que lo "
                              "enderece."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: no es un espejo --------------------------------------
        # Los dos betas salen de la pieza; el segundo se calculo con el M2
        # que dejo el primero, no con M1.
        cifras = VGroup(
            Text(f"beta 1 = {REFLEJO['beta1']:.1f}", font=FUENTE_HUD,
                 font_size=18, color=C_SUPER),
            Text(f"beta 2 = {REFLEJO['beta2']:.1f}", font=FUENTE_HUD,
                 font_size=18, color=C_SUPER),
            Text(f"M: {REFLEJO['M1']:.2f} → {REFLEJO['M2']:.2f} → "
                 f"{REFLEJO['M3']:.2f}", font=FUENTE_HUD, font_size=18,
                 color=C_CALCULO)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        cifras.next_to(onda, DOWN, buff=0.30).align_to(onda, LEFT)
        self.play(FadeIn(cifras, shift=0.10 * UP), run_time=0.7)
        rot.mostrar(pie_curso("Y no rebota con el mismo ángulo: el segundo "
                              "choque lo ve todo con un Mach más bajo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Una onda no se refleja como la luz. Se "
                              "refleja como lo pide el contorno."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
