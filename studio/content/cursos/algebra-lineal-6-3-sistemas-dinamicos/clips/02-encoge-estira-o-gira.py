class Clip2(Scene):
    """6.3.2 - Tres matrices en tres mini-planos: |lambda| < 1 encoge (y el
    angulo la hace espiral), > 1 estira una direccion (silla), = 1 solo
    gira. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Encoge, estira o gira")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Tres mini-planos. plano_leccion() usa el alcance de la familia (12
        # unidades) y tres rejillas asi se cruzarian: aqui se llama a
        # plano() directo, con el alcance y la unidad de la tabla.
        def mini(centro, M):
            pl = plano(unidad=UNIDAD_MINI, alcance=ALCANCE_MINI)
            pl.move_to(centro)
            mat = matriz_columnas(M, dec=2, font_size=22, h_buff=0.7,
                                  v_buff=0.55)
            mat.move_to(centro + ALTO_MATRIZ_MINI)
            _, mod, ang = autos_complejos(M)
            cif = MathTex(r"|\lambda| = " + fmt(mod, 2) + r"\quad "
                          + fmt(ang, 0) + r"^\circ", font_size=26,
                          color=C_CALCULO)
            cif.move_to(centro + ALTO_CIFRA_MINI)
            return pl, mat, cif

        izq, mat_i, cif_i = mini(CENTROS_MINI[0], A_CONTRAE)
        cen, mat_c, cif_c = mini(CENTROS_MINI[1], A_SILLA)
        der, mat_d, cif_d = mini(CENTROS_MINI[2], A_GIRA)

        rot.mostrar(pie_curso("Tres matrices distintas. Tres destinos "
                              "distintos para el mismo sistema."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(izq), FadeIn(cen), FadeIn(der), run_time=1.1)
        self.wait(3.8)

        # --- momento: la contractiva ---------------------------------------
        rot.mostrar(pie_curso("La primera encoge un poco y gira: el estado "
                              "cae en espiral hacia el cero."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(mat_i), run_time=0.5)
        self.play(*izq.anim_matriz(A_CONTRAE), run_time=1.3)
        self.play(*izq.anim_matriz(np.eye(2)), run_time=0.7)
        tr_i = trayectoria(izq, TRAY_CONTRAE_MINI, color=C_VEC, radio=0.055,
                           grosor=2.0)
        self.play(Create(tr_i.segmentos), FadeIn(tr_i.puntos), run_time=1.4)
        self.play(FadeIn(cif_i), run_time=0.5)
        self.wait(1.4)

        # --- momento: la silla ---------------------------------------------
        rot.mostrar(pie_curso("La segunda estira una dirección y encoge la "
                              "otra: una silla de montar."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(mat_c), run_time=0.5)
        self.play(*cen.anim_matriz(A_SILLA), run_time=1.3)
        self.play(*cen.anim_matriz(np.eye(2)), run_time=0.7)
        tr_c = VGroup(*[trayectoria(cen, t, color=C_VEC, radio=0.055,
                                    grosor=2.0) for t in TRAY_SILLA_MINI])
        self.play(*[Create(t.segmentos) for t in tr_c],
                  *[FadeIn(t.puntos) for t in tr_c], run_time=1.4)
        self.play(FadeIn(cif_c), run_time=0.5)
        self.wait(1.4)

        # --- momento: la rotacion pura --------------------------------------
        rot.mostrar(pie_curso("La tercera solo gira: ni encoge ni estira. "
                              "El estado da vueltas para siempre."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(mat_d), run_time=0.5)
        self.play(*der.anim_matriz(A_GIRA), run_time=1.3)
        self.play(*der.anim_matriz(np.eye(2)), run_time=0.7)
        tr_d = trayectoria(der, TRAY_GIRA_MINI, color=C_VEC, radio=0.055,
                           grosor=2.0)
        self.play(Create(tr_d.segmentos), FadeIn(tr_d.puntos), run_time=1.4)
        self.play(FadeIn(cif_d), run_time=0.5)
        self.wait(1.4)

        # --- momento: el veredicto ------------------------------------------
        rot.mostrar(pie_curso("El módulo del autovalor decide el destino: "
                              "menor que uno cae, mayor que uno se escapa."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(cif_i, color=C_CALCULO, scale_factor=1.12),
                  run_time=0.8)
        self.play(Indicate(cif_c, color=C_CALCULO, scale_factor=1.12),
                  run_time=0.8)
        self.wait(3.6)

        rot.mostrar(pie_curso("Y el ángulo dice si además da vueltas por el "
                              "camino. Con módulo uno exacto, solo gira."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(cif_d, color=C_CALCULO, scale_factor=1.12),
                  run_time=0.8)
        self.wait(4.4)
