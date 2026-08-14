class Clip4(Scene):
    """4.2.4 - Efecto sobre la pendiente de la curva de sustentacion.

    La correccion no solo mueve un cp: mueve la PENDIENTE de cl frente a
    alfa. El mismo perfil sustenta mas por grado al ir mas rapido, y eso
    cambia el pilotaje — la misma palanca produce mas g. Cierre de la
    leccion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La curva de sustentación se empina")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Dos rectas cl(alfa): incompresible y corregida. Las pendientes
        # salen del style_block (2pi y 2pi/beta), no de un trazo a ojo.
        ancho, alto = 5.2, 2.7
        alfa_max = 8.0
        ejes = VGroup(Line(LEFT * ancho / 2, RIGHT * ancho / 2,
                           stroke_width=2.0, color=C_EJE),
                      Line(LEFT * ancho / 2, LEFT * ancho / 2 + UP * alto,
                           stroke_width=2.0, color=C_EJE))
        ejes.move_to(LEFT * 0.6 + DOWN * 0.45)
        base = ejes[0].get_start()
        cl_max = PENDIENTE_M * np.deg2rad(alfa_max) * 1.10

        def punto(alfa, pendiente):
            return base + np.array([alfa / alfa_max * ancho,
                                    pendiente * np.deg2rad(alfa) / cl_max
                                    * alto, 0.0])

        recta0 = Line(punto(0, PENDIENTE_0), punto(alfa_max, PENDIENTE_0),
                      stroke_width=3.0, color=C_TENUE)
        rectaM = Line(punto(0, PENDIENTE_M), punto(alfa_max, PENDIENTE_M),
                      stroke_width=3.0, color=C_CALCULO)
        tag_x = Text("ángulo de ataque", font_size=17, color=C_EJE)
        tag_x.next_to(ejes[0], DOWN, buff=0.18)
        tag_y = Text("cl", font=FUENTE_HUD, font_size=18, color=C_EJE)
        tag_y.next_to(ejes[1], UP, buff=0.12)

        self.play(FadeIn(ejes), FadeIn(tag_x), FadeIn(tag_y), run_time=0.6)
        self.play(Create(recta0), run_time=0.9)
        etiqueta0 = Text("incompresible", font_size=19, color=C_TENUE)
        etiqueta0.next_to(recta0.get_end(), DR, buff=0.10)
        self.play(FadeIn(etiqueta0), run_time=0.5)
        rot.mostrar(pie_curso("A baja velocidad, un perfil delgado sustenta "
                              "dos pi por radián."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        self.play(Create(rectaM), run_time=0.9)
        etiquetaM = Text(f"Mach {M_COMPARA:g}", font_size=19, color=C_CALCULO)
        etiquetaM.next_to(rectaM.get_end(), UL, buff=0.10)
        self.play(FadeIn(etiquetaM), run_time=0.5)
        rot.mostrar(pie_curso(f"A Mach {M_COMPARA:g}, la misma raíz empina "
                              "la recta."), zona="abajo", run_time=0.5)
        self.wait(4.8)

        cifras = VGroup(
            Text(f"{PENDIENTE_0:.2f} /rad", font=FUENTE_HUD, font_size=19,
                 color=C_TENUE),
            Text(f"{PENDIENTE_M:.2f} /rad", font=FUENTE_HUD, font_size=19,
                 color=C_CALCULO)).arrange(DOWN, aligned_edge=LEFT, buff=0.20)
        cifras.move_to(RIGHT * 4.3 + UP * 0.35)
        self.play(FadeIn(cifras, shift=0.10 * UP), run_time=0.7)
        rot.mostrar(pie_curso(f"Un {(PENDIENTE_M / PENDIENTE_0 - 1) * 100:.0f}"
                              " % más de sustentación por grado."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("El mismo tirón de palanca produce más g. Y el "
                              "piloto lo nota."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(ejes, tag_x, tag_y, recta0, rectaM,
                                 etiqueta0, etiquetaM, cifras)),
                  run_time=0.8)
        cierre = VGroup(
            titulo_marca("La compresibilidad no espera a Mach 1.",
                         font_size=34, color=C_TITULO),
            titulo_marca("Lleva avisando desde mucho antes.", font_size=34,
                         color=C_CALCULO)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)
