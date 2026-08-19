class Clip2(Scene):
    """5.3.2 - La distribucion de hoy p0 = (1, 0, 0) se mueve con T: tras
    uno, dos y cinco pasos, las barras casi dejan de moverse. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La matriz mueve la distribución")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: T queda a mano, como referencia ------------------------
        etiqueta_t = tag_hud("T", font_size=18, color=C_TENUE)
        mat = matriz_columnas(T, colores=COLORES_ESTADOS, font_size=26)
        panel = panel_derecha(etiqueta_t, mat, buff=0.16)
        self.play(FadeIn(panel), run_time=0.6)

        # --- momento: hoy, toda la probabilidad en Nominal --------------------
        rot.mostrar(pie_curso("Hoy el satélite está en modo nominal: toda "
                              "la probabilidad en un solo estado."),
                    zona="abajo", run_time=0.5)
        b = barras(P0_N, colores=COLORES_ESTADOS, ancho=0.85, alto=2.5,
                  etiquetas=ESTADOS, font_size=18)
        b.move_to(DOWN * 0.55 + LEFT * 0.6)

        def cifras_de(bb, valores):
            g = VGroup()
            for i, r in enumerate(bb.barras):
                t = tag_hud(fmt(valores[i], 2), font_size=15,
                           color=COLORES_ESTADOS[i])
                t.next_to(r, UP, buff=0.12)
                g.add(t)
            return g

        cifras = cifras_de(b, P0_N)
        paso = tag_hud("k = 0", font_size=18, color=C_TENUE)
        paso.to_corner(UL, buff=0.5).shift(DOWN * 0.62)
        self.play(FadeIn(b), FadeIn(cifras), FadeIn(paso), run_time=0.8)
        self.wait(4.0)

        # -- avanzar un paso de la iteracion (nunca se reasigna b: Transform
        # deja las barras y la linea base con sus puntos NUEVOS, y
        # con_valores() solo necesita esa posicion, no el .valores viejo) --
        def avanza(valores, texto_paso):
            nonlocal cifras, paso
            nuevo_b = b.con_valores(valores)
            nuevas_cifras = cifras_de(nuevo_b, valores)
            nuevo_paso = tag_hud(texto_paso, font_size=18, color=C_TENUE)
            nuevo_paso.move_to(paso)
            self.play(Transform(b, nuevo_b), FadeOut(cifras), FadeOut(paso),
                      run_time=1.1)
            self.play(FadeIn(nuevas_cifras), FadeIn(nuevo_paso), run_time=0.4)
            cifras, paso = nuevas_cifras, nuevo_paso

        # --- momento: un paso -------------------------------------------------
        rot.mostrar(pie_curso("Mañana: multiplicamos por T. p uno es T "
                              "por p cero."), zona="abajo", run_time=0.5)
        avanza(ITERADOS_N[1], "k = 1")
        self.wait(3.6)

        # --- momento: dos pasos -------------------------------------------------
        rot.mostrar(pie_curso("Pasado mañana, otra vez T: la probabilidad "
                              "se sigue repartiendo."), zona="abajo",
                    run_time=0.5)
        avanza(ITERADOS_N[2], "k = 2")
        self.wait(3.6)

        # --- momento: cinco pasos ------------------------------------------------
        rot.mostrar(pie_curso("Repite la cuenta cinco veces: las barras "
                              "casi no se mueven más."), zona="abajo",
                    run_time=0.5)
        avanza(ITERADOS_N[PASOS_CLIP2], "k = " + str(PASOS_CLIP2))
        self.wait(4.4)

        rot.mostrar(pie_curso("La matriz de hoy escribe la distribución "
                              "de mañana. Una y otra vez."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
