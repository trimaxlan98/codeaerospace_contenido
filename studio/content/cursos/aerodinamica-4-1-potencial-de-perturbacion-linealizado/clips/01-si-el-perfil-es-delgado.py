class Clip1(Scene):
    """4.1.1 - Hipotesis de perturbaciones pequeñas.

    Todo el modulo 4 se apoya en una renuncia: aceptar que el perfil apenas
    molesta al aire. Si el cuerpo es delgado y va poco inclinado, la
    velocidad en cualquier punto es la de la corriente MAS un pellizco, y los
    productos de pellizcos se tiran. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Si el perfil es delgado")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Un perfil MUY fino: el dibujo tiene que hacer creible la hipotesis.
        cuerda = 4.4
        perfil = VMobject(color=C_TENUE, stroke_width=2.6)
        pts = [np.array([(x - 0.5) * cuerda,
                         ESPESOR_FINO * cuerda * np.sin(np.pi * x) * signo,
                         0.0])
               for signo in (1, -1)
               for x in (np.linspace(0, 1, 22) if signo > 0
                         else np.linspace(1, 0, 22))]
        perfil.set_points_smoothly(pts)
        perfil.set_fill(C_EJE, opacity=0.4)
        perfil.move_to(UP * 0.75)

        self.play(Create(perfil), run_time=1.0)
        rot.mostrar(pie_curso("Un perfil delgado, a poco ángulo. El aire "
                              "apenas se entera de que está ahí."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: la velocidad, como suma ------------------------------
        corriente = Arrow(perfil.get_left() + LEFT * 2.1 + UP * 0.15,
                          perfil.get_left() + LEFT * 0.55 + UP * 0.15,
                          buff=0, stroke_width=3.4, color=C_TRANS,
                          max_tip_length_to_length_ratio=0.20)
        tag_v = MathTex(r"V_\infty", font_size=30, color=C_TRANS)
        tag_v.next_to(corriente, UP, buff=0.14)
        self.play(FadeIn(corriente), FadeIn(tag_v), run_time=0.6)

        rot.mostrar(formula_pie(r"u = V_\infty + u' \qquad v = v'"),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("La velocidad en cualquier punto es la de la "
                              "corriente más un pellizco."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: lo que se tira ---------------------------------------
        tirados = MathTex(r"u'^2,\; v'^2,\; u'v' \;\approx\; 0",
                          font_size=40, color=C_SUPER)
        tirados.move_to(DOWN * 1.35)
        self.play(Write(tirados), run_time=1.0)
        rot.mostrar(pie_curso("Y si el pellizco es pequeño, su cuadrado es "
                              "despreciable."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Eso es todo el truco. Y con eso las "
                              "ecuaciones dejan de ser no lineales."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Se paga un precio, claro. Pero antes de "
                              "pagarlo, veamos qué se compra."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
