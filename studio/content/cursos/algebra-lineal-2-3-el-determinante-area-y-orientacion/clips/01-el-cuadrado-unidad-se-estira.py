class Clip1(Scene):
    """2.3.1 - El cuadrado que encierran i y j se convierte en el
    paralelogramo de las columnas; su area es el determinante. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El cuadrado unidad se estira")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el cuadrado unidad ------------------------------------
        pl = plano_leccion()
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        cuadrado = paralelogramo(pl, np.eye(2))
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("î y ĵ encierran un cuadrado. Su área es "
                              "uno: es la unidad de medida."),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(i_hat.flecha), GrowArrow(j_hat.flecha),
                  run_time=0.7)
        self.play(FadeIn(i_hat.etiqueta), FadeIn(j_hat.etiqueta),
                  FadeIn(cuadrado), run_time=0.6)
        cifra = self._cifra("area = " + fmt(cuadrado.area))
        self.play(FadeIn(cifra), run_time=0.4)
        self.wait(4.2)

        # --- momento: la matriz que vamos a aplicar -------------------------
        col_i, col_j = M_ESTIRA[:, 0], M_ESTIRA[:, 1]
        rot.mostrar(pie_curso("Esta matriz manda î a (" + fmt(col_i[0], 0)
                              + ", " + fmt(col_i[1], 0) + ") y ĵ a ("
                              + fmt(col_j[0], 0) + ", " + fmt(col_j[1], 0)
                              + "). Sus columnas, en ámbar y cian."),
                    zona="abajo", run_time=0.5)
        mat = matriz_columnas(M_ESTIRA, font_size=40)
        panel = panel_derecha(mat)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.6)

        # --- momento: la rejilla se deforma y el cuadrado con ella ----------
        rot.mostrar(pie_curso("Mira la rejilla: el cuadrado se estira hasta "
                              "el paralelogramo."),
                    zona="abajo", run_time=0.5)
        estirado = paralelogramo(pl, M_ESTIRA)
        # La cifra se apaga mientras el cuadrado viaja: a medio camino el
        # area no es ni la de antes ni la de despues (no se miente en
        # pantalla), y vuelve ya con el valor calculado.
        self.play(*pl.anim_matriz(M_ESTIRA, i_hat, j_hat, run_time=2.0),
                  Transform(cuadrado, estirado, run_time=2.0),
                  FadeOut(cifra, run_time=0.6))
        i_hat = i_hat.con_matriz(M_ESTIRA)
        j_hat = j_hat.con_matriz(M_ESTIRA)
        cifra = self._cifra("area = " + fmt(estirado.area))
        self.play(FadeIn(cifra), run_time=0.5)
        self.wait(3.4)

        # --- momento: la cuenta ---------------------------------------------
        a, b = M_ESTIRA[0]
        c, d = M_ESTIRA[1]
        rot.mostrar(formula_pie(r"\det M = " + fmt(a, 0) + r" \cdot "
                                + fmt(d, 0) + " - " + fmt(b, 0) + r" \cdot "
                                + fmt(c, 0) + " = " + fmt(DET_ESTIRA)),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(mat.columna(0), color=C_I, scale_factor=1.08),
                  run_time=0.7)
        self.play(Indicate(mat.columna(1), color=C_J, scale_factor=1.08),
                  run_time=0.7)
        self.wait(4.2)

        rot.mostrar(pie_curso("El determinante es eso: el área del "
                              "cuadrado unidad tras el viaje."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(cuadrado, color=C_AREA, scale_factor=1.04),
                  Indicate(cifra, color=C_AREA, scale_factor=1.06),
                  run_time=0.9)
        self.wait(5.4)

    # -- cifra de area, bajo el HUD (con fondo: la rejilla pasa por debajo) --
    def _cifra(self, texto):
        g = _con_fondo(tag_hud(texto, font_size=20), buff=0.13, opacidad=0.82)
        g.to_corner(UL, buff=0.5).shift(DOWN * 0.66)
        return g
