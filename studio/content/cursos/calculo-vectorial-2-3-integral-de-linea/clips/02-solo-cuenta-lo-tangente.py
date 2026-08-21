class Clip2(Scene):
    """2.3.2 - En un punto del camino, F se parte en lo que va POR el
    camino (cuenta) y lo que va de traves (no cuenta). La cifra F.T mide
    la parte que cuenta. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Solo cuenta lo tangente")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: volvemos a un solo tramito --------------------------
        pl = plano_leccion()
        campo = campo_leccion(pl, ancho=4.05, opacidad=0.55)
        cam = camino(pl, R_CAM, grosor=2.6, flechas=3, opacidad=0.45)
        self.play(FadeIn(pl), FadeIn(campo), run_time=0.9)
        rot.mostrar(pie_curso("Volvamos a UN solo tramito del camino y "
                              "miremos qué parte del viento cuenta."),
                    zona="abajo", run_time=0.5)
        self.play(Create(cam.trazo), run_time=1.0)
        self.play(FadeIn(cam.marcas), run_time=0.4)
        self.wait(3.2)

        # --- momento: los dos vectores del tramito ------------------------
        rot.mostrar(pie_curso("Aquí el campo F empuja así; el paso dr "
                              "apunta a lo largo del camino."),
                    zona="abajo", run_time=0.5)
        par = par_F_dr(pl, cam, T_LUPA, esc_F=ESC_LUPA, esc_T=0.9)
        p, F, T = par.p, par.F, par.T
        rot_F = tag_hud("F", font_size=22, color=C_CAMPO)
        rot_F.next_to(par.flecha_F.get_end(),
                      np.array([F[0], F[1], 0.0]), buff=0.14)
        rot_T = tag_hud("dr", font_size=22, color=C_CIFRA)
        rot_T.next_to(par.flecha_T.get_end(),
                      np.array([-T[1], T[0], 0.0]), buff=0.14)
        self.play(FadeIn(par.punto, scale=0.4), run_time=0.4)
        self.play(GrowArrow(par.flecha_F), FadeIn(rot_F), run_time=0.7)
        self.play(GrowArrow(par.flecha_T), FadeIn(rot_T), run_time=0.7)
        self.wait(3.2)

        # --- momento: partir F en dos -------------------------------------
        rot.mostrar(pie_curso("F se parte en dos: lo que va POR el camino "
                              "y lo que va de través."),
                    zona="abajo", run_time=0.5)
        # La direccion del paso, prolongada: sobre esa recta cae la sombra.
        recta_tg = DashedLine(pl.p(p - T * 0.5), pl.p(p + T * 1.5),
                              color=C_CIFRA, stroke_width=2.6,
                              dash_length=0.13)
        recta_tg.set_opacity(0.5)
        tang = par.escalar * T                # (F . T) T : la componente
        normal = F - tang                     # el resto, perpendicular
        fl_tang = flecha_libre(pl, p, p + tang * ESC_LUPA, color=C_RES,
                               grosor=7.0)
        fl_normal = flecha_libre(pl, p + tang * ESC_LUPA, p + F * ESC_LUPA,
                                 color=C_GRAD, grosor=4.4, opacidad=0.65)
        self.play(FadeOut(par.flecha_T), FadeOut(rot_T),
                  Create(recta_tg), run_time=0.7)
        self.play(GrowArrow(fl_tang), run_time=0.9)
        self.play(GrowArrow(fl_normal), run_time=0.7)
        self.wait(2.8)

        # --- momento: la parte de traves no se cobra ----------------------
        rot.mostrar(pie_curso("La parte de través no adelanta camino: no "
                              "se cobra. Solo cuenta la verde."),
                    zona="abajo", run_time=0.5)
        legenda = panel_derecha(
            VGroup(Dot(radius=0.06, color=C_RES),
                   tag_hud("cuenta", font_size=18,
                           color=C_RES)).arrange(RIGHT, buff=0.12),
            VGroup(Dot(radius=0.06, color=C_GRAD),
                   tag_hud("no cuenta", font_size=18,
                           color=C_GRAD)).arrange(RIGHT, buff=0.12),
            tag_hud(f"F . T = {fmt(par.escalar, 2)}", font_size=24,
                    color=C_RES),
            buff=0.22)
        self.play(FadeIn(legenda, shift=0.15 * LEFT), run_time=0.6)
        self.play(Indicate(fl_normal, color=C_GRAD, scale_factor=1.1),
                  run_time=0.8)
        self.wait(3.4)

        # --- momento: la formula del tramito ------------------------------
        rot.mostrar(formula_pie(r"\vec F \cdot d\vec r = "
                                r"(\vec F \cdot \hat T)\, ds"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: de lado casi nada, a favor entero -------------------
        rot.mostrar(pie_curso("De lado, el viento apenas aporta; a favor, "
                              "aporta entero."), zona="abajo", run_time=0.5)
        self.play(FadeOut(fl_normal), FadeOut(par.flecha_F),
                  FadeOut(rot_F), FadeOut(recta_tg), run_time=0.6)
        extras = VGroup()
        for t in (T_CRUZA, T_FAVOR):
            otro = par_F_dr(pl, cam, t, esc_F=ESC_LUPA, esc_T=0.9)
            comp = flecha_libre(pl, otro.p,
                                otro.p + otro.escalar * otro.T * ESC_LUPA,
                                color=C_RES, grosor=7.0)
            extras.add(VGroup(otro.punto, otro.flecha_F, comp))
        tabla = panel_derecha(
            tag_hud("F . T", font_size=20),
            tag_hud(f"lado    {fmt(par_F_dr(pl, cam, T_CRUZA).escalar, 2)}",
                    font_size=21, color=C_RES),
            tag_hud(f"oblicuo {fmt(par.escalar, 2)}", font_size=21,
                    color=C_RES),
            tag_hud(f"a favor {fmt(par_F_dr(pl, cam, T_FAVOR).escalar, 2)}",
                    font_size=21, color=C_RES),
            buff=0.20)
        self.play(FadeOut(legenda), FadeIn(tabla, shift=0.15 * LEFT),
                  run_time=0.6)
        for g in extras:
            self.play(FadeIn(g[0], scale=0.4), GrowArrow(g[1]),
                      GrowArrow(g[2]), run_time=0.7)
        self.wait(3.6)
