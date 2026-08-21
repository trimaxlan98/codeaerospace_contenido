class Clip2(Scene):
    """1.2.2 - Fijar y = y0 y rebanar la superficie con un plano; la curva
    del corte pasa a su propia grafica 2D, con tangente. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Cortar con x: ∂f/∂x")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el paisaje y el plano de corte ------------------------
        esp = espacio_leccion()
        sup = superficie3(esp, PAISAJE, n=15)
        self.play(FadeIn(esp), FadeIn(sup), run_time=1.0)
        rot.mostrar(pie_curso("Para aislar la pendiente en x, fijemos "
                              "y y cortemos con un plano."), zona="abajo",
                    run_time=0.5)
        tapa = plano_corte3(esp, "y", Y0)
        self.play(FadeIn(tapa, shift=0.3 * DOWN), run_time=1.0)
        self.wait(2.0)

        # --- momento: la curva del corte -------------------------------------
        rot.mostrar(pie_curso("El plano deja una curva sobre la "
                              "superficie: solo x se mueve."), zona="abajo",
                    run_time=0.5)
        corte = curva_corte3(esp, PAISAJE, "y", Y0, color=C_VEC)
        cifra_corte = tag_hud(f"y = {fmt(Y0)}", font_size=20, color=C_VEC)
        cifra_corte.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(Create(corte), FadeIn(cifra_corte), run_time=1.2)
        self.wait(2.8)

        # --- momento: esa curva, en su propia grafica -------------------------
        rot.mostrar(pie_curso("Esa curva es el paisaje visto SOLO en x: "
                              "llevémosla a su propia gráfica."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(esp), FadeOut(sup), FadeOut(tapa), FadeOut(corte),
                  FadeOut(cifra_corte), run_time=0.8)
        g2 = grafica(lambda x: float(PAISAJE(np.array([x, Y0]))),
                    RANGO_CORTE, RANGO_F_CORTE_X, ancho=6.6, alto=3.4,
                    color=C_VEC, etiqueta_x="x", etiqueta_y="f")
        g2.move_to(DOWN * 0.25)
        self.play(FadeIn(g2), run_time=0.9)
        p0_2d = Dot(g2.punto_de(X0), radius=0.08, color=C_VEC)
        self.play(FadeIn(p0_2d, scale=0.4), run_time=0.5)
        self.wait(2.6)

        # --- momento: la pendiente en ese punto es la parcial -----------------
        rot.mostrar(pie_curso("La pendiente de esa curva, justo ahí, es "
                              "la parcial en x."), zona="abajo",
                    run_time=0.5)
        tangente = Line(g2._en(X0 - 0.7, F0 - DFDX * 0.7),
                        g2._en(X0 + 0.7, F0 + DFDX * 0.7),
                        color=C_CIFRA, stroke_width=3.6)
        self.play(Create(tangente), run_time=1.0)
        self.wait(2.6)

        rot.mostrar(formula_pie(r"\frac{\partial f}{\partial x}(x_0, y_0) = "
                                + fmt(DFDX)), zona="abajo", run_time=0.5)
        self.wait(3.4)

        rot.mostrar(pie_curso("Ahora fijemos x y cortemos en la otra "
                              "dirección: y."), zona="abajo", run_time=0.5)
        self.wait(4.4)
