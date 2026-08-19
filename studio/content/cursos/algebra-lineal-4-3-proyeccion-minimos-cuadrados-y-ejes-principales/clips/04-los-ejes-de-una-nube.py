class Clip4(Scene):
    """4.3.4 - Una nube de datos tiene ejes propios: los vectores propios de
    su covarianza. El mayor dice hacia donde se estira; girar el mundo hasta
    ponerlo horizontal endereza el problema. Cierra la leccion y la familia.
    (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Los ejes de una nube")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la nube ---------------------------------------------------
        # unidad 0.85: la nube girada llega a 4.1 unidades en x y ahi tiene
        # que caber ANTES del panel de cifras de la derecha.
        pl = plano_leccion(unidad=0.85, vivo=True)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Medidas de dos sensores, ya centradas. La nube "
                              "no es una bola: está estirada."),
                    zona="abajo", run_time=0.5)
        datos = puntos_nube(pl, NUBE_PCA, color=C_VEC, radio=0.06)
        self.play(LaggedStart(*[FadeIn(p, scale=0.6) for p in datos],
                              lag_ratio=0.02), run_time=1.4)
        self.wait(3.6)

        # --- momento: la covarianza ---------------------------------------------
        rot.mostrar(pie_curso("¿Estirada hacia dónde? Lo dice una matriz que "
                              "sale de los propios datos: la covarianza."),
                    zona="abajo", run_time=0.5)
        et_cov = tag_hud("covarianza", font_size=18, color=C_TENUE)
        mat_cov = matriz_columnas(COV_N, dec=2, font_size=30)
        panel = panel_derecha(VGroup(et_cov, mat_cov).arrange(DOWN, buff=0.18))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.2)

        # --- momento: los ejes principales --------------------------------------
        rot.mostrar(pie_curso("Sus vectores propios son los ejes de la nube. "
                              "El mayor apunta a donde más se estira."),
                    zona="abajo", run_time=0.5)
        # Cada eje mide dos desviaciones tipicas: la raiz de su autovalor.
        e1 = vector(pl, EJES_2SD[0], color=C_PROPIO, nombre=r"\vec e_1",
                    etiqueta_dir=RIGHT, font_size=28)
        e2 = vector(pl, EJES_2SD[1], color=C_PROPIO, nombre=r"\vec e_2",
                    etiqueta_dir=LEFT, font_size=28)
        self.play(GrowArrow(e1.flecha), FadeIn(e1.etiqueta), run_time=0.9)
        self.play(GrowArrow(e2.flecha), FadeIn(e2.etiqueta), run_time=0.7)
        # El rotulo va corto a proposito: una linea larga aqui se mete en el
        # cuadro y le pasa por encima a la punta de e1 cuando la nube gira.
        cifras = VGroup(
            tag_hud("varianza", font_size=18, color=C_TENUE),
            tag_hud("eje 1 : " + fmt(PESO_PCA[0], 0) + " %", font_size=18,
                    color=C_PROPIO),
            tag_hud("eje 2 : " + fmt(PESO_PCA[1], 0) + " %", font_size=18,
                    color=C_PROPIO),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        panel_2 = panel_derecha(cifras)
        panel_2.next_to(panel, DOWN, buff=0.20).align_to(panel, RIGHT)
        self.play(FadeIn(panel_2, shift=0.15 * LEFT), run_time=0.5)
        self.wait(3.4)

        # --- momento: enderezar la nube -----------------------------------------
        rot.mostrar(pie_curso("Gira el mundo hasta poner ese eje en "
                              "horizontal: la nube se endereza sola."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(R_PCA, e1, e2),
                  Transform(datos, puntos_nube(pl, NUBE_GIRADA, color=C_VEC,
                                               radio=0.06)),
                  run_time=2.0)
        self.wait(3.0)

        # --- momento: recap de la familia ---------------------------------------
        rot.mostrar(pie_curso("Aquí cabe la familia entera: una matriz mueve "
                              "la rejilla, y sus ejes propios solo se "
                              "estiran."), zona="abajo", run_time=0.5)
        self.play(FadeOut(datos), FadeOut(panel), FadeOut(panel_2),
                  run_time=0.6)
        # M_RECAP es el estado TOTAL (estirar DESPUES de girar): sobre la
        # pantalla ya girada, e1 y e2 no cambian de direccion.
        self.play(*pl.anim_matriz(M_RECAP, e1, e2), run_time=1.8)
        self.wait(2.6)

        # --- cierre de la leccion y de la familia -------------------------------
        cierre_leccion(self, rot, "Encuentra los ejes",
                       "y el problema se endereza.",
                       "Una flecha, un movimiento, una pregunta al revés y "
                       "los ejes que lo enderezan todo. Hasta aquí.",
                       pl, e1, e2)
