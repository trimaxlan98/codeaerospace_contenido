class Clip1(Scene):
    """1.4.1 - Continuidad, cantidad de movimiento y energia en forma integral.

    Las tres cuentas son la misma idea repetida sobre tres magnitudes
    distintas: lo que hay dentro de la caja solo cambia por lo que cruza sus
    paredes. Aqui se enuncian sobre el volumen de control, sin hipotesis
    todavia — esas llegan en el clip 2. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Tres cuentas que siempre cuadran")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        vc = volumen_control(ancho=3.4, alto=2.0, con_calor=False,
                             con_trabajo=False)
        vc.move_to(UP * 0.55)
        self.play(Create(vc.superficie), run_time=0.9)
        self.play(FadeIn(vc.entrada, shift=0.2 * RIGHT),
                  FadeIn(vc.salida, shift=0.2 * RIGHT), run_time=0.8)
        rot.mostrar(pie_curso("Una caja imaginaria. Lo de dentro solo cambia "
                              "por lo que cruza sus paredes."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: las tres, una a una ---------------------------------
        # Los tres renglones se colocan de una vez y se encienden por turnos:
        # asi ninguno se mueve cuando entra el siguiente.
        filas = VGroup(
            VGroup(Text("masa", font_size=21, color=C_SUB),
                   MathTex(r"\dot m_1 = \dot m_2", font_size=34,
                           color=C_SUB)),
            VGroup(Text("cantidad de movimiento", font_size=21,
                        color=C_TRANS),
                   MathTex(r"\textstyle\sum F = \dot m\,(V_2 - V_1)",
                           font_size=34, color=C_TRANS)),
            VGroup(Text("energía", font_size=21, color=C_CALCULO),
                   MathTex(r"q - w = h_{0,2} - h_{0,1}", font_size=34,
                           color=C_CALCULO)))
        for fila in filas:
            fila.arrange(RIGHT, buff=0.45)
        filas.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        filas.move_to(DOWN * 1.85)
        # La columna de nombres se alinea a la derecha para que las tres
        # formulas arranquen en la misma x: en columnas desalineadas la
        # lectura se va detras del texto en vez de detras de las ecuaciones.
        x_formula = max(f[1].get_left()[0] for f in filas)
        for fila in filas:
            fila[1].shift(RIGHT * (x_formula - fila[1].get_left()[0]))
            fila[0].next_to(fila[1], LEFT, buff=0.45)

        for fila, pie in zip(filas, (
                "La masa que entra es la que sale. Ni una molécula de más.",
                "La fuerza sobre el aire es lo que le cambia la cantidad de "
                "movimiento.",
                "Y el calor y el trabajo le cambian la entalpía total.")):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(fila, shift=0.12 * UP), run_time=0.7)
            self.wait(4.8)

        rot.mostrar(pie_curso("Tres cuentas. Valen para cualquier flujo, "
                              "compresible o no."), zona="abajo",
                    run_time=0.5)
        self.wait(5.4)
