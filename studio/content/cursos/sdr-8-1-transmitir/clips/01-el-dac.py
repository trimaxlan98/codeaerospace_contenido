class Clip1(Scene):
    """8.1.1 - El DAC reconstruye un tono de 0.1 fs con retencion de orden
    cero: las muestras (ambar) se sostienen en escalones (blanco) hasta la
    siguiente. La forma de ese sostenimiento es un sinc, que es la causa de
    las imagenes del clip 2. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El DAC"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- marco propio: 2 periodos del tono (T = 1/F0_REL muestras) -----
        N = int(round(2 / F0_REL))
        ANCHO, ALTO = 11.4, 3.2
        YLIM = 1.25
        ORIG = UP * 0.15

        def en(t, y):
            fx = t / N
            fy = (y - (-YLIM)) / (2 * YLIM)
            return ORIG + np.array([(fx - 0.5) * ANCHO, (fy - 0.5) * ALTO, 0.0])

        eje = Line(en(0, 0), en(N, 0), color=C_EJE, stroke_width=1.6)
        self.play(Create(eje), run_time=0.5)

        # --- la onda ideal, continua ----------------------------------------
        t_cont = np.linspace(0.0, N, 480)
        x_cont = np.cos(2 * np.pi * F0_REL * t_cont)
        ideal = VMobject(stroke_color=C_SENAL, stroke_width=2.2)
        ideal.set_points_as_corners([en(t, x) for t, x in zip(t_cont, x_cont)])
        ideal.set_stroke(opacity=0.55)
        t_ideal = tag_junto(ideal, "onda ideal", UP, buff=0.18, font_size=20,
                            color=C_SENAL)
        t_ideal.move_to(en(N * 0.18, 1.35))
        self.play(Create(ideal), run_time=1.8)
        self.play(FadeIn(t_ideal), run_time=0.4)
        self.wait(1.0)

        # --- las muestras, ambar ---------------------------------------------
        n_s = np.arange(0, N + 1)
        x_s = np.cos(2 * np.pi * F0_REL * n_s)
        muestras = VGroup(*[Dot(en(n, x), radius=0.07, color=C_SENAL)
                            for n, x in zip(n_s, x_s)])
        t_mue = tag_junto(muestras[1], "muestras", DOWN, buff=0.55,
                          font_size=20, color=C_SENAL)
        t_mue.shift(LEFT * 0.6)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in muestras],
                              lag_ratio=0.12), run_time=1.6)
        self.play(FadeIn(t_mue), run_time=0.4)
        rot.mostrar(dato_pie(f"tono en {fmt(F0_REL, 1)} fs"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- la escalera del DAC: retencion de orden cero, blanca -----------
        pts = []
        for i, ti in enumerate(n_s):
            pts.append(en(ti, x_s[i]))
            if i + 1 < len(n_s):
                pts.append(en(n_s[i + 1], x_s[i]))
        escalera = VMobject(stroke_color=C_TITULO, stroke_width=2.8)
        escalera.set_points_as_corners(pts)
        t_esc = tag_junto(escalera, "salida DAC", DOWN, buff=0.5,
                          font_size=20, color=C_TITULO)
        t_esc.shift(RIGHT * 3.4)
        self.play(Create(escalera), run_time=2.4)
        self.play(FadeIn(t_esc), run_time=0.4)
        self.wait(3.2)

        # --- la forma del sostenimiento es un sinc ---------------------------
        rot.mostrar(formula_pie(r"|H(f)| = \left|\mathrm{sinc}(f/f_s)\right|"),
                   zona="abajo", run_time=0.5)
        self.wait(6.0)
        self.play(Indicate(escalera, color=C_TITULO, scale_factor=1.02),
                  run_time=1.2)
        self.wait(6.5)
