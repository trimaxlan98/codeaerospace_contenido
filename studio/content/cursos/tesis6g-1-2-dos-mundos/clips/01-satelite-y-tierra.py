class Clip1(Scene):
    """1.2.1 - El banco de pruebas de la tesis, sin nombre todavia: dos
    satelites, un gateway y una ruta terrestre alterna. Tres caminos para
    el mismo trafico. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Satelite y tierra"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        suelo = Line([-6.6, -2.0, 0], [6.6, -2.0, 0], stroke_color=C_TENUE, stroke_width=2)
        gw_p = np.array([-1.7, -1.55, 0])
        nuc_p = np.array([4.7, -1.55, 0])
        arco = ArcBetweenPoints([-6.2, 1.2, 0], [4.2, 1.2, 0], angle=-40 * DEGREES,
                                stroke_color=C_TENUE, stroke_width=1.5, stroke_opacity=0.5)
        gw = Square(side_length=0.42, stroke_width=0, fill_color=CODE_INK,
                    fill_opacity=1.0).move_to(gw_p)
        nuc = Circle(radius=0.3, stroke_color=CODE_INK, stroke_width=4).move_to(nuc_p)
        et_gw = tag_junto(gw, "gateway", DOWN, buff=0.3, font_size=24)
        et_nuc = tag_junto(nuc, "red terrestre", DOWN, buff=0.3, font_size=24)
        self.play(Create(suelo), FadeIn(gw), FadeIn(nuc), FadeIn(et_gw), FadeIn(et_nuc),
                  run_time=1.0)
        self.play(Create(arco), run_time=0.8)
        self.wait(1.4)

        # dos satelites que recorren su orbita con medio cuarto de fase entre si
        u = ValueTracker(0.12)
        pos = lambda k: arco.point_from_proportion(float(np.clip(u.get_value() + 0.36 * k, 0, 1)))
        s1 = always_redraw(lambda: satelite_en(pos(0)))
        s2 = always_redraw(lambda: satelite_en(pos(1)))
        l1 = always_redraw(lambda: Line(pos(0), gw_p, stroke_color=C_ENLACE, stroke_width=3))
        l2 = always_redraw(lambda: Line(pos(1), gw_p, stroke_color=C_ENLACE, stroke_width=3))
        self.add(l1, l2, s1, s2)
        self.play(u.animate.set_value(0.2), run_time=1.2, rate_func=linear)
        ruta = Line(gw_p, nuc_p, stroke_color=C_OK, stroke_width=6)
        self.play(Create(ruta), run_time=0.9)
        self.wait(1.2)

        # tres caminos: dos canales de espectro y la ruta terrestre alterna
        caminos = VGroup(tag_hud("espectro bajo", font_size=19, color=C_ENLACE),
                         tag_hud("espectro alto", font_size=19, color=C_ENLACE),
                         tag_hud("ruta alterna", font_size=19, color=C_OK))
        caminos.arrange(DOWN, buff=0.22, aligned_edge=LEFT).to_corner(UR, buff=0.6).shift(DOWN * 0.5)
        self.play(LaggedStart(*[FadeIn(c, shift=LEFT * 0.1) for c in caminos],
                              lag_ratio=0.3), run_time=1.4)
        self.wait(2.0)
        tp = E["tabla_tp"]
        rot.mostrar(dato_pie(f"capacidad {tp[0]:.0f} / {tp[1]:.0f} / {tp[2]:.0f}"),
                    zona="abajo", run_time=0.5)
        self.play(u.animate.set_value(0.28), run_time=4.0, rate_func=linear)
        rot.mostrar(cifra_pie(f"retardo satelite = {fmt(RET_CENIT, 1)} ms"), zona="abajo",
                    run_time=0.5)
        self.play(u.animate.set_value(0.34), run_time=4.0, rate_func=linear)
        rot.mostrar(dato_pie(f"{E['agentes']} agentes que deciden"), zona="abajo", run_time=0.5)
        self.play(u.animate.set_value(0.42), run_time=5.6, rate_func=linear)
        self.wait(2.6)
