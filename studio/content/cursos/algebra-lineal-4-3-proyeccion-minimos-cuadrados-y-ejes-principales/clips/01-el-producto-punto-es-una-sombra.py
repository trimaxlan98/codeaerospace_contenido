class Clip1(Scene):
    """4.3.1 - El producto punto es la sombra de un vector sobre otro por lo
    que mide ese otro; si son perpendiculares, la sombra -y el numero- se
    van a cero. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El producto punto es una sombra")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: dos vectores -------------------------------------------
        pl = plano_leccion(vivo=False)
        v = vector(pl, V_PP, color=C_VEC, nombre=r"\vec v", etiqueta_dir=RIGHT)
        u = vector(pl, U_PP, color=C_VEC_2, nombre=r"\vec u", etiqueta_dir=DOWN)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Dos vectores. Hay una forma de multiplicarlos "
                              "que devuelve un solo número."),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(v.flecha), GrowArrow(u.flecha), run_time=0.9)
        self.play(FadeIn(v.etiqueta), FadeIn(u.etiqueta), run_time=0.3)
        self.wait(3.4)

        # --- momento: en listas, multiplicar y sumar --------------------------
        rot.mostrar(pie_curso("En el idioma de las listas es fácil: "
                              "multiplica y suma."), zona="abajo",
                    run_time=0.5)
        col_v = vector_columna(V_PP, color=C_VEC, font_size=30)
        col_u = vector_columna(U_PP, color=C_VEC_2, font_size=30)
        signo = MathTex(r"\cdot", font_size=32, color=C_TENUE)
        igual = MathTex("=", font_size=32, color=C_TENUE)
        res = MathTex(fmt(DOT_VU, 1), font_size=36, color=C_CALCULO)
        cuenta = VGroup(col_v, signo, col_u, igual, res).arrange(RIGHT,
                                                                buff=0.20)
        panel = panel_derecha(cuenta)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(3.2)

        # --- momento: la sombra ----------------------------------------------
        rot.mostrar(pie_curso("¿Y qué mide ese número? La sombra que v echa "
                              "sobre la recta de u."), zona="abajo",
                    run_time=0.5)
        proy = proyeccion_dibujo(pl, V_PP, U_PP, color=C_IMG, color_guia=C_J)
        self.play(Create(proy.guia), run_time=0.7)
        self.play(GrowArrow(proy.sombra), run_time=0.8)
        t_sombra = tag_hud("sombra = " + fmt(ESC_VU, 2), font_size=18,
                           color=C_IMG)
        t_sombra.next_to(pl.p(PROY_VU / 2.0), DOWN, buff=0.52)
        self.play(FadeIn(t_sombra), run_time=0.4)
        self.wait(3.2)

        # --- momento: la sombra por el largo de u ------------------------------
        rot.mostrar(pie_curso("Esa sombra, por lo que mide u, es "
                              "exactamente el producto punto."),
                    zona="abajo", run_time=0.5)
        detalle = tag_hud(fmt(ESC_VU, 2) + " x " + fmt(NORM_U, 2) + " = "
                          + fmt(ESC_VU * NORM_U, 2), font_size=20)
        panel_2 = panel_derecha(detalle)
        panel_2.next_to(panel, DOWN, buff=0.20).align_to(panel, RIGHT)
        self.play(FadeIn(panel_2, shift=0.15 * LEFT), run_time=0.5)
        self.wait(3.2)

        # --- momento: el angulo -------------------------------------------------
        rot.mostrar(formula_pie(r"\vec v \cdot \vec u = |\vec v|\,"
                                r"|\vec u|\cos\theta"), zona="abajo",
                    run_time=0.5)
        # La cifra del angulo va al panel: el hueco entre v, u y la guia
        # punteada es mas estrecho que el propio rotulo.
        ang = marca_angulo(pl, U_PP, V_PP, radio=0.95, color=C_CALCULO,
                           cifra=False)
        t_ang = tag_hud("angulo = " + fmt(ANG_VU, 0) + " deg", font_size=20)
        panel_3 = panel_derecha(t_ang)
        panel_3.next_to(panel_2, DOWN, buff=0.20).align_to(panel_2, RIGHT)
        self.play(Create(ang.arco), FadeIn(panel_3), run_time=0.7)
        self.wait(3.2)

        # --- momento: perpendicular = cero -------------------------------------
        rot.mostrar(pie_curso("Y un vector perpendicular a u no proyecta "
                              "sombra ninguna: el número es cero."),
                    zona="abajo", run_time=0.5)
        w = vector(pl, W_PP, color=C_VEC, nombre=r"\vec w", etiqueta_dir=LEFT)
        w.set_opacity(0.65)
        # Sin guia punteada: la de w seria colineal con la propia flecha (su
        # sombra es el origen) y solo ensuciaria el trazo rojo.
        ang_w = marca_angulo(pl, U_PP, W_PP, radio=0.55, color=C_CALCULO,
                             cifra=False)
        cifras_w = VGroup(
            tag_hud("w . u = " + fmt(DOT_WU, 1), font_size=20),
            tag_hud(fmt(ANG_WU, 0) + " deg", font_size=20),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras_w.move_to(pl.p(-3.1, 2.1))
        self.play(GrowArrow(w.flecha), FadeIn(w.etiqueta), run_time=0.8)
        self.play(Create(ang_w.arco), FadeIn(cifras_w), run_time=0.6)
        self.wait(3.4)

        # --- cierre del clip ---------------------------------------------------
        rot.mostrar(pie_curso("Producto punto cero significa una sola cosa: "
                              "en ángulo recto."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(VGroup(w, ang_w, cifras_w)), run_time=0.6)
        self.wait(4.2)
