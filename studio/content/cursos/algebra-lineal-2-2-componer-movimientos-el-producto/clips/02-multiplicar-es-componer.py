class Clip2(Scene):
    """2.2.2 - El producto por columnas: cada columna de B A es B aplicada
    a la columna correspondiente de A. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Multiplicar es componer")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: i y j otra vez -----------------------------------
        pl = plano_leccion()
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("î y ĵ, otra vez. Primero les aplicamos "
                              "A."), zona="abajo", run_time=0.5)
        self.play(GrowArrow(i_hat.flecha), FadeIn(i_hat.etiqueta),
                  GrowArrow(j_hat.flecha), FadeIn(j_hat.etiqueta),
                  run_time=0.8)
        self.wait(3.2)

        # --- momento: A convierte i, j en sus columnas ----------------------
        self.play(*pl.anim_matriz(A, i_hat, j_hat), run_time=1.8)
        # h_buff mayor que el default: A tiene una entrada negativa y con el
        # espaciado por defecto el signo "-" queda pegado al numero de al
        # lado (se ve "0.87-0.50" sin aire entre columnas).
        mat_a = matriz_columnas(A, font_size=34, h_buff=1.2)
        panel_a = panel_derecha(tag_hud("A"), mat_a)
        self.play(FadeIn(panel_a, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.6)

        rot.mostrar(pie_curso("Esas dos flechas SON las columnas de A. "
                              "Ahora aplícales B."), zona="abajo",
                    run_time=0.5)
        self.wait(0.8)
        # M total desde la identidad: i_hat y j_hat nunca se reasignaron,
        # asi que sus coords siguen siendo (1,0) y (0,1); B A @ esas coords
        # aterriza exactamente en la columna de B A que le toca a cada uno.
        self.play(*pl.anim_matriz(BA, i_hat, j_hat), run_time=2.0)
        self.wait(3.4)

        # --- momento: las columnas del producto -----------------------------
        rot.mostrar(pie_curso("Cada columna de A, movida por B, aterriza "
                              "justo en la columna del producto."),
                    zona="abajo", run_time=0.5)
        mat_ba = matriz_columnas(BA, font_size=34)
        panel_ba = panel_derecha(tag_hud("B A"), mat_ba)
        self.play(FadeOut(panel_a), FadeIn(panel_ba, shift=0.15 * LEFT),
                  run_time=0.7)
        self.wait(3.6)

        self.play(Indicate(i_hat.flecha, color=C_I, scale_factor=1.08),
                  Indicate(mat_ba.columna(0), color=C_I, scale_factor=1.2),
                  run_time=0.9)
        self.play(Indicate(j_hat.flecha, color=C_J, scale_factor=1.08),
                  Indicate(mat_ba.columna(1), color=C_J, scale_factor=1.2),
                  run_time=0.9)
        self.wait(3.4)

        rot.mostrar(pie_curso("Multiplicar matrices es aplicar la "
                              "segunda a las columnas de la primera."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
