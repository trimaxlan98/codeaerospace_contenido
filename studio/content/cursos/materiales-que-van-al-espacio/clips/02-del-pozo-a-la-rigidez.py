class Clip2(Scene):
    """2 - Del pozo a la rigidez. El fondo del pozo de Lennard-Jones se lee
    como una parabola verde: un resorte escondido. A la derecha, una red
    atomica entera cizalla y regresa dos veces: la rigidez de un material
    es el pozo de un solo atomo, multiplicado por miles. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo ------------------------------------------
        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Del pozo a la rigidez")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        # --- momento: el pozo a la izquierda ----------------------------------
        pozo = pozo_lennard_jones(ancho=3.6, alto=3.0)
        pozo.move_to(np.array([-2.9, -0.1, 0.0]))

        self.play(Create(pozo.ejes), FadeIn(pozo.etiquetas), run_time=0.5)
        self.play(Create(pozo.curva), Create(pozo.r0_linea), run_time=1.0)

        pie1 = pie_curso("Cerca del fondo, el pozo parece una parábola: "
                         "el átomo está atado a un resorte.")
        rot.mostrar(pie1, zona="abajo", run_time=0.45)
        self.wait(1.3)

        # --- momento: la parabola verde sobre el fondo ------------------------
        rs = np.linspace(0.85, 1.2, 12)
        pts = np.array([pozo.punto_de(r) for r in rs])
        parabola = VMobject(color=C_OK, stroke_width=5)
        parabola.set_points_smoothly(pts)
        self.play(Create(parabola), run_time=1.2)
        self.wait(4.0)

        # --- momento: la red atomica a la derecha -------------------------------
        # El pie cambia ANTES de que la red aparezca.
        pie2 = pie_curso("Un material es una multitud de esos resortes en "
                         "formación.")
        rot.mostrar(pie2, zona="abajo", run_time=0.45)
        self.wait(0.7)

        red = red_atomica(filas=4, columnas=5, paso=0.58)
        red.move_to(np.array([2.9, -0.1, 0.0]))
        self.play(FadeIn(red.atomos), Create(red.resortes), run_time=1.1)
        self.wait(0.7)

        for _ in range(2):
            self.play(red.animate.cizallar(0.35), run_time=0.75,
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(red.animate.cizallar(0.0), run_time=0.75,
                      rate_func=rate_functions.ease_in_out_sine)

        # --- momento: el modulo de Young ---------------------------------------
        pie3 = pie_curso("Pozo profundo y angosto: resortes duros. Eso, a "
                         "lo grande, es el módulo de Young.")
        rot.mostrar(pie3, zona="abajo", run_time=0.45)
        self.wait(5.5)

        formula = formula_pie(r"E \propto U''(r_0)")
        rot.mostrar(formula, zona="abajo", run_time=0.45)
        self.wait(5.5)

        # --- momento: cierre -------------------------------------------------
        pie4 = pie_curso("La rigidez de un ala se decidió en un enlace.")
        rot.mostrar(pie4, zona="abajo", run_time=0.45)
        self.wait(6.5)
