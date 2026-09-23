class Clip1(Scene):
    """3.2.1 - Tres clases de politicas, una dentro de otra: las estaticas,
    las desplegables (cada agente con lo suyo) y las privilegiadas (ven el
    estado). Sus mejores valores quedan ordenados y de ahi salen dos
    margenes, los dos medidos en la tesis como cotas inferiores. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Tres clases de politicas"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        c = np.array([-3.3, 0.05, 0])
        cajas, noms = VGroup(), VGroup()
        for w, h, col, nom, sim in ((6.2, 4.9, C_PRIV, "privilegiadas", r"\Pi_{\mathrm{priv}}"),
                                    (4.6, 3.4, C_ADAPTA, "desplegables", r"\Pi_{\mathrm{dec}}"),
                                    (2.9, 1.9, C_ESTATICA, "estaticas", r"\Pi_{\mathrm{const}}")):
            r = RoundedRectangle(corner_radius=0.3, width=w, height=h, stroke_color=col,
                                 stroke_width=4).move_to(c + DOWN * (4.9 - h) * 0.42)
            g = VGroup(MathTex(sim, color=col, font_size=34), tag_hud(nom, font_size=17, color=col))
            g.arrange(RIGHT, buff=0.15).next_to(r.get_corner(UL), DR, buff=0.18)
            cajas.add(r)
            noms.add(g)
        for i in (2, 1, 0):
            self.play(GrowFromCenter(cajas[i]), FadeIn(noms[i]), run_time=0.8)
            self.wait(1.4)
        rot.mostrar(dato_pie("cada clase contiene otra"), zona="abajo", run_time=0.5)
        self.wait(2.4)

        xe, yb = 1.9, -2.3
        y_de = lambda m: yb + 0.3 + 14.0 * m
        eje = Line([xe, yb - 0.1, 0], [xe, 2.4, 0], stroke_color=C_TENUE, stroke_width=2)
        niveles = [(C_ESTATICA, 0.0, r"V^{\star}_{\mathrm{est}}"), (C_ADAPTA, MA_DEC, r"V^{\star}_{\mathrm{dec}}"),
                   (C_PRIV, MA_G1, r"V^{\star}_{\mathrm{priv}}")]
        self.play(Create(eje), run_time=0.5)
        for (col, m, sim), k in zip(niveles, (2, 1, 0)):
            y = y_de(m)
            tic = Line([xe - 0.22, y, 0], [xe + 0.22, y, 0], stroke_color=col, stroke_width=6)
            t = MathTex(sim, color=col, font_size=36).next_to(tic, LEFT, buff=0.18)
            self.play(FadeIn(VGroup(tic, t), shift=RIGHT * 0.2), cajas[k].animate.set_stroke(width=7), run_time=0.6)
            self.play(cajas[k].animate.set_stroke(width=4), run_time=0.25)
            self.wait(1.6)
        y0, y1, y2 = (y_de(m) for _, m, _ in niveles)
        ll_ma = Brace(Line([xe, y0, 0], [xe, y2, 0]), direction=RIGHT, buff=0.35, color=C_PRIV)
        ll_dec = Brace(Line([xe, y0, 0], [xe, y1, 0]), direction=RIGHT, buff=1.25, color=C_ADAPTA)
        t_ma = MathTex(rf"\mathrm{{MA}} \ge {100 * MA_G1:.1f}\%", color=C_PRIV, font_size=32).next_to(ll_ma, RIGHT, buff=0.15)
        t_dec = MathTex(rf"\mathrm{{MA_{{dec}}}} \ge {100 * MA_DEC:.1f}\%", color=C_ADAPTA, font_size=30).next_to(ll_dec, RIGHT, buff=0.15)
        self.play(GrowFromCenter(ll_ma), FadeIn(t_ma), run_time=0.8)
        self.wait(1.4)
        self.play(GrowFromCenter(ll_dec), FadeIn(t_dec), run_time=0.8)
        rot.mostrar(dato_pie("G1 y G2b, cotas inferiores"), zona="abajo", run_time=0.5)
        self.wait(4.6)
        self.wait(1.2)
        self.wait(1.0)
