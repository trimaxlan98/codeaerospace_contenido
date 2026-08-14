class Clip4(Scene):
    """4 - Partido en dos. Dos centros de datos y su enlace: una escritura
    entra en A, la replica cruza a B... y el cable se corta. Con la
    particion encima, responder o esperar deja de ser lo mismo: esa es la
    disyuntiva real de CAP. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Partido en dos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: dos centros, una sola verdad -------------------------
        rot.mostrar(pie_curso("Dos centros de datos que fingen ser uno solo."),
                    zona="abajo", run_time=0.5)

        centros = par_centros()
        centros.shift(UP * 0.35)
        tag_a = tag_junto(centros.caja(0), "centro A", UP, buff=0.18)
        tag_b = tag_junto(centros.caja(1), "centro B", UP, buff=0.18)

        self.play(FadeIn(centros.cajas, shift=0.12 * UP), run_time=0.8)
        self.play(Create(centros.enlace),
                  FadeIn(tag_a), FadeIn(tag_b), run_time=0.7)
        self.wait(3.4)

        # --- momento: una escritura y su replica ---------------------------
        rot.mostrar(pie_curso("Escribes en A y la réplica cruza el enlace "
                              "hasta B."),
                    zona="abajo", run_time=0.5)

        escritura = Dot(np.array([-6.3, 0.35, 0.0]), radius=0.11, color=C_OK)
        tag_escribe = tag_junto(escritura, "escribe", UP, buff=0.14,
                                font_size=17, color=C_OK)
        self.play(FadeIn(escritura, shift=0.25 * RIGHT),
                  FadeIn(tag_escribe, shift=0.25 * RIGHT), run_time=0.5)
        centro_a = centros.caja(0).get_center()
        self.play(escritura.animate.move_to(centro_a),
                  tag_escribe.animate.move_to(centro_a + UP * 0.44),
                  run_time=1.0)
        self.wait(0.3)

        replica = Dot(centros.punto_enlace(0.04), radius=0.10,
                      color=C_MENSAJE)
        tag_replica = tag_hud("la réplica", font_size=15, color=C_MENSAJE)
        tag_replica.move_to(centros.punto_enlace(0.5) + UP * 0.62)
        self.play(FadeIn(replica), FadeIn(tag_replica), run_time=0.4)
        self.play(replica.animate.move_to(centros.punto_enlace(0.96)),
                  run_time=1.2)
        self.wait(1.1)
        self.play(FadeOut(tag_replica), run_time=0.4)

        # --- momento: se corta el cable ------------------------------------
        rot.mostrar(pie_curso("Se corta el cable: partición. Los dos siguen "
                              "vivos, pero ciegos."),
                    zona="abajo", run_time=0.5)

        corte = centros.corte()
        self.play(FadeIn(corte, scale=1.5),
                  Flash(centros.punto_enlace(0.5), color=C_FALLO,
                        line_length=0.26, num_lines=14, flash_radius=0.52,
                        line_stroke_width=3),
                  centros.enlace.animate.set_stroke(opacity=0.3),
                  run_time=0.9)
        self.wait(3.9)

        # --- momento: la disyuntiva ----------------------------------------
        rot.mostrar(pie_curso("Llega una lectura a B: ¿responder o esperar?"),
                    zona="abajo", run_time=0.5)

        lectura = Dot(np.array([6.3, 0.35, 0.0]), radius=0.11, color=C_OK)
        tag_lee = tag_junto(lectura, "lee", UP, buff=0.14, font_size=17,
                            color=C_OK)
        self.play(FadeIn(lectura, shift=0.25 * LEFT),
                  FadeIn(tag_lee, shift=0.25 * LEFT), run_time=0.5)
        centro_b = centros.caja(1).get_center()
        self.play(lectura.animate.move_to(centro_b),
                  tag_lee.animate.move_to(centro_b + UP * 0.44),
                  run_time=1.0)
        self.wait(0.3)

        opcion_a = Text("A · responder lo que tengo → disponible "
                        "(quizá viejo)", font_size=19, color=C_OK)
        opcion_c = Text("C · esperar al enlace → consistente (no responde)",
                        font_size=19, color=C_TIEMPO)
        opciones = VGroup(opcion_a, opcion_c)
        opciones.arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        opciones.move_to(np.array([0.0, -1.72, 0.0]))
        self.play(LaggedStart(FadeIn(opcion_a, shift=0.14 * UP),
                              FadeIn(opcion_c, shift=0.14 * UP),
                              lag_ratio=0.45), run_time=1.2)
        self.wait(2.4)

        # --- momento: el cierre --------------------------------------------
        rot.mostrar(pie_curso("Ésa es la disyuntiva real de CAP: durante la "
                              "partición, eliges."),
                    zona="abajo", run_time=0.5)
        self.wait(5.8)
