class Clip3(Scene):
    """5.3.3 - Dos arranques distintos convergen a la misma distribucion;
    con solo dos estados, ese mismo hecho se ve como un camino que cae en
    un punto del plano. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Todo camino lleva al mismo sitio")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: dos arranques distintos --------------------------------
        rot.mostrar(pie_curso("Empecemos en dos sitios distintos: modo "
                              "nominal, y eclipse."), zona="abajo",
                    run_time=0.5)
        pos_izq = LEFT * 3.1 + DOWN * 0.2
        pos_der = RIGHT * 3.1 + DOWN * 0.2
        b_n = barras(P0_N, colores=COLORES_ESTADOS, ancho=0.5, alto=1.7,
                    etiquetas=ESTADOS, font_size=14)
        b_n.move_to(pos_izq)
        b_e = barras(P0_E, colores=COLORES_ESTADOS, ancho=0.5, alto=1.7,
                    etiquetas=ESTADOS, font_size=14)
        b_e.move_to(pos_der)
        cap_n = Text("Empieza en N", font_size=16, color=C_TENUE)
        cap_n.next_to(b_n, UP, buff=0.3)
        cap_e = Text("Empieza en E", font_size=16, color=C_TENUE)
        cap_e.next_to(b_e, UP, buff=0.3)
        self.play(FadeIn(b_n), FadeIn(b_e), FadeIn(cap_n), FadeIn(cap_e),
                  run_time=0.9)
        self.wait(4.2)

        # --- momento: la misma matriz, ocho veces ----------------------------
        rot.mostrar(pie_curso("A los dos les aplicamos la misma matriz T, "
                              "una y otra vez."), zona="abajo", run_time=0.5)
        final_n = ITERADOS_N8[PASOS_CONVERGE]
        final_e = ITERADOS_E8[PASOS_CONVERGE]
        self.play(Transform(b_n, b_n.con_valores(final_n)),
                  Transform(b_e, b_e.con_valores(final_e)), run_time=2.0)
        self.wait(2.6)

        # --- momento: llegan casi al mismo sitio -----------------------------
        rot.mostrar(pie_curso("Llegan casi al mismo sitio: de dónde "
                              "empezaste deja de importar."), zona="abajo",
                    run_time=0.5)
        cif_n = VGroup(*[tag_hud(fmt(final_n[i], 2), font_size=14,
                                 color=COLORES_ESTADOS[i])
                        .next_to(b_n.barras[i], UP, buff=0.1)
                        for i in range(3)])
        cif_e = VGroup(*[tag_hud(fmt(final_e[i], 2), font_size=14,
                                 color=COLORES_ESTADOS[i])
                        .next_to(b_e.barras[i], UP, buff=0.1)
                        for i in range(3)])
        self.play(FadeIn(cif_n), FadeIn(cif_e), run_time=0.5)
        self.play(Indicate(b_n, color=C_TITULO, scale_factor=1.04),
                  Indicate(b_e, color=C_TITULO, scale_factor=1.04),
                  run_time=0.9)
        self.wait(3.8)

        # --- momento: transicion a solo dos estados --------------------------
        grupo_barras = VGroup(b_n, b_e, cap_n, cap_e, cif_n, cif_e)
        rot.mostrar(pie_curso("Con solo dos estados, ese mismo camino se "
                              "dibuja en el plano."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(grupo_barras), run_time=0.6)
        pl = plano_leccion(unidad=3.0, vivo=False,
                           centro=LEFT * 1.3 + DOWN * 0.55)
        lbl_x = tag_hud("p(N)", font_size=15, color=C_EJE)
        lbl_x.move_to(pl.p(1.08, -0.14))
        lbl_y = tag_hud("p(no N)", font_size=15, color=C_EJE)
        lbl_y.move_to(pl.p(-0.34, 1.02))
        self.play(FadeIn(pl), FadeIn(lbl_x), FadeIn(lbl_y), run_time=0.9)
        self.wait(2.8)

        # --- momento: cada paso, un punto -------------------------------------
        rot.mostrar(pie_curso("Cada paso de T es un punto nuevo: el "
                              "camino cae, siempre, en el mismo sitio."),
                    zona="abajo", run_time=0.5)
        tray = trayectoria(pl, TRAYECTORIA_N2)
        self.play(Create(tray), run_time=2.2)
        p_estrella = Dot(pl.p(P_ESTACIONARIO_2), radius=0.09, color=C_IMG)
        et_estrella = tag_hud("p*", font_size=16, color=C_IMG)
        et_estrella.next_to(p_estrella, UR, buff=0.08)
        self.play(FadeIn(p_estrella), FadeIn(et_estrella),
                  Flash(p_estrella, color=C_IMG, line_length=0.2),
                  run_time=0.8)
        self.wait(4.8)
