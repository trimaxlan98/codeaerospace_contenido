class Clip3(Scene):
    """5.3.3 - El lazo converge: el desfase efectivo del reloj (fucsia),
    simbolo a simbolo, cae de 0.37 (parametro) a una franja de +-0.05
    alrededor de cero; residuo medido en la ventana 200-400. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El lazo converge"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        NV = 400                       # simbolos dibujados
        tau = TAU_L[:NV]
        W, H = 11.0, 4.6
        Y0, Y1 = -0.15, 0.45
        centro = np.array([0.3, 0.0, 0.0])

        def en(k, v):
            fx = k / NV
            fy = (float(np.clip(v, Y0, Y1)) - Y0) / (Y1 - Y0)
            return centro + np.array([(fx - 0.5) * W, (fy - 0.5) * H, 0.0])

        marco = VGroup(Line(en(0, Y0), en(NV, Y0), color=C_EJE,
                            stroke_width=1.8),
                       Line(en(0, Y0), en(0, Y1), color=C_EJE,
                            stroke_width=1.8))
        cero = DashedLine(en(0, 0), en(NV, 0), color=C_TENUE,
                          stroke_width=1.4, dash_length=0.08)
        marcas = VGroup()
        for k in (0, 100, 200, 300, 400):
            p = en(k, Y0)
            marcas.add(Line(p, p + DOWN * 0.1, color=C_EJE, stroke_width=1.6))
            lb = tag_hud(str(k), font_size=17, color=C_TENUE)
            lb.next_to(p, DOWN, buff=0.14)
            marcas.add(lb)
        u_x = tag_junto(marcas[-1], "simbolos", RIGHT, buff=0.16,
                        font_size=18)
        for v in (0.0, 0.1, 0.2, 0.3, 0.4):
            p = en(0, v)
            marcas.add(Line(p, p + LEFT * 0.1, color=C_EJE, stroke_width=1.6))
            lb = tag_hud(fmt(v, 1), font_size=17, color=C_TENUE)
            lb.next_to(p, LEFT, buff=0.12)
            marcas.add(lb)
        u_y = tag_junto(en(0, Y1), "desfase", UP, buff=0.16, font_size=20)

        self.play(Create(marco), FadeIn(marcas), FadeIn(u_x), FadeIn(u_y),
                  FadeIn(cero), run_time=1.0)
        self.wait(0.8)

        # --- el arranque: el reloj del receptor va 0.37 de simbolo tarde ---
        inicio = Dot(en(0, tau[0]), radius=0.09, color=C_LO)
        guia = DashedLine(en(0, tau[0]), en(70, tau[0]), color=C_DATO,
                          stroke_width=1.3, dash_length=0.07)
        t_ini = tag_dato(fmt(tau[0], 2), font_size=22)
        t_ini.next_to(guia, RIGHT, buff=0.16)
        self.play(FadeIn(inicio, scale=1.5), Create(guia), FadeIn(t_ini),
                  run_time=0.7)
        self.wait(3.2)

        # --- el lazo corrige, simbolo a simbolo ------------------------------
        traza = VMobject(stroke_color=C_LO, stroke_width=2.4)
        traza.set_points_as_corners([en(k, v) for k, v in enumerate(tau)])
        punta = Dot(en(0, tau[0]), radius=0.07, color=C_LO)
        punta.add_updater(lambda d: d.move_to(traza.get_end()))
        self.add(punta)
        self.play(Create(traza), run_time=7.0, rate_func=linear)
        punta.clear_updaters()
        self.play(FadeOut(punta), run_time=0.3)
        self.wait(1.4)

        # --- la franja de +-0.05 (elegida) -------------------------------------
        TOL = 0.05
        franja = Rectangle(width=W, height=abs(en(0, TOL)[1] - en(0, -TOL)[1]),
                           stroke_width=0, fill_color=C_DATO,
                           fill_opacity=0.16)
        franja.move_to(en(NV / 2, 0))
        bordes = VGroup(DashedLine(en(0, TOL), en(NV, TOL), color=C_DATO,
                                   stroke_width=1.2, dash_length=0.06),
                        DashedLine(en(0, -TOL), en(NV, -TOL), color=C_DATO,
                                   stroke_width=1.2, dash_length=0.06))
        t_tol = MathTex(r"\pm 0.05", font_size=30, color=C_DATO)
        t_tol.next_to(en(160, TOL), UP, buff=0.12)
        self.play(FadeIn(franja), Create(bordes), FadeIn(t_tol),
                  run_time=0.8)
        self.add(traza)
        self.wait(4.0)

        # --- el residuo, medido en la ventana 200-400 -------------------------
        K_A = 200
        cola = tau[K_A:NV]
        ventana = Rectangle(width=W * (NV - K_A) / NV,
                            height=abs(en(0, 0.1)[1] - en(0, -0.08)[1]),
                            stroke_color=C_CALCULO, stroke_width=2.0,
                            fill_opacity=0.0)
        ventana.move_to((en(K_A, -0.08) + en(NV, 0.1)) / 2)
        self.play(Create(ventana), run_time=0.8)
        rot.mostrar(cifra_pie(f"residuo {fmt(np.mean(cola), 2)} +- "
                              f"{fmt(np.std(cola), 2)} simbolo"),
                    zona="abajo", run_time=0.5)
        self.wait(11.0)
