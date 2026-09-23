class Clip3(Scene):
    """3.1.3 - Dos algoritmos IDENTICOS evaluados con 5 semillas: uno parece
    mejor. Con 10, el orden se invierte. Le pasa a uno de cada cuatro
    experimentos. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Cinco semillas no bastan"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        a, b = INV["a"], INV["b"]
        lo, hi = min(a.min(), b.min()) - 0.3, max(a.max(), b.max()) + 0.3
        c = Cuadro((-2.6, 2.6, -2.0, 2.0), (0, 1), (lo, hi))
        ya = lambda v: c.p(0, v)[1]
        xa, xb = -1.3, 1.3
        eje = Line([-3.0, ya(0), 0], [3.0, ya(0), 0], stroke_color=C_TIERRA, stroke_width=2)
        la = tag_hud("A", font_size=22, color=C_ADAPTA).move_to([xa, -2.45, 0])
        lb = tag_hud("B", font_size=22, color=C_PRIV).move_to([xb, -2.45, 0])
        self.play(FadeIn(eje), FadeIn(la), FadeIn(lb), run_time=0.5)
        rot.mostrar(dato_pie("A y B son identicos"), zona="abajo", run_time=0.5)
        self.wait(2.0)

        def puntos(v, x, col, k):
            return VGroup(*[Dot([x + 0.18 * ((i % 3) - 1), ya(v[i]), 0], radius=0.08, color=col)
                            for i in range(k)])

        def media(v, x, col):
            return Line([x - 0.55, ya(v.mean()), 0], [x + 0.55, ya(v.mean()), 0], stroke_color=col,
                        stroke_width=6)
        pa, pb = puntos(a, xa, C_ADAPTA, 5), puntos(b, xb, C_PRIV, 5)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in (*pa, *pb)], lag_ratio=0.1), run_time=1.6)
        ma, mb = media(a[:5], xa, C_ADAPTA), media(b[:5], xb, C_PRIV)
        self.play(Create(ma), Create(mb), run_time=0.7)
        rot.mostrar(cifra_pie("5 semillas: gana A"), zona="abajo", run_time=0.5)
        self.wait(3.6)

        pa2 = VGroup(*[Dot([xa + 0.18 * ((i % 3) - 1), ya(a[i]), 0], radius=0.08, color=C_ADAPTA)
                       for i in range(5, 10)])
        pb2 = VGroup(*[Dot([xb + 0.18 * ((i % 3) - 1), ya(b[i]), 0], radius=0.08, color=C_PRIV)
                       for i in range(5, 10)])
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in (*pa2, *pb2)], lag_ratio=0.1), run_time=1.6)
        self.play(Transform(ma, media(a, xa, C_ADAPTA)), Transform(mb, media(b, xb, C_PRIV)), run_time=1.0)
        rot.mostrar(cifra_pie("10 semillas: gana B"), zona="abajo", run_time=0.5)
        self.wait(3.6)
        rot.mostrar(cifra_pie(f"se invierte en {fmt(100 * INV['p_inversion'], 1)} %"), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)
        rot.mostrar(formula_pie(r"P = \arccos\!\left(\sqrt{5/10}\right)/\pi = 0.25"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
        self.wait(1.2)
