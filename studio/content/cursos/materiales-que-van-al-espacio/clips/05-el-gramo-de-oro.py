class Clip5(Scene):
    """5 - El gramo que cuesta oro: la resistencia especifica sigma/rho y
    el mapa de Ashby. Las burbujas de las cuatro familias se acomodan por
    barrios; COMPUESTOS, arriba a la izquierda, es el barrio dorado: fuerte
    y ligero. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ------------------------------------------------
        modulo = hud_modulo("Modulo 05")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("El gramo que cuesta oro")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(1.0)

        # --- momento: gana el mas fuerte por gramo ------------------------
        rot.mostrar(pie_curso("Poner un kilo en órbita cuesta miles de "
                              "dólares: aquí no gana el más fuerte, gana "
                              "el más fuerte POR GRAMO."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(formula_pie(r"\sigma_{esp} = \sigma_y / \rho"),
                    zona="abajo", run_time=0.6)
        self.wait(4.6)

        # --- momento: el mapa de Ashby -------------------------------------
        mapa = mapa_ashby()
        mapa.move_to(np.array([0.0, -0.15, 0.0]))

        rot.mostrar(pie_curso("El mapa de Ashby: densidad contra "
                              "resistencia. Cada familia, su barrio."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(mapa.ejes), FadeIn(mapa.etiquetas), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(b) for b in mapa.grupo_burbujas],
                              lag_ratio=0.35), run_time=1.3)
        self.wait(2.6)

        # --- momento: las diagonales de empate ------------------------------
        rot.mostrar(pie_curso("Las diagonales son líneas de empate: "
                              "misma resistencia por kilo."), zona="abajo",
                    run_time=0.5)
        self.play(Create(mapa.diagonales), run_time=1.2)
        self.wait(3.3)

        # --- momento: el barrio dorado ---------------------------------------
        rot.mostrar(pie_curso("Arriba a la izquierda, el barrio dorado: "
                              "fuerte y ligero. Ahí viven la fibra de "
                              "carbono y el titanio de las naves."),
                    zona="abajo", run_time=0.5)
        compuestos = mapa.burbuja("COMPUESTOS")
        self.play(Indicate(compuestos, color=C_MAT, scale_factor=1.15),
                  run_time=0.8)
        self.wait(4.2)

        # --- momento: cierre -------------------------------------------------
        rot.mostrar(pie_curso("Por eso los aviones dejaron el acero en "
                              "el suelo."), zona="abajo", run_time=0.5)
        self.wait(5.2)
