class Clip3(Scene):
    """1.2.3 - El corte perpendicular (x = x0 fijo) da la otra parcial;
    las dos, juntas, quedan en el panel. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Cortar con y: ∂f/∂y")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el corte perpendicular ----------------------------------
        esp = espacio_leccion()
        sup = superficie3(esp, PAISAJE, n=15)
        self.play(FadeIn(esp), FadeIn(sup), run_time=1.0)
        rot.mostrar(pie_curso("Ahora fijemos x y cortemos "
                              "perpendicular al primero."), zona="abajo",
                    run_time=0.5)
        tapa = plano_corte3(esp, "x", X0)
        self.play(FadeIn(tapa, shift=0.3 * LEFT), run_time=1.0)
        self.wait(2.0)

        rot.mostrar(pie_curso("Esta vez es y quien se mueve; x queda "
                              "congelado."), zona="abajo", run_time=0.5)
        corte = curva_corte3(esp, PAISAJE, "x", X0, color=C_VEC)
        cifra_corte = tag_hud(f"x = {fmt(X0)}", font_size=20, color=C_VEC)
        cifra_corte.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(Create(corte), FadeIn(cifra_corte), run_time=1.2)
        self.wait(2.6)

        # --- momento: esa curva, en su propia grafica ---------------------------
        rot.mostrar(pie_curso("Otra vez: llevamos el corte a su propia "
                              "gráfica."), zona="abajo", run_time=0.5)
        self.play(FadeOut(esp), FadeOut(sup), FadeOut(tapa), FadeOut(corte),
                  FadeOut(cifra_corte), run_time=0.8)
        g3 = grafica(lambda y: float(PAISAJE(np.array([X0, y]))),
                    RANGO_CORTE, RANGO_F_CORTE_Y, ancho=6.6, alto=3.4,
                    color=C_VEC, etiqueta_x="y", etiqueta_y="f")
        g3.move_to(DOWN * 0.25)
        self.play(FadeIn(g3), run_time=0.9)
        p0_2d = Dot(g3.punto_de(Y0), radius=0.08, color=C_VEC)
        self.play(FadeIn(p0_2d, scale=0.4), run_time=0.5)
        self.wait(2.4)

        rot.mostrar(pie_curso("Su pendiente en el punto es la parcial "
                              "en y."), zona="abajo", run_time=0.5)
        tangente = Line(g3._en(Y0 - 0.7, F0 - DFDY * 0.7),
                        g3._en(Y0 + 0.7, F0 + DFDY * 0.7),
                        color=C_CIFRA, stroke_width=3.6)
        self.play(Create(tangente), run_time=1.0)
        self.wait(2.4)

        rot.mostrar(formula_pie(r"\frac{\partial f}{\partial y}(x_0, y_0) = "
                                + fmt(DFDY)), zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- momento: las dos parciales, juntas en el panel -----------------
        rot.mostrar(pie_curso("Las dos, juntas, describen cómo se "
                              "inclina el paisaje justo ahí."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(g3), FadeOut(tangente), FadeOut(p0_2d),
                  run_time=0.7)
        pl = plano_leccion()
        mapa = curvas_nivel(pl, PAISAJE, opacidad=0.5)
        p0dot = pl.punto(P0, color=C_VEC)
        panel = panel_derecha(
            MathTex(r"\frac{\partial f}{\partial x} = " + fmt(DFDX),
                   font_size=32, color=C_CIFRA),
            MathTex(r"\frac{\partial f}{\partial y} = " + fmt(DFDY),
                   font_size=32, color=C_CIFRA))
        self.play(FadeIn(pl), FadeIn(mapa), FadeIn(p0dot), run_time=0.9)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.6)

        rot.mostrar(pie_curso("Con esas dos pendientes armaremos el "
                              "plano tangente."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
