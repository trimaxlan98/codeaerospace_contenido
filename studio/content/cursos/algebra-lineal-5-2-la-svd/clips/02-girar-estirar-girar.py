class Clip2(Scene):
    """5.2.2 - La misma rejilla hace V^T, luego Sigma, luego U: girar,
    estirar, girar. Los tres pasos se encadenan con productos PARCIALES
    porque anim_matriz quiere el estado total desde la identidad. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Girar, estirar, girar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: las dos direcciones de entrada ------------------------
        pl = plano_leccion()
        c = circulo_unidad(pl, color=C_VEC)
        v1 = vector(pl, V1_M, color=C_PROPIO, grosor=5.5, nombre=r"\vec v_1",
                    etiqueta_dir=DOWN)
        v2 = vector(pl, V2_M, color=C_PROPIO, grosor=5.5, nombre=r"\vec v_2",
                    etiqueta_dir=LEFT)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Dos direcciones de entrada muy concretas: "
                              "las que acabarán en los ejes de la elipse."),
                    zona="abajo", run_time=0.5)
        self.play(Create(c), run_time=0.8)
        self.play(GrowArrow(v1.flecha), GrowArrow(v2.flecha),
                  FadeIn(v1.etiqueta), FadeIn(v2.etiqueta), run_time=0.9)
        self.wait(3.2)

        panel, filas = self._panel()

        # --- paso 1: girar --------------------------------------------------
        rot.mostrar(pie_curso("Primero, girar: V transpuesta las lleva a los "
                              "ejes. El círculo sigue siendo un círculo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(panel[0]), FadeIn(filas[0]), run_time=0.5)
        self.wait(0.6)
        self.play(*pl.anim_matriz(PASO_GIRO, v1, v2),
                  Transform(c, c.con_matriz(PASO_GIRO)), run_time=2.0)
        self.wait(2.6)

        # --- paso 2: estirar -------------------------------------------------
        rot.mostrar(pie_curso("Ahora, estirar cada eje por su valor "
                              "singular: uno por 2.56, el otro por 0.98."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(filas[1]), run_time=0.5)
        self.wait(0.6)
        self.play(*pl.anim_matriz(PASO_ESTIRA, v1, v2),
                  Transform(c, c.con_matriz(PASO_ESTIRA)), run_time=2.0)
        self.wait(2.4)

        # --- paso 3: girar otra vez ------------------------------------------
        rot.mostrar(pie_curso("Y girar otra vez: U coloca la elipse donde "
                              "tenía que estar."), zona="abajo", run_time=0.5)
        self.play(FadeIn(filas[2]), run_time=0.5)
        self.wait(0.6)
        self.play(*pl.anim_matriz(PASO_GIRO_2, v1, v2),
                  Transform(c, c.con_matriz(PASO_GIRO_2)), run_time=2.0)
        self.wait(2.4)

        # --- momento: era la misma matriz ------------------------------------
        rot.mostrar(formula_pie(r"M = U\,\Sigma\,V^{T}"), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(c, color=C_VEC, scale_factor=1.04),
                  Indicate(filas, color=C_CALCULO, scale_factor=1.03),
                  run_time=1.0)
        self.wait(3.8)

        rot.mostrar(pie_curso("Toda matriz es eso: un giro, un estiramiento "
                              "y otro giro. Sin excepciones."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

    # -- el panel de la derecha: V^T, Sigma y U, una fila por paso ----------
    def _panel(self):
        """Las tres matrices en columna, con su nombre a la izquierda. Las
        etiquetas van dentro de una caja invisible del MISMO ancho para que
        `panel_derecha` (que centra) no descoloque unas matrices respecto a
        otras."""
        nombres = [MathTex(t, font_size=30, color=C_TITULO)
                   for t in (r"V^{T}", r"\Sigma", r"U")]
        ancho = max(n.width for n in nombres)
        filas = VGroup()
        for nombre, m in zip(nombres, (VT_M, SIGMA_M, U_M)):
            caja = Rectangle(width=ancho, height=0.5, stroke_opacity=0.0,
                             fill_opacity=0.0)
            nombre.move_to(caja)
            filas.add(VGroup(VGroup(caja, nombre),
                             matriz_columnas(m, font_size=26)
                             ).arrange(RIGHT, buff=0.22))
        panel = panel_derecha(*filas, buff=0.26)
        return panel, filas
