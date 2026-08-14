class Clip5(Scene):
    """5 - La mayoria manda. Sin jefe se acuerda por quorum: escribir exige
    mayoria, leer tambien, y como W + R > N los dos conjuntos NO pueden
    evitarse: siempre comparten un nodo. Cierre con el porque de los
    numeros nones. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 05")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La mayoría manda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: sin jefe ---------------------------------------------
        rot.mostrar(pie_curso("Sin jefe, ¿cómo se ponen de acuerdo?"),
                    zona="abajo", run_time=0.5)

        nq = nodos_quorum()
        nq.scale(1.15)
        nq.shift(UP * 0.55)
        tag_n = tag_hud(f"N = {N_QUORUM} réplicas", font_size=14,
                        color=C_TENUE)
        tag_n.move_to(np.array([0.0, -0.62, 0.0]))

        self.play(LaggedStart(*[FadeIn(nq.nodo(i), scale=1.3)
                                for i in range(N_QUORUM)],
                              lag_ratio=0.18), run_time=0.9)
        self.play(FadeIn(tag_n), run_time=0.45)
        self.wait(3.15)

        # --- momento: escribir exige mayoria --------------------------------
        rot.mostrar(pie_curso("Escribir no vale con uno: exige mayoría."),
                    zona="abajo", run_time=0.5)

        aros_w = nq.aro(IDX_W, C_OK, 0.30)
        tag_w = tag_hud(f"escritura W = {W_QUORUM}", font_size=16, color=C_OK)
        tag_w.next_to(aros_w, LEFT, buff=0.32)
        self.play(Create(aros_w), run_time=0.9)
        self.play(FadeIn(tag_w, shift=0.14 * RIGHT), run_time=0.45)
        self.wait(3.2)

        # --- momento: leer tambien ------------------------------------------
        rot.mostrar(pie_curso("Leer tampoco: hay que preguntar a una "
                              "mayoría."),
                    zona="abajo", run_time=0.5)

        aros_r = nq.aro(IDX_R, C_MENSAJE, 0.42)
        tag_r = tag_hud(f"lectura R = {R_QUORUM}", font_size=16,
                        color=C_MENSAJE)
        tag_r.next_to(aros_r, RIGHT, buff=0.32)
        self.play(Create(aros_r), run_time=0.9)
        self.play(FadeIn(tag_r, shift=0.14 * LEFT), run_time=0.45)
        self.wait(3.15)

        # --- momento: el remate ---------------------------------------------
        rot.mostrar(formula_pie(r"W + R > N"), zona="abajo", run_time=0.5)

        inter = nq.interseccion(IDX_W, IDX_R)
        comun = nq.nodo(inter[0])
        self.play(Indicate(comun, color=C_OK, scale_factor=1.6),
                  Flash(comun, color=C_OK, line_length=0.28, num_lines=14,
                        flash_radius=0.62, line_stroke_width=3),
                  run_time=1.0)
        tag_inter = tag_hud(f"al menos {INTERSECCION} nodo en común",
                            font_size=16, color=C_OK)
        tag_inter.move_to(np.array([0.0, 1.88, 0.0]))
        self.play(FadeIn(tag_inter, shift=0.14 * DOWN),
                  comun.animate.set_color(C_OK), run_time=0.55)
        self.wait(3.0)

        # --- momento: por eso son nones --------------------------------------
        rot.mostrar(pie_curso("Cinco aguantan dos caídas y siguen teniendo "
                              "mayoría; cuatro, una sola."),
                    zona="abajo", run_time=0.5)

        caidos = VGroup(nq.nodo(3), nq.nodo(4))
        self.play(*[d.animate.set_color(C_FALLO) for d in caidos],
                  run_time=0.9)
        self.play(Indicate(aros_w, color=C_OK, scale_factor=1.10),
                  run_time=0.8)
        self.wait(2.85)

        # --- momento: el cierre -----------------------------------------------
        rot.mostrar(formula_pie(r"W + R > N"), zona="abajo", run_time=0.5)
        self.wait(4.6)
