class Clip3(Scene):
    """4.3.3 - Catorce lecturas con deriva no caben en ninguna recta; la de
    minimos cuadrados es la unica que hace minima la suma de los cuadrados
    de lo que sobra, y recupera la deriva real. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La recta que mejor ajusta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion(unidad=0.8, vivo=False)

        def residuos_de(m, b):
            """Los catorce restos verticales: del dato a la recta."""
            return VGroup(*[Line(pl.p(x, y), pl.p(x, m * x + b),
                                 color=C_AREA, stroke_width=3.4)
                            for (x, y) in PTS_TELE])

        # --- momento: la telemetria ------------------------------------------
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Catorce lecturas de un sensor. Hay deriva, "
                              "pero también ruido."), zona="abajo",
                    run_time=0.5)
        datos = puntos_nube(pl, PTS_TELE, color=C_VEC, radio=0.075)
        self.play(LaggedStart(*[FadeIn(p, scale=0.6) for p in datos],
                              lag_ratio=0.06), run_time=1.2)
        self.wait(4.2)

        # --- momento: una recta cualquiera deja un resto ------------------------
        rot.mostrar(pie_curso("Ninguna recta pasa por todas. Cada una deja "
                              "un resto en cada punto."), zona="abajo",
                    run_time=0.5)
        m0, b0 = CAND_RECTAS[0]
        ajuste = recta(pl, m0, b0, x0=-3.2, x1=3.2, color=C_CALCULO,
                       grosor=3.4)
        restos = residuos_de(m0, b0)
        t_err = tag_hud("error = " + fmt(ERRORES[0], 1), font_size=20,
                        color=C_AREA)
        panel = panel_derecha(t_err)
        self.play(Create(ajuste), run_time=0.9)
        self.play(LaggedStart(*[Create(r) for r in restos], lag_ratio=0.05),
                  FadeIn(panel), run_time=1.0)
        self.wait(2.6)

        # --- momento: inclinarla baja el error ----------------------------------
        rot.mostrar(pie_curso("Mínimos cuadrados suma esos restos al "
                              "cuadrado y busca el total más pequeño."),
                    zona="abajo", run_time=0.5)
        m1, b1 = CAND_RECTAS[1]
        self.play(Transform(ajuste, recta(pl, m1, b1, x0=-3.2, x1=3.2,
                                          color=C_CALCULO, grosor=3.4)),
                  Transform(restos, residuos_de(m1, b1)),
                  Transform(t_err, tag_hud("error = " + fmt(ERRORES[1], 1),
                                           font_size=20,
                                           color=C_AREA).move_to(t_err)),
                  run_time=1.4)
        self.wait(4.0)

        # --- momento: la ganadora -----------------------------------------------
        rot.mostrar(pie_curso("Y hay una sola que lo consigue. Esta."),
                    zona="abajo", run_time=0.5)
        self.play(Transform(ajuste, recta(pl, M_FIT, B_FIT, x0=-3.2, x1=3.2,
                                          color=C_IMG, grosor=4.0)),
                  Transform(restos, residuos_de(M_FIT, B_FIT)),
                  Transform(t_err, tag_hud("error = " + fmt(ERRORES[2], 1),
                                           font_size=20,
                                           color=C_AREA).move_to(t_err)),
                  run_time=1.5)
        t_recta = tag_hud("y = " + fmt(M_FIT, 2) + " x + " + fmt(B_FIT, 2),
                          font_size=20, color=C_IMG)
        panel_2 = panel_derecha(t_recta)
        panel_2.next_to(panel, DOWN, buff=0.20).align_to(panel, RIGHT)
        self.play(FadeIn(panel_2, shift=0.15 * LEFT), run_time=0.5)
        self.wait(2.8)

        # --- momento: la pendiente ES la deriva ----------------------------------
        rot.mostrar(pie_curso("Esa pendiente no es un adorno: es la deriva "
                              "real del sensor, medida."), zona="abajo",
                    run_time=0.5)
        t_real = tag_hud("deriva real = " + fmt(M_REAL, 2), font_size=20)
        panel_3 = panel_derecha(t_real)
        panel_3.next_to(panel_2, DOWN, buff=0.20).align_to(panel_2, RIGHT)
        self.play(FadeIn(panel_3, shift=0.15 * LEFT), run_time=0.5)
        self.play(Indicate(ajuste, color=C_IMG, scale_factor=1.03),
                  run_time=0.8)
        self.wait(4.1)

        # --- cierre del clip ------------------------------------------------------
        rot.mostrar(pie_curso("Ajustar es proyectar: la recta más cercana a "
                              "unos datos que no caben en ninguna."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
