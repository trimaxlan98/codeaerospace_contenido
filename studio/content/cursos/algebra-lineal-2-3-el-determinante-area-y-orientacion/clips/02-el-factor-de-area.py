class Clip2(Scene):
    """2.3.2 - El determinante no es cosa del cuadrado unidad: TODA area del
    plano se multiplica por el mismo factor (y con det < 1, encoge). (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El factor de área")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: una figura cualquiera ---------------------------------
        pl = plano_leccion()
        figura = celdas(pl, np.eye(2), FIGURA)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("El cuadrado unidad no era especial. "
                              "Tomemos tres celdas cualesquiera."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(figura), run_time=0.8)
        cifra = self._cifra("area celda = " + fmt(figura.area_celda), 0)
        self.play(FadeIn(cifra), run_time=0.4)
        self.wait(3.0)

        # --- momento: la misma matriz del clip anterior ---------------------
        rot.mostrar(pie_curso("Aplicamos la matriz de antes y miramos qué "
                              "le pasa a cada celda."), zona="abajo",
                    run_time=0.5)
        panel = panel_derecha(matriz_columnas(M_ESTIRA, font_size=40))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(1.4)
        estirada = celdas(pl, M_ESTIRA, FIGURA)
        # La cifra se apaga durante el estiron: a medio camino el area de la
        # celda no es ni uno ni tres (en pantalla no se miente).
        self.play(*pl.anim_matriz(M_ESTIRA, run_time=2.0),
                  Transform(figura, estirada, run_time=2.0),
                  FadeOut(cifra, run_time=0.6))
        cifra = self._cifra("area celda = " + fmt(estirada.area_celda), 0)
        self.play(FadeIn(cifra), run_time=0.5)

        # --- momento: el factor es el mismo para todas ----------------------
        rot.mostrar(pie_curso("Cada celda pasó de área uno a área tres. "
                              "Todas, por el mismo número."),
                    zona="abajo", run_time=0.5)
        factor = self._cifra("factor = x " + fmt(DET_ESTIRA), 1)
        self.play(FadeIn(factor), run_time=0.4)
        self.wait(4.2)

        rot.mostrar(pie_curso("Toda figura se cubre con celdas: toda área "
                              "escala por ese factor."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(figura, color=C_AREA, scale_factor=1.03),
                  Indicate(factor, color=C_AREA, scale_factor=1.06),
                  run_time=0.9)
        self.wait(4.0)

        # --- momento: un determinante menor que uno encoge ------------------
        rot.mostrar(pie_curso("¿Y si el factor es menor que uno? Volvamos y "
                              "probemos otra matriz."), zona="abajo",
                    run_time=0.5)
        identidad = celdas(pl, np.eye(2), FIGURA)
        self.play(*pl.anim_matriz(np.eye(2), run_time=1.4),
                  Transform(figura, identidad, run_time=1.4),
                  FadeOut(panel, run_time=0.6), FadeOut(factor, run_time=0.6),
                  FadeOut(cifra, run_time=0.5))
        cifra = self._cifra("area celda = " + fmt(identidad.area_celda), 0)
        panel_2 = panel_derecha(matriz_columnas(M_ENCOGE, font_size=40))
        self.play(FadeIn(cifra), FadeIn(panel_2, shift=0.15 * LEFT),
                  run_time=0.6)
        self.wait(1.2)
        encogida = celdas(pl, M_ENCOGE, FIGURA)
        self.play(*pl.anim_matriz(M_ENCOGE, run_time=1.8),
                  Transform(figura, encogida, run_time=1.8),
                  FadeOut(cifra, run_time=0.6))
        cifra = self._cifra("area celda = " + fmt(encogida.area_celda), 0)
        self.play(FadeIn(cifra),
                  FadeIn(self._cifra("factor = x " + fmt(DET_ENCOGE), 1)),
                  run_time=0.5)
        self.wait(1.6)

        rot.mostrar(pie_curso("Media unidad por cada unidad: un "
                              "determinante menor que uno comprime."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

    # -- cifras bajo el HUD, con fondo (la rejilla pasa por debajo) ---------
    def _cifra(self, texto, fila=0):
        g = _con_fondo(tag_hud(texto, font_size=20), buff=0.13, opacidad=0.82)
        g.to_corner(UL, buff=0.5).shift(DOWN * (0.66 + 0.46 * fila))
        return g
