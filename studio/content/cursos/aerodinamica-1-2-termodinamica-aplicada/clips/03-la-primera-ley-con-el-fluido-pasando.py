class Clip3(Scene):
    """1.2.3 - Primera ley para sistemas abiertos en regimen permanente.

    De la forma general (con calor y trabajo de eje) al caso que usa todo el
    curso: en un conducto no hay eje que gire ni tiempo para que el calor
    entre, y la entalpia total se queda quieta. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La primera ley, con el fluido pasando")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        vc = volumen_control()
        vc.move_to(DOWN * 0.25)

        # --- momento: la caja imaginaria ----------------------------------
        self.play(Create(vc.superficie), run_time=0.9)
        rot.mostrar(pie_curso("Dibuja una caja imaginaria y haz la cuenta de "
                              "lo que la cruza."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        self.play(FadeIn(vc.entrada, shift=0.2 * RIGHT),
                  FadeIn(vc.salida, shift=0.2 * RIGHT), run_time=0.9)
        rot.mostrar(pie_curso("En régimen permanente, lo que entra por 1 "
                              "sale por 2. Ni se acumula ni desaparece."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: la forma general ------------------------------------
        self.play(FadeIn(vc.calor, shift=0.2 * UP),
                  FadeIn(vc.trabajo, shift=0.2 * UP), run_time=0.8)
        rot.mostrar(formula_pie(r"q - w = \left(h_2 + \tfrac{V_2^2}{2}\right)"
                                r" - \left(h_1 + \tfrac{V_1^2}{2}\right)"),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: lo que se cae en un conducto -------------------------
        # El pie va ANTES de tachar: si los terminos desaparecen primero, el
        # espectador ve el resultado sin saber que hipotesis lo permite.
        rot.mostrar(pie_curso("Pero en una tobera no hay eje que gire, y el "
                              "aire pasa demasiado rápido para calentarse."),
                    zona="abajo", run_time=0.5)
        self.wait(1.4)
        self.play(FadeOut(vc.calor, shift=0.3 * DOWN),
                  FadeOut(vc.trabajo, shift=0.3 * UP), run_time=1.0)
        self.wait(3.4)

        rot.mostrar(formula_pie(r"h_1 + \frac{V_1^2}{2} = "
                                r"h_2 + \frac{V_2^2}{2} = h_0",
                                color=C_SUB), zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Esa suma tiene nombre: entalpía total. Es la "
                              "que no se mueve en todo el módulo 2."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
