class Clip3(Scene):
    """2.4.3 - Comportamiento opuesto en regimen subsonico y supersonico.

    Los cuatro casos de la ecuacion anterior, dibujados. Lo antiintuitivo
    —que un tubo que se ensancha ACELERE el flujo— deja de serlo en cuanto
    se recuerda que aguas abajo de la garganta la densidad cae mas deprisa
    de lo que crece el area. (~42 s)"""

    ROTULO = {"convergente": "se estrecha", "divergente": "se ensancha"}

    def _panel(self, perfil, regimen, x, y):
        """Un tubo pequeno con su regimen y la flecha de lo que le pasa al
        flujo. La flecha crece o mengua segun acelere o frene."""
        color = C_SUB if regimen == "M < 1" else C_SUPER
        acelera = ((perfil == "convergente") == (regimen == "M < 1"))
        tubo = conducto(perfil, area_garganta=0.45, largo=2.5, alto=1.05,
                        color=C_TENUE)
        tubo.move_to(RIGHT * x + UP * y)

        largo = 0.85 if acelera else 0.42
        flecha = Arrow(tubo.punto_de(0.30) + LEFT * largo / 2,
                       tubo.punto_de(0.30) + RIGHT * largo / 2, buff=0,
                       stroke_width=3.2, color=color,
                       max_tip_length_to_length_ratio=0.30)
        veredicto = Text("acelera" if acelera else "frena", font_size=20,
                         color=color)
        veredicto.next_to(tubo, DOWN, buff=0.18)
        return VGroup(tubo, flecha, veredicto)

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El tubo que hace lo contrario")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Cabeceras de la matriz: los tubos van en dos columnas (perfil) y
        # dos filas (regimen), y cada rotulo se coloca UNA vez.
        cabeceras = VGroup()
        for texto, x in (("se estrecha", -2.6), ("se ensancha", 2.6)):
            tag = Text(texto, font_size=21, color=C_TENUE)
            tag.move_to(RIGHT * x + UP * 1.95)
            cabeceras.add(tag)
        for texto, y, color in (("M < 1", 0.95, C_SUB), ("M > 1", -0.85,
                                                         C_SUPER)):
            tag = Text(texto, font=FUENTE_HUD, font_size=22, color=color)
            tag.move_to(LEFT * 5.6 + UP * y)
            cabeceras.add(tag)
        self.play(FadeIn(cabeceras), run_time=0.6)

        paneles = VGroup(
            self._panel("convergente", "M < 1", -2.6, 0.95),
            self._panel("divergente", "M < 1", 2.6, 0.95),
            self._panel("convergente", "M > 1", -2.6, -0.85),
            self._panel("divergente", "M > 1", 2.6, -0.85))

        pies = ("Subsónico y estrechando: acelera. Esto ya lo sabías: es una "
                "manguera con el dedo puesto.",
                "Subsónico y ensanchando: frena. También cuadra.",
                "Ahora supersónico. Estrechas... y frena.",
                "Ensanchas... y acelera. Al revés de todo lo anterior.")
        for panel, pie in zip(paneles, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(panel, shift=0.12 * UP), run_time=0.7)
            self.wait(4.4)

        rot.mostrar(pie_curso("No es magia: pasada la garganta, la densidad "
                              "cae más deprisa de lo que crece el área."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Y por eso una tobera de cohete se abre al "
                              "final."), zona="abajo", run_time=0.5)
        self.wait(4.8)
