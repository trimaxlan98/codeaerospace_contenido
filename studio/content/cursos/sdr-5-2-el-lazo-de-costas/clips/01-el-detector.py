from comunicaciones import Onda  # noqa: E402


class Clip1(Scene):
    """5.2.1 - El detector de Costas: un simbolo BPSK girado fuera del eje I
    tiene I (azul) y Q (violeta); el producto I*Q (fucsia, el area del
    rectangulo) mide el giro: positivo a un lado, negativo al otro, cero
    en el eje. Los dos simbolos (+1 y -1) dan el MISMO signo: el detector
    no mira el bit. A la derecha, la curva del detector (e contra el
    giro), calculada con la misma cuenta que el lazo. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El detector"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- el plano IQ ----------------------------------------------------
        plano = S.PlanoIQ(unidad=1.95, alcance=1.27)
        plano.move_to(LEFT * 3.35 + DOWN * 0.12)
        th = ValueTracker(0.0)             # giro en grados

        def z():
            return complex(np.exp(1j * np.radians(th.get_value())))

        def error(zz):
            # la misma cuenta que S.costas_bpsk: Re(y) Im(y) / |y|^2
            return float(np.real(zz) * np.imag(zz) / (abs(zz) ** 2 + 1e-12))

        def rect(s):
            zz = s * z()
            i, q = np.real(zz), np.imag(zz)
            return Polygon(plano.p(0, 0), plano.p(i, 0), plano.p(i, q),
                           plano.p(0, q), stroke_color=C_LO,
                           stroke_width=1.6, fill_color=C_LO,
                           fill_opacity=0.30)

        def proyecciones(s):
            zz = s * z()
            i, q = np.real(zz), np.imag(zz)
            return VGroup(
                Line(plano.p(0, 0), plano.p(i, 0), color=C_I,
                     stroke_width=7),
                Line(plano.p(0, 0), plano.p(0, q), color=C_Q,
                     stroke_width=7),
                DashedLine(plano.p(zz), plano.p(i, 0), color=C_TENUE,
                           stroke_width=1.6, dash_length=0.07),
                DashedLine(plano.p(zz), plano.p(0, q), color=C_TENUE,
                           stroke_width=1.6, dash_length=0.07))

        rect_a = always_redraw(lambda: rect(1))
        rect_b = always_redraw(lambda: rect(-1))
        proy_a = always_redraw(lambda: proyecciones(1))
        proy_b = always_redraw(lambda: proyecciones(-1))
        pt_a = always_redraw(lambda: Dot(plano.p(z()), radius=0.11,
                                         color=C_SENAL))
        pt_b = always_redraw(lambda: Dot(plano.p(-z()), radius=0.11,
                                         color=C_SENAL))

        # --- la curva del detector -----------------------------------------
        gr = np.linspace(-90.0, 90.0, 361)
        ee = np.array([error(np.exp(1j * np.radians(g))) for g in gr])
        curva = Onda(gr, ee, rango_y=(-0.62, 0.62), ancho=5.3, alto=4.1,
                     color=C_LO)
        curva.move_to(RIGHT * 3.55 + DOWN * 0.12)
        cero_v = curva.vertical_en(0.0, color=C_EJE)
        ticks = VGroup()
        for g, t in ((-90.0, "-90"), (0.0, "0"), (90.0, "90")):
            tk = Text(t, font=FUENTE_HUD, font_size=18, color=C_TENUE)
            tk.next_to(curva.en(g, 0.0), DOWN, buff=0.14)
            if g == 0.0:
                tk.shift(RIGHT * 0.2)
            if g < 0.0:
                tk.shift(LEFT * 0.3)
            ticks.add(tk)
        u_x = tag_junto(curva, "giro, grados", DOWN, buff=0.12,
                        font_size=22)
        u_x.next_to(curva, DOWN, buff=0.12).align_to(curva, RIGHT)
        u_y = MathTex("e", font_size=34, color=C_LO)
        u_y.next_to(curva.en(-90.0, 0.62), RIGHT, buff=0.18)
        signo_p = MathTex("+", font_size=40, color=C_LO)
        signo_p.move_to(curva.en(45.0, 0.5) + UP * 0.38)
        signo_m = MathTex("-", font_size=40, color=C_LO)
        signo_m.move_to(curva.en(-45.0, -0.5) + DOWN * 0.38)
        marca = always_redraw(lambda: Dot(
            curva.en(th.get_value(), error(z())), radius=0.1, color=C_LO))
        guia = always_redraw(lambda: DashedLine(
            curva.en(th.get_value(), 0.0),
            curva.en(th.get_value(), error(z())) + UP * 1e-3,
            color=C_LO, stroke_width=1.6, dash_length=0.06))

        self.play(Create(plano), Create(curva.ejes), Create(cero_v),
                  FadeIn(ticks), FadeIn(u_x), FadeIn(u_y), run_time=1.0)
        self.play(Create(curva.curva), run_time=1.6)
        self.play(FadeIn(pt_a, scale=0.5), FadeIn(pt_b, scale=0.5),
                  FadeIn(marca), run_time=0.7)
        self.wait(1.4)

        # --- se gira: aparecen I y Q, y su producto ---------------------------
        self.add(rect_a, rect_b, proy_a, proy_b, pt_a, pt_b, guia, marca)
        self.play(th.animate.set_value(35.0), run_time=2.2)
        self.wait(1.2)
        c35, s35 = np.cos(np.radians(35.0)), np.sin(np.radians(35.0))
        et_i = Text("I", font=FUENTE_HUD, font_size=24, color=C_I)
        et_i.move_to(plano.p(c35 / 2, -0.17))
        et_q = Text("Q", font=FUENTE_HUD, font_size=24, color=C_Q)
        et_q.move_to(plano.p(-0.15, s35 / 2))
        et_iq = MathTex(r"I \cdot Q", font_size=34, color=C_LO)
        et_iq.move_to(plano.p(0.62, 0.98))
        self.play(FadeIn(et_i), FadeIn(et_q), run_time=0.6)
        self.wait(0.8)
        self.play(FadeIn(et_iq, shift=DOWN * 0.1), FadeIn(signo_p),
                  run_time=0.6)
        self.wait(1.4)
        rot.mostrar(formula_pie(r"e = I \cdot Q"), zona="abajo",
                    run_time=0.5)
        self.wait(1.6)

        # --- al otro lado: el producto cambia de signo ------------------------
        self.play(FadeOut(et_i), FadeOut(et_q), FadeOut(et_iq),
                  run_time=0.4)
        self.play(th.animate.set_value(0.0), run_time=2.0)
        self.wait(1.6)
        self.play(th.animate.set_value(-35.0), run_time=2.0)
        self.play(FadeIn(signo_m), run_time=0.5)
        self.wait(2.4)
        self.play(th.animate.set_value(20.0), run_time=2.6)
        self.wait(1.0)
        self.play(th.animate.set_value(0.0), run_time=2.2)
        self.wait(4.0)
