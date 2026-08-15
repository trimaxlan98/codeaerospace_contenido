class Clip1(Scene):
    """1.2.1 - Oersted, 1820: la corriente tuerce la brujula. El campo
    magnetico no sale del hilo: lo RODEA en circulos cerrados, y cae
    como 1/r.

    El hilo visto de frente (la corriente sale del papel); las brujulas
    se orientan tangentes —ninguna apunta al hilo— y los circulos de B,
    cada vez mas finos, hacen visible el 1/r. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La brújula que se tuerce")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el hilo de Oersted, visto de frente ------------------
        oersted = hilo_corriente(n_circulos=4, n_brujulas=6)
        oersted.move_to(DOWN * 0.2)
        rot.mostrar(pie_curso("Copenhague, 1820. Oersted enciende una "
                              "corriente y una brújula cercana se tuerce."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(oersted.hilo, scale=1.4), run_time=0.7)
        self.wait(4.4)

        # --- momento: las brujulas tangentes -------------------------------
        rot.mostrar(pie_curso("Rodea el hilo de brújulas: NINGUNA le "
                              "apunta. Todas se ponen de lado."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(oersted.brujulas, lag_ratio=0.12), run_time=1.2)
        self.wait(4.4)

        # --- momento: los circulos del campo -------------------------------
        rot.mostrar(pie_curso("El campo magnético no sale del hilo: lo "
                              "RODEA. Sus líneas son círculos cerrados."),
                    zona="abajo", run_time=0.5)
        self.play(Create(oersted.circulos, lag_ratio=0.25), run_time=1.8)
        self.wait(4.4)

        rot.mostrar(formula_pie(r"B = \frac{\mu_0\, I}{2\pi r}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: la cifra de Oersted ----------------------------------
        rot.mostrar(pie_curso("Un amperio, a un metro: dos "
                              "diezmillonésimas de tesla. Débil, pero real."),
                    zona="abajo", run_time=0.5)
        cifra = tag_hud(f"{B_HILO_1M * 1e7:.0f}e-7 T con "
                        f"{I_HILO:.0f} A a 1 m", font_size=16)
        cifra.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(cifra, shift=0.1 * DOWN), run_time=0.5)
        self.wait(4.4)

        rot.mostrar(pie_curso("Mira el trazo: cada círculo sale más fino. "
                              "El campo cae como 1/r al alejarse."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
