class Clip2(Scene):
    """3.4.2 - La compuerta G2b por semilla: la mejor estatica, QMIX y el
    oraculo (cota inferior del optimo, a trazos). QMIX le gana a la estatica
    en las tres semillas, entre 9.5 y 16.3 %, y se queda en 84-87 % del
    oraculo. Modesto y honesto. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("La compuerta G2b"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        y0, alto = -2.2, 4.0
        vmax = max(g["oraculo"] for g in G)
        cs = [-3.6, 0.0, 3.6]
        paso = 0.9

        def barra(x, v, col, contorno=False):
            h = alto * v / vmax
            if contorno:
                r = DashedVMobject(Rectangle(width=0.74, height=h, stroke_color=col, stroke_width=3), num_dashes=36)
            else:
                r = Rectangle(width=0.74, height=h, stroke_width=0, fill_color=col, fill_opacity=1.0)
            return r.move_to([x, y0 + h / 2, 0])
        suelo = Line([-6.0, y0, 0], [6.0, y0, 0], stroke_color=C_TENUE, stroke_width=2)
        sem = VGroup(*[tag_hud(f"semilla {g['semilla']}", font_size=17, color=C_TENUE).move_to([c, y0 - 0.35, 0])
                       for c, g in zip(cs, G)])
        ley = VGroup(tag_hud("estatica", font_size=17, color=C_ESTATICA), tag_hud("QMIX", font_size=17, color=C_ADAPTA),
                     tag_hud("oraculo", font_size=17, color=C_PRIV)).arrange(RIGHT, buff=0.9).move_to([0, 2.45, 0])
        self.play(FadeIn(suelo), FadeIn(sem), run_time=0.5)
        be = [barra(c - paso, g["estatica"], C_ESTATICA) for c, g in zip(cs, G)]
        self.play(*[GrowFromEdge(b, DOWN) for b in be], FadeIn(ley[0]), run_time=1.0)
        rot.mostrar(dato_pie("mejor de 27 fijas"), zona="abajo", run_time=0.5)
        self.wait(4.7)
        bq = [barra(c, g["qmix"], C_ADAPTA) for c, g in zip(cs, G)]
        self.play(*[GrowFromEdge(b, DOWN) for b in bq], FadeIn(ley[1]), run_time=1.2)
        mj = VGroup(*[tag_hud(f"+{fmt(100 * g['mejora'], 1)} %", font_size=17, color=C_ADAPTA).next_to(b, UP, buff=0.1)
                      for b, g in zip(bq, G)])
        self.play(FadeIn(mj), run_time=0.5)
        rot.mostrar(dato_pie("3 de 3 semillas"), zona="abajo", run_time=0.5)
        self.wait(4.9)
        bo = [barra(c + paso, g["oraculo"], C_PRIV, contorno=True) for c, g in zip(cs, G)]
        self.play(*[FadeIn(b, shift=UP * 0.2) for b in bo], FadeIn(ley[2]), run_time=0.9)
        fr = [g["frac_oraculo"] for g in G]
        rot.mostrar(dato_pie(f"{fmt(100 * min(fr), 0)} a {fmt(100 * max(fr), 0)} % del oraculo"), zona="abajo",
                    run_time=0.5)
        self.wait(5.7)
        rot.mostrar(dato_pie("oraculo: cota inferior"), zona="abajo", run_time=0.5)
        self.wait(5.5)
