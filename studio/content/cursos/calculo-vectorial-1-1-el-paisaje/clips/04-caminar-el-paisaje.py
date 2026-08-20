class Clip4(Scene):
    """1.1.4 - Pasear el mapa con altimetro: cruzar niveles es subir,
    bordearlos es mantener la altura. Cierre de la leccion. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Caminar el paisaje")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mapa y el altimetro ------------------------------
        pl = plano_leccion()
        mapa = curvas_nivel(pl, PAISAJE, niveles=NIVELES, n=100,
                            opacidad=0.75)
        self.play(FadeIn(pl), FadeIn(mapa), run_time=1.0)
        rot.mostrar(pie_curso("Paseemos por el mapa con un altímetro en "
                              "la mano."), zona="abajo", run_time=0.5)

        t = ValueTracker(0.0)
        dot = Dot(pl.p(CAM_SUBIDA(0)), radius=0.09, color=C_VEC)
        dot.add_updater(lambda d: d.move_to(pl.p(CAM_SUBIDA(
            t.get_value()))))
        alti = DecimalNumber(PAISAJE(CAM_SUBIDA(0)), num_decimal_places=2,
                             color=C_CALCULO, font_size=34)
        etiqueta = tag_hud("altimetro f =", font_size=20)
        alti.add_updater(lambda a: a.set_value(PAISAJE(CAM_SUBIDA(
            t.get_value()))))
        grupo_alti = VGroup(etiqueta, alti).arrange(RIGHT, buff=0.18)
        grupo_alti.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        alti.add_updater(lambda a: a.next_to(etiqueta, RIGHT, buff=0.18))
        self.play(FadeIn(dot, scale=0.5), FadeIn(grupo_alti), run_time=0.7)
        self.wait(2.8)

        # --- momento: cruzar niveles es subir -----------------------------
        rot.mostrar(pie_curso("Rumbo a la cima: cada curva de nivel "
                              "cruzada es altura ganada."), zona="abajo",
                    run_time=0.5)
        ruta = camino(pl, CAM_SUBIDA, color=C_VEC, grosor=2.6, flechas=2)
        self.play(Create(ruta.trazo), run_time=0.6)
        self.play(t.animate.set_value(1.0), run_time=4.0, rate_func=linear)
        self.wait(2.6)

        # --- momento: bordear el nivel es no subir ------------------------
        rot.mostrar(pie_curso("Ahora bordeando una curva de nivel: el "
                              "altímetro se congela."), zona="abajo",
                    run_time=0.5)
        dot.clear_updaters()
        alti.clear_updaters()
        s = ValueTracker(0.0)
        dot.add_updater(lambda d: d.move_to(pl.p(CAM_NIVEL(
            s.get_value()))))
        alti.add_updater(lambda a: a.set_value(PAISAJE(CAM_NIVEL(
            s.get_value()))))
        alti.add_updater(lambda a: a.next_to(etiqueta, RIGHT, buff=0.18))
        self.play(dot.animate.move_to(pl.p(CAM_NIVEL(0))), run_time=0.01)
        anillo = camino(pl, CAM_NIVEL, color=C_FLUJO, grosor=2.6)
        self.play(Create(anillo.trazo), run_time=0.8)
        self.play(s.animate.set_value(1.0), run_time=4.0, rate_func=linear)
        self.wait(2.2)

        # --- cierre -------------------------------------------------------
        dot.clear_updaters()
        alti.clear_updaters()
        cierre_leccion(self, rot,
                       "Una función de dos variables es un paisaje.",
                       "Las curvas de nivel son su mapa.",
                       "Siguiente lección: cortar el paisaje para derivarlo.",
                       pl, mapa, ruta, anillo, dot, grupo_alti)
