class Clip3(Scene):
    """2.2.3 - Los cuatro renglones juntos. Lo importante no es operarlos:
    es ver la SIMETRIA entre el flujo magnetico que cambia (Faraday) y el
    electrico que cambia (Maxwell) — el bucle que puede sostenerse solo.
    (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Cuatro renglones")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # El color de cada renglon dice QUE CAMPO se esta sumando; en cian,
        # los dos terminos que hacen simetrica la pareja.
        eq1 = MathTex(r"\oint \vec E\cdot d\vec A", "=",
                      r"\frac{q}{\varepsilon_0}", font_size=26, color=C_E)
        eq2 = MathTex(r"\oint \vec B\cdot d\vec A", "=", "0",
                      font_size=26, color=C_B)
        eq3 = MathTex(r"\oint \vec E\cdot d\vec l", "=",
                      r"-\frac{d\Phi_B}{dt}", font_size=26, color=C_E)
        eq4 = MathTex(r"\oint \vec B\cdot d\vec l", "=", r"\mu_0 I", "+",
                      r"\mu_0\varepsilon_0\,\frac{d\Phi_E}{dt}",
                      font_size=26, color=C_B)
        eq3[2].set_color(C_CALCULO)
        eq4[2].set_color(C_CARGA)
        eq4[4].set_color(C_CALCULO)

        renglones = VGroup(eq1, eq2, eq3, eq4)
        renglones.arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        renglones.move_to(RIGHT * 1.05 + UP * 0.1)

        nombres = VGroup()
        for eq, texto in zip(renglones,
                             ["Gauss (E)", "Gauss (B)", "Faraday",
                              "Ampere-Maxwell"]):
            n = tag_hud(texto, font_size=16, color=C_TENUE)
            n.next_to(eq, LEFT, buff=0.55)
            nombres.add(n)

        # --- momento: las dos que ya conoces ------------------------------
        rot.mostrar(pie_curso("Cuatro renglones. Los dos primeros ya los "
                              "tienes: las dos de Gauss."), zona="abajo",
                    run_time=0.5)
        self.play(Write(eq1), FadeIn(nombres[0]), run_time=0.9)
        self.play(Write(eq2), FadeIn(nombres[1]), run_time=0.9)
        self.wait(4.6)

        # --- momento: Faraday ---------------------------------------------
        rot.mostrar(pie_curso("El tercero es Faraday: un flujo magnético "
                              "que cambia empuja las cargas."),
                    zona="abajo", run_time=0.5)
        self.play(Write(eq3), FadeIn(nombres[2]), run_time=1.0)
        self.wait(4.6)

        # --- momento: Ampere con el termino de Maxwell --------------------
        rot.mostrar(pie_curso("El cuarto es Ampère, ya con el término que "
                              "le añadió Maxwell."), zona="abajo",
                    run_time=0.5)
        self.play(Write(eq4), FadeIn(nombres[3]), run_time=1.2)
        self.wait(4.6)

        # --- momento: la simetria -----------------------------------------
        marco3 = SurroundingRectangle(eq3[2], color=C_CALCULO, buff=0.09,
                                      stroke_width=2.0)
        marco4 = SurroundingRectangle(eq4[4], color=C_CALCULO, buff=0.09,
                                      stroke_width=2.0)
        rot.mostrar(pie_curso("Mira los dos términos en cian: son la misma "
                              "frase, dicha al revés."), zona="abajo",
                    run_time=0.5)
        self.play(Create(marco3), Create(marco4), run_time=0.9)
        self.wait(4.6)

        rot.mostrar(pie_curso("Un campo magnético que cambia hace campo "
                              "eléctrico. Y al revés."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Ahí hay un bucle capaz de sostenerse solo, "
                              "lejos de cualquier carga."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)
