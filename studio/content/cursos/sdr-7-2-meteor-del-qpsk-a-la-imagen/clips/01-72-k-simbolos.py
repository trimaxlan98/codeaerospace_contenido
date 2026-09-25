class Clip1(Scene):
    """7.2.1 - La constelacion QPSK de Meteor-M tal como llega tras Costas
    y el lazo de reloj (modulo 5): 400 simbolos de bits aleatorios con
    ruido a Es/N0 = 4 dB (parametro elegido, gris). La norma en gris. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("72 k simbolos"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        plano = S.PlanoIQ(unidad=1.4, alcance=1.75)
        plano.move_to(LEFT * 3.0 + DOWN * 0.05)
        self.play(Create(plano.ejes), Create(plano.unidad_circulo),
                  run_time=0.8)
        self.remove(*plano.get_family())
        self.add(plano)
        self.wait(0.4)

        # --- los 4 puntos ideales de la QPSK ---------------------------------
        ideal = S.qpsk_de_bits([0, 0, 0, 1, 1, 0, 1, 1])
        pts = plano.puntos(ideal, color=C_TITULO, radio=0.1)
        self.play(FadeIn(pts), run_time=0.6)
        self.wait(1.0)

        # --- 400 simbolos recibidos a Es/N0 = 4 dB ---------------------------
        n_sim = 400
        bits = np.random.default_rng(72).integers(0, 2, 2 * n_sim)
        rx = S.qpsk_de_bits(bits) + S.ruido_complejo(
            n_sim, 10 ** (-ESN0 / 10), 72)
        nube = plano.nube(rx, color=C_SENAL, maximo=n_sim, radio=0.045)
        self.play(LaggedStart(*[FadeIn(d) for d in nube], lag_ratio=0.02),
                  run_time=4.0)
        self.bring_to_front(pts)
        self.wait(0.8)
        t_costas = tag_dato("tras Costas y reloj", font_size=20)
        t_costas.next_to(plano, UP, buff=0.05).align_to(plano, RIGHT)
        t_costas.shift(RIGHT * 0.9)
        self.play(FadeIn(t_costas), run_time=0.5)
        rot.mostrar(dato_pie(f"Es/N0 = {fmt(ESN0, 0)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        # --- la norma, en gris ------------------------------------------------
        filas = VGroup(
            tag_dato("Meteor-M N2-4", font_size=36),
            tag_dato("137.9 MHz", font_size=36),
            tag_dato("72 k simbolos/s", font_size=36),
            tag_dato("QPSK", font_size=36),
        ).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        filas.move_to(RIGHT * 3.6 + DOWN * 0.15)
        linea = Line(filas.get_corner(UL) + LEFT * 0.35 + UP * 0.1,
                     filas.get_corner(DL) + LEFT * 0.35 + DOWN * 0.1,
                     color=C_EJE, stroke_width=2)
        self.play(Create(linea), run_time=0.5)
        for f in filas:
            self.play(FadeIn(f, shift=LEFT * 0.15), run_time=0.5)
            self.wait(1.3)
        self.wait(1.2)

        # --- la nube se ilumina: 2 bits por punto ----------------------------
        self.play(Indicate(filas[3], color=C_DATO, scale_factor=1.08),
                  nube.animate.set_fill(opacity=1.0), run_time=1.0)
        self.play(nube.animate.set_fill(opacity=0.75), run_time=0.8)
        rot.mostrar(dato_pie("NOAA APT: apagado en 2025"), zona="abajo",
                    run_time=0.5)
        self.wait(4.5)
        self.play(Indicate(filas[0], color=C_DATO, scale_factor=1.06),
                  run_time=1.0)
        self.wait(3.0)
