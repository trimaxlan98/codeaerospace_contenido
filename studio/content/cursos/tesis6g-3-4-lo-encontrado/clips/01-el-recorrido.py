class Clip1(Scene):
    """3.4.1 - El banco de pruebas de la tesis medido con su propio
    termometro: la version 1 no premiaba adaptarse (1.7 %, un termometro
    roto: el mio); la version 2 si (31.8 %, con el umbral en 25 %). Y el
    margen alcanzado por una politica desplegable: 9.5 %. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Mi termometro, medido"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        y_b, y_t, ma_max = -1.5, 2.55, 0.40
        y_de = lambda m: y_b + (y_t - y_b) * m / ma_max
        x1, x2 = -2.2, 2.2

        def termo(x):
            tubo = RoundedRectangle(corner_radius=0.3, width=0.6, height=y_t - y_b + 0.35,
                                    stroke_color=C_TENUE, stroke_width=3).move_to([x, (y_t + y_b) / 2 + 0.17, 0])
            bulbo = Circle(radius=0.48, stroke_color=C_TENUE, stroke_width=3).move_to([x, y_b - 0.38, 0])
            return VGroup(tubo, bulbo)

        def col(x, m, c):
            h = max(y_de(m) - y_b, 1e-3)
            return Rectangle(width=0.38, height=h, stroke_width=0, fill_color=c, fill_opacity=1.0).move_to([x, y_b + h / 2, 0])

        def bulbo(x, c):
            return Circle(radius=0.36, stroke_width=0, fill_color=c, fill_opacity=1.0).move_to([x, y_b - 0.38, 0])
        t1, t2 = termo(x1), termo(x2)
        n1 = tag_hud("entorno v1", font_size=18, color=CODE_INK).next_to(t1, DOWN, buff=0.15)
        n2 = tag_hud("entorno v2", font_size=18, color=CODE_INK).next_to(t2, DOWN, buff=0.15)
        self.play(Create(t1), Create(t2), FadeIn(n1), FadeIn(n2), run_time=1.0)
        yu = y_de(D["umbral"])
        um = DashedLine([x1 - 1.7, yu, 0], [x2 + 1.7, yu, 0], dash_length=0.14, stroke_color=CODE_INK, stroke_width=3)
        eu = tag_hud(f"umbral {fmt(100 * D['umbral'], 0)} %", font_size=18, color=CODE_INK).next_to(um, RIGHT, buff=0.15)
        self.play(Create(um), FadeIn(eu), run_time=0.8)
        rot.mostrar(dato_pie("la raya, antes de medir"), zona="abajo", run_time=0.5)
        self.wait(3.2)

        c1 = col(x1, D["g0_ma"], C_NO)
        self.play(FadeIn(bulbo(x1, C_NO)), GrowFromEdge(c1, DOWN), run_time=1.0)
        e1 = tag_hud(T6.pct(D["g0_ma"]), font_size=22, color=C_NO).next_to(c1, RIGHT, buff=0.4).align_to(c1, DOWN)
        self.play(FadeIn(e1), run_time=0.4)
        rot.mostrar(dato_pie("G0: v1 reprobado"), zona="abajo", run_time=0.5)
        self.wait(3.4)

        c2 = col(x2, D["g1_ma"], C_TENUE)
        b2 = bulbo(x2, C_TENUE)
        self.play(FadeIn(b2), run_time=0.3)
        self.play(GrowFromEdge(c2, DOWN), run_time=2.4, rate_func=linear)
        self.play(c2.animate.set_fill(C_OK), b2.animate.set_fill(C_OK), run_time=0.5)
        e2 = tag_hud(T6.pct(D["g1_ma"]), font_size=22, color=C_OK).next_to(c2, RIGHT, buff=0.4).align_to(c2, UP)
        self.play(FadeIn(e2), run_time=0.4)
        rot.mostrar(dato_pie("G1: v2 aprobado"), zona="abajo", run_time=0.5)
        self.wait(3.4)
        c3 = col(x2, MA_DEC, C_ADAPTA)
        ll = Brace(c3, direction=LEFT, buff=0.35, color=C_ADAPTA)
        e3 = tag_hud(f"alcanzado {T6.pct(MA_DEC)}", font_size=18, color=C_ADAPTA).next_to(ll, LEFT, buff=0.12)
        self.play(GrowFromEdge(c3, DOWN), run_time=1.0)
        self.play(FadeIn(ll), FadeIn(e3), run_time=0.6)
        rot.mostrar(cifra_pie(f"par reportado: [{fmt(MA_DEC, 3)}, {fmt(D['g1_ma'], 3)}]"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)
        self.wait(1.6)
