class Clip3(Scene):
    """4.2.3 - Elevar A a una potencia grande es fácil si D es diagonal:
    D^n solo eleva números. El mismo truco explica Fibonacci y el número
    φ. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Potencias sin sudar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Multiplicar A por sí misma, otra vez y "
                              "otra, ya cuesta trabajo a mano."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(potencia(A, 2)), run_time=2.0)
        self.wait(3.0)

        rot.mostrar(pie_curso("Pero A = P D P⁻¹, y D es diagonal: D a la "
                              "n es solo elevar cada número."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(np.eye(2)), run_time=1.2)
        mat_d10 = matriz_columnas(D_N, dec=0, font_size=32)
        etq_d10 = MathTex("D^{10} = ", font_size=30, color=C_CALCULO)
        fila_d10 = VGroup(etq_d10, mat_d10).arrange(RIGHT, buff=0.2)
        panel1 = panel_derecha(fila_d10)
        self.play(FadeIn(panel1, shift=0.15 * LEFT), run_time=0.7)
        self.wait(3.4)

        rot.mostrar(pie_curso("Multiplicamos por P y P⁻¹ una sola vez: "
                              "sale A a la diez, exacta."), zona="abajo",
                    run_time=0.5)
        mat_a10 = matriz_columnas(A_N, dec=0, font_size=28)
        etq_a10 = MathTex("A^{10} = ", font_size=28, color=C_CALCULO)
        fila_a10 = VGroup(etq_a10, mat_a10).arrange(RIGHT, buff=0.2)
        panel2 = panel_derecha(fila_a10)
        self.play(FadeOut(panel1), FadeIn(panel2, shift=0.15 * LEFT),
                  run_time=0.7)
        self.wait(3.8)

        rot.mostrar(pie_curso("El mismo truco explica Fibonacci: "
                              "1, 1, 2, 3, 5, 8…"), zona="abajo",
                    run_time=0.5)
        mat_q = matriz_columnas(Q_BASE, dec=0, font_size=32)
        etq_q = MathTex("Q = ", font_size=30, color=C_CALCULO)
        fila_q = VGroup(etq_q, mat_q).arrange(RIGHT, buff=0.2)
        panel3 = panel_derecha(fila_q)
        self.play(FadeOut(panel2), FadeIn(panel3, shift=0.15 * LEFT),
                  run_time=0.7)
        self.wait(3.0)

        rot.mostrar(pie_curso("Q a la diez esconde F10 en su esquina: "
                              "55."), zona="abajo", run_time=0.5)
        mat_q10 = matriz_columnas(Q10_MAT, dec=0, font_size=28)
        f10 = tag_hud("F10 = " + fmt(FIB_10, 0), font_size=20,
                     color=C_CALCULO)
        fila_q10 = VGroup(mat_q10, f10).arrange(DOWN, buff=0.2)
        panel4 = panel_derecha(fila_q10)
        self.play(FadeOut(panel3), FadeIn(panel4, shift=0.15 * LEFT),
                  run_time=0.7)
        self.wait(3.2)

        rot.mostrar(pie_curso("El autovalor que domina esa sucesión tiene "
                              "nombre: φ, el número áureo."), zona="abajo",
                    run_time=0.5)
        phi_tex = MathTex(r"\varphi = " + fmt(PHI, 3), font_size=30,
                          color=C_CALCULO)
        phi_tex.next_to(panel4, DOWN, buff=0.2).align_to(panel4, RIGHT)
        self.play(FadeIn(phi_tex, shift=0.1 * UP), run_time=0.6)
        self.wait(4.4)
