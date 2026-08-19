class Clip2(Scene):
    """2.1.2 - Todo el movimiento del plano cabe en dos datos: a donde va
    i-sombrero y a donde va j-sombrero. Esos dos destinos, puestos en
    columna, SON la matriz. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Basta saber a dónde van î y ĵ")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion()
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Todo vector es una mezcla de î y ĵ. Fíjate "
                              "solo en esas dos."), zona="abajo",
                    run_time=0.5)
        self.play(GrowArrow(i_hat.flecha), FadeIn(i_hat.etiqueta),
                  run_time=0.7)
        self.play(GrowArrow(j_hat.flecha), FadeIn(j_hat.etiqueta),
                  run_time=0.7)
        self.wait(4.6)

        # --- momento: se van con el plano -----------------------------------
        rot.mostrar(pie_curso("Cuando el plano se mueve, î y ĵ se van con "
                              "él."), zona="abajo", run_time=0.5)
        self.wait(1.0)
        self.play(*pl.anim_matriz(M_LECCION, i_hat, j_hat), run_time=2.2)
        # Las coords del objeto animado siguen siendo las viejas: `con_matriz`
        # calcula el destino correcto y de paso les pone la prima.
        self.play(Transform(i_hat, i_hat.con_matriz(
                      M_LECCION, nombre=r"\hat{\imath}\,'")),
                  Transform(j_hat, j_hat.con_matriz(
                      M_LECCION, nombre=r"\hat{\jmath}\,'")),
                  run_time=0.6)
        self.wait(4.4)

        # --- momento: los dos destinos son las columnas ---------------------
        rot.mostrar(pie_curso("A dónde llega î es la primera columna de la "
                              "matriz."), zona="abajo", run_time=0.5)
        mat = matriz_columnas(M_LECCION, font_size=38, h_buff=1.2)
        panel = panel_derecha(mat)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.play(Indicate(i_hat.flecha, color=C_I, scale_factor=1.08),
                  Indicate(mat.columna(0), color=C_I, scale_factor=1.25),
                  run_time=0.9)
        self.wait(4.2)

        rot.mostrar(pie_curso("Y a dónde llega ĵ, la segunda. La matriz es "
                              "eso: dos destinos."), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(j_hat.flecha, color=C_J, scale_factor=1.08),
                  Indicate(mat.columna(1), color=C_J, scale_factor=1.25),
                  run_time=0.9)
        self.wait(4.4)

        rot.mostrar(pie_curso("Cuatro números bastan para mover el plano "
                              "entero."), zona="abajo", run_time=0.5)
        self.wait(5.4)
