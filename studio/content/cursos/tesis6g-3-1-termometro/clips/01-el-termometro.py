class Clip1(Scene):
    """3.1.1 - La analogia de la tesis: dos medicos comparados con un
    termometro que marca 37 grados pase lo que pase. La diferencia entre
    ellos no significa nada: no hay nada que medir. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("El termometro roto"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        yb = -2.1
        def barra(x, v, col):
            h = 4.4 * v
            return Rectangle(width=1.0, height=h, stroke_width=0, fill_color=col,
                             fill_opacity=1.0).move_to([x, yb + h / 2, 0])
        xa, xb = 3.3, 5.0
        ba, bb = barra(xa, ACIERTO_A, C_ESTATICA), barra(xb, ACIERTO_B, C_ADAPTA)
        suelo = Line([2.5, yb, 0], [5.8, yb, 0], stroke_color=C_TENUE, stroke_width=2)
        la = tag_hud("A", font_size=22, color=C_ESTATICA).move_to([xa, yb - 0.35, 0])
        lb = tag_hud("B", font_size=22, color=C_ADAPTA).move_to([xb, yb - 0.35, 0])
        self.play(FadeIn(suelo), FadeIn(la), FadeIn(lb), run_time=0.5)
        self.play(GrowFromEdge(ba, DOWN), GrowFromEdge(bb, DOWN), run_time=1.2)
        ca = tag_hud(f"{ACIERTO_A:.0%}".replace("%", " %"), font_size=20, color=C_ESTATICA).next_to(ba, UP, buff=0.12)
        cb = tag_hud(f"{ACIERTO_B:.0%}".replace("%", " %"), font_size=20, color=C_ADAPTA).next_to(bb, UP, buff=0.12)
        self.play(FadeIn(ca), FadeIn(cb), run_time=0.5)
        rot.mostrar(dato_pie("analogia, no son datos"), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # el termometro: la columna no se mueve
        xt, y_min, y_max = 0.4, -2.0, 2.2
        t_min, t_max = 35.0, 40.5
        y_de = lambda T: y_min + (y_max - y_min) * (T - t_min) / (t_max - t_min)
        tubo = RoundedRectangle(corner_radius=0.24, width=0.48, height=y_max - y_min + 0.3,
                                stroke_color=C_TENUE, stroke_width=3).move_to([xt, (y_max + y_min) / 2 + 0.15, 0])
        bulbo = Circle(radius=0.38, stroke_width=0, fill_color=C_NO, fill_opacity=1.0).move_to([xt, y_min - 0.28, 0])
        hcol = y_de(LECTURA) - y_min + 0.1
        col = Rectangle(width=0.26, height=hcol, stroke_width=0, fill_color=C_NO,
                        fill_opacity=1.0).move_to([xt, y_min - 0.1 + hcol / 2, 0])
        et = tag_hud(f"{LECTURA} grados", font_size=19, color=C_NO).next_to(col.get_top(), RIGHT, buff=0.35)
        self.play(FadeIn(tubo), FadeIn(bulbo), GrowFromEdge(col, DOWN), FadeIn(et), run_time=1.0)
        fase = ValueTracker(0.0)
        xs = np.linspace(-6.2, -1.2, 160)

        def verdad(x, f):
            u = (x + 6.2) / 5.0
            return 37.6 + 1.3 * np.sin(2 * np.pi * (1.3 * u + f)) + 0.5 * np.sin(2 * np.pi * (3.1 * u - 0.7 * f))
        viva = always_redraw(lambda: VMobject(stroke_color=CODE_INK, stroke_width=4).set_points_smoothly(
            [[x, y_de(verdad(x, fase.get_value())), 0] for x in xs]))
        lect = DashedLine([-6.2, y_de(LECTURA), 0], [xt - 0.3, y_de(LECTURA), 0], dash_length=0.12,
                          stroke_color=C_NO, stroke_width=3)
        e_p = tag_hud("paciente", font_size=17, color=CODE_INK).move_to([-5.4, 2.45, 0])
        self.play(Create(viva), FadeIn(e_p), run_time=1.0)
        self.play(Create(lect), run_time=0.6)
        self.play(fase.animate.set_value(1.8), run_time=5.0, rate_func=linear)
        rot.mostrar(dato_pie("paciente cambia, lectura no"), zona="abajo", run_time=0.5)
        self.play(fase.animate.set_value(2.6), run_time=2.4, rate_func=linear)

        # con ese instrumento, A y B no se distinguen
        ba2, bb2 = barra(xa, ACIERTO_A, C_TIERRA), barra(xb, ACIERTO_B, C_TIERRA)
        igual = MathTex("=", color=CODE_INK, font_size=100).move_to([(xa + xb) / 2, yb + 1.5, 0])
        self.play(Transform(ba, ba2), Transform(bb, bb2), ca.animate.set_color(C_TENUE),
                  cb.animate.set_color(C_TENUE), fase.animate.set_value(3.2), run_time=1.6, rate_func=linear)
        self.play(FadeIn(igual, scale=0.7), fase.animate.set_value(3.8), run_time=1.2, rate_func=linear)
        rot.mostrar(dato_pie("no hay nada que medir"), zona="abajo", run_time=0.5)
        self.play(fase.animate.set_value(5.8), run_time=5.8, rate_func=linear)
