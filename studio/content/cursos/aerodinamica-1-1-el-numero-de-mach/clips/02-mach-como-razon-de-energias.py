class Clip2(Scene):
    """1.1.2 - Definicion fisica del numero de Mach como razon de energias.

    Arranca con la definicion de manual (M = V/a) y la desmonta: lo que M
    mide es cuanta energia ORDENADA de movimiento lleva el flujo frente a la
    energia DESORDENADA de agitacion termica que el aire ya tenia. La balanza
    sube de M en M hasta que el movimiento se come al calor. (~43 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Mach no es una velocidad")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la definicion de manual, y su insuficiencia ---------
        definicion = MathTex(r"M = \frac{V}{a}", font_size=64, color=C_TENUE)
        definicion.move_to(UP * 0.35)
        self.play(Write(definicion), run_time=1.0)
        rot.mostrar(pie_curso("El manual lo define así: velocidad entre "
                              "velocidad del sonido. ¿Pero qué mide?"),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: la balanza de energias ------------------------------
        balanza = balanza_energias(mach=0.30)
        balanza.move_to(DOWN * 0.30)
        self.play(FadeOut(definicion, shift=0.3 * UP), run_time=0.5)
        self.play(FadeIn(balanza), run_time=0.8)
        rot.mostrar(pie_curso("Esto: la energía del movimiento contra la "
                              "agitación térmica que el aire ya traía."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(formula_pie(r"\frac{V^2/2}{e} = "
                                r"\frac{\gamma(\gamma-1)}{2}\,M^2 = "
                                rf"{FACTOR_ENERGIAS:.2f}\,M^2"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: subir de Mach y ver quien manda ---------------------
        # Un solo pie cubre los dos primeros saltos: entra ANTES de las
        # animaciones que ilustra (la regla del curso) y las anuncia a las
        # dos, en vez de interrumpir la subida a mitad.
        # Los numeros del rotulo los escribe la propia balanza: barra y cifra
        # salen de la misma llamada y no pueden desincronizarse.
        rot.mostrar(pie_curso("A Mach 1 el movimiento aún es un cuarto del "
                              "calor. A Mach 2 ya se han igualado."),
                    zona="abajo", run_time=0.5)
        self.wait(1.3)
        self.play(balanza.a_mach(1.0), run_time=1.1)
        self.wait(2.6)
        self.play(balanza.a_mach(2.0), run_time=1.1)
        self.wait(3.0)

        rot.mostrar(pie_curso("A Mach 5 lo septuplica. Y toda esa energía "
                              "hay que ir frenándola."), zona="abajo",
                    run_time=0.5)
        self.wait(1.0)
        self.play(balanza.a_mach(5.0), run_time=1.2)
        self.wait(4.0)

        rot.mostrar(pie_curso("Por eso a Mach alto el aire no se aparta: "
                              "se calienta."), zona="abajo", run_time=0.5)
        self.wait(4.8)
