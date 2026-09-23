class Clip2(Scene):
    """3.1.2 - En SMAC, el banco canonico del aprendizaje multiagente
    cooperativo, una politica que solo mira el reloj ganaba escenarios: el
    mundo se repetia. Con azar, el plan fijo deja de servir. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("La politica que no mira"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        def panel(x0, tr, color):
            g = VGroup()
            xy = lambda t, v: [x0 + 5.4 * t, -0.3 + 3.0 * v / 2.2, 0]
            for fila in tr:
                m = VMobject(stroke_color=color, stroke_width=3, stroke_opacity=0.8)
                m.set_points_smoothly([xy(t, v) for t, v in zip(T_TR, fila)])
                g.add(m)
            return g, xy
        xa, xb = -6.1, 0.7
        sin, xy_a = panel(xa, SIN_AZAR, C_ESTATICA)
        con, xy_b = panel(xb, CON_AZAR, C_ESTATICA)
        ea = tag_hud("sin azar", font_size=20, color=CODE_INK).move_to([xa + 2.7, 2.35, 0])
        eb = tag_hud("con azar", font_size=20, color=CODE_INK).move_to([xb + 2.7, 2.35, 0])
        sep = Line([0.3, -2.4, 0], [0.3, 2.5, 0], stroke_color=C_TIERRA, stroke_width=2)
        self.play(FadeIn(ea), Create(sep), run_time=0.5)
        for m in sin:
            self.play(Create(m), run_time=0.5, rate_func=linear)
        rot.mostrar(dato_pie("seis episodios iguales"), zona="abajo", run_time=0.5)
        self.wait(2.6)

        def plan(xy):
            m = VMobject(stroke_color=C_ADAPTA, stroke_width=6)
            m.set_points_smoothly([xy(t, v) for t, v in zip(T_TR, SIN_AZAR[0])])
            return DashedVMobject(m, num_dashes=40)
        pa = plan(xy_a)
        e_p = tag_hud("lazo abierto: solo el reloj", font_size=18, color=C_ADAPTA).move_to([0.3, -2.5, 0])
        self.play(Create(pa), FadeIn(e_p), run_time=1.8, rate_func=linear)
        rot.mostrar(dato_pie("Ellis et al., NeurIPS 2023"), zona="abajo", run_time=0.5)
        self.wait(3.6)

        self.play(FadeIn(eb), run_time=0.4)
        self.play(*[Create(m) for m in con], run_time=2.4, rate_func=linear)
        pb = plan(xy_b)
        self.play(Create(pb), run_time=1.8, rate_func=linear)
        rot.mostrar(dato_pie("SMACv2 anade el azar"), zona="abajo", run_time=0.5)
        self.wait(3.6)
        rot.mostrar(dato_pie("margen casi cero, sin medir"), zona="abajo", run_time=0.5)
        self.wait(4.0)
        self.wait(1.2)
