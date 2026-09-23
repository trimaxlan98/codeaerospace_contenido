class Clip1(Scene):
    """1.1.1 - Un operador vigila decenas de satelites; en orbita hay mas
    de dieciseis mil, dos de cada tres de una sola constelacion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Dieciseis mil satelites"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        # --- la escala humana ---------------------------------------------
        op = Square(side_length=0.34, stroke_width=0, fill_color=CODE_INK,
                    fill_opacity=1.0).move_to([-4.7, -0.3, 0])
        rng = np.random.default_rng(42)
        ang = rng.uniform(0, 2 * np.pi, 24)
        rad = rng.uniform(0.7, 1.35, 24)
        pocos = VGroup(*[Dot(op.get_center() + r * np.array([np.cos(a), np.sin(a), 0]),
                             radius=0.065, color=C_ESTATICA) for a, r in zip(ang, rad)])
        cerco = Circle(radius=1.55, stroke_color=C_TENUE, stroke_width=2).move_to(op)
        et_op = tag_junto(cerco, "un operador", DOWN, buff=0.22, font_size=24)
        self.play(FadeIn(op), Create(cerco), FadeIn(et_op), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pocos], lag_ratio=0.06),
                  run_time=1.8)
        self.wait(2.6)

        # --- la escala real: cada punto, cien satelites -------------------
        por_punto = 100
        n = int(round(ESC["activos"] / por_punto))
        n_sl = int(round(ESC["starlink"] / por_punto))
        cols, paso = 21, 0.33
        x0, y0 = -1.3, 1.1
        malla = VGroup(*[Dot([x0 + (i % cols) * paso, y0 - (i // cols) * paso, 0],
                             radius=0.095, color=C_ESTATICA) for i in range(n)])
        clave = VGroup(Dot(radius=0.095, color=C_ESTATICA),
                       tag_hud(f"= {por_punto} satelites", font_size=18, color=C_TENUE))
        clave[1].next_to(clave[0], RIGHT, buff=0.14)
        clave.next_to(malla, UP, buff=0.3).align_to(malla, LEFT)
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in malla], lag_ratio=0.012),
                  FadeIn(clave), run_time=3.2)
        self.wait(1.0)
        rot.mostrar(dato_pie(f"{ESC['activos']:,} activos".replace(",", " ")), zona="abajo", run_time=0.5)
        self.wait(4.0)

        # --- dos de cada tres, de una sola constelacion -------------------
        sl = [malla[i].copy().set_color(C_ADAPTA) for i in range(n_sl)]
        self.play(LaggedStart(*[Transform(malla[i], sl[i]) for i in range(n_sl)],
                              lag_ratio=0.01), run_time=2.6)
        self.wait(0.8)
        frac = ESC["starlink"] / ESC["activos"]
        rot.mostrar(cifra_pie(f"una constelacion = {fmt(100 * frac, 0)} %"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        # el cerco del operador frente a la malla: la proporcion se ve sola
        self.play(Indicate(cerco, color=C_ADAPTA, scale_factor=1.06), run_time=1.2)
        self.wait(3.6)
