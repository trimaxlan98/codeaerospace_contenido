class Clip4(Scene):
    """4.1.4 - Rango de validez y sus fronteras (transonico e hipersonico).

    La honestidad del modulo: decir donde NO vale antes de usarlo. El
    coeficiente (1 - M^2) se anula en Mach 1 y la linealizada se rompe por
    dentro; y a Mach muy alto el cono se cierra tanto que las perturbaciones
    dejan de ser pequeñas. Cierre de la leccion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Dónde deja de valer")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        banda = banda_regimenes(ancho=9.0, alto=0.62)
        banda.move_to(UP * 0.55)
        self.play(FadeIn(banda), run_time=0.8)
        rot.mostrar(pie_curso("La teoría linealizada no vale en todas "
                              "partes. Vale en dos trozos."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # Los dos trozos buenos y los dos malos, colgados de la propia banda
        # por sus localizadores: si la banda se mueve, las marcas la siguen.
        buenos = VGroup()
        for m0, m1, color in ((0.15, 0.72, C_SUB), (1.35, 4.6, C_SUB)):
            barra = Line(banda.punto_de(m0, 0.55), banda.punto_de(m1, 0.55),
                         stroke_width=7.0, color=color).set_stroke(opacity=0.8)
            buenos.add(barra)
        tag_buenos = Text("aquí sí", font_size=20, color=C_SUB)
        tag_buenos.next_to(buenos[0], UP, buff=0.16)

        self.play(Create(buenos), FadeIn(tag_buenos), run_time=0.9)
        rot.mostrar(pie_curso("Subsónico lejos de 1, y supersónico lejos de "
                              "1. Ahí funciona muy bien."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: la primera frontera ----------------------------------
        malo_trans = Line(banda.punto_de(0.78, 0.55),
                          banda.punto_de(1.28, 0.55), stroke_width=7.0,
                          color=C_SUPER).set_stroke(opacity=0.85)
        tag_trans = Text("aquí no", font_size=20, color=C_SUPER)
        tag_trans.next_to(malo_trans, UP, buff=0.16)
        self.play(Create(malo_trans), FadeIn(tag_trans), run_time=0.8)
        rot.mostrar(formula_pie(r"1 - M_\infty^2 \to 0", color=C_SUPER),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("En transónico el coeficiente se anula y la "
                              "ecuación se queda sin término dominante."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: la segunda -------------------------------------------
        malo_hiper = Line(banda.punto_de(5.5, 0.55),
                          banda.punto_de(25.0, 0.55), stroke_width=7.0,
                          color=C_HIPER).set_stroke(opacity=0.85)
        tag_hiper = Text("ni aquí", font_size=20, color=C_HIPER)
        tag_hiper.next_to(malo_hiper, UP, buff=0.16)
        self.play(Create(malo_hiper), FadeIn(tag_hiper), run_time=0.8)
        rot.mostrar(pie_curso("Y en hipersónico las perturbaciones dejan de "
                              "ser pequeñas: la onda va pegada al cuerpo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(banda, buenos, tag_buenos, malo_trans,
                                 tag_trans, malo_hiper, tag_hiper)),
                  run_time=0.8)
        cierre = VGroup(
            titulo_marca("Una teoría que sabe dónde falla", font_size=35,
                         color=C_TITULO),
            titulo_marca("vale más que una que no.", font_size=35,
                         color=C_CALCULO)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)
