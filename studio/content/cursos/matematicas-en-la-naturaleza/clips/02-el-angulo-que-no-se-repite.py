class Clip2(Scene):
    """2 - El angulo que no se repite. El experimento del curso: el mismo
    generador con 90, 120 y 137.5 grados. Los angulos racionales dejan
    rayos y cuñas vacias (rojas); el aureo llena parejo. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El ángulo que no se repite")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: 90 grados deja rayos --------------------------------
        rot.mostrar(pie_curso("Si cada hoja saliera a 90° de la anterior, "
                              "taparía a las de abajo: rayos y huecos."),
                    zona="abajo", run_time=0.5)
        disco = filotaxis(N_SEMILLAS, ANGULO_MALO_1, escala=2.15)
        disco.move_to(UP * 0.35)
        self.play(FadeIn(disco), run_time=1.1)

        giro = tag_junto(disco, f"giro: {ANGULO_MALO_1:.0f}°", UP, buff=0.0,
                         font_size=20, color=C_MITO)
        giro.move_to(LEFT * 4.9 + UP * 2.1)
        rot.mostrar(giro, zona="giro", run_time=0.4)

        cunas = disco.rayos_vacios()
        self.play(FadeIn(cunas), run_time=0.8)
        self.wait(3.4)

        # --- momento: cualquier fraccion exacta se repite -----------------
        rot.mostrar(pie_curso("Cualquier fracción exacta de vuelta acaba "
                              "repitiéndose."), zona="abajo", run_time=0.5)
        disco120 = disco.con_angulo(ANGULO_MALO_2)
        giro120 = tag_junto(disco, f"giro: {ANGULO_MALO_2:.0f}°", UP,
                            buff=0.0, font_size=20, color=C_MITO)
        giro120.move_to(LEFT * 4.9 + UP * 2.1)
        self.play(FadeOut(cunas), run_time=0.4)
        self.play(Transform(disco, disco120), run_time=1.5)
        rot.mostrar(giro120, zona="giro", run_time=0.4)
        cunas120 = disco120.rayos_vacios()
        self.play(FadeIn(cunas120), run_time=0.7)
        self.wait(3.2)

        # --- momento: el angulo aureo no cae nunca en el mismo sitio ------
        rot.mostrar(pie_curso("El ángulo áureo nunca cae en el mismo sitio: "
                              "cada semilla hereda un lugar libre."),
                    zona="abajo", run_time=0.5)
        disco_oro = disco.con_angulo(ANGULO_AUREO_DEG)
        giro_oro = tag_junto(disco, f"giro: {ANGULO_AUREO_DEG:.1f}°", UP,
                             buff=0.0, font_size=20, color=C_CONSTANTE)
        giro_oro.move_to(LEFT * 4.9 + UP * 2.1)
        self.play(FadeOut(cunas120), run_time=0.4)
        self.play(Transform(disco, disco_oro), run_time=1.8)
        rot.mostrar(giro_oro, zona="giro", run_time=0.4)
        self.wait(2.8)

        # --- momento: la formula del reparto ------------------------------
        formula = formula_pie(r"360^\circ/\varphi^{2}\ \approx\ 137.5^\circ",
                              color=C_CONSTANTE)
        rot.mostrar(formula, zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: la moraleja -----------------------------------------
        rot.mostrar(pie_curso("La planta no lo eligió: lo que reparte "
                              "mejor, sobrevive mejor."), zona="abajo",
                    run_time=0.5)
        self.wait(5.6)
