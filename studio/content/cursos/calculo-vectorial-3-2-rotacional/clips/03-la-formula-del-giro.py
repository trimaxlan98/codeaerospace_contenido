class Clip3(Scene):
    """3.2.3 - La formula del rotacional descompuesta termino a termino
    sobre el rotor, y comprobada de nuevo en la cizalla (-1.0) y en el
    radial, que no gira en absoluto (0.0). (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La fórmula del giro")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el rotor y la formula ---------------------------------
        pl = plano_leccion()
        campo_a = campo_flechas(pl, CAMPO_ROTOR, opacidad=0.6)
        rd_a = rueda(pl, P_FORMULA)
        self.play(FadeIn(pl), FadeIn(campo_a), run_time=0.9)
        self.play(FadeIn(rd_a, scale=0.6), run_time=0.5)
        rot.mostrar(pie_curso("Descompongamos ese giro en dos términos: "
                              "cómo cambia Fy al movernos en x, y cómo "
                              "cambia Fx al movernos en y."), zona="abajo",
                    run_time=0.5)
        formula = MathTex(r"\nabla\times F = ",
                          r"\frac{\partial F_y}{\partial x}",
                          r" - ",
                          r"\frac{\partial F_x}{\partial y}",
                          font_size=32, color=C_TITULO)
        if formula.width > 5.6:
            formula.scale_to_fit_width(5.6)
        panel = panel_derecha(formula, buff=0.2)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.play(Rotate(rd_a.aspas, angle=ROT_ROTOR_F / 2.0 * 2.0,
                         about_point=rd_a.centro()), run_time=2.0,
                  rate_func=linear)
        self.wait(1.6)

        # --- momento: primer termino ------------------------------------------
        rot.mostrar(pie_curso("El primero mide cuánto crece Fy al "
                              "avanzar en x."), zona="abajo", run_time=0.5)
        self.play(formula[1].animate.set_color(C_GRAD), run_time=0.4)
        term_x_t = tag_hud(f"dFy/dx = {fmt(DFYDX_ROTOR)}", font_size=17,
                           color=C_GRAD)
        term_x_t.next_to(panel, DOWN, buff=0.18).align_to(panel, RIGHT)
        self.play(FadeIn(term_x_t, shift=0.1 * UP), run_time=0.6)
        self.wait(3.0)

        # --- momento: segundo termino ------------------------------------------
        rot.mostrar(pie_curso("El segundo, cuánto crece Fx al avanzar en "
                              "y. La resta de los dos es el giro."),
                    zona="abajo", run_time=0.5)
        self.play(formula[3].animate.set_color(C_GRAD), run_time=0.4)
        term_y_t = tag_hud(f"dFx/dy = {fmt(DFXDY_ROTOR)}", font_size=17,
                           color=C_GRAD)
        term_y_t.next_to(term_x_t, DOWN, buff=0.12).align_to(panel, RIGHT)
        self.play(FadeIn(term_y_t, shift=0.1 * UP), run_time=0.6)
        self.wait(3.2)

        rot.mostrar(pie_curso("Restados, dan la misma cifra que la "
                              "ruedecita ya nos mostró girando."),
                    zona="abajo", run_time=0.5)
        rot_a_t = tag_hud(f"rot F = {fmt(ROT_ROTOR_F)}", font_size=18,
                          color=C_RES)
        rot_a_t.next_to(term_y_t, DOWN, buff=0.16).align_to(panel, RIGHT)
        self.play(FadeIn(rot_a_t, shift=0.1 * UP), run_time=0.6)
        self.wait(3.4)

        # --- momento: la misma formula en la cizalla ----------------------------
        rot.mostrar(pie_curso("La misma cuenta, ahora en la cizalla: "
                              "sigue dando el mismo -1.0 de antes."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(campo_a), FadeOut(rd_a), FadeOut(term_x_t),
                  FadeOut(term_y_t), FadeOut(rot_a_t), run_time=0.6)
        campo_b = campo_flechas(pl, CAMPO_CIZALLA, opacidad=0.6)
        rd_b = rueda(pl, P_FORMULA)
        self.play(FadeIn(campo_b), FadeIn(rd_b, scale=0.6), run_time=0.7)
        self.play(Rotate(rd_b.aspas, angle=ROT_CIZALLA_F / 2.0 * 3.0,
                         about_point=rd_b.centro()), run_time=3.0,
                  rate_func=linear)
        rot_b_t = tag_hud(f"rot F = {fmt(ROT_CIZALLA_F)}", font_size=18,
                          color=C_RES)
        rot_b_t.next_to(panel, DOWN, buff=0.18).align_to(panel, RIGHT)
        self.play(FadeIn(rot_b_t, shift=0.1 * UP), run_time=0.6)
        self.wait(3.4)

        # --- momento: el radial no gira, y la formula lo confirma -----------------
        rot.mostrar(pie_curso("Y en el radial, la ruedecita ni se "
                              "inmuta: la fórmula da cero, tal cual."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(campo_b), FadeOut(rd_b), FadeOut(rot_b_t),
                  run_time=0.6)
        campo_c = campo_flechas(pl, CAMPO_RADIAL, opacidad=0.6)
        rd_c = rueda(pl, P_FORMULA)
        self.play(FadeIn(campo_c), FadeIn(rd_c, scale=0.6), run_time=0.7)
        self.wait(1.2)
        rot_c_t = tag_hud(f"rot F = {fmt(ROT_RADIAL_F)}", font_size=18,
                          color=C_RES)
        rot_c_t.next_to(panel, DOWN, buff=0.18).align_to(panel, RIGHT)
        self.play(FadeIn(rot_c_t, shift=0.1 * UP), run_time=0.6)
        self.wait(4.0)
