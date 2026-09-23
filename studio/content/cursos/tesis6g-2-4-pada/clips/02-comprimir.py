class Clip2(Scene):
    """2.4.2 - Los agentes no se lo pueden contar todo: el enlace es el
    cuello de botella. La curva del cuello de botella de informacion dice
    cuanto de lo relevante sobrevive a cada bit enviado. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Comprimir lo que se dice"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        c = Cuadro((-4.8, 4.6, -2.1, 2.0), (0, 4), (0, 1.35))
        self.play(Create(c.suelo()), Create(Line(c.p(0, 0), c.p(0, 1.35), stroke_color=C_TENUE,
                                                   stroke_width=2)), run_time=0.6)
        ex = MathTex(r"I(T;X)\ \text{bits enviados}", color=C_TENUE, font_size=30)
        ex.next_to(c.p(4, 0), DOWN, buff=0.15).align_to(c.p(4, 0), RIGHT)
        ey = MathTex(r"I(T;Y)", color=C_TENUE, font_size=30).next_to(c.p(0, 1.35), UP, buff=0.1)
        self.play(FadeIn(ex), FadeIn(ey), run_time=0.5)
        techo = c.raya(IB_MAX, C_PRIV)
        et = tag_hud(f"I(X;Y) = {fmt(IB_MAX, 2)} bits", font_size=18, color=C_PRIV)
        et.next_to(c.p(4, IB_MAX), UP, buff=0.1).align_to(c.p(4, 0), RIGHT)
        self.play(Create(techo), FadeIn(et), run_time=0.8)
        rot.mostrar(dato_pie(f"juguete gaussiano, rho = {RHO}"), zona="abajo", run_time=0.5)
        self.wait(2.6)

        curva = c.serie(IB_BITS, IB_REL, C_CALCULO, 5, esquinas=False)
        self.play(Create(curva), run_time=3.0)
        self.wait(1.2)
        diag = DashedLine(c.p(0, 0), c.p(1.35, 1.35), dash_length=0.1, stroke_color=C_TENUE,
                          stroke_width=2)
        self.play(Create(diag), run_time=0.6)
        rot.mostrar(dato_pie("nunca mas de lo enviado"), zona="abajo", run_time=0.5)
        self.wait(3.0)

        p2 = Dot(c.p(2.0, IB_2 * IB_MAX), radius=0.1, color=C_ADAPTA)
        guias = VGroup(DashedLine(c.p(2.0, 0), c.p(2.0, IB_2 * IB_MAX), dash_length=0.08,
                                  stroke_color=C_ADAPTA, stroke_width=2),
                       DashedLine(c.p(0, IB_2 * IB_MAX), c.p(2.0, IB_2 * IB_MAX), dash_length=0.08,
                                  stroke_color=C_ADAPTA, stroke_width=2))
        self.play(Create(guias), FadeIn(p2), run_time=0.8)
        rot.mostrar(cifra_pie(f"2 bits: {fmt(100 * IB_2, 1)} % relevante"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)
        rot.mostrar(formula_pie(r"\min\ I(T;X) - \beta\, I(T;Y)"), zona="abajo", run_time=0.5)
        self.wait(4.4)
        self.wait(2.6)
