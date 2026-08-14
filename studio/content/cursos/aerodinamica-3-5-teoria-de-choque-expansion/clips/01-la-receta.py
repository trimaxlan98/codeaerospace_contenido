class Clip1(Scene):
    """3.5.1 - Metodologia general de aplicacion.

    Toda la teoria de choque-expansion cabe en una regla: recorre el
    contorno cara a cara y, en cada vertice, mira el SIGNO del giro. Si el
    aire tiene que doblarse hacia dentro, choque; si hacia fuera, abanico.
    No hay mas decisiones. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La receta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        rot.mostrar(pie_curso("Ya tienes las dos herramientas: el choque "
                              "oblicuo y el abanico."), zona="abajo",
                    run_time=0.5)
        self.wait(1.2)

        # Las dos herramientas, lado a lado, con el signo del giro que las
        # dispara. Es literalmente el unico 'if' de toda la teoria.
        rampa = onda_oblicua(M_PERFIL, 12.0, largo=1.9, entrada=1.5)
        grupo_rampa = VGroup(rampa.pared, rampa.choque, rampa.flujo_entrada)
        grupo_rampa.move_to(LEFT * 3.4 + UP * 0.85)
        esquina = abanico_expansion(M_PERFIL, 12.0, n_lineas=6, largo=1.9,
                                    entrada=1.5)
        grupo_esquina = VGroup(esquina.pared, esquina.abanico,
                               esquina.flujo_entrada)
        grupo_esquina.move_to(RIGHT * 3.4 + UP * 0.85)

        rotulos = VGroup(
            VGroup(MathTex(r"\theta > 0", font_size=32, color=C_SUPER),
                   Text("hacia dentro: choque", font_size=20,
                        color=C_SUPER)).arrange(DOWN, buff=0.14),
            VGroup(MathTex(r"\theta < 0", font_size=32, color=C_CALCULO),
                   Text("hacia fuera: abanico", font_size=20,
                        color=C_CALCULO)).arrange(DOWN, buff=0.14))
        rotulos[0].next_to(grupo_rampa, DOWN, buff=0.40)
        rotulos[1].next_to(grupo_esquina, DOWN, buff=0.40)

        self.play(FadeIn(grupo_rampa), FadeIn(rotulos[0]), run_time=0.9)
        self.wait(3.4)
        rot.mostrar(pie_curso("Si la pared obliga al aire a doblarse hacia "
                              "dentro, choque."), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)

        self.play(FadeIn(grupo_esquina), FadeIn(rotulos[1]), run_time=0.9)
        rot.mostrar(pie_curso("Si le deja sitio para abrirse, abanico."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: la receta --------------------------------------------
        rot.mostrar(pie_curso("La teoría de choque-expansión no es más que "
                              "aplicar eso cara a cara."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Recorres el contorno, miras el signo del giro "
                              "en cada vértice, y encadenas."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("El resultado es EXACTO. No hay ninguna "
                              "aproximación en ninguno de los dos pasos."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
