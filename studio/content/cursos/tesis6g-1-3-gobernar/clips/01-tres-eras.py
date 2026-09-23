class Clip1(Scene):
    """1.3.1 - Tres maneras de mantener una red: a mano, nodo por nodo; con
    automatismos por funcion (SON, 3GPP Rel-16); y con un lazo que gobierna
    el conjunto. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Tres eras"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        rng = np.random.default_rng(7)
        pts = [np.array([x, y, 0]) for x, y in
               ((-2.2, 1.3), (0.4, 1.8), (2.6, 1.0), (-1.4, -0.9), (1.2, -0.6), (3.2, -1.4))]
        nodos = VGroup(*[Circle(radius=0.26, stroke_color=CODE_INK, stroke_width=3).move_to(p)
                         for p in pts])
        enlaces = VGroup(*[Line(pts[i], pts[j], stroke_color=C_TENUE, stroke_width=1.5,
                                stroke_opacity=0.6) for i, j in
                           ((0, 1), (1, 2), (0, 3), (3, 4), (1, 4), (4, 5), (2, 5))])
        self.play(FadeIn(enlaces), LaggedStart(*[GrowFromCenter(n) for n in nodos],
                                               lag_ratio=0.12), run_time=1.4)
        self.wait(0.8)

        # --- era 1: a mano ------------------------------------------------
        op = Square(side_length=0.36, stroke_width=0, fill_color=C_ESTATICA,
                    fill_opacity=1.0).move_to([-5.4, 0.2, 0])
        et1 = tag_junto(op, "manual", DOWN, buff=0.2, font_size=24, color=C_ESTATICA)
        self.play(FadeIn(op), FadeIn(et1), run_time=0.6)
        for n in nodos:
            l = Line(op.get_center(), n.get_center(), stroke_color=C_ESTATICA, stroke_width=2)
            self.play(Create(l), n.animate.set_stroke(C_ESTATICA), run_time=0.35)
            self.play(FadeOut(l), run_time=0.2)
        self.wait(2.4)

        # --- era 2: automatismos por funcion (SON) ------------------------
        lazos = VGroup(*[Arc(radius=0.42, start_angle=0.3, angle=5.2, arc_center=p,
                             stroke_color=C_ENLACE, stroke_width=3).add_tip(tip_length=0.12)
                         for p in pts])
        et2 = tag_hud("SON · Rel-16", font_size=20, color=C_ENLACE).move_to([-5.2, -1.6, 0])
        self.play(FadeOut(op), FadeOut(et1), LaggedStart(*[Create(l) for l in lazos],
                                                         lag_ratio=0.1), FadeIn(et2),
                  run_time=1.6)
        self.play(*[Rotate(l, angle=2 * PI, about_point=p) for l, p in zip(lazos, pts)],
                  run_time=2.4, rate_func=linear)
        rot.mostrar(dato_pie("3GPP Rel-16 SON"), zona="abajo", run_time=0.5)
        self.wait(3.8)

        # --- era 3: un lazo que gobierna el conjunto ----------------------
        grande = Ellipse(width=8.2, height=4.3, stroke_color=C_ADAPTA, stroke_width=4)
        grande.move_to([0.5, 0.2, 0])
        et3 = tag_junto(grande, "autonoma", UP, buff=0.12, font_size=26, color=C_ADAPTA)
        self.play(FadeOut(et2), Create(grande), FadeIn(et3), run_time=1.4)
        pulso = Dot(radius=0.11, color=C_ADAPTA)
        self.play(MoveAlongPath(pulso, grande), *[Rotate(l, angle=2 * PI, about_point=p)
                                                 for l, p in zip(lazos, pts)],
                  run_time=3.2, rate_func=linear)
        self.remove(pulso)
        rot.mostrar(dato_pie("TM Forum L0 a L5"), zona="abajo", run_time=0.5)
        self.wait(5.6)
