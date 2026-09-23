class Clip4(Scene):
    """2.4.4 - Ninguna politica nueva toca la red sin pasar antes por su
    gemelo digital, y el gemelo solo la deja salir si el entorno de prueba
    premia adaptarse: la compuerta del margen adaptativo. Cierre. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Primero el gemelo"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        c_real, c_gem = np.array([-3.0, 0.0, 0.0]), np.array([3.6, 0.7, 0.0])
        n_r, f_r = lazo_pada(c_real, 1.9, 0.3, CODE_INK)
        n_g, f_g = lazo_pada(c_gem, 1.1, 0.2, C_TENUE, ancho=3, discontinuo=True)
        e_r = tag_hud("red real", font_size=19, color=CODE_INK).next_to(VGroup(n_r, f_r), DOWN, buff=0.25)
        e_g = tag_hud("gemelo digital", font_size=19, color=C_TENUE).next_to(VGroup(n_g, f_g), UP, buff=0.25)
        self.play(*[GrowFromCenter(n) for n in n_r], *[Create(f) for f in f_r], FadeIn(e_r), run_time=1.2)
        ang = ValueTracker(90.0)
        pulso = always_redraw(lambda: Dot(en_circulo(c_real, 1.9, ang.get_value()), radius=0.12,
                                          color=C_ADAPTA))
        self.add(pulso)
        self.play(ang.animate.set_value(-270), run_time=3.0, rate_func=linear)
        self.play(FadeIn(n_g), Create(f_g), FadeIn(e_g), ang.animate.set_value(-630), run_time=3.0,
                  rate_func=linear)
        rot.mostrar(dato_pie("NTNEnv-v2 como gemelo"), zona="abajo", run_time=0.5)
        self.wait(1.4)

        pol = Square(side_length=0.34, stroke_width=0, fill_color=C_ADAPTA,
                     fill_opacity=1.0).move_to(c_gem + UP * 2.4)
        self.play(FadeIn(pol, shift=DOWN * 0.3), ang.animate.set_value(-720), run_time=0.8, rate_func=linear)
        self.play(pol.animate.move_to(c_gem), ang.animate.set_value(-810), run_time=1.0, rate_func=linear)
        comp = Rectangle(width=1.8, height=0.16, stroke_width=0, fill_color=C_TENUE,
                         fill_opacity=1.0).move_to(c_gem + DOWN * 1.75)
        e_c = tag_hud(f"MA >= {fmt(100 * D['umbral'], 0)} %", font_size=18, color=C_TENUE)
        e_c.next_to(comp, DOWN, buff=0.15)
        self.play(FadeIn(comp), FadeIn(e_c), ang.animate.set_value(-900), run_time=0.8, rate_func=linear)
        self.play(pol.animate.move_to(comp.get_center() + UP * 0.35), ang.animate.set_value(-990),
                  run_time=0.9, rate_func=linear)
        self.play(comp.animate.set_fill(C_OK), e_c.animate.set_color(C_OK), run_time=0.5)
        rot.mostrar(dato_pie(f"G1: MA = {fmt(D['g1_ma'], 3)}"), zona="abajo", run_time=0.5)
        destino = n_r[2].get_center()
        self.play(MoveAlongPath(pol, ArcBetweenPoints(pol.get_center(), destino, angle=-35 * DEGREES)),
                  ang.animate.set_value(-1170), run_time=1.6, rate_func=linear)
        self.play(n_r[2].animate.set_stroke(C_ADAPTA), pol.animate.scale(0.6),
                  ang.animate.set_value(-1530), run_time=3.0, rate_func=linear)
        self.wait(2.0)

        self.remove(pulso)
        cierre_leccion(self, rot, "Pensar despacio por fuera,",
                       "actuar rapido por dentro.",
                       n_r, f_r, n_g, f_g, e_r, e_g, pol, comp, e_c)
