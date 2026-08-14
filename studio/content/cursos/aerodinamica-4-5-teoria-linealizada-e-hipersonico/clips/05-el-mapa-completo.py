class Clip5(Scene):
    """4.5.5 - Cierre: mapa integrador de todo el curso.

    La banda de regimenes de la leccion 1.1, ahora con la herramienta que
    resuelve cada tramo. El curso entero cabe en una imagen, y esa imagen es
    la misma con la que empezo. Cierre de la leccion, del modulo 4 y del
    curso. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))

        titulo = titulo_curso("El mapa completo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        banda = banda_regimenes(ancho=9.4, alto=0.68)
        banda.move_to(UP * 0.35)
        self.play(FadeIn(banda), run_time=0.8)
        rot.mostrar(pie_curso("La misma regla con la que empezó el curso, en "
                              "la lección 1.1."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # Cada herramienta cuelga de SU zona por el localizador de la banda:
        # si la regla se mueve, el mapa entero se mueve con ella.
        herramientas = (("Prandtl-Glauert", 0.40, 1),
                        ("nada cerrado:\nhay que negociar", 1.0, -1),
                        ("choque-expansión\ny Ackeret", 2.6, 1),
                        ("gas real:\notra asignatura", 12.0, -1))
        marcas = VGroup()
        for texto, mach, lado in herramientas:
            color = banda.color_de(mach)
            tag = Text(texto, font_size=18, color=color, line_spacing=0.7)
            ancla = banda.punto_de(mach, 0.0)
            tag.move_to([ancla[0], ancla[1] + lado * 0.95, 0])
            guia = DashedLine(
                [ancla[0], ancla[1] + lado * 0.34, 0],
                [ancla[0], tag.get_bottom()[1] - 0.08 if lado > 0
                 else tag.get_top()[1] + 0.08, 0],
                stroke_width=1.2, color=color,
                dash_length=0.06).set_opacity(0.6)
            marcas.add(VGroup(guia, tag))

        pies = ("En subsónico basta con corregir un dato de túnel.",
                "En transónico no hay fórmula: hay flecha, perfil "
                "supercrítico y regla del área.",
                "En supersónico, choque-expansión si quieres exactitud y "
                "Ackeret si quieres entender.",
                "Y en hipersónico, el aire deja de ser el que hemos "
                "supuesto.")
        for marca, pie in zip(marcas, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(marca, shift=0.10 * UP), run_time=0.7)
            self.wait(4.6)

        rot.mostrar(pie_curso("Cuatro tramos, cuatro herramientas, y un solo "
                              "número que decide cuál usar."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        # --- cierre del curso -----------------------------------------------
        self.play(FadeOut(VGroup(banda, marcas)), run_time=0.8)
        cierre = VGroup(
            titulo_marca("Empezamos preguntando cuándo deja", font_size=34,
                         color=C_TITULO),
            titulo_marca("de valer «incompresible».", font_size=34,
                         color=C_TITULO),
            titulo_marca("Ya sabes qué hay al otro lado.", font_size=34,
                         color=C_SUPER)).arrange(DOWN, buff=0.26)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.2)
        self.wait(4.2)
