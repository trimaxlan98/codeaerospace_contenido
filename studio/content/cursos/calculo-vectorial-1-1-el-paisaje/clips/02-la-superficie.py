class Clip2(Scene):
    """1.1.2 - Levantar cada altura sobre su punto: la grafica z = f(x, y)
    es una superficie con colinas y valle. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La superficie")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el suelo y la regla del juego -----------------------
        esp = espacio_leccion()
        self.play(FadeIn(esp), run_time=0.9)
        rot.mostrar(pie_curso("Levantemos cada número COMO altura sobre "
                              "su punto: z = f(x, y)."), zona="abajo",
                    run_time=0.5)
        panel = panel_derecha(MathTex(r"z = f(x,\, y)", font_size=36,
                                      color=C_TITULO))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.4)

        # --- momento: la superficie se levanta ----------------------------
        rot.mostrar(pie_curso("El plano entero se alza a la vez: nace la "
                              "superficie."), zona="abajo", run_time=0.5)
        plano_cero = superficie3(esp, lambda p: 0.001, n=15, opacidad=0.55)
        sup = superficie3(esp, PAISAJE, n=15)
        self.play(FadeIn(plano_cero), run_time=0.7)
        self.play(Transform(plano_cero, sup), run_time=2.6)
        self.wait(2.8)

        # --- momento: colinas y valle, con cifras -------------------------
        rot.mostrar(pie_curso("Dos colinas y un llano: este paisaje nos "
                              "acompañará toda la familia."), zona="abajo",
                    run_time=0.5)
        cimas = VGroup()
        for p in ((1.2, 0.8), (-1.8, -1.2)):
            z = PAISAJE(np.array(p))
            d = Dot(esp.p(p[0], p[1], z), radius=0.07,
                    color=color_calor(z / Z_MAX))
            t = tag_hud(fmt(z), font_size=20, color=color_calor(z / Z_MAX))
            t.next_to(d, UP, buff=0.14)
            cimas.add(VGroup(d, t))
        self.play(LaggedStart(*[FadeIn(c, scale=0.5) for c in cimas],
                              lag_ratio=0.4), run_time=1.4)
        self.wait(4.0)

        # --- momento: el color cuenta la altura ---------------------------
        rot.mostrar(pie_curso("El color también mide: frío en el llano, "
                              "cálido en la cima."), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(cimas[0], color=C_GRAD, scale_factor=1.08),
                  run_time=0.8)
        self.wait(4.2)

        rot.mostrar(pie_curso("Pero una superficie se dibuja mal en papel. "
                              "Necesitamos su mapa."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
