class Clip2(Scene):
    """3.1.2 - La inversa deshace el movimiento: si A lleva la rejilla a un
    sitio, A^-1 la trae de vuelta a la identidad; juntas dan I. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Deshacer el movimiento: la inversa")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la rejilla ya movida por A -----------------------------
        pl = plano_leccion(vivo=True)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Esta es la rejilla que A ya movió."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(A), run_time=2.0)
        self.wait(2.4)

        # --- momento: deshacer el movimiento ---------------------------------
        rot.mostrar(pie_curso("¿Qué movimiento la trae de vuelta a su "
                              "sitio?"), zona="abajo", run_time=0.5)
        self.wait(2.2)
        self.play(*pl.anim_matriz(np.eye(2)), run_time=2.0)
        self.wait(1.0)
        rot.mostrar(pie_curso("Ese movimiento tiene nombre: es aplicar "
                              "la inversa de A."), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        # --- momento: la inversa, calculada -----------------------------------
        etiqueta_a = MathTex("A", font_size=34, color=C_TITULO)
        m_a = matriz_columnas(A)
        fila_a = VGroup(etiqueta_a, m_a).arrange(RIGHT, buff=0.28)

        etiqueta_ainv = MathTex(r"A^{-1}", font_size=34, color=C_TITULO)
        m_ainv = matriz_columnas(A_INV, dec=2)
        fila_ainv = VGroup(etiqueta_ainv, m_ainv).arrange(RIGHT, buff=0.28)

        panel = panel_derecha(fila_a, fila_ainv)
        rot.mostrar(pie_curso("Cada columna de la inversa se calcula: no "
                              "se adivina."), zona="abajo", run_time=0.5)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(3.6)

        # --- momento: A inversa por A es la identidad ---------------------------
        rot.mostrar(formula_pie(r"A^{-1}A = I"), zona="abajo", run_time=0.5)
        self.wait(4.0)

        rot.mostrar(pie_curso("Deshacer un movimiento es, en el fondo, "
                              "aplicar su inversa."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
