class Clip2(Scene):
    """2.2.2 - CTDE, el paradigma de QMIX: se ENTRENA con un mezclador que
    ve el estado global y se EJECUTA sin el, cada agente con lo suyo.
    (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Entrenar juntos, decidir solos"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        xs = [-3.4, 0.0, 3.4]
        y_ag, y_mz, y_st = -1.5, 0.9, 2.3

        def caja(w, h, color):
            return RoundedRectangle(corner_radius=0.16, width=w, height=h, stroke_color=color,
                                    stroke_width=4)
        agentes = VGroup(*[VGroup(caja(1.8, 0.9, C_ADAPTA).move_to([x, y_ag, 0]),
                                  MathTex(rf"Q_{i + 1}", color=C_ADAPTA, font_size=42).move_to([x, y_ag, 0]))
                           for i, x in enumerate(xs)])
        obs = VGroup(*[MathTex(rf"o_{i + 1}", color=CODE_INK, font_size=38).move_to([x, y_ag - 1.15, 0])
                       for i, x in enumerate(xs)])
        f_obs = VGroup(*[Arrow(o.get_top(), a.get_bottom(), buff=0.08, stroke_width=4, color=CODE_INK,
                               max_tip_length_to_length_ratio=0.3) for o, a in zip(obs, agentes)])
        self.play(*[FadeIn(a) for a in agentes], FadeIn(obs), *[GrowArrow(f) for f in f_obs],
                  run_time=1.2)
        self.wait(2.8)
        entrenar = tag_hud("entrenamiento", font_size=20, color=C_PRIV).move_to([-5.2, y_st, 0])
        mz = caja(5.0, 0.9, C_PRIV).move_to([0, y_mz, 0])
        q_tot = MathTex(r"Q_{\mathrm{tot}}", color=C_PRIV, font_size=42).move_to(mz)
        f_mz = VGroup(*[Arrow(a.get_top(), mz.get_bottom() + RIGHT * x * 0.55, buff=0.08,
                              stroke_width=4, color=C_ADAPTA, max_tip_length_to_length_ratio=0.25)
                        for a, x in zip(agentes, xs)])
        est = MathTex("s", color=C_PRIV, font_size=46).move_to([0, y_st, 0])
        f_st = Arrow(est.get_bottom(), mz.get_top(), buff=0.1, stroke_width=4, color=C_PRIV,
                     max_tip_length_to_length_ratio=0.3)
        self.play(FadeIn(entrenar), FadeIn(mz), FadeIn(q_tot), *[GrowArrow(f) for f in f_mz],
                  run_time=1.0)
        self.play(FadeIn(est), GrowArrow(f_st), run_time=0.7)
        rot.mostrar(dato_pie("el mezclador ve el estado"), zona="abajo", run_time=0.5)
        self.wait(4.0)
        rot.mostrar(formula_pie(r"\partial Q_{\mathrm{tot}} / \partial Q_i \ge 0"), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)

        ejecutar = tag_hud("ejecucion", font_size=20, color=C_ADAPTA).move_to(entrenar)
        fantasma = DashedVMobject(mz.copy().set_stroke(C_TENUE, width=2), num_dashes=40)
        self.play(FadeOut(VGroup(q_tot, f_mz, est, f_st, mz)), FadeIn(fantasma),
                  Transform(entrenar, ejecutar), run_time=1.0)
        acc = VGroup(*[Arrow(a.get_top(), a.get_top() + UP * 1.0, buff=0.06, stroke_width=5,
                             color=C_ADAPTA, max_tip_length_to_length_ratio=0.35) for a in agentes])
        a_t = VGroup(*[MathTex(rf"a_{i + 1}", color=C_ADAPTA, font_size=38).next_to(f, UP, buff=0.06)
                       for i, f in enumerate(acc)])
        self.play(*[GrowArrow(f) for f in acc], FadeIn(a_t), run_time=0.8)
        rot.mostrar(dato_pie("cada agente con lo suyo"), zona="abajo", run_time=0.5)
        self.wait(4.4)
        rot.mostrar(dato_pie("QMIX, Rashid et al. 2018"), zona="abajo", run_time=0.5)
        self.wait(3.6)
        self.wait(1.4)
