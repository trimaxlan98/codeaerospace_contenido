class Clip3(Scene):
    """1.3.3 - O-RAN separa los lazos por escala de tiempo: tiempo real,
    near-RT (10 ms a 1 s) y non-RT (mas de 1 s). Lo que piensa despacio va
    por fuera; lo que actua rapido, por dentro. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Tres lazos, tres ritmos"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        c = np.array([-2.2, -0.35, 0.0])
        radios = [0.85, 1.75, 2.65]
        colores = [CODE_INK, C_ENLACE, C_ADAPTA]
        anillos = VGroup(*[Circle(radius=r, stroke_color=col, stroke_width=3, stroke_opacity=0.7)
                           .move_to(c) for r, col in zip(radios, colores)])
        red = VGroup(*[Dot(c + 0.35 * np.array([np.cos(a), np.sin(a), 0]), radius=0.07,
                           color=C_TENUE) for a in np.linspace(0, 2 * PI, 5, endpoint=False)])
        self.play(FadeIn(red), run_time=0.5)
        etiquetas = VGroup()
        for (nombre, escala), r, col in zip(LAZOS, radios, colores):
            e = VGroup(tag_hud(nombre, font_size=19, color=col),
                       tag_hud(escala, font_size=17, color=C_DATO)).arrange(DOWN, buff=0.08,
                                                                            aligned_edge=LEFT)
            etiquetas.add(e)
        etiquetas.arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to([3.7, 0.0, 0])
        for anillo, e in zip(anillos, etiquetas):
            self.play(Create(anillo), FadeIn(e, shift=LEFT * 0.1), run_time=0.9)
            self.wait(0.6)

        # un pulso por lazo; las velocidades estan en razon 16 : 4 : 1
        t = ValueTracker(0.0)
        vel = [16.0, 4.0, 1.0]
        pulsos = [always_redraw(lambda r=r, v=v, col=col: Dot(
            c + r * np.array([np.cos(v * t.get_value()), np.sin(v * t.get_value()), 0]),
            radius=0.11, color=col)) for r, v, col in zip(radios, vel, colores)]
        self.add(*pulsos)
        self.play(t.animate.set_value(2 * PI), run_time=8.0, rate_func=linear)
        rot.mostrar(dato_pie("O-RAN: xApp y rApp"), zona="abajo", run_time=0.5)
        self.play(t.animate.set_value(3 * PI), run_time=4.0, rate_func=linear)

        # dónde vive cada modulo de PADA (mapa de la tesis, COMPATIBILIDAD)
        mods = VGroup(tag_hud("Accion", font_size=18, color=CODE_INK),
                      tag_hud("Decision", font_size=18, color=C_ENLACE),
                      tag_hud("Analisis", font_size=18, color=C_ADAPTA))
        for m, r in zip(mods, radios):
            m.move_to(c + np.array([0, r + 0.02, 0]))
            m.add_background_rectangle(color=CODE_BG, opacity=0.9, buff=0.06)
        self.play(LaggedStart(*[FadeIn(m) for m in mods], lag_ratio=0.3), run_time=1.2)
        self.play(t.animate.set_value(4 * PI), run_time=4.0, rate_func=linear)
        rot.mostrar(dato_pie("PADA sobre los lazos"), zona="abajo", run_time=0.5)
        self.wait(4.8)
