class Clip3(Scene):
    """3.3.3 - La maldicion del ganador: la mejor de 27 estaticas, elegida
    por su promedio en pocos episodios, sale sobreestimada; el denominador
    del margen se infla y el margen sale deprimido. Con 30 episodios el
    sesgo desaparece y la curva de la tesis converge. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("La maldicion del ganador"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        vmin, vmax = 76.0, 124.0
        X0, X1, Y = -6.2, 0.4, 1.1
        x_de = lambda v: X0 + (X1 - X0) * (v - vmin) / (vmax - vmin)

        def nube(vals, col):
            off = ((np.argsort(np.argsort(vals)) % 3) - 1) * 0.3
            return VGroup(*[Dot([x_de(v), Y + o, 0], radius=0.065, color=col) for v, o in zip(vals, off)])
        recta = Line([X0 - 0.2, Y - 0.9, 0], [X1 + 0.2, Y - 0.9, 0], stroke_color=C_TENUE, stroke_width=2)
        mejor = float(VERDAD.max())
        raya = DashedLine([x_de(mejor), Y - 1.05, 0], [x_de(mejor), Y + 0.9, 0], dash_length=0.1,
                          stroke_color=C_ESTATICA, stroke_width=3)
        e_r = tag_hud("mejor real", font_size=17, color=C_ESTATICA).next_to(raya, UP, buff=0.1)
        nub = nube(VERDAD, C_ESTATICA)
        self.play(Create(recta), FadeIn(nub), run_time=0.8)
        self.play(Create(raya), FadeIn(e_r), run_time=0.6)
        rot.mostrar(dato_pie("27 estaticas de juguete"), zona="abajo", run_time=0.5)
        self.wait(3.7)

        p1 = nube(M1, C_TENUE)
        k1 = int(np.argmax(M1))
        p1[k1].set_color(C_ADAPTA).scale(1.6)
        self.play(Transform(nub, p1), run_time=1.0)
        fl = Line([x_de(mejor), Y - 1.3, 0], [x_de(M1[k1]), Y - 1.3, 0], stroke_color=C_ADAPTA,
                  stroke_width=5).add_tip(tip_length=0.18)
        e1 = tag_hud("1 episodio", font_size=18, color=CODE_INK).move_to([X0 + 0.9, Y + 1.4, 0])
        self.play(Create(fl), FadeIn(e1), run_time=0.7)
        rot.mostrar(cifra_pie(f"sesgo = +{fmt(M1[k1] - mejor, 1)}"), zona="abajo", run_time=0.5)
        self.wait(4.9)
        p30 = nube(M30, C_TENUE)
        k30 = int(np.argmax(M30))
        p30[k30].set_color(C_ADAPTA).scale(1.6)
        e30 = tag_hud("30 episodios", font_size=18, color=CODE_INK).move_to(e1)
        self.play(Transform(nub, p30), FadeOut(fl), Transform(e1, e30), run_time=1.2)
        rot.mostrar(cifra_pie(f"sesgo = {M30[k30] - mejor:+.2f}"), zona="abajo", run_time=0.5)
        self.wait(4.7)

        # la curva MEDIDA en la tesis
        gx0, gx1, gy0, gy1 = 1.8, 6.3, -2.4, 0.9
        lx = lambda e: gx0 + (gx1 - gx0) * np.log10(e) / np.log10(30)
        ly = lambda v: gy0 + (gy1 - gy0) * (v - 0.15) / 0.2
        base = Line([gx0 - 0.1, gy0, 0], [gx1 + 0.1, gy0, 0], stroke_color=C_TENUE, stroke_width=2)
        um = DashedLine([gx0 - 0.1, ly(D["umbral"]), 0], [gx1 + 0.1, ly(D["umbral"]), 0], dash_length=0.12,
                        stroke_color=CODE_INK, stroke_width=2)
        e_u = tag_hud(f"{fmt(100 * D['umbral'], 0)} %", font_size=16, color=CODE_INK).next_to(um, LEFT, buff=0.1)
        pts = [[lx(e), ly(v), 0] for e, v in SENS]
        tr = VMobject(stroke_color=C_PRIV, stroke_width=4).set_points_as_corners(pts)
        dots = VGroup(*[Dot(p, radius=0.08, color=C_PRIV) for p in pts])
        eps = VGroup(*[tag_hud(str(e), font_size=15, color=C_TENUE).move_to([lx(e), gy0 - 0.3, 0]) for e, _ in SENS])
        self.play(Create(base), Create(um), FadeIn(e_u), FadeIn(eps), run_time=0.7)
        self.play(Create(tr), FadeIn(dots), run_time=1.6)
        rot.mostrar(dato_pie(f"tesis: {fmt(SENS[0][1], 3)} a {fmt(SENS[-1][1], 3)}"), zona="abajo",
                    run_time=0.5)
        self.wait(5.9)
