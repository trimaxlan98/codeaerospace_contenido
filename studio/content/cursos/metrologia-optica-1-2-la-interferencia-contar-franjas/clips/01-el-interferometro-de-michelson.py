class Clip1(Scene):
    """1 - El interferometro de Michelson. El esquema se construye por
    partes: el laser rojo, el divisor que parte el haz, los dos brazos con
    sus espejos y el retorno al detector. Ahi las dos ondas se suman y
    aparecen las franjas (patron grande a la derecha). Michelson lo armo en
    1881 y sigue siendo el instrumento de la metrologia. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("El interferómetro de Michelson"),
                    zona="arriba", run_time=0.6)

        # El esquema va a la izquierda al 84 %: el dibujo visible mide 4.6 x
        # 3.8 y ocupa la banda central-izquierda (de -1.9 a +1.8) sin tocar
        # el titulo ni el pie. Ojo: el `move_to` cuenta el bounding box
        # ENTERO (anclas en +-3.3 y la lectura, que aqui no se muestra), por
        # eso el centro va corrido respecto del dibujo. El patron grande vive
        # a la derecha, lejos de la marca de agua (x > 4.6, y < -2.9).
        m = michelson()
        m.scale(0.84).move_to(np.array([-3.47, -0.19, 0.0]))

        patron = patron_franjas(0.0, 1.0, n_franjas=6, ancho=4.2, alto=2.2,
                                n_barras=120)
        patron.move_to(np.array([3.25, 0.25, 0.0]))
        t_det = tag_junto(patron, "lo que ve el detector", DOWN, buff=0.22,
                          font_size=18, color=C_MEDIDA)

        # --- momento: un divisor parte el haz -----------------------------
        rot.mostrar(pie_curso("Un divisor parte el haz en dos caminos que "
                              "vuelven a juntarse."), zona="abajo")
        self.play(FadeIn(m.fuente, shift=0.12 * RIGHT),
                  FadeIn(m.rotulos[0]), run_time=0.7)
        self.play(Create(m.haces[0]), run_time=0.9)
        self.play(FadeIn(m.divisor), FadeIn(m.rotulos[1]), run_time=0.7)
        # Los dos brazos salen a la vez: es el reparto, no una secuencia.
        self.play(Create(m.haces[1]), Create(m.haces[2]),
                  FadeIn(m.espejo_fijo), FadeIn(m.espejo_movil),
                  FadeIn(m.flecha), FadeIn(m.rotulos[2]),
                  FadeIn(m.rotulos[3]), run_time=1.5)
        self.play(Create(m.haces[3]), FadeIn(m.detector),
                  FadeIn(m.rotulos[4]), run_time=1.2)
        self.wait(3.2)

        # --- momento: las dos ondas se suman ------------------------------
        rot.mostrar(pie_curso("En el detector, las dos ondas se suman: "
                              "aparecen franjas."), zona="abajo")
        self.play(FadeIn(m.franjas), run_time=1.0)
        self.play(FadeIn(patron, shift=0.14 * LEFT), run_time=1.2)
        self.play(FadeIn(t_det), run_time=0.5)
        self.wait(5.6)

        # --- momento: 1881 -------------------------------------------------
        rot.mostrar(pie_curso("Michelson lo construyó en 1881; hoy es el "
                              "instrumento de la metrología."), zona="abajo")
        t_ano = tag_hud("Michelson, 1881", font_size=16, color=C_TENUE)
        t_ano.move_to(np.array([3.25, 1.98, 0.0]))
        self.play(FadeIn(t_ano, shift=0.10 * UP), run_time=0.6)
        self.wait(5.4)

        # --- cierre ---------------------------------------------------------
        rot.mostrar(pie_curso("Dos caminos, una suma: el interferómetro "
                              "convierte fase en brillo."), zona="abajo")
        self.wait(5.0)
