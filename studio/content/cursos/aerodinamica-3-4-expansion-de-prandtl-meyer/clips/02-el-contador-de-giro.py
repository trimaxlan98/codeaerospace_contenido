class Clip2(Scene):
    """3.4.2 - Funcion de Prandtl-Meyer nu(M) y su tabulacion.

    nu no es un angulo del dibujo: es un contador. Dice cuanto ha tenido que
    girar un flujo, desde Mach 1, para llegar a su Mach. Y por eso una
    expansion se resuelve SUMANDO, sin resolver nada. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El contador de giro")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        curva = curva_nu(m_max=6.0, ancho=5.2, alto=2.7)
        curva.move_to(LEFT * 0.25 + DOWN * 0.35)
        self.play(FadeIn(curva.ejes), run_time=0.6)
        self.play(Create(curva.curva), run_time=1.8)
        rot.mostrar(pie_curso("Cuánto ha tenido que girar el flujo, desde "
                              "Mach 1, para llegar a cada Mach."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # Los puntos y sus cifras salen de la misma funcion que traza la
        # curva: si el trazo estuviese mal, los puntos no caerian encima.
        marcas = VGroup()
        for m in MACHS_NU:
            punto = Dot(curva.punto_de(m), radius=0.065, color=C_TRANS)
            cifra = Text(f"{curva.nu(m):.1f}", font=FUENTE_HUD, font_size=16,
                         color=C_TRANS)
            # Arriba y a la IZQUIERDA: abajo el punto de Mach 1.5 se monta
            # sobre la marca del eje, y arriba-derecha la propia curva —que
            # sube— le pasa por encima al rotulo. A la izquierda de cada
            # punto la curva ya ha quedado por debajo.
            cifra.next_to(punto, UL, buff=0.10)
            marcas.add(VGroup(punto, cifra))
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in marcas],
                              lag_ratio=0.3), run_time=1.4)
        rot.mostrar(pie_curso(f"A Mach 2, {prandtl_meyer(2.0):.2f} grados. A "
                              f"Mach 3, {prandtl_meyer(3.0):.2f}."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: por eso se suma --------------------------------------
        rot.mostrar(formula_pie(r"\nu_2 = \nu_1 + \theta"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Gira la pared quince grados y súmalos al "
                              "contador. Ya está resuelto."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: el tope -----------------------------------------------
        self.play(Create(curva.asintota), FadeIn(curva.etiquetas),
                  run_time=0.8)
        rot.mostrar(pie_curso(f"Y hay un tope: {NU_TOPE:.1f} grados. Más allá "
                              "no queda nada que expandir."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)
