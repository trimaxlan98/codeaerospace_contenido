class Clip3(Scene):
    """5.2.3 - El cociente sigma1/sigma2 es el numero de condicion: con 1.35
    la elipse es casi un circulo; con 25.6 es una aguja y dos entradas muy
    distintas dan casi la misma salida. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Cuánto estira: el número de condición")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la pregunta -------------------------------------------
        pl = plano_leccion()
        c = circulo_unidad(pl, color=C_VEC)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("¿Cuánto estira una matriz? Depende de la "
                              "dirección. Y esa diferencia importa."),
                    zona="abajo", run_time=0.5)
        self.play(Create(c), run_time=0.9)
        self.wait(3.6)

        # --- momento: una matriz que reparte bien ---------------------------
        rot.mostrar(pie_curso("Esta reparte bien: estira 1.93 por un lado y "
                              "1.43 por el otro."), zona="abajo",
                    run_time=0.5)
        panel_buena = self._panel(A_BUENA, S_BUENA, COND_BUENA)
        self.play(FadeIn(panel_buena, shift=0.15 * LEFT), run_time=0.6)
        self.wait(0.6)
        self.play(*pl.anim_matriz(A_BUENA),
                  Transform(c, c.con_matriz(A_BUENA)), run_time=2.0)
        self.wait(2.4)

        rot.mostrar(pie_curso("El cociente entre los dos vale 1.35: la "
                              "elipse casi no se distingue del círculo."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(panel_buena, color=C_PROPIO, scale_factor=1.04),
                  run_time=0.9)
        self.wait(4.2)

        # --- momento: otra matriz y dos entradas distintas -------------------
        rot.mostrar(pie_curso("Ahora otra matriz, y dos entradas bien "
                              "separadas: una distancia de 1.50."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(np.eye(2)),
                  Transform(c, c.con_matriz(np.eye(2))), run_time=1.2)
        panel_mala = self._panel(A_MALA, S_MALA, COND_MALA)
        x1 = vector(pl, X_ERR, color=C_VEC, nombre=r"\vec x_1",
                    etiqueta_dir=DOWN)
        x2 = vector(pl, X_ERR_2, color=C_VEC_2, nombre=r"\vec x_2",
                    etiqueta_dir=UP)
        seg = Line(pl.p(X_ERR), pl.p(X_ERR_2), color=C_IMG, stroke_width=4.0)
        caja, lineas = self._caja_distancias()
        self.play(FadeOut(panel_buena), FadeIn(panel_mala), run_time=0.6)
        self.play(GrowArrow(x1.flecha), GrowArrow(x2.flecha),
                  FadeIn(x1.etiqueta), FadeIn(x2.etiqueta), run_time=0.9)
        self.play(Create(seg), FadeIn(caja[0]), FadeIn(lineas[0]),
                  run_time=0.6)
        self.wait(2.4)

        # --- momento: la aguja -----------------------------------------------
        rot.mostrar(pie_curso("Casi aplasta el plano: el círculo sale hecho "
                              "una aguja y las dos entradas se juntan."),
                    zona="abajo", run_time=0.5)
        self.wait(0.6)
        self.play(*pl.anim_matriz(A_MALA, x1, x2),
                  Transform(c, c.con_matriz(A_MALA)),
                  Transform(seg, Line(pl.p(A_MALA @ X_ERR),
                                      pl.p(A_MALA @ X_ERR_2), color=C_IMG,
                                      stroke_width=4.0)), run_time=2.2)
        self.play(FadeIn(lineas[1]), run_time=0.5)
        self.wait(2.2)

        # --- momento: la moraleja --------------------------------------------
        rot.mostrar(pie_curso("Al revés: un error mínimo en la salida "
                              "desbarata la entrada. La matriz lo amplifica."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(lineas, color=C_IMG, scale_factor=1.05),
                  Indicate(panel_mala, color=C_PROPIO, scale_factor=1.04),
                  run_time=0.9)
        self.wait(4.0)

        rot.mostrar(pie_curso("Cuánto lo amplifica es el número de "
                              "condición: sigma uno entre sigma dos."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

    # -- la matriz, sus valores singulares y su condicion -------------------
    def _panel(self, m, s, cond):
        sigmas = MathTex(r"\sigma_1 = " + fmt(s[0], 2) + r",\quad "
                         r"\sigma_2 = " + fmt(s[1], 2), font_size=26,
                         color=C_CALCULO)
        condicion = MathTex(r"\mathrm{cond} = " + fmt(cond, 2), font_size=32,
                            color=C_PROPIO)
        return panel_derecha(matriz_columnas(m, font_size=30), sigmas,
                             condicion, buff=0.26)

    # -- las dos distancias, arriba a la izquierda --------------------------
    def _caja_distancias(self):
        """Antes y despues, una debajo de otra. Se construyen juntas (para
        que el fondo no cambie de tamaño a media escena) y se encienden por
        separado."""
        antes = MathTex(r"\|\vec x_1 - \vec x_2\| = " + fmt(D_ANTES, 2),
                        font_size=28, color=C_VEC_2)
        despues = MathTex(r"\|A\vec x_1 - A\vec x_2\| = "
                          + fmt(D_DESPUES, 2), font_size=28, color=C_IMG)
        lineas = VGroup(antes, despues).arrange(DOWN, buff=0.24,
                                                aligned_edge=LEFT)
        caja = _con_fondo(lineas, buff=0.16, opacidad=0.78)
        caja.to_corner(UL, buff=0.5).shift(DOWN * 1.05)
        return caja, lineas
