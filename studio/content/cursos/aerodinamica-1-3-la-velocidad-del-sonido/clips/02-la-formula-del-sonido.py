class Clip2(Scene):
    """1.3.2 - Deduccion de a = sqrt(gamma R T).

    Del balance a traves del frente sale a^2 = (dp/drho) a entropia
    constante; con gas ideal y proceso isentropico eso es gamma R T. La
    consecuencia es la que importa: `a` no depende de la presion ni de la
    densidad — solo de la temperatura. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("De dónde sale la fórmula")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el balance a traves del frente ----------------------
        paso = MathTex(r"a^2 = \left(\frac{\partial p}{\partial \rho}"
                       r"\right)_{\!s}", font_size=54, color=C_TENUE)
        paso.move_to(UP * 0.55)
        self.play(Write(paso), run_time=1.1)
        rot.mostrar(pie_curso("Del balance de masa y de cantidad de "
                              "movimiento a través del frente sale esto."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Cuánto sube la presión cuando aprietas el "
                              "aire. Y sin generar entropía: el escalón era "
                              "diminuto."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: con gas ideal, se cierra -----------------------------
        formula = MathTex(r"a = \sqrt{\gamma\,R\,T}", font_size=60,
                          color=C_CALCULO)
        formula.move_to(UP * 0.55)
        self.play(TransformMatchingShapes(paso, formula), run_time=1.2)
        rot.mostrar(pie_curso("Con gas ideal y proceso isentrópico, todo se "
                              "reduce a una raíz."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: la consecuencia --------------------------------------
        curva = curva_sonido(ancho=5.6, alto=2.4)
        curva.move_to(DOWN * 1.05)
        self.play(formula.animate.move_to(UP * 2.15).scale(0.62),
                  run_time=0.7)
        self.play(FadeIn(curva.ejes), Create(curva.curva), run_time=1.4)
        rot.mostrar(pie_curso("Ni presión ni densidad aparecen. Solo la "
                              "temperatura."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # Los dos puntos y sus cifras los da la libreria: la curva dibujada y
        # el numero rotulado salen del mismo sqrt(gamma R T).
        marcas = VGroup()
        for t, color in ((T_MAR, C_TRANS), (T_TROPO, C_CALCULO)):
            punto = Dot(curva.punto_de(t), radius=0.068, color=color)
            tag = Text(f"{curva.a(t):.0f} m/s", font=FUENTE_HUD, font_size=17,
                       color=color)
            # Los dos rotulos van ARRIBA del punto: el de la tropopausa cae
            # al pie de la curva, y debajo de el solo esta el eje.
            tag.next_to(punto, UP, buff=0.14)
            if t == T_TROPO:
                tag.shift(RIGHT * 0.22)
            marcas.add(VGroup(punto, tag))
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in marcas],
                              lag_ratio=0.45), run_time=1.2)
        rot.mostrar(pie_curso(f"Al nivel del mar, {A_MAR:.0f} metros por "
                              f"segundo. A once kilómetros, {A_TROPO:.0f}."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso(f"{A_MAR - A_TROPO:.0f} metros por segundo "
                              "menos, solo por hacer frío."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)
