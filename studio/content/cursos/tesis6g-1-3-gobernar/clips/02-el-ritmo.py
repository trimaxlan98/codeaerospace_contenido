class Clip2(Scene):
    """1.3.2 - ASTREA: un modelo de lenguaje aconseja al control termico de
    una carga en la ISS. Aconsejando cada 15 minutos empeora; al ritmo de la
    orbita (90 minutos) mejora. No fallo la inteligencia: fallo el ritmo.
    (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El ritmo equivocado"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        c = np.array([-3.4, -0.3, 0.0])
        r_o = 2.3
        en = lambda g: c + r_o * np.array([np.cos(np.radians(g)), np.sin(np.radians(g)), 0.0])
        tierra = Circle(radius=1.25, stroke_color=C_TENUE, stroke_width=2.5,
                        fill_color=C_TIERRA, fill_opacity=1.0).move_to(c)
        orbita = Circle(radius=r_o, stroke_color=C_TENUE, stroke_width=1.5,
                        stroke_opacity=0.6).move_to(c)
        ang, giro = ValueTracker(90.0), ValueTracker(0.0)
        sat_m = always_redraw(lambda: VGroup(
            Arc(radius=0.34, start_angle=np.radians(giro.get_value()), angle=np.radians(260),
                arc_center=en(ang.get_value()), stroke_color=CODE_INK, stroke_width=3),
            Dot(en(ang.get_value()), radius=0.11, color=C_ADAPTA)))
        self.play(FadeIn(tierra), Create(orbita), run_time=1.0)
        self.add(sat_m)
        et_c = tag_hud("control SAC", font_size=18, color=C_TENUE).next_to(orbita, DOWN, buff=0.2)
        self.play(ang.animate.set_value(-270), giro.animate.set_value(-360 * 7),
                  FadeIn(et_c), run_time=4.0, rate_func=linear)
        self.wait(1.0)

        # barras: violaciones termicas relativas a la linea base (= 1)
        y0, h1 = -2.4, 2.3
        xs = [2.2, 3.9, 5.6]

        def barra(x, rel, color):
            r = Rectangle(width=1.0, height=h1 * rel, stroke_width=0, fill_color=color,
                          fill_opacity=1.0)
            return r.move_to([x, y0 + h1 * rel / 2, 0])
        suelo = Line([1.4, y0, 0], [6.4, y0, 0], stroke_color=C_TENUE, stroke_width=2)
        b0 = barra(xs[0], 1.0, C_ESTATICA)
        e0 = tag_hud("base", font_size=18, color=C_TENUE).move_to([xs[0], y0 - 0.35, 0])
        tit = tag_hud("violaciones termicas", font_size=18, color=C_TENUE)
        tit.move_to([xs[1], y0 + h1 * 1.35 + 0.35, 0])
        self.play(FadeIn(suelo), GrowFromEdge(b0, DOWN), FadeIn(e0), FadeIn(tit), run_time=0.9)
        self.wait(0.8)

        n = round(A["ventana_orbital_min"] / A["ventana_rapida_min"])
        marcas = VGroup(*[Dot(en(-270 - k * 360 / n), radius=0.07, color=C_PRIV) for k in range(n)])
        self.play(FadeIn(marcas), run_time=0.4)
        for k in range(n):
            self.play(ang.animate.set_value(-270 - (k + 1) * 360 / n),
                      giro.animate.set_value(giro.get_value() - 420), run_time=0.62, rate_func=linear)
            o = Circle(radius=0.2, stroke_color=C_PRIV, stroke_width=3).move_to(en(ang.get_value()))
            self.add(o)
            self.play(o.animate.scale(3.0).set_stroke(opacity=0), run_time=0.18)
            self.remove(o)
        b1 = barra(xs[1], 1 + A["violaciones_rapida"], C_NO)
        e1 = tag_hud(f"{A['ventana_rapida_min']} min", font_size=18, color=C_NO).move_to([xs[1], y0 - 0.35, 0])
        self.play(GrowFromEdge(b1, DOWN), FadeIn(e1), run_time=0.8)
        rot.mostrar(dato_pie(f"cada {A['ventana_rapida_min']} min: +{fmt(100 * A['violaciones_rapida'], 1)} %"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)

        self.play(Transform(marcas, VGroup(Dot(en(-630), radius=0.07, color=C_PRIV))), run_time=0.5)
        self.play(ang.animate.set_value(-990), giro.animate.set_value(giro.get_value() - 2520),
                  run_time=3.6, rate_func=linear)
        o = Circle(radius=0.2, stroke_color=C_PRIV, stroke_width=3).move_to(en(ang.get_value()))
        self.add(o)
        self.play(o.animate.scale(3.4).set_stroke(opacity=0), run_time=0.3)
        self.remove(o)
        b2 = barra(xs[2], 1 + A["violaciones_orbital"], C_OK)
        e2 = tag_hud(f"{A['ventana_orbital_min']} min", font_size=18, color=C_OK).move_to([xs[2], y0 - 0.35, 0])
        self.play(GrowFromEdge(b2, DOWN), FadeIn(e2), run_time=0.8)
        rot.mostrar(dato_pie(f"al ritmo orbital: {fmt(100 * A['violaciones_orbital'], 1)} %"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
