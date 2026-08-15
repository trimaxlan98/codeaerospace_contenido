class Clip1(Scene):
    """2.2.1 - Las dos leyes de Gauss, lado a lado. Con una carga dentro
    de una superficie cerrada todas las flechas SALEN (flujo neto); con
    un iman dentro, cada linea que sale vuelve a entrar (flujo cero): no
    hay polos magneticos sueltos. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Las dos de Gauss")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # Los dos paneles se construyen con el MISMO radio de superficie:
        # la comparacion solo vale si la caja es la misma en los dos casos.
        caja_e = caja_gauss("electrica", radio_superficie=0.8)
        caja_b = caja_gauss("magnetica", radio_superficie=0.8)
        caja_e.move_to(LEFT * 3.4 + UP * 0.35)
        caja_b.move_to(RIGHT * 3.4 + UP * 0.35)

        ley_e = MathTex(r"\oint \vec E\cdot d\vec A = \frac{q}{\varepsilon_0}",
                        font_size=30, color=C_E)
        ley_e.next_to(caja_e, DOWN, buff=0.5)
        ley_b = MathTex(r"\oint \vec B\cdot d\vec A = 0",
                        font_size=30, color=C_B)
        ley_b.next_to(caja_b, DOWN, buff=0.5)
        tag_e = tag_hud("flujo neto", font_size=18)
        tag_e.next_to(caja_e, UP, buff=0.22)
        tag_b = tag_hud("flujo cero", font_size=18)
        tag_b.next_to(caja_b, UP, buff=0.22)

        # --- momento: la superficie cerrada y su carga --------------------
        rot.mostrar(pie_curso("Encierra una carga en una superficie "
                              "cerrada imaginaria."), zona="abajo",
                    run_time=0.5)
        self.play(Create(caja_e.superficie), FadeIn(caja_e.fuente,
                                                    scale=1.4),
                  run_time=0.9)
        self.wait(4.6)

        # --- momento: todo sale = flujo neto ------------------------------
        rot.mostrar(pie_curso("Todas las flechas salen y ninguna vuelve. "
                              "Eso es flujo neto: hay fuente dentro."),
                    zona="abajo", run_time=0.5)
        self.play(*[GrowArrow(f) for f in caja_e.flechas], run_time=1.0)
        self.play(FadeIn(tag_e), FadeIn(ley_e), run_time=0.6)
        self.wait(4.6)

        # --- momento: la misma caja, ahora con un iman --------------------
        rot.mostrar(pie_curso("Ahora un imán dentro de la misma caja. "
                              "Misma pregunta, otra historia."),
                    zona="abajo", run_time=0.5)
        self.play(Create(caja_b.superficie), FadeIn(caja_b.fuente),
                  run_time=0.9)
        self.wait(4.6)

        # --- momento: lo que sale, vuelve ---------------------------------
        rot.mostrar(pie_curso("Cada línea que sale por arriba vuelve a "
                              "entrar por abajo. Suma cero."),
                    zona="abajo", run_time=0.5)
        self.play(Create(caja_b.flechas), run_time=1.6)
        self.play(FadeIn(tag_b), FadeIn(ley_b), run_time=0.6)
        self.wait(4.6)

        # --- momento: por que el cero -------------------------------------
        rot.mostrar(pie_curso("Parte el imán y salen dos imanes. Nadie ha "
                              "encontrado nunca un polo suelto."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("La eléctrica tiene fuente. La magnética, "
                              "ninguna. Esas son las dos primeras."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
