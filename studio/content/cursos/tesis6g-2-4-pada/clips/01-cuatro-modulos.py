class Clip1(Scene):
    """2.4.1 - PADA: percibir, analizar, decidir, actuar, y vuelta a
    percibir. Un lazo cerrado de gobernanza sobre la red, no un controlador
    mas dentro de ella. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Cuatro modulos"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        c, r = np.array([0.0, 0.1, 0.0]), 1.85
        nodos, flechas = lazo_pada(c, r, 0.36, CODE_INK)
        etq = VGroup()
        for (nm, g), n in zip(MODULOS, nodos):
            e = tag_junto(n, nm, en_circulo(np.zeros(3), 1.0, g), buff=0.2, font_size=26,
                          color=CODE_INK)
            etq.add(e)
        red = VGroup(*[Dot(c + 0.45 * np.array([np.cos(a), np.sin(a), 0]), radius=0.08, color=C_TENUE)
                       for a in np.linspace(0, 2 * PI, 5, endpoint=False)])
        self.play(FadeIn(red), run_time=0.5)
        for n, e in zip(nodos, etq):
            self.play(GrowFromCenter(n), FadeIn(e), run_time=0.6)
            self.wait(1.4)
        self.play(*[Create(f) for f in flechas], run_time=1.2)
        self.wait(1.2)
        rot.mostrar(dato_pie("PADA, capitulo 3"), zona="abajo", run_time=0.5)
        ang = ValueTracker(90.0)
        pulso = always_redraw(lambda: Dot(en_circulo(c, r, ang.get_value()), radius=0.13, color=C_ADAPTA))
        self.add(pulso)
        self.play(ang.animate.set_value(90 - 720), run_time=6.0, rate_func=linear)
        rot.mostrar(dato_pie("capa de gobernanza, no controlador"), zona="abajo", run_time=0.5)
        self.play(ang.animate.set_value(90 - 1440), run_time=6.0, rate_func=linear)
        self.wait(2.4)
        self.wait(1.6)
