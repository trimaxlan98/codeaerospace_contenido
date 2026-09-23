class Clip2(Scene):
    """3.3.2 - Desde el mismo estado, dos acciones distintas dejan mundos
    distintos: la colision carga la interferencia y la carga se descarga
    despacio. La accion de hoy decide el estado de manana: NTNEnv-v2 no es
    exogeno, y por eso el oraculo de un paso no es exacto. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("La accion deja huella"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # el mismo estado, dos acciones conjuntas
        raiz = Dot([-4.6, 0.3, 0], radius=0.14, color=CODE_INK)
        e_r = tag_hud("mismo estado", font_size=17, color=CODE_INK).next_to(raiz, LEFT, buff=0.2).shift(DOWN * 0.45)
        self.play(FadeIn(raiz), FadeIn(e_r), run_time=0.5)
        ra = Arrow(raiz.get_center(), [-3.4, 1.6, 0], buff=0.15, stroke_width=4, color=C_NO)
        rb = Arrow(raiz.get_center(), [-3.4, -1.0, 0], buff=0.15, stroke_width=4, color=C_OK)
        ea = tag_hud("[0,0,0] choca", font_size=17, color=C_NO).next_to(ra.get_end(), UP, buff=0.25).shift(LEFT * 0.6)
        eb = tag_hud("[0,1,2] libre", font_size=17, color=C_OK).next_to(rb.get_end(), DOWN, buff=0.25).shift(LEFT * 0.6)
        self.play(GrowArrow(ra), GrowArrow(rb), FadeIn(ea), FadeIn(eb), run_time=0.9)
        self.wait(2.5)

        def barras(v, x0, y, col):
            g = VGroup()
            for i, val in enumerate(v):
                h = 1.0 * val
                g.add(Rectangle(width=0.36, height=max(h, 0.02), stroke_width=0, fill_color=col,
                                fill_opacity=1.0).move_to([x0 + i * 0.45, y + h / 2, 0]))
            return g
        ba = barras(RAMA_CHOQUE, -2.6, 1.2, C_NO)
        bb = barras(RAMA_LIBRE, -2.6, -1.4, C_OK)
        self.play(*[GrowFromEdge(b, DOWN) for b in (*ba, *bb)], run_time=0.9)
        rot.mostrar(dato_pie("interferencia de los 3 agentes"), zona="abajo", run_time=0.5)
        self.wait(4.5)
        rot.mostrar(dato_pie(f"diferencia maxima {fmt(DELTA0, 2)}"), zona="abajo", run_time=0.5)
        self.wait(4.3)

        # la huella: la diferencia se descarga como 0.7^t
        c = Cuadro((0.4, 6.0, -1.8, 1.8), (0, len(HUELLA) - 1), (0, 0.8))
        self.play(Create(c.suelo()), run_time=0.4)
        pts = VGroup(*[Dot(c.p(t, v), radius=0.07, color=C_CALCULO) for t, v in enumerate(HUELLA)])
        curva = c.serie(np.arange(len(HUELLA)), HUELLA, C_CALCULO, 3)
        e_h = tag_hud("huella", font_size=18, color=C_CALCULO).next_to(c.p(0, 0.8), UP, buff=0.05).align_to(c.p(0, 0), LEFT)
        e_t = tag_hud("pasos", font_size=16, color=C_TENUE).next_to(c.p(len(HUELLA) - 1, 0), DOWN, buff=0.12)
        self.play(Create(curva), LaggedStart(*[FadeIn(p) for p in pts], lag_ratio=0.1), FadeIn(e_h),
                  FadeIn(e_t), run_time=2.0)
        rot.mostrar(formula_pie(rf"\Delta I_t = {fmt(DELTA0, 2)}\cdot {E['decaimiento']}^t"), zona="abajo",
                    run_time=0.5)
        self.wait(5.5)
        rot.mostrar(dato_pie("no exogeno: T(s'|s,a)"), zona="abajo", run_time=0.5)
        self.wait(5.5)
