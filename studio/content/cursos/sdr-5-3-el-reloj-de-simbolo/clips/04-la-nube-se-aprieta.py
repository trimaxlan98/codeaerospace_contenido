class Clip4(Scene):
    """5.3.4 - La nube se aprieta: las muestras que toma el lazo en el
    plano IQ; mientras el reloj aun va tarde (simbolos 1-59) la nube es
    ancha, al final (ultimos 300) se aprieta en dos puntos. EVM medido
    35.4 % -> 6.4 %. Cierre. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La nube se aprieta"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        # --- el plano IQ (izquierda) ----------------------------------------
        plano = S.PlanoIQ(unidad=1.42, alcance=1.7)
        plano.shift(np.array([-3.35, 0.05, 0.0]))
        self.play(FadeIn(plano), run_time=0.8)

        # --- el desfase del lazo, entero (derecha) ---------------------------
        NT = len(TAU_L)
        W, H = 5.6, 2.9
        Y0, Y1 = -0.15, 0.45
        c = np.array([3.45, 0.95, 0.0])

        def en(k, v):
            fx = k / (NT - 1)
            fy = (float(np.clip(v, Y0, Y1)) - Y0) / (Y1 - Y0)
            return c + np.array([(fx - 0.5) * W, (fy - 0.5) * H, 0.0])

        ejes = VGroup(Line(en(0, Y0), en(NT - 1, Y0), color=C_EJE,
                           stroke_width=1.8),
                      Line(en(0, Y0), en(0, Y1), color=C_EJE,
                           stroke_width=1.8))
        cero = DashedLine(en(0, 0), en(NT - 1, 0), color=C_TENUE,
                          stroke_width=1.2, dash_length=0.07)
        l_cero = tag_hud("0", font_size=17, color=C_TENUE)
        l_cero.next_to(en(0, 0), LEFT, buff=0.12)
        marcas = VGroup()
        for k in (0, 500, 1000):
            p = en(k, Y0)
            marcas.add(Line(p, p + DOWN * 0.1, color=C_EJE, stroke_width=1.6))
            lb = tag_hud(str(k), font_size=17, color=C_TENUE)
            lb.next_to(p, DOWN, buff=0.12)
            marcas.add(lb)
        u_x = tag_junto(en(NT - 1, Y0), "simbolos", DOWN, buff=0.14,
                        font_size=18)
        u_x.align_to(en(NT - 1, Y0), RIGHT)
        u_y = tag_junto(en(0, Y1), "desfase", UP, buff=0.14, font_size=20)
        traza = VMobject(stroke_color=C_LO, stroke_width=1.8)
        traza.set_points_as_corners([en(k, v) for k, v in enumerate(TAU_L)])
        self.play(Create(ejes), FadeIn(cero), FadeIn(l_cero), FadeIn(marcas),
                  FadeIn(u_x), FadeIn(u_y), run_time=0.8)
        self.play(Create(traza), run_time=2.0)
        self.wait(1.4)

        # --- ventana A: los primeros simbolos ---------------------------------
        def ventana(k0, k1):
            a, b = en(k0, Y0), en(k1, Y1)
            r = Rectangle(width=abs(b[0] - a[0]), height=abs(b[1] - a[1]),
                          stroke_color=C_CALCULO, stroke_width=2.0,
                          fill_color=C_CALCULO, fill_opacity=0.10)
            return r.move_to((a + b) / 2)

        K_A0, K_A1 = 1, 60
        K_B0 = NT - 300
        v_a = ventana(K_A0, K_A1)
        t_va = tag_dato(f"simbolos {K_A0} a {K_A1 - 1}", font_size=19)
        t_va.next_to(v_a, RIGHT, buff=0.16).align_to(v_a, UP)
        self.play(FadeIn(v_a), FadeIn(t_va), run_time=0.6)

        nube_a = plano.nube(YS[K_A0:K_A1], color=C_SENAL, radio=0.06,
                            opacidad=0.85)
        self.play(LaggedStart(*[FadeIn(d, scale=1.5) for d in nube_a],
                              lag_ratio=0.05), run_time=2.4)
        evm_a = tag_hud(f"EVM {fmt(EVM0, 1)} %", font_size=34)
        evm_a.move_to([3.45, -1.55, 0])
        self.play(FadeIn(evm_a), run_time=0.5)
        self.wait(4.0)

        # --- ventana B: los ultimos 300 ---------------------------------------
        v_b = ventana(K_B0, NT - 1)
        t_vb = tag_dato(f"ultimos {NT - K_B0}", font_size=19)
        t_vb.next_to(v_b, UP, buff=0.14).align_to(v_b, RIGHT)
        self.play(FadeOut(evm_a), FadeOut(nube_a), FadeOut(t_va),
                  run_time=0.6)
        self.play(Transform(v_a, v_b), FadeIn(t_vb), run_time=1.0)
        nube_b = plano.nube(YS[K_B0:], color=C_SENAL, radio=0.04,
                            opacidad=0.7)
        self.play(FadeIn(nube_b), run_time=1.2)
        evm_b = tag_hud(f"EVM {fmt(EVM1, 1)} %", font_size=34)
        evm_b.move_to(evm_a)
        self.play(FadeIn(evm_b), run_time=0.5)
        self.wait(3.4)

        rot.mostrar(cifra_pie(f"EVM {fmt(EVM0, 1)} % -> {fmt(EVM1, 1)} %"),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        cierre_leccion(self, rot, "Tres relojes que ajustar:",
                       "frecuencia, fase y simbolo.", plano, ejes, cero,
                       l_cero, marcas, u_x, u_y, traza, v_a, t_vb, nube_b,
                       evm_b)
