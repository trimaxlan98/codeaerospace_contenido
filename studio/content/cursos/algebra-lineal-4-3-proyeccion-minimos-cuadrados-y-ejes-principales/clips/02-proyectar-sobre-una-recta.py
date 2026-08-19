class Clip2(Scene):
    """4.3.2 - De todos los puntos de una recta, el mas cercano a un dato es
    aquel cuyo error sale perpendicular; y llegar a el es aplicar una matriz
    que aplasta el plano sobre la recta. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Proyectar sobre una recta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la recta -------------------------------------------------
        pl = plano_leccion(unidad=0.8, vivo=True)
        # largo 5.3 unidades: pasa del candidato mas lejano (2.2 u = 4.9
        # unidades, o el punto flotaria fuera de la recta) y se queda corta
        # antes del panel de cifras.
        linea = span_recta(pl, U_REC, color=C_VEC_2, opacidad=0.55,
                           largo=5.3)
        u = vector(pl, U_REC, color=C_VEC_2, nombre=r"\vec u",
                   etiqueta_dir=DOWN, buff_etiqueta=0.30)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Una recta: todos los múltiplos de u."),
                    zona="abajo", run_time=0.5)
        self.play(Create(linea), run_time=0.9)
        self.play(GrowArrow(u.flecha), FadeIn(u.etiqueta), run_time=0.8)
        self.wait(3.0)

        # --- momento: un dato que no está en la recta ---------------------------
        rot.mostrar(pie_curso("Y un dato que no cae en ella. ¿Cuál es el "
                              "punto de la recta más cercano?"),
                    zona="abajo", run_time=0.5)
        d = vector(pl, D_REC, color=C_VEC, nombre=r"\vec d",
                   etiqueta_dir=np.array([-0.7, 0.7, 0.0]))
        self.play(GrowArrow(d.flecha), FadeIn(d.etiqueta), run_time=0.9)
        self.wait(3.6)

        # --- momento: el punto recorre la recta ---------------------------------
        rot.mostrar(pie_curso("Probemos: un punto recorre la recta y "
                              "medimos lo que sobra."), zona="abajo",
                    run_time=0.5)
        # El punto de prueba es cian (una medida); solo cuando cae en el
        # minimo se vuelve verde: ahi ya es el resultado.
        punto_c = Dot(pl.p(CAND_REC[0]), radius=0.09, color=C_CALCULO)
        seg_c = DashedLine(pl.p(D_REC), pl.p(CAND_REC[0]), color=C_J,
                           stroke_width=2.2, dash_length=0.1)
        t_dist = tag_hud("distancia = " + fmt(DIST_CAND[0], 2), font_size=20)
        panel = panel_derecha(t_dist)
        self.play(FadeIn(punto_c), Create(seg_c), FadeIn(panel), run_time=0.9)
        self.wait(1.9)

        self.play(Transform(punto_c, Dot(pl.p(CAND_REC[1]), radius=0.09,
                                         color=C_CALCULO)),
                  Transform(seg_c, DashedLine(pl.p(D_REC), pl.p(CAND_REC[1]),
                                              color=C_J, stroke_width=2.2,
                                              dash_length=0.1)),
                  Transform(t_dist, tag_hud("distancia = "
                                            + fmt(DIST_CAND[1], 2),
                                            font_size=20).move_to(t_dist)),
                  run_time=1.0)
        self.wait(1.9)

        # --- momento: el minimo es el perpendicular -----------------------------
        rot.mostrar(pie_curso("El mínimo llega justo cuando lo que sobra "
                              "sale perpendicular a la recta."),
                    zona="abajo", run_time=0.5)
        self.play(Transform(punto_c, Dot(pl.p(PROY_D), radius=0.09,
                                         color=C_IMG)),
                  Transform(seg_c, DashedLine(pl.p(D_REC), pl.p(PROY_D),
                                              color=C_J, stroke_width=2.2,
                                              dash_length=0.1)),
                  Transform(t_dist, tag_hud("distancia = "
                                            + fmt(DIST_CAND[2], 2),
                                            font_size=20).move_to(t_dist)),
                  run_time=1.3)
        sombra = flecha_libre(pl, (0, 0), PROY_D, color=C_IMG, grosor=5.0)
        esquina = RightAngle(Line(pl.p(PROY_D), pl.p(D_REC)),
                             Line(pl.p(PROY_D), pl.p(PROY_D + U_REC)),
                             length=0.26, color=C_CALCULO, stroke_width=2.4)
        self.play(GrowArrow(sombra), run_time=0.8)
        self.play(Create(esquina), run_time=0.4)
        self.wait(2.2)

        # --- momento: el residuo es ortogonal a la recta ------------------------
        rot.mostrar(pie_curso("Ese resto se llama residuo, y su producto "
                              "punto con u es cero."), zona="abajo",
                    run_time=0.5)
        t_res = tag_hud("residuo . u = " + fmt(DOT_RES, 2), font_size=20)
        panel_2 = panel_derecha(t_res)
        panel_2.next_to(panel, DOWN, buff=0.20).align_to(panel, RIGHT)
        self.play(FadeIn(panel_2, shift=0.15 * LEFT), run_time=0.5)
        self.wait(4.2)

        # --- momento: proyectar es una matriz -----------------------------------
        rot.mostrar(pie_curso("Y proyectar es lineal: hay una matriz que lo "
                              "hace, y aplasta el plano en la recta."),
                    zona="abajo", run_time=0.5)
        mat_p = matriz_columnas(P_PROY, dec=1, font_size=32)
        t_det = tag_hud("det P = " + fmt(DET_P, 1), font_size=19)
        panel_3 = panel_derecha(VGroup(mat_p, t_det).arrange(DOWN, buff=0.22))
        panel_3.next_to(panel, DOWN, buff=0.20).align_to(panel, RIGHT)
        self.play(FadeOut(panel_2), FadeIn(panel_3), run_time=0.6)
        self.play(*pl.anim_matriz(P_PROY), run_time=2.0)
        self.wait(1.9)

        # --- cierre del clip ----------------------------------------------------
        rot.mostrar(pie_curso("Con un dato ya sabemos. ¿Y con catorce, que "
                              "ni siquiera caben en la recta?"),
                    zona="abajo", run_time=0.5)
        self.wait(4.5)
