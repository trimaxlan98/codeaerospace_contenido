class Clip3(Scene):
    """3.1.3 - Riccati devuelve las ganancias, y con ellas la velocidad
    del lazo: q/r = 100 se establece en 1.75 s y q/r = 1 en 5.53 s, la
    raiz cuarta de cien. El regalo es que zeta sale 0.7071 en las dos.
    (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Riccati, y el regalo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        rot.mostrar(formula_pie(
            r"A^{T}P + PA - PBR^{-1}B^{T}P + Q = 0"), zona="abajo")
        self.wait(2.6)

        # --- el escalon del lazo cerrado, con su banda del 2 % -------------
        t_fin = 7.0
        ejes = Axes(x_range=[0.0, t_fin, 1.0], y_range=[0.0, 1.4, 0.5],
                    x_length=5.8, y_length=2.3,
                    axis_config={"color": C_EJE, "stroke_width": 2.2,
                                 "include_ticks": False,
                                 "include_tip": False})
        ejes.move_to(LEFT * 2.35 + DOWN * 0.25)
        t_x = tag_hud("t (s)", font_size=17, color=C_TENUE)
        t_x.next_to(ejes.x_axis, DOWN, buff=0.16).align_to(ejes.x_axis, RIGHT)
        t_y = tag_hud("salida", font_size=17, color=C_TENUE)
        t_y.next_to(ejes.y_axis, UP, buff=0.12)

        ref = DashedVMobject(
            Line(ejes.c2p(0.0, 1.0), ejes.c2p(t_fin, 1.0),
                 stroke_width=2.0, color=C_TENUE), num_dashes=30)
        banda = Polygon(ejes.c2p(0.0, 0.98), ejes.c2p(t_fin, 0.98),
                        ejes.c2p(t_fin, 1.02), ejes.c2p(0.0, 1.02),
                        stroke_width=0, fill_color=C_OK, fill_opacity=0.30)
        t_banda = tag_hud("banda 2%", font_size=16, color=C_OK)
        t_banda.move_to(ejes.c2p(t_fin, 1.0) + RIGHT * 0.72 + UP * 0.05)

        self.play(Create(ejes), FadeIn(t_x), FadeIn(t_y), run_time=1.0)
        self.play(FadeIn(banda), Create(ref), FadeIn(t_banda), run_time=0.9)
        self.wait(0.4)

        # La respuesta es la del segundo orden que define el par
        # (zeta, wn) que devuelve la libreria: ni un numero a mano.
        z = ZETA_LQR
        wd_f = float(np.sqrt(1.0 - z * z))
        t_s = np.linspace(0.0, t_fin, 421)

        def salto(wn):
            wd = wn * wd_f
            return 1.0 - np.exp(-z * wn * t_s) * (
                np.cos(wd * t_s) + z / wd_f * np.sin(wd * t_s))

        def curva_de(wn, color):
            c = VMobject(color=color, stroke_width=3.6)
            c.set_points_as_corners([ejes.c2p(a, b)
                                     for a, b in zip(t_s, salto(wn))])
            return c

        # --- el ajuste rapido: q/r = 100 -----------------------------------
        c_rap = curva_de(WN_R, C_CALCULO)
        t_rap = tag_hud(f"q/r {fmt(Q_ALTO / R_BAJO, 0)}", font_size=20)
        t_rap.move_to(np.array([-3.60, 1.40, 0.0]))
        self.play(Create(c_rap), FadeIn(t_rap), run_time=1.6)

        m_rap = DashedVMobject(
            Line(ejes.c2p(TS_R, 0.0), ejes.c2p(TS_R, 1.25),
                 stroke_width=2.6, color=C_CALCULO), num_dashes=14)
        self.play(Create(m_rap), run_time=0.7)
        rot.mostrar(cifra_pie(f"t_est {fmt(TS_R, 2)} s"), zona="abajo")
        self.wait(2.2)

        # --- las ganancias que devuelve el metodo ---------------------------
        k_vec = MathTex(r"K = " + _al.matriz_tex([[K1_R, K2_R]], 2),
                        font_size=40, color=C_CALCULO)
        k_vec.move_to(np.array([4.15, 0.95, 0.0]))
        t_cond = tag_hud("doble integrador", font_size=17, color=C_TENUE)
        t_cond.next_to(k_vec, DOWN, buff=0.22)
        self.play(Write(k_vec), run_time=1.0)
        self.play(FadeIn(t_cond), run_time=0.5)
        rot.mostrar(cifra_pie(f"wn {fmt(WN_R, 2)} rad/s"), zona="abajo")
        self.wait(2.2)

        # --- el ajuste lento: q/r = 1 ---------------------------------------
        # el carril se apaga primero: "wn 3.16" es del ajuste rapido y no
        # puede seguir abajo mientras entra la curva del otro.
        rot.limpiar("abajo", run_time=0.3)
        c_len = curva_de(WN_L, C_CIELO)
        t_len = tag_hud(f"q/r {fmt(Q_ALTO_2 / R_ALTO, 0)}", font_size=20,
                        color=C_CIELO)
        t_len.move_to(np.array([-1.30, 1.40, 0.0]))
        self.play(Create(c_len), FadeIn(t_len), run_time=1.6)

        m_len = DashedVMobject(
            Line(ejes.c2p(TS_L, 0.0), ejes.c2p(TS_L, 1.25),
                 stroke_width=2.6, color=C_CIELO), num_dashes=14)
        self.play(Create(m_len), run_time=0.7)
        rot.mostrar(cifra_pie(f"t_est {fmt(TS_L, 2)} s"), zona="abajo")
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"{fmt(RAZON_WN, 2)} veces mas lento"),
                    zona="abajo")
        self.wait(2.4)
        razon_qr = (Q_ALTO / R_BAJO) / (Q_ALTO_2 / R_ALTO)
        rot.mostrar(formula_pie(f"{fmt(RAZON_WN, 3)} = "
                                r"\sqrt[4]{" + fmt(razon_qr, 0) + "}"),
                    zona="abajo")
        self.wait(2.6)

        # --- EL REGALO: el amortiguamiento no depende de q ni de r ----------
        z_rap = tag_hud(f"zeta {fmt(ZETA_LQR, 4)}", font_size=19, color=C_OK)
        z_rap.move_to(np.array([float(ejes.c2p(TS_R, 0.0)[0]), -2.28, 0.0]))
        z_len = tag_hud(f"zeta {fmt(ZETA_LQR, 4)}", font_size=19, color=C_OK)
        z_len.move_to(np.array([float(ejes.c2p(TS_L, 0.0)[0]), -2.28, 0.0]))
        self.play(FadeIn(z_rap), FadeIn(z_len), run_time=0.8)

        caja = VGroup(tag_hud(f"zeta {fmt(ZETA_LQR, 4)}", font_size=24,
                              color=C_OK),
                      tag_hud("para cualquier q/r", font_size=18,
                              color=C_OK))
        caja.arrange(DOWN, buff=0.18)
        caja.move_to(np.array([4.15, -1.15, 0.0]))
        marco = SurroundingRectangle(caja, color=C_OK, stroke_width=2.4,
                                     buff=0.24)
        self.play(FadeIn(caja), Create(marco), run_time=1.0)
        self.wait(1.6)

        rot.mostrar(formula_pie(r"\zeta = 1/\sqrt{2} = " + fmt(ZETA_LQR, 4)),
                    zona="abajo")
        self.wait(2.6)
        rot.mostrar(cifra_pie(f"zeta {fmt(ZETA_LQR, 3)} siempre"),
                    zona="abajo")
        self.wait(2.4)

        panel = panel_cifras(f"wn {fmt(WN_R, 2)} rad/s",
                             (f"wn {fmt(WN_L, 2)} rad/s", C_CIELO),
                             (f"zeta {fmt(ZETA_LQR, 4)}", C_OK))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)
