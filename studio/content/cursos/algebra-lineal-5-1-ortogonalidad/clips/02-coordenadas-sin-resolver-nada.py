class Clip2(Scene):
    """5.1.2 - En una base ortonormal (aunque este oblicua respecto a la
    canonica), las coordenadas de un vector son sus sombras: dos productos
    punto y nada de resolver un sistema. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Coordenadas sin resolver nada")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: una base ortonormal, pero oblicua ----------------------
        pl = plano_leccion(vivo=False)
        q1 = vector(pl, Q1_COORD, color=C_I, nombre=r"\vec q_1",
                   etiqueta_dir=DOWN)
        q2 = vector(pl, Q2_COORD, color=C_J, nombre=r"\vec q_2",
                   etiqueta_dir=UP)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Esta base también es perpendicular y mide "
                              "uno, pero no está alineada con los ejes."),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(q1.flecha), GrowArrow(q2.flecha), run_time=0.9)
        self.play(FadeIn(q1.etiqueta), FadeIn(q2.etiqueta), run_time=0.3)
        self.wait(3.2)

        # --- momento: el vector protagonista ----------------------------------
        rot.mostrar(pie_curso("¿Cuáles son las coordenadas de v en esta "
                              "base? No hace falta resolver ningún "
                              "sistema."), zona="abajo", run_time=0.5)
        v = vector(pl, V_COORD, color=C_VEC, nombre=r"\vec v",
                  etiqueta_dir=UP)
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.9)
        self.wait(3.4)

        # --- momento: la sombra sobre q1 ---------------------------------------
        rot.mostrar(pie_curso("Basta proyectar v sobre cada eje: la "
                              "sombra sobre q1 es un producto punto."),
                    zona="abajo", run_time=0.5)
        proy1 = proyeccion_dibujo(pl, V_COORD, Q1_COORD, color=C_I,
                                  color_guia=C_TENUE)
        self.play(Create(proy1.guia), run_time=0.6)
        self.play(GrowArrow(proy1.sombra), run_time=0.7)
        cifra1 = tag_hud("v . q1 = " + fmt(COEF_V_Q1, 1), font_size=19,
                         color=C_I)
        cifra1.next_to(proy1.sombra, UP, buff=0.16)
        self.play(FadeIn(cifra1), run_time=0.4)
        self.wait(3.0)

        # --- momento: la sombra sobre q2 ---------------------------------------
        rot.mostrar(pie_curso("Y la sombra sobre q2, el mismo truco: otro "
                              "producto punto."), zona="abajo",
                    run_time=0.5)
        proy2 = proyeccion_dibujo(pl, V_COORD, Q2_COORD, color=C_J,
                                  color_guia=C_TENUE)
        self.play(Create(proy2.guia), run_time=0.6)
        self.play(GrowArrow(proy2.sombra), run_time=0.7)
        cifra2 = tag_hud("v . q2 = " + fmt(COEF_V_Q2, 1), font_size=19,
                         color=C_J)
        cifra2.next_to(proy2.sombra, LEFT, buff=0.16)
        self.play(FadeIn(cifra2), run_time=0.4)
        self.wait(3.0)

        # --- momento: el panel de coordenadas -----------------------------------
        rot.mostrar(pie_curso("Esas dos sombras SON las coordenadas de v "
                              "en la base q1, q2."), zona="abajo",
                    run_time=0.5)
        columna = vector_columna(COORD_V_BASE, color=C_VEC, dec=1,
                                 font_size=38)
        columna.matriz.get_rows()[0].set_color(C_I)
        columna.matriz.get_rows()[1].set_color(C_J)
        panel = panel_derecha(columna)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(3.8)

        # --- cierre del clip ---------------------------------------------------
        rot.mostrar(pie_curso("En una base ortonormal, coordenada es "
                              "sombra: el producto punto y ya."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(panel, color=C_CALCULO, scale_factor=1.05),
                  run_time=0.8)
        self.wait(4.0)
