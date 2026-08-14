class Clip4(Scene):
    """4.3.4 - Numero de Mach de divergencia del arrastre (Mdd).

    Mcr avisa; Mdd cobra. Se define con un criterio operativo —la pendiente
    del arrastre— y se estima con la ecuacion de Korn, donde el espesor y la
    carga se pagan directamente en Mach. Cierre de la leccion. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El Mach que de verdad duele")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        curva = curva_arrastre_transonico(ancho=5.0, alto=2.6)
        curva.move_to(LEFT * 0.85 + DOWN * 0.40)
        self.play(FadeIn(curva.ejes), run_time=0.6)
        self.play(Create(curva.curva(0)), run_time=1.2)
        self.play(FadeIn(curva.etiquetas[0]), run_time=0.5)
        rot.mostrar(pie_curso("El arrastre de un perfil convencional al "
                              "subir el Mach. Plano, plano... y de repente "
                              "no."), zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("El Mach crítico ya ha pasado hace rato y "
                              "apenas se nota en la curva."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- momento: el criterio ------------------------------------------
        self.play(FadeIn(curva.marcas[0]), FadeIn(curva.marcas[1]),
                  run_time=0.7)
        rot.mostrar(formula_pie(r"\frac{d c_d}{dM} = 0.1", color=C_TRANS),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: la ecuacion de Korn -----------------------------------
        korn = MathTex(r"M_{dd} + \frac{c_l}{10} + \frac{t}{c} = \kappa",
                       font_size=40, color=C_CALCULO)
        korn.move_to(RIGHT * 4.0 + UP * 1.35)
        cuentas = VGroup(
            Text(f"convencional   {MDD_CONV:.2f}", font=FUENTE_HUD,
                 font_size=18, color=C_TRANS),
            Text(f"supercrítico   {MDD_SUPER:.2f}", font=FUENTE_HUD,
                 font_size=18, color=C_SUB)).arrange(
                     DOWN, aligned_edge=LEFT, buff=0.18)
        cuentas.next_to(korn, DOWN, buff=0.55)

        self.play(FadeIn(korn), run_time=0.8)
        rot.mostrar(pie_curso("Y se estima así. El espesor y la carga se "
                              "pagan directamente en Mach."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        self.play(Create(curva.curva(1)), FadeIn(curva.etiquetas[1]),
                  FadeIn(curva.marcas[2]), FadeIn(curva.marcas[3]),
                  run_time=1.2)
        self.play(FadeIn(cuentas, shift=0.10 * UP), run_time=0.7)
        rot.mostrar(pie_curso("Un perfil supercrítico cambia la constante, y "
                              "con ella toda la curva."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(curva, korn, cuentas)), run_time=0.8)
        cierre = VGroup(
            titulo_marca("El Mach crítico avisa.", font_size=36,
                         color=C_TITULO),
            titulo_marca("El de divergencia cobra.", font_size=36,
                         color=C_SUPER)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)
